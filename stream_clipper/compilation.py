"""Подборка дня (strategy.autopilot.compilation): 2–3 лучших свежих момента одного стримера в одном ролике
20–30 с с нумерацией #1–#3 и хуком «{S}'S CRAZIEST MOMENTS TODAY». Наш монтаж поверх чужого стрима —
против штрафа TikTok за неоригинальность. Подборка встаёт в план как обычный клип (с пометкой compilation).
"""
from __future__ import annotations

import os
import subprocess
import time

from . import daily, paths

FLAGS = 0x08000000 if os.name == "nt" else 0


def _cfg() -> dict:
    from . import strategy
    c = (strategy.get().get("autopilot") or {}).get("compilation") or {}
    return c if isinstance(c, dict) else {}


def wanted() -> bool:
    return any(int(v or 0) > 0 for v in (_cfg().get("per_day") or {}).values())


def _dur(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=FLAGS)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def pick(clips: list[dict], n_max: int = 3) -> tuple[str, list[dict]] | None:
    """Стример с самыми сильными свежими невыложенными клипами (минимум 2) и сами клипы, лучшие первыми."""
    by: dict = {}
    for c in clips:
        if c.get("compilation") or any((c.get("posted") or {}).values()) or not os.path.exists(c.get("path", "")):
            continue
        by.setdefault(c.get("channel", ""), []).append(c)
    best = None
    for ch, lst in by.items():
        lst = sorted(lst, key=lambda c: -float(c.get("score10") or c.get("score") or 0))[:n_max]
        total = sum(float(c.get("score10") or 0) for c in lst)
        if len(lst) >= 2 and (best is None or total > best[2]):
            best = (ch, lst, total)
    return (best[0], best[1]) if best else None


def _ass(path: str, number: int, hook: str | None) -> None:
    from .montage import ASS_HEAD, _ts
    style = ("Style: N,Arial,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,10,4,5,40,40,0,1\n"
             "Style: H,Arial,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H28000000,-1,0,0,0,100,100,0,0,3,16,0,8,70,70,0,1")
    ev = f"Dialogue: 3,{_ts(0)},{_ts(2.2)},N,,0,0,0,,{{\\an5\\pos(540,1480)\\fad(80,200)}}#{number}\n"
    if hook:
        ev += f"Dialogue: 4,{_ts(0)},{_ts(3)},H,,0,0,0,,{{\\an8\\pos(540,300)\\fad(0,250)}}{hook}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(ASS_HEAD.format(styles=style) + ev)


def build(channel: str, parts: list[dict], out: str, length: float = 25.0) -> float:
    """Склеить куски вокруг пиков с номерами. Возвращает длину ролика."""
    from .caption import short_nick
    from .montage import _enc, _run
    work = os.path.dirname(os.path.abspath(out))
    each = max(6.0, length / len(parts))
    hook = f"{short_nick(channel)}'S CRAZIEST MOMENTS TODAY".upper().replace("{", "(").replace("}", ")")
    inputs, chains, names = [], [], []
    for i, c in enumerate(parts):
        d = _dur(c["path"])
        p = max(0.0, min(d, float(c.get("peak", 0) or 0) - float(c.get("start", 0) or 0)))
        a = max(0.0, min(p - each * 0.45, d - each))
        name = f"comp_{int(time.time() * 1000)}_{i}.ass"
        names.append(name)
        _ass(os.path.join(work, name), i + 1, hook if i == 0 else None)
        inputs += ["-ss", f"{a:.2f}", "-t", f"{each:.2f}", "-i", os.path.abspath(c["path"])]
        chains.append(f"[{i}:v]setpts=PTS-STARTPTS,ass={name}[v{i}];[{i}:a]asetpts=PTS-STARTPTS[a{i}]")
    graph = ";".join(chains) + ";" + "".join(f"[v{i}][a{i}]" for i in range(len(parts))) + \
        f"concat=n={len(parts)}:v=1:a=1[v][a]"
    try:
        _run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
              *_enc(True), os.path.abspath(out)], cwd=work)
    finally:
        for name in names:
            try:
                os.remove(os.path.join(work, name))
            except OSError:
                pass
    return _dur(out)


def make_today(state: dict, clips: list[dict], event) -> str | None:
    """Одна подборка в день (state["compilation_day"]). Возвращает путь к новому клипу или None."""
    if not wanted() or state.get("compilation_day") == time.strftime("%Y-%m-%d"):
        return None
    cfg = _cfg()
    lo, hi = (cfg.get("length_sec") or [20, 30])[:2]
    got = pick(clips, int((cfg.get("moments") or [2, 3])[-1]))
    if not got:
        return None
    channel, parts = got
    tmp = os.path.join(paths.default_work_dir(), f"compilation_{int(time.time())}.mp4")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    dur = build(channel, parts, tmp, (float(lo) + float(hi)) / 2)
    from .caption import short_nick
    first = parts[0]
    d = {"start": 0.0, "end": round(dur, 2), "peak": 1.0, "compilation": True,
         "caption": f"{short_nick(channel)}'S CRAZIEST MOMENTS TODAY".upper(),
         "score": max(float(c.get("score") or 0) for c in parts),
         "top_messages": [m for c in parts for m in (c.get("top_messages") or [])[:1]],
         "vod_url": first.get("vod_url", ""), "vod_title": first.get("vod_title", ""),
         "platform": first.get("platform", ""), "credit_name": first.get("credit_name", ""), "credit_burned": True,
         "parts": [os.path.basename(c["path"]) for c in parts]}
    daily.set_state_dir(paths.default_work_dir())  # как у нарезчика (cli): дневник — в служебной папке, его читает библиотека
    path = daily.deliver_clip(paths.default_out_dir(), tmp, d, channel)
    state["compilation_day"] = time.strftime("%Y-%m-%d")
    event("🎞", f"{channel}: подборка дня из {len(parts)} моментов готова ({round(dur)} с)", path, "clip")
    return path
