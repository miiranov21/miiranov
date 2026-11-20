"""Фильтры качества «Доктора» (strategy.json → quality_filters): не брать моменты, где стример спит или отошёл.

Всё локально и бесплатно:
  * чат про сон — доля сообщений «wake up», «zzz», «😴»… в окне момента;
  * неподвижная картинка — разница соседних кадров (без вебки и полос интерфейса);
  * вебка — есть ли лицо и двигается ли оно;
  * голос стримера — по субтитрам (faster-whisper) или по голосовой полосе 300–3400 Гц; озвучка донатов (TTS)
    и ровная музыка не считаются.
Решение осторожное: спокойный момент, где стример говорит, не выбрасываем.
"""
from __future__ import annotations

import os
import re
import subprocess

import numpy as np

FLAGS = 0x08000000 if os.name == "nt" else 0

DEFAULT_SLEEP_WORDS = ["sleep", "sleeping", "asleep", "wake up", "wakeup", "zzz", "😴", "💤", "snoring", "nap",
                       "goodnight", "gn", "спит", "проснись", "спать"]
DEFAULT_TITLE_WORDS = ["sleep stream", "sleeping", "24/7", "24 hour", "subathon sleep"]
TTS_MARKERS = ("donated", "donation", "dollars", "bits", "cheered", "gifted", "subscribed", "resubscribed",
               "tier", "says:", "said:", "thank you for the", "thanks for the")

# пороги (подобраны осторожно: лучше пропустить спящего, чем выкинуть смешной спокойный момент)
STATIC_MOTION = 1.6        # средняя разница соседних кадров игры (0–255) — ниже: картинка почти стоит
FACE_STILL = 1.2           # средняя разница кадров внутри лица — ниже: лицо не двигается
VOICE_MIN = 0.20           # доля клипа с голосом стримера
SILENT = 0.08              # почти ни слова — не берём, даже если картинка двигается


def rules() -> dict:
    try:
        from . import strategy
        q = strategy.get().get("quality_filters") or {}
        return q if isinstance(q, dict) else {}
    except Exception:
        return {}


def enabled() -> bool:
    return bool(rules())


# ---------- 1) чат про сон ----------
def _matcher(words: list[str]):
    alpha = [w for w in words if re.fullmatch(r"[\w' ]+", w)]
    other = [w for w in words if w not in alpha]
    rx = re.compile(r"(?<![\w])(" + "|".join(re.escape(w) for w in sorted(alpha, key=len, reverse=True)) + r")(?![\w])",
                    re.I) if alpha else None

    def hit(text: str) -> bool:
        t = (text or "").lower()
        return bool((rx and rx.search(t)) or any(o in t for o in other))
    return hit


def sleep_share(msgs, t0: float, t1: float) -> tuple[float, int]:
    """(доля сообщений про сон, сколько всего сообщений) в окне [t0, t1]."""
    rs = rules().get("reject_sleep") or {}
    hit = _matcher([w.lower() for w in (rs.get("chat_keywords") or DEFAULT_SLEEP_WORDS)])
    win = [m for m in msgs if t0 <= m.t <= t1]
    if not win:
        return 0.0, 0
    return sum(1 for m in win if hit(m.text)) / len(win), len(win)


def sleep_threshold(title: str) -> float:
    rs = rules().get("reject_sleep") or {}
    thr = float(rs.get("chat_keyword_share") or 0.25)
    words = [w.lower() for w in (rs.get("title_keywords") or DEFAULT_TITLE_WORDS)]
    if any(w in (title or "").lower() for w in words):
        thr *= 0.6  # «sleep stream», «24/7» в названии — осторожнее во всём стриме
    return thr


def filter_highlights(hl: list, msgs, title: str, channel: str, chat_lag: float = 5.0, log=print) -> list:
    """Убирает моменты, где чат в основном про сон стримера."""
    if not enabled() or not msgs:
        return hl
    thr = sleep_threshold(title)
    out = []
    for h in hl:
        share, n = sleep_share(msgs, h.start, h.end + chat_lag)
        if n >= 8 and share >= thr:
            from .pipeline import _fmt
            log(f"💤 пропущен момент {_fmt(h.peak)} у {channel} — стример спит (чат: {share:.0%} про сон)")
            continue
        out.append(h)
    return out


# ---------- 2–4) картинка, вебка, голос ----------
def _frames(path: str, fps: float = 2.0, w: int = 320):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", path], capture_output=True, text=True, creationflags=FLAGS)
    try:
        W, H = [int(x) for x in r.stdout.strip().split(",")[:2]]
    except ValueError:
        return None
    h = int(round(H * w / W / 2) * 2)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
                        "-pix_fmt", "bgr24", "-"], capture_output=True, creationflags=FLAGS)
    data = np.frombuffer(r.stdout, dtype=np.uint8)
    n = data.size // (w * h * 3)
    if n < 2:
        return None
    return data[: n * w * h * 3].reshape(n, h, w, 3)


def visual_metrics(path: str, facecam: tuple | None) -> dict:
    """motion — движение в игре; face_seen — доля кадров с лицом на вебке; face_still — доля кадров,
    где лицо почти не двигается (среди кадров с лицом)."""
    fr = _frames(path)
    if fr is None:
        return {}
    n, h, w, _ = fr.shape
    gray = fr.mean(axis=3)
    mask = np.ones((h, w), dtype=bool)
    mask[: int(h * 0.08)] = False      # полосы интерфейса (донаты, счётчики)
    mask[int(h * 0.92):] = False
    cam = None
    if facecam:
        x, y, fw, fh = facecam
        cam = (int(x * w), int(y * h), max(2, int(fw * w)), max(2, int(fh * h)))
        mask[cam[1]:cam[1] + cam[3] + 1, cam[0]:cam[0] + cam[2] + 1] = False
    diffs = np.abs(np.diff(gray, axis=0))
    motion = float(diffs[:, mask].mean()) if mask.any() else float(diffs.mean())
    out = {"motion": round(motion, 2), "frames": n}
    if cam:
        from . import facecam as fc
        seen, still, prev_box = 0, 0, None
        big = _frames(path, fps=2.0, w=640)
        if big is not None:
            bn, bh, bw, _ = big.shape
            cx, cy, cw, ch = (int(facecam[0] * bw), int(facecam[1] * bh), int(facecam[2] * bw), int(facecam[3] * bh))
            prev_crop = None
            for i in range(bn):
                crop = np.ascontiguousarray(big[i, cy:cy + ch, cx:cx + cw])
                if crop.size == 0:
                    continue
                faces = fc._faces(crop, crop.shape[1], crop.shape[0])
                if faces:
                    seen += 1
                    fx, fy, fw_, fh_ = max(faces, key=lambda f: f[2] * f[3])
                    box = (int(fx * crop.shape[1]), int(fy * crop.shape[0]),
                           max(4, int(fw_ * crop.shape[1])), max(4, int(fh_ * crop.shape[0])))
                    g = crop.mean(axis=2)
                    if prev_crop is not None and prev_box is not None:
                        x0, y0, bw_, bh_ = box
                        a = g[y0:y0 + bh_, x0:x0 + bw_]
                        b = prev_crop[y0:y0 + bh_, x0:x0 + bw_]
                        shift = abs(box[0] - prev_box[0]) + abs(box[1] - prev_box[1])
                        if a.shape == b.shape and a.size and float(np.abs(a - b).mean()) < FACE_STILL and shift <= 2:
                            still += 1
                    prev_crop, prev_box = g, box
                else:
                    prev_crop, prev_box = None, None
            out["face_seen"] = round(seen / max(1, bn), 2)
            out["face_still"] = round(still / max(1, seen - 1), 2) if seen > 1 else 0.0
    return out


def voice_ratio_energy(path: str) -> float:
    """Доля клипа с голосом по голосовой полосе: всплески над «ковром» звука (ровная музыка не считается)."""
    from .shape import voice_energy
    db = voice_energy(path)
    if db.size < 10:
        return 0.0
    floor = float(np.percentile(db, 20))
    if float(np.percentile(db, 90)) - floor < 6:  # всё ровное — музыка или тишина
        return 0.0
    active = db > floor + 8
    # голос «рваный»: короткие всплески; убираем одиночные кусочки 50 мс
    k = np.convolve(active.astype(float), np.ones(5) / 5, mode="same") > 0.4
    return float(k.mean())


def voice_ratio_words(words: list, duration: float) -> float:
    """Доля клипа с речью стримера по субтитрам; фразы-озвучки донатов (TTS) не считаем."""
    if not words or duration <= 0:
        return 0.0
    # разбиваем на фразы по паузам ≥0,6 с
    phrases, cur = [], [words[0]]
    for w in words[1:]:
        if w[0] - cur[-1][1] >= 0.6:
            phrases.append(cur)
            cur = [w]
        else:
            cur.append(w)
    phrases.append(cur)
    talk = 0.0
    for ph in phrases:
        text = " ".join(str(w[2]) for w in ph).lower()
        if any(m in text for m in TTS_MARKERS):
            continue
        talk += max(0.0, ph[-1][1] - ph[0][0])
    return min(1.0, talk / duration)


def verdict(vis: dict, voice: float, has_cam: bool, by_energy: bool = False) -> str | None:
    """None — момент хороший; иначе причина, почему не брать."""
    if voice >= VOICE_MIN and by_energy and has_cam and vis.get("face_seen", 0) >= 0.4 \
            and vis.get("face_still", 0) > 0.85:
        # голос есть, а лицо совсем не двигается — говорит не стример (озвучка доната, видео на фоне)
        return "стример спит (голос — похоже, озвучка доната)"
    if voice >= VOICE_MIN:
        return None  # стример говорит — спокойный момент со смешной речью оставляем
    motion = vis.get("motion", 99.0)
    if has_cam and vis.get("face_seen", 1.0) < 0.4:
        return "стримера нет в кадре (отошёл)"
    if voice < SILENT and motion < STATIC_MOTION * 2:
        return "стример молчит и в кадре почти ничего не происходит"
    if has_cam and vis.get("face_seen", 0) >= 0.4 and vis.get("face_still", 0) > 0.7:
        return "стример спит (лицо не двигается)"
    if motion < STATIC_MOTION:
        return "кадр почти не двигается и стример молчит"
    return None


def duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=FLAGS)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def check_clip(path: str, facecam: tuple | None, words: list | None = None) -> tuple[str | None, dict]:
    """(причина отказа или None, метрики) для готового или нарезанного куска."""
    vis = visual_metrics(path, facecam)
    dur = duration(path)
    voice = voice_ratio_words(words, dur) if words else voice_ratio_energy(path)
    m = dict(vis, voice=round(voice, 2), by="subs" if words else "energy")
    return verdict(vis, voice, bool(facecam), by_energy=not words), m
