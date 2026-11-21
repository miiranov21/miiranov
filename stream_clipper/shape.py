"""Форма клипа по правилам «Доктора» (strategy.json → clip_settings):
длина под момент с границами по паузам в речи и выбор, сколько игры показывать в кадре (game_view = auto)."""
from __future__ import annotations

import os
import subprocess

import numpy as np

FLAGS = 0x08000000 if os.name == "nt" else 0
PAD = 2.0  # при «длине под момент» кусок режется с запасом по 2 с с каждой стороны — границу потом ставим в паузу
VIEW_NAMES = {"center": "центр", "wide": "крупнее", "full": "целиком"}


def length_rules() -> dict:
    try:
        from . import strategy
        r = (strategy.get().get("clip_settings") or {}).get("length_rules") or {}
        return r if isinstance(r, dict) else {}
    except Exception:
        return {}


TRICKS = ("pattern_interrupt_sec", "speed_talk", "hook_from_frame0", "subtitle_keyword_highlight", "voice_over_game_db",
          "question_overlay", "freeze_wait", "sfx_accents", "instant_replay", "face_fullscreen_on_peak", "context_line")


def defaults() -> dict:
    """clip_settings.defaults из стратегии «Доктора» (с твоими ✋-значениями поверх)."""
    try:
        from . import strategy
        d = (strategy.get().get("clip_settings") or {}).get("defaults") or {}
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def trick(name: str, default=False):
    """Значение приёма монтажа: False/0 — выключен; True или число — включён."""
    v = defaults().get(name, default)
    return v


def min_max() -> tuple[float, float]:
    r = length_rules()
    try:
        lo = float(r.get("min_sec") or 10)
        hi = float(r.get("max_sec") or 60)
    except (TypeError, ValueError):
        lo, hi = 10.0, 60.0
    lo = max(5.0, min(lo, 60.0))
    hi = max(lo + 5, min(hi, 180.0))
    return lo, hi


def target_for(platform: str) -> tuple[float, float] | None:
    t = (length_rules().get("target_sec") or {}).get(platform)
    try:
        return float(t[0]), float(t[1])
    except (TypeError, ValueError, IndexError, KeyError):
        return None


def _duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=FLAGS)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def voice_energy(path: str, hop: float = 0.05) -> np.ndarray:
    """Громкость голосовой полосы (300–3400 Гц) по кусочкам 50 мс, в дБ."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "8000",
                        "-af", "highpass=f=300,lowpass=f=3400", "-f", "s16le", "-"],
                       capture_output=True, creationflags=FLAGS)
    pcm = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32)
    n = int(8000 * hop)
    if pcm.size < n:
        return np.zeros(0, dtype=np.float32)
    frames = pcm[: pcm.size // n * n].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1)) + 1e-3
    return 20 * np.log10(rms)


def pauses(db: np.ndarray, hop: float = 0.05, min_len: float = 0.4) -> list[tuple[float, float]]:
    """Паузы в голосе ≥ min_len: [(начало, конец)] в секундах."""
    if db.size == 0:
        return []
    quiet_level = min(float(np.percentile(db, 25)) + 4.0, float(np.median(db)) - 2.0)
    quiet = db <= quiet_level
    out, i, n = [], 0, len(db)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * hop >= min_len:
                out.append((i * hop, j * hop))
            i = j
        else:
            i += 1
    return out


def snap_bounds(segment: str, pad_start: float, pad_end: float, words: list | None = None,
                lo: float | None = None, hi: float | None = None) -> tuple[float, float]:
    """Куда поставить начало и конец внутри куска с запасами: начало — в паузу возле задуманного начала
    (не с середины фразы), конец — в паузу возле задуманного конца (не на середине слова). (a, b) в секундах куска."""
    dur = _duration(segment)
    if dur <= 0:
        return 0.0, dur
    lo_, hi_ = min_max()
    lo = lo or lo_
    hi = hi or hi_
    want_a, want_b = pad_start, max(pad_start + 1, dur - pad_end)
    a, b = want_a, want_b
    if words:  # есть субтитры: границы — между словами
        gaps = [(words[i][1], words[i + 1][0]) for i in range(len(words) - 1)
                if words[i + 1][0] - words[i][1] >= 0.25]
        starts = [g[1] - 0.1 for g in gaps if 0 <= g[1] - 0.1 <= want_a + 0.5]
        if starts:
            a = max(0.0, max(starts))
        ends = [g[0] + 0.25 for g in gaps if want_b - 0.5 <= g[0] + 0.25 <= dur]
        if ends:
            b = min(ends)
        elif words and words[-1][1] > want_b - 0.5:
            b = min(dur, words[-1][1] + 0.3)
    else:  # по паузам в голосе ≥0,4 с
        ps = pauses(voice_energy(segment))
        starts = [p[1] - 0.15 for p in ps if 0 <= p[1] - 0.15 <= want_a + 0.5]
        if starts:
            a = max(0.0, max(starts))
        ends = [p[0] + 0.25 for p in ps if want_b - 0.5 <= p[0] + 0.25 <= dur]
        if ends:
            b = min(ends)
    if b - a < lo:
        b = min(dur, a + lo)
        a = max(0.0, b - lo)
    if b - a > hi:
        a = b - hi
    return round(max(0.0, a), 2), round(min(dur, b), 2)


def trim(segment: str, a: float, b: float, out: str) -> str:
    """Точный рез куска [a, b] (перекодирование почти без потерь)."""
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.2f}", "-i", segment, "-t", f"{b - a:.2f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-c:a", "aac", "-b:a", "192k", out],
                       capture_output=True, creationflags=FLAGS)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="replace")[-300:])
    return out


# ---------- сколько игры показывать: center / wide / full ----------
def _gray_frames(segment: str, center: float, span: float = 3.0, n: int = 8) -> np.ndarray:
    w, h = 96, 54
    dur = _duration(segment) or (center + span)
    t0 = max(0.0, min(center - span, dur - 2 * span))
    fps = n / (2 * span)
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.2f}", "-i", segment, "-t", f"{2 * span:.2f}",
                        "-vf", f"fps={fps:.3f},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, creationflags=FLAGS)
    data = np.frombuffer(r.stdout, dtype=np.uint8)
    k = data.size // (w * h)
    return data[: k * w * h].reshape(k, h, w).astype(np.float32) if k else np.zeros((0, h, w), np.float32)


def heuristic_view(segment: str, center: float, facecam: tuple | None = None) -> tuple[str, str]:
    """Без Claude: где на экране движение (разница кадров). В центральной полосе → center,
    заметно у краёв → full, иначе → wide."""
    fr = _gray_frames(segment, center)
    if len(fr) < 3:
        return "wide", "мало кадров — по умолчанию"
    motion = np.abs(np.diff(fr, axis=0)).mean(axis=0)  # h × w
    h, w = motion.shape
    if facecam:  # вебка внутри игры двигается всегда — её не считаем
        x, y, fw, fh = facecam
        motion[int(y * h):int((y + fh) * h) + 1, int(x * w):int((x + fw) * w) + 1] = 0
    motion[: int(h * 0.08)] = 0  # верхняя полоса (часто счётчики/чат)
    total = float(motion.sum())
    if total < w * h * 0.6:
        return "wide", "почти нет движения — по умолчанию"
    cols = motion.sum(axis=0) / total
    mid = cols[int(w * 0.23):int(w * 0.77)].sum()  # то, что видно при «только центр» (~54% ширины)
    edges = cols[: int(w * 0.125)].sum() + cols[int(w * 0.875):].sum()  # то, что теряется даже при «крупнее»
    if mid >= 0.78:
        return "center", f"движение в центре ({mid:.0%})"
    if edges >= 0.22:
        return "full", f"движение у краёв ({edges:.0%})"
    return "wide", f"движение шире центра ({mid:.0%} в центре)"


VIEW_PROMPT = """You choose how much of a game screen to keep when a horizontal livestream is turned into a vertical Short.
Options:
- center: the action is in the middle (character, car, crosshair) and the edges do not matter — biggest and most readable on a phone;
- wide: the action is wider than the center but small UI and edges are not needed (the default);
- full: the whole picture matters — a map, a menu, a full-screen scene, the event happens near the edge, on-screen game text.
{rules}
Ignore the streamer's webcam overlay and stream overlays. If unsure, answer wide.
Reply with exactly one word: center, wide or full."""


def claude_view(key: str, frames: list[str]) -> str | None:
    import base64
    import anthropic
    from . import strategy
    rules = (strategy.get().get("clip_settings") or {}).get("game_view_rules") or {}
    extra = "\n".join(f"{k}: {v}" for k, v in rules.items() if k in ("center", "wide", "full")) if isinstance(rules, dict) else ""
    content: list = []
    for p in frames[:3]:
        with open(p, "rb") as f:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                        "data": base64.standard_b64encode(f.read()).decode()}})
    if not content:
        return None
    content.append({"type": "text", "text": "Frames from the moment, in order. Which option?"})
    client = anthropic.Anthropic(api_key=key, max_retries=2)
    resp = client.beta.messages.create(
        model="claude-opus-5-5", max_tokens=1000, output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        system=VIEW_PROMPT.format(rules=("Strategy notes:\n" + extra) if extra else ""),
        messages=[{"role": "user", "content": content}])
    text = next((b.text for b in resp.content if b.type == "text"), "").strip().lower()
    for v in ("center", "full", "wide"):
        if v in text.split() or text.startswith(v):
            return v
    return None


def choose_view(segment: str, center: float, key: str | None, frames: list[str] | None = None,
                facecam: tuple | None = None, log=print) -> tuple[str, str]:
    """(вариант, почему). С ключом Claude — по кадрам, без ключа или при ошибке — по движению."""
    if key and frames:
        try:
            v = claude_view(key, frames)
            if v:
                return v, "по кадрам (Claude)"
        except Exception as e:
            log(f"    кадр по Claude не выбрался ({e}) — смотрю по движению")
    try:
        return heuristic_view(segment, center, facecam)
    except Exception as e:
        return "wide", f"не удалось определить ({e})"
