"""Автосубтитры (крупные слова по центру, как в Shorts) через faster-whisper."""
from __future__ import annotations

_model = None
_model_name = None

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


def _get_model(name: str):
    global _model, _model_name
    if _model is None or _model_name != name:
        from faster_whisper import WhisperModel
        _model = WhisperModel(name, device="auto", compute_type="auto")
        _model_name = name
    return _model


def make_ass(media: str, ass_path: str, model: str = "small", language: str | None = None,
             words_per_line: int = 3) -> bool:
    """Распознаёт речь и пишет .ass файл. Возвращает False, если речи нет."""
    segments, _ = _get_model(model).transcribe(media, language=language, word_timestamps=True, vad_filter=True)
    words = [w for s in segments for w in (s.words or []) if w.word.strip()]
    if not words:
        return False
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
    return True
