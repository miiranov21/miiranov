"""Автосубтитры (крупные слова по центру, как в Shorts) через faster-whisper."""
from __future__ import annotations

import re

_model = None
_model_name = None
LAST_WORDS: list = []  # слова последнего клипа: (начало, конец, слово) — для цитаты стримера в надписи

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ts(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _load_audio(media: str, sr: int = 16000):
    """Звук клипа как массив чисел 16 кГц моно (такой ждёт распознавание речи)."""
    import subprocess
    import numpy as np
    flags = 0x08000000 if __import__("os").name == "nt" else 0
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", media, "-vn", "-ac", "1", "-ar", str(sr),
                        "-f", "s16le", "-"], capture_output=True, creationflags=flags)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("не удалось достать звук из клипа: " + r.stderr.decode("utf-8", "replace")[-300:])
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def _quiet_huggingface() -> None:
    """Прячем служебные предупреждения библиотеки скачивания моделей (про symlinks, токен и т.п.) —
    они безвредны, но пугают в журнале."""
    import logging
    import os
    import warnings
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    warnings.filterwarnings("ignore", module="huggingface_hub")
    warnings.filterwarnings("ignore", message=".*symlink.*")
    warnings.filterwarnings("ignore", message=".*Developer Mode.*")
    for name in ("huggingface_hub", "faster_whisper"):
        logging.getLogger(name).setLevel(logging.ERROR)
    try:
        from huggingface_hub.utils import logging as hf_logging
        hf_logging.set_verbosity_error()
    except Exception:
        pass


def _get_model(name: str):
    global _model, _model_name
    if _model is None or _model_name != name:
        _quiet_huggingface()
        from faster_whisper import WhisperModel
        print(f"    загружаю модель распознавания речи «{name}» (в первый раз скачается ~0.5 ГБ)...")
        _model = WhisperModel(name, device="auto", compute_type="auto")
        _model_name = name
    return _model


KEYWORDS = {"no", "what", "wait", "bro", "yo", "oh", "insane", "crazy", "dead", "run", "stop", "help", "why", "god", "omg",
            "lets", "let's", "go", "bruh", "nah", "yes", "wow", "never", "huh", "how", "dude", "chill", "please", "won",
            "lost", "win", "lose", "fire", "scared", "crying", "jesus", "nooo", "noo", "boom", "gg", "rip", "hell",
            "нет", "что", "стоп", "блин", "жесть", "капец", "давай", "беги", "помогите", "почему", "боже", "вау", "да"}
HL_CUR = "&H0000E5FF&"   # текущее слово — жёлтое
HL_KEY = "&H0066FF00&"   # ключевое слово — зелёное и крупнее


def is_keyword(word: str) -> bool:
    w = (word or "").strip()
    core = re.sub(r"[^\w']", "", w.lower())
    if not core:
        return False
    return core in KEYWORDS or w.endswith(("!", "?")) or core.isdigit() or re.search(r"(.)\1\1", core) is not None


def styled_words(texts: list[str], raw: list[str], cur: int | None) -> str:
    """Строка субтитров: ключевые слова зелёные и крупнее, текущее слово — жёлтое."""
    out = []
    for j, (t, r) in enumerate(zip(texts, raw)):
        key = is_keyword(r)
        if j == cur:
            out.append("{\\c" + HL_CUR + ("\\fscx118\\fscy118" if key else "\\fscx108\\fscy108") + "}" + t
                       + "{\\c&H00FFFFFF&\\fscx100\\fscy100}")
        elif key:
            out.append("{\\c" + HL_KEY + "\\fscx115\\fscy115}" + t + "{\\c&H00FFFFFF&\\fscx100\\fscy100}")
        else:
            out.append(t)
    return " ".join(out)


def _clean_word(w: str, censor: bool = True) -> str:
    if censor:
        from .policy import censor_text
        w = censor_text(w)
    return w.upper().replace("{", "(").replace("}", ")").replace("\n", " ")


def make_ass(media: str, ass_path: str, model: str = "small", language: str | None = None,
             words_per_line: int = 3, censor: bool = True) -> str:
    """Распознаёт речь и пишет .ass файл. Возвращает распознанный текст ('' — речи нет)."""
    m = _get_model(model)
    audio = _load_audio(media)  # звук вынимаем сами через ffmpeg — без капризной библиотеки av
    try:
        segments, _ = m.transcribe(audio, language=language, word_timestamps=True, vad_filter=True)
        segments = list(segments)
    except Exception as e:
        if "onnxruntime" not in str(e):
            raise
        # фильтр тишины требует onnxruntime (под новые Python его может не быть) — распознаём без него
        segments, _ = m.transcribe(audio, language=language, word_timestamps=True, vad_filter=False)
        segments = list(segments)
    words = [w for s in segments for w in (s.words or []) if w.word.strip()]
    global LAST_WORDS
    LAST_WORDS = [(float(w.start), float(w.end), w.word) for w in words]
    if not words:
        return ""
    try:
        from .shape import trick
        highlight = bool(trick("subtitle_keyword_highlight", True))
    except Exception:
        highlight = False
    lines, cur = [], []
    for w in words:
        if cur and (len(cur) >= words_per_line or w.start - cur[-1].end > 0.6):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        for i, ln in enumerate(lines):
            start = ln[0].start
            end = ln[-1].end + 0.15
            if i + 1 < len(lines):
                end = min(end, lines[i + 1][0].start)
            if highlight:  # пословно: текущее слово жёлтое, ключевые — зелёные и крупнее
                raw = [w.word.strip() for w in ln]
                texts = [_clean_word(r, censor) for r in raw]
                for wi, w in enumerate(ln):
                    a = w.start if wi else start
                    b = ln[wi + 1].start if wi + 1 < len(ln) else end
                    if b > a:
                        f.write(f"Dialogue: 0,{_ts(a)},{_ts(b)},Default,,0,0,0,,{styled_words(texts, raw, wi)}\n")
                continue
            text = " ".join(w.word.strip() for w in ln)
            if censor:  # мат и оскорбления в субтитрах — звёздочками (платформы читают и текст на видео)
                from .policy import censor_text
                text = censor_text(text)
            text = text.upper()
            text = text.replace("{", "(").replace("}", ")").replace("\n", " ")
            f.write(f"Dialogue: 0,{_ts(start)},{_ts(end)},Default,,0,0,0,,{text}\n")
    return " ".join(w.word.strip() for w in words)


def available() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False
