"""Общая папка для двоих (ты и друг): общие клипы, общие галочки «выложено» (с тем, кто выложил).

Как устроено: папка лежит в облаке (Google Диск / Яндекс Диск / Dropbox — с приложением на обоих компьютерах),
расшарена только вам двоим. Клипы нарезаются прямо в неё (<папка>/Клипы/...), а служебные данные — в <папка>/.team.
Каждый компьютер пишет ТОЛЬКО свои файлы (имя_файла.<твоё имя>.json), а читает файлы обоих — поэтому облако никогда
не ловит одновременную правку одного файла. Ключи — пути клипов относительно общей папки (у вас они разные на дисках).
"""
from __future__ import annotations

import glob
import json
import os
import time

from . import paths


def enabled() -> bool:
    return bool(paths.team_dir())


def shared_dir() -> str:
    d = os.path.join(paths.team_dir(), ".team")
    os.makedirs(d, exist_ok=True)
    return d


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name) or "user"


def me() -> str:
    return paths.user_name()


def own_file(kind: str) -> str:
    return os.path.join(shared_dir(), f"{kind}.{_safe(me())}.json")


def files(kind: str) -> list[tuple[str, str]]:
    """[(чей файл, путь)] — свои и друга (а также «конфликтные копии», которые иногда делает облако)."""
    out = []
    for p in glob.glob(os.path.join(shared_dir(), f"{kind}.*.json")):
        user = os.path.basename(p)[len(kind) + 1:-5].split(" ")[0].split("(")[0].strip()
        out.append((user, p))
    return out


def _read(p: str) -> dict:
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def read_own(kind: str) -> dict:
    return _read(own_file(kind))


def write_own(kind: str, data: dict) -> None:
    p = own_file(kind)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def rel(path: str) -> str:
    return os.path.relpath(os.path.normpath(path), os.path.normpath(paths.default_out_dir())).replace(os.sep, "/")


def absp(key: str) -> str:
    return os.path.normpath(os.path.join(paths.default_out_dir(), key.replace("/", os.sep)))


# ---------- галочки «выложено» (общие, с тем, кто выложил) ----------
def load_posted() -> tuple[dict, dict]:
    """({путь: {площадка: True}}, {путь: {площадка: кто выложил}}) — по последней отметке любого из вас."""
    best: dict = {}
    for user, p in files("posted"):
        for k, plats in _read(p).items():
            for pl, v in (plats or {}).items():
                if not isinstance(v, dict):
                    continue
                cur = best.setdefault(k, {}).get(pl)
                if cur is None or v.get("t", 0) > cur.get("t", 0):
                    best[k][pl] = dict(v, by=v.get("by") or user)
    posted, by = {}, {}
    for k, plats in best.items():
        a = absp(k)
        for pl, v in plats.items():
            if v.get("v"):
                posted.setdefault(a, {})[pl] = True
                by.setdefault(a, {})[pl] = v.get("by", "")
    return posted, by


def set_posted(path: str, value: bool, platform: str) -> None:
    data = read_own("posted")
    data.setdefault(rel(path), {})[platform] = {"v": bool(value), "t": time.time(), "by": me()}
    write_own("posted", data)


# ---------- общие словари «ключ → запись» (что выложено, проверка правил, оценки) ----------
def load_merged(kind: str, ts_field: str = "t") -> dict:
    out: dict = {}
    for user, p in files(kind):
        for k, v in _read(p).items():
            cur = out.get(k)
            if cur is None or (isinstance(v, dict) and isinstance(cur, dict)
                               and v.get(ts_field, 0) > cur.get(ts_field, 0)):
                out[k] = v
    return {absp(k): v for k, v in out.items()}


def put(kind: str, path: str, value) -> None:
    data = read_own(kind)
    data[rel(path)] = value
    write_own(kind, data)


def put_many(kind: str, items: dict) -> None:
    data = read_own(kind)
    for path, value in items.items():
        data[rel(path)] = value
    write_own(kind, data)


def migrate(old_out: str, log=print) -> int:
    """Перенести мои клипы (с Рабочего стола\\YouTube) в общую папку: файлы, дневник, галочки, оценки, проверки.
    Возвращает, сколько клипов перенесено."""
    import shutil
    new_out = paths.default_out_dir()
    os.makedirs(new_out, exist_ok=True)
    work = paths.default_work_dir()

    def jload(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    old_posted = jload(os.path.join(work, "posted.json"))
    old_pub = jload(os.path.join(work, "published.json"))
    old_pol = jload(os.path.join(work, "policy.json"))
    old_rat = jload(os.path.join(work, "ratings.json"))
    moved = 0
    days = os.path.join(work, "days")
    for fn in sorted(os.listdir(days)) if os.path.isdir(days) else []:
        if not fn.endswith(".json"):
            continue
        date = fn[:-5]
        data = jload(os.path.join(days, fn))
        clips = data.get("clips", [])
        if not clips:
            continue
        own = os.path.join(shared_dir(), "days", f"{date}.{_safe(me())}.json")
        os.makedirs(os.path.dirname(own), exist_ok=True)
        cur = jload(own) or {"clips": [], "events": []}
        have = {c.get("file") for c in cur.get("clips", [])}
        for c in clips:
            src = os.path.normpath(os.path.join(old_out, date, c.get("file", "")))
            dst = os.path.normpath(os.path.join(new_out, date, c.get("file", "")))
            if not os.path.exists(src):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                shutil.move(src, dst)
            if c.get("file") not in have:
                cur["clips"].append(c)
            v = old_posted.get(src)
            for pl, on in ((v if isinstance(v, dict) else {"youtube": bool(v)}) or {}).items():
                if on:
                    set_posted(dst, True, pl)
            if src in old_pub:
                put("published", dst, dict(old_pub[src], t=time.time()))
            if src in old_pol:
                put("policy", dst, old_pol[src])
            if src in old_rat:
                put("ratings", dst, old_rat[src])
            moved += 1
        cur.setdefault("events", []).extend(data.get("events", []))
        with open(own, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=1)
    log(f"Перенесено клипов в общую папку: {moved}")
    return moved
