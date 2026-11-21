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


DEFAULT_T = {"static_motion": STATIC_MOTION, "face_still": FACE_STILL, "voice_min": VOICE_MIN, "silence_max": SILENT,
             "face_absent_max": 0.60, "face_still_max": 0.70, "tts_face_still": 0.85, "title_keyword_factor": 0.6,
             "min_chat_messages": 8}


def th(name: str) -> float:
    """Порог из strategy.json → quality_filters.thresholds (если нет — значение по умолчанию)."""
    try:
        v = (rules().get("thresholds") or {}).get(name)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else float(DEFAULT_T[name])
    except Exception:
        return float(DEFAULT_T[name])


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
        thr *= th("title_keyword_factor")  # «sleep stream», «24/7» в названии — осторожнее во всём стриме
    return thr


def filter_highlights(hl: list, msgs, title: str, channel: str, chat_lag: float = 5.0, log=print) -> list:
    """Убирает моменты, где чат в основном про сон стримера."""
    if not enabled() or not msgs:
        return hl
    thr = sleep_threshold(title)
    out = []
    for h in hl:
        share, n = sleep_share(msgs, h.start, h.end + chat_lag)
        if n >= th("min_chat_messages") and share >= thr:
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
                        if a.shape == b.shape and a.size and float(np.abs(a - b).mean()) < th("face_still") and shift <= 2:
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
    """None — момент хороший; иначе причина, почему не брать. Пороги — из стратегии «Доктора»."""
    vmin, silent, still_max = th("voice_min"), th("silence_max"), th("face_still_max")
    seen_min = 1.0 - th("face_absent_max")
    motion_min = th("static_motion")
    if voice >= vmin and by_energy and has_cam and vis.get("face_seen", 0) >= seen_min \
            and vis.get("face_still", 0) > th("tts_face_still"):
        # голос есть, а лицо совсем не двигается — говорит не стример (озвучка доната, видео на фоне)
        return "стример спит (голос — похоже, озвучка доната)"
    if voice >= vmin:
        return None  # стример говорит — спокойный момент со смешной речью оставляем
    motion = vis.get("motion", 99.0)
    if has_cam and vis.get("face_seen", 1.0) < seen_min:
        return "стримера нет в кадре (отошёл)"
    if voice < silent and motion < motion_min * 2:
        return "стример молчит и в кадре почти ничего не происходит"
    if has_cam and vis.get("face_seen", 0) >= seen_min and vis.get("face_still", 0) > still_max:
        return "стример спит (лицо не двигается)"
    if motion < motion_min:
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


# ---------- вторая, строгая проверка «спит ли стример» (сумма признаков) ----------
def _gray_small(path: str, fps: float = 2.0, w: int = 270):
    fr = _frames(path, fps=fps, w=w)
    return None if fr is None else fr.mean(axis=3)


def deep_metrics(path: str) -> dict:
    """still — медиана доли «сильно изменившихся» пикселей между соседними кадрами (без полосы субтитров):
    у спящего стрима почти ноль, даже если мигают таймер и алерты; dark — средняя яркость;
    face_seen / face_still — самое крупное лицо в любом месте кадра."""
    g = _gray_small(path)
    if g is None or len(g) < 3:
        return {}
    n, h, w = g.shape
    keep = np.ones((h, w), dtype=bool)
    if h > w:  # вертикальный клип: полоса субтитров и надписи меняется сама — её не считаем
        keep[int(h * 0.52):int(h * 0.82)] = False
    d = np.abs(np.diff(g, axis=0))[:, keep]
    changed = (d > 14).mean(axis=1)  # доля пикселей, где картинка заметно поменялась
    out = {"changed": round(float(np.median(changed)), 4), "dark": round(float(g.mean()), 1)}
    from . import facecam as fc
    big = _frames(path, fps=1.0, w=480)
    if big is not None:
        seen = still = 0
        prev = None
        for i in range(len(big)):
            img = np.ascontiguousarray(big[i])
            faces = fc._faces(img, img.shape[1], img.shape[0])
            if not faces:
                prev = None
                continue
            seen += 1
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            H, W = img.shape[:2]
            box = (int(fx * W), int(fy * H), max(6, int(fw * W)), max(6, int(fh * H)))
            crop = img[box[1]:box[1] + box[3], box[0]:box[0] + box[2]].mean(axis=2)
            if prev is not None:
                pb, pc = prev
                if abs(box[0] - pb[0]) + abs(box[1] - pb[1]) <= 3 and pc.shape == crop.shape \
                        and float(np.abs(crop - pc).mean()) < th("face_still") * 1.5:
                    still += 1
            prev = (box, crop)
        out["face_seen"] = round(seen / len(big), 2)
        out["face_still"] = round(still / max(1, seen - 1), 2) if seen > 1 else (1.0 if seen else 0.0)
    return out


def sleep_score(m: dict, voice: float, voice_by_words: bool, title: str = "", chat_hits: int = 0) -> tuple[int, list]:
    """Сколько признаков сна набралось и какие. Отказ — от 3 (или чат явно про сон)."""
    why = []
    thr = float((rules().get("thresholds") or {}).get("deep_changed_max", 0.015))
    if m.get("changed", 1) >= thr * 2:
        # в кадре идёт игра (картинка заметно меняется) — стример не спит; ночная сцена, маленькая вебка
        # или «24 hour» в названии сами по себе ничего не значат. Сон тут выдаёт только чат.
        return (1, ["чат пишет про сон"]) if chat_hits else (0, [])
    if m.get("changed", 1) < thr:
        why.append("картинка почти не меняется")
    if m.get("dark", 255) < float((rules().get("thresholds") or {}).get("deep_dark_max", 55)):
        why.append("в кадре темно")
    if m.get("face_seen", 0) < 0.3:
        why.append("лица почти не видно")
    elif m.get("face_still", 0) > 0.6:
        why.append("лицо не двигается")
    if voice_by_words and voice < 0.25:
        why.append(f"стример почти не говорит ({voice:.0%})")
    elif not voice_by_words and m.get("face_seen", 0) >= 0.3 and m.get("face_still", 0) > 0.6:
        why.append("голос — не стримера (озвучка/музыка)")
    words = [w.lower() for w in ((rules().get("reject_sleep") or {}).get("title_keywords") or DEFAULT_TITLE_WORDS)]
    if any(w in (title or "").lower() for w in words) or "sleep" in (title or "").lower():
        why.append("в названии стрима — сон/24/7")
    if chat_hits:
        why.append("чат пишет про сон")
    return len(why), why


def deep_check(path: str, words: list | None = None, title: str = "", top_messages: list | None = None) -> tuple[str | None, dict]:
    """Строгая проверка готового клипа или куска: None — оставить, иначе причина."""
    rs = rules().get("reject_sleep") or {}
    hit = _matcher([w.lower() for w in (rs.get("chat_keywords") or DEFAULT_SLEEP_WORDS)])
    top = [t for t in (top_messages or []) if t][:3]
    chat_hits = sum(1 for t in top if hit(t))
    if chat_hits >= 2 or (top and chat_hits / len(top) >= 0.5):
        return f"стример спит (чат: {', '.join(top)})", {"chat": top}
    m = deep_metrics(path)
    if not m:
        return None, {}
    dur = duration(path)
    by_words = bool(words)
    voice = voice_ratio_words(words, dur) if by_words else voice_ratio_energy(path)
    n, why = sleep_score(m, voice, by_words, title, chat_hits)
    m.update(voice=round(voice, 2), score=n, signs=why)
    need = int((rules().get("thresholds") or {}).get("deep_score_min", 3))
    if n >= need:
        return "стример спит: " + ", ".join(why), m
    return None, m


# ---------- подвисания: стоп-кадры в куске (лаг стрима, реклама Twitch, рваная запись) ----------
def freezes(path: str, noise: float = 0.002, min_dur: float = 0.6) -> list[tuple[float, float]]:
    """Отрезки, где ВЕСЬ кадр стоит (картинка не меняется вообще, вебка тоже): [(начало, конец)]."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf", f"freezedetect=n={noise}:d={min_dur}", "-map", "0:v:0",
                        "-f", "null", "-"], capture_output=True, text=True, creationflags=FLAGS)
    out, start = [], None
    for line in r.stderr.splitlines():
        if "freeze_start" in line:
            try:
                start = float(line.rsplit(":", 1)[1])
            except ValueError:
                start = None
        elif "freeze_end" in line and start is not None:
            try:
                out.append((start, float(line.rsplit(":", 1)[1])))
            except ValueError:
                pass
            start = None
    if start is not None:
        out.append((start, duration(path)))
    return out


def lag_check(path: str) -> str | None:
    """None — видео идёт ровно; иначе причина (клип с подвисаниями не берём)."""
    fr = freezes(path)
    if not fr:
        return None
    dur = duration(path) or 1.0
    total = sum(b - a for a, b in fr)
    longest = max(b - a for a, b in fr)
    t = rules().get("thresholds") or {}
    if longest >= float(t.get("freeze_max_sec", 1.2)) or total / dur >= float(t.get("freeze_share_max", 0.08)):
        return f"видео подвисает (стоп-кадр {longest:.1f} с, всего {total:.1f} с) — лаг стрима или записи"
    return None


# ---------- только яркие моменты ----------
def strong_moments(hl: list, have_media: bool, log=print) -> list:
    """Отсеиваем «средние» моменты: клип берём, только если реакция заметно сильнее обычного.
    Правила (strategy.json → quality_filters.moment, можно менять):
      min_relative — не слабее этой доли от лучшего момента этого куска (по умолчанию 0,6);
      need_two_signals — кроме чата должен «выстрелить» звук (крик, смех) или картинка (взрыв, авария);
      chat_only_z — если чат взорвался очень сильно, хватит одного чата."""
    if not hl:
        return hl
    m = (rules().get("moment") or {}) if isinstance(rules().get("moment"), dict) else {}
    rel = float(m.get("min_relative", 0.6))
    two = bool(m.get("need_two_signals", True)) and have_media
    chat_only = float(m.get("chat_only_z", 4.0))
    sig = float(m.get("signal_z", 1.5))
    try:  # веса типов момента от «Доктора»: шок и смех ценнее, чем просто разговор
        from . import strategy
        from .caption import _category
        wts = (strategy.get().get("scoring") or {}).get("moment_type_weights") or {}
        if wts:
            for h in hl:
                cat = _category(list(getattr(h, "top_messages", []) or []))
                w = float(wts.get(cat, 1.0)) if cat in wts else 1.0
                if w != 1.0:
                    h.score = round(float(h.score or 0) * w, 2)
            hl.sort(key=lambda h: -float(getattr(h, "score", 0) or 0))
    except Exception:
        pass
    best = max(float(getattr(h, "score", 0) or 0) for h in hl)
    out = []
    from .pipeline import _fmt
    for h in hl:
        sc = float(getattr(h, "score", 0) or 0)
        other = max(float(getattr(h, "audio_z", 0) or 0), float(getattr(h, "jump_z", 0) or 0), float(getattr(h, "vis_z", 0) or 0))
        chat = float(getattr(h, "chat_z", 0) or 0)
        why = None
        if best > 0 and sc < best * rel:
            why = f"слабее лучшего момента ({sc:.1f} из {best:.1f})"
        elif two and chat < chat_only and other < sig:
            why = "реагирует только чат, а стример и картинка — нет"
        if why:
            log(f"  ⤼ пропущен скучный момент {_fmt(h.peak)}: {why}")
            continue
        out.append(h)
    return out


def first_seconds_check(path: str, peak: float, cold_open: bool, before: float = 0.75, after: float = 0.75) -> str | None:
    """Первые 2 секунды решают, пролистают ли клип (quality_filters.first_seconds).
    Если начало тише среднего по клипу, а яркого пика, который холодный старт поставит первым, нет — клип не берём.
    Без холодного старта: если до пика больше need_context_max_sec секунд подводки — тоже не берём
    (монтаж обрежет подводку, но если и после обрезки начало тихое — клип скучный)."""
    fs = rules().get("first_seconds")
    if fs is False or (isinstance(fs, dict) and fs.get("on") is False):
        return None
    try:
        from .shape import voice_energy
        e = voice_energy(path)
    except Exception:
        return None
    if e.size < 60:  # короче 3 с — не судим
        return None
    hop = 0.05
    mean = float(np.mean(e))
    first = float(np.mean(e[: int(2 / hop)]))
    i0, i1 = max(0, int((peak - before) / hop)), min(e.size, int((peak + after) / hop))
    peak_lvl = float(np.max(e[i0:i1])) if i1 > i0 else -99.0
    loud = float(np.percentile(e, 90))
    if first >= mean:
        return None
    if i1 > i0:
        peak = (i0 + int(np.argmax(e[i0:i1]))) * hop  # где реакция громче всего
    if cold_open and peak > 1.5 and peak_lvl >= loud - 1.0:
        return None  # холодный старт поставит громкий пик первым кадром
    if peak <= 2.0 and peak_lvl >= loud - 1.0:
        return None  # пик и так в начале
    return ("первые 2 секунды тихие, а громкой реакции, которую можно поставить в начало, нет — "
            "такой клип пролистают")
