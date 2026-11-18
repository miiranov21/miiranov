"""Автосубтитры (крупные слова по центру, как в Shorts) через faster-whisper."""
from __future__ import annotations

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


def make_ass(media: str, ass_path: str, model: str = "small", language: str | None = None,
             words_per_line: int = 3) -> str:
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
            text = " ".join(w.word.strip() for w in ln).upper()
            text = text.replace("{", "(").replace("}", ")").replace("\n", " ")
            f.write(f"Dialogue: 0,{_ts(start)},{_ts(end)},Default,,0,0,0,,{text}\n")
    return " ".join(w.word.strip() for w in words)


def available() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False
