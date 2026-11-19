"""Стратегия от «Доктора шортсов»: лимиты и окна публикаций, пороги оценки, веса, правила рисков и текстов,
тренды и уроки из аналитики. «Доктор» обновляет её в облаке два раза в день; Stream Clipper скачивает
раз в час (как обновление программы — без API GitHub) и при ошибке работает по последней копии.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

from . import paths

BASE = "https://raw.githubusercontent.com/miiranov21/miiranov/refs/heads/claude/blissful-wozniak-v9vk56/doctor/"
FILES = ("strategy.json", "EDIT_STYLE.md")
REFRESH = 3600

# если стратегию ещё ни разу не скачали — разумные значения по умолчанию
DEFAULT = {
    "autopilot": {"auto_publish": True, "auto_delete": True, "delete_mode": "archive",
                  "posts_per_day": {"tiktok": 3, "youtube": 3, "instagram": 2}, "min_gap_hours": 4,
                  "platform_stagger_minutes": 20, "post_window_local": {"from": 12, "to": 23},
                  "min_score_to_post": 55, "archive_below_score": 20, "auto_restore": False},
    "scoring": {"weights": {"rating": 6, "ai_score": 3, "has_hook": 10, "fresh_bonus_per_day_under_3": 0,
                            "stale_penalty_per_day_over_3": 5},
                "duration_sweet_spot_sec": {"tiktok": [12, 45], "youtube": [15, 50], "instagram": [8, 30]},
                "streamer_weights": {}, "moment_type_weights": {}},
    "platform_fit": {}, "risk_rules": [], "text_rules": {}, "credit_rules": {}, "trends": [], "lessons": [],
}


def _dir() -> str:
    d = os.path.join(paths.default_work_dir(), "doctor")
    os.makedirs(d, exist_ok=True)
    return d


def refresh(force: bool = False, log=print) -> bool:
    """Скачивает свежую стратегию, если прошло больше часа. True — получилось (или ещё свежая)."""
    stamp = os.path.join(_dir(), ".fetched")
    if not force and os.path.exists(stamp) and time.time() - os.path.getmtime(stamp) < REFRESH:
        return True
    ok = True
    for name in FILES:
        try:
            req = urllib.request.Request(BASE + name, headers={"User-Agent": "StreamClipper"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            if name.endswith(".json"):
                json.loads(data.decode("utf-8"))  # битый файл не сохраняем
            tmp = os.path.join(_dir(), name + ".tmp")
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, os.path.join(_dir(), name))
        except Exception as e:
            ok = False
            log(f"стратегию «Доктора» обновить не удалось ({name}: {e}) — работаю по последней копии")
    if ok:
        with open(stamp, "w") as f:
            f.write(str(time.time()))
    return ok


def _merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def get() -> dict:
    """Текущая стратегия (последняя скачанная поверх значений по умолчанию)."""
    try:
        with open(os.path.join(_dir(), "strategy.json"), encoding="utf-8") as f:
            return _merge(DEFAULT, json.load(f))
    except Exception:
        return json.loads(json.dumps(DEFAULT))


def edit_style() -> str:
    try:
        with open(os.path.join(_dir(), "EDIT_STYLE.md"), encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def generated() -> str:
    return str(get().get("generated", ""))
