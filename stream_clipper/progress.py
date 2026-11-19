"""Память «что уже разобрано»: для каждого стрима — какие отрезки (от начала стрима) программа уже
проанализировала. Видно во вкладке «Стримы»: на каком стриме и на каком месте остановились,
и откуда продолжать. Файл: <служебная папка>/progress.json.
"""
from __future__ import annotations

import json
import os
import threading
import time

from . import paths
from .i18n import T

_lock = threading.Lock()
GAP = 120  # дырки короче 2 минут не считаем «непросмотренным»


def _file() -> str:
    return os.path.join(paths.default_work_dir(), "progress.json")


def load() -> dict:
    if not os.path.exists(_file()):
        _backfill()
    try:
        with open(_file(), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(data: dict) -> None:
    p = _file()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def merge(ranges: list) -> list[list[float]]:
    out: list[list[float]] = []
    for a, b in sorted([float(a), float(b)] for a, b in ranges if b > a):
        if out and a <= out[-1][1] + GAP:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def record(key: str, start: float, end: float, *, channel: str, platform: str, title: str = "",
           url: str = "", stream_ts: float | None = None, duration: float = 0, live: bool = False,
           clips: int = 0) -> None:
    """Отмечает, что отрезок [start, end] (секунды от начала стрима) разобран."""
    if not key:
        return
    with _lock:
        data = load()
        e = data.get(key) or {}
        e.update({k: v for k, v in {"channel": channel, "platform": platform, "title": title, "url": url,
                                    "stream_ts": stream_ts}.items() if v})
        e["duration"] = max(float(duration or 0), float(e.get("duration") or 0))
        e["live"] = bool(live)
        e["ranges"] = merge(list(e.get("ranges") or []) + ([[max(0.0, start), end]] if end > start else []))
        e["clips"] = int(e.get("clips") or 0) + int(clips)
        e["updated"] = time.time()
        data[key] = e
        try:
            _save(data)
        except OSError:
            pass


def forget(key: str) -> None:
    with _lock:
        data = load()
        if data.pop(key, None) is not None:
            _save(data)


def set_done(key: str) -> None:
    """Пометить стрим полностью разобранным (вручную)."""
    with _lock:
        data = load()
        e = data.get(key)
        if e and e.get("duration"):
            e["ranges"] = [[0.0, float(e["duration"])]]
            _save(data)


def fmt(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}"


def summary(e: dict) -> dict:
    """Что разобрано и откуда продолжать: {'done': '0:00–12:00', 'left': '2:30', 'resume': 43200, 'finished': bool}."""
    ranges = merge(e.get("ranges") or [])
    dur = float(e.get("duration") or 0)
    done_txt = ", ".join(f"{fmt(a)}–{fmt(b)}" for a, b in ranges) or "—"
    # первое непросмотренное место: дырка в начале/середине или хвост
    resume, pos = None, 0.0
    for a, b in ranges:
        if a - pos > GAP:
            resume = pos
            break
        pos = max(pos, b)
    if resume is None and (not dur or dur - pos > GAP):
        resume = pos
    gaps, pos = [], 0.0
    for a, b in ranges:
        if a - pos > GAP:
            gaps.append([pos, a])
        pos = max(pos, b)
    if dur and dur - pos > GAP:
        gaps.append([pos, dur])
    elif not dur and not ranges:
        gaps.append([0.0, 0.0])
    seen = sum(b - a for a, b in ranges)
    finished = bool(dur) and not e.get("live") and dur - seen <= GAP
    if finished:
        resume = None
    left = max(0.0, dur - seen) if dur else None
    gaps_txt = ", ".join(f"{fmt(a)}–{fmt(b)}" if b else T('с {0}').format(fmt(a)) for a, b in gaps)
    if e.get("live") and ranges:
        gaps_txt = ", ".join([t for t in [gaps_txt] if t] + [T("эфир идёт")])
    upto = max((b for a, b in ranges), default=0.0)  # до какого времени стрима всё уже проверено
    return {"done": done_txt, "left": left, "resume": resume, "finished": finished, "seen": seen, "upto": upto,
            "gaps": gaps, "gaps_txt": gaps_txt or "—"}


def match_vod(data: dict, channel: str, vod_ts: float | None, vod_id: str) -> str | None:
    """Ключ записи эфира (когда программа писала эфир сама), совпадающей по времени с VOD — это тот же стрим."""
    if not vod_ts:
        return None
    for k, e in data.items():
        if k != vod_id and e.get("channel", "").lower() == channel.lower() and e.get("stream_ts") \
                and abs(float(e["stream_ts"]) - float(vod_ts)) < 1800:
            return k
    return None


def _backfill() -> None:
    """Первый запуск после обновления: восстанавливаем, что уже разбирали раньше (по скачанному чату и
    готовым клипам), чтобы старые стримы тоже были видны во вкладке «Стримы»."""
    try:
        from . import library
        from .chat import load_chat_file
        by_vid: dict = {}
        for date in library.list_dates():
            for c in library.list_clips(date):
                url = c.get("vod_url") or ""
                if "/videos/" in url:
                    vid = url.rstrip("/").split("/")[-1].split("?")[0].lstrip("v")
                elif "watch?v=" in url:
                    vid = url.split("watch?v=")[-1].split("&")[0]
                else:
                    continue
                e = by_vid.setdefault(vid, {"channel": c.get("channel", ""), "title": c.get("vod_title", ""),
                                            "url": url, "clips": 0, "end": 0.0})
                e["clips"] += 1
                e["end"] = max(e["end"], float(c.get("end") or 0))
        data = {}
        work = paths.default_work_dir()
        for vid, e in by_vid.items():
            end = e["end"]
            cache = os.path.join(work, vid, "chat.json")
            try:
                msgs = load_chat_file(cache) if os.path.exists(cache) else []
                if msgs:
                    end = max(end, msgs[-1].t)
            except Exception:
                pass
            data[vid] = {"channel": e["channel"], "platform": "YouTube" if "youtu" in e["url"] else "Twitch",
                         "title": e["title"], "url": e["url"], "duration": 0, "live": False,
                         "ranges": [[0.0, end]] if end else [], "clips": e["clips"], "updated": time.time()}
        _save(data)
    except Exception:
        pass
