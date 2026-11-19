"""Архив клипов (вместо удаления).

Клип, который не пошёл в публикацию, уходит сюда: сохраняются все данные (стример, запись стрима, момент,
надпись, речь, оценки, причина), картинка-превью и сжатая копия (720p). Полный файл удаляется — место освобождается.
Достать обратно: заново нарезать из записи стрима в полном качестве, а если запись уже удалена — взять сжатую копию.
Если тема клипа или стример попадут в тренды (стратегия «Доктора»), архив подскажет, что можно достать.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

from . import library, paths

FLAGS = 0x08000000 if os.name == "nt" else 0


def _dir() -> str:
    d = os.path.join(paths.default_work_dir(), "archive")
    os.makedirs(d, exist_ok=True)
    return d


def _index() -> str:
    return os.path.join(_dir(), "index.json")


def load() -> list[dict]:
    try:
        with open(_index(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(items: list[dict]) -> None:
    tmp = _index() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _index())


def archived_paths() -> set:
    return {i["orig"] for i in load() if not i.get("restored")}


def archive_clip(clip: dict, reason: str, score=None) -> dict:
    """Клип → в архив. Возвращает запись архива; сколько места освободилось — в rec["freed"]."""
    path = os.path.normpath(clip["path"])
    stamp = f"{int(time.time() * 1000)}"
    small = os.path.join(_dir(), f"{stamp}.mp4")
    thumb = os.path.join(_dir(), f"{stamp}.png")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", "scale=720:-2", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "30", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
                        small], capture_output=True, creationflags=FLAGS)
    if r.returncode != 0:
        raise RuntimeError("не удалось сделать сжатую копию: " + r.stderr.decode(errors="replace")[-300:])
    tp = library.thumb_path(path)
    if os.path.exists(tp):
        shutil.copy2(tp, thumb)
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2", "-i", path, "-frames:v", "1", "-vf", "scale=-2:128",
                        thumb], capture_output=True, creationflags=FLAGS)
    size = os.path.getsize(path)
    rec = {k: clip.get(k) for k in ("channel", "vod_url", "moment", "start", "end", "caption", "transcript", "lang",
                                    "rating", "ai_score", "date", "words", "platform", "credit_name")}
    rec.update({"id": stamp, "orig": path, "small": small, "thumb": thumb if os.path.exists(thumb) else "",
                "reason": reason, "score": score, "archived": time.time(), "size": size})
    os.remove(path)
    try:
        os.remove(tp)
    except OSError:
        pass
    items = [i for i in load() if i["orig"] != path or i.get("restored")]
    items.append(rec)
    _save(items)
    rec["freed"] = size - os.path.getsize(small)
    return rec


def mark_restored(rec: dict) -> None:
    items = load()
    for i in items:
        if i["id"] == rec["id"]:
            i["restored"] = time.time()
    _save(items)


def restore_from_small(rec: dict) -> str:
    """Запись стрима недоступна — возвращаем сжатую копию (720p) на прежнее место."""
    os.makedirs(os.path.dirname(rec["orig"]), exist_ok=True)
    shutil.copy2(rec["small"], rec["orig"])
    library.make_thumb(rec["orig"])
    mark_restored(rec)
    return rec["orig"]


def forget(rec: dict) -> None:
    """Удалить из архива насовсем (сжатую копию и превью)."""
    for f in (rec.get("small"), rec.get("thumb")):
        if f and os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass
    _save([i for i in load() if i["id"] != rec["id"]])


def search(query: str = "") -> list[dict]:
    q = (query or "").strip().lower()
    items = [i for i in load() if not i.get("restored")]
    if q:
        items = [i for i in items if q in " ".join(str(i.get(k) or "") for k in
                                                     ("channel", "caption", "transcript", "reason", "date")).lower()]
    return sorted(items, key=lambda i: -(i.get("archived") or 0))


def trend_matches(trends: list) -> list[tuple[dict, str]]:
    """Архивные клипы, совпавшие с трендами из стратегии «Доктора»: [(запись, что совпало)]."""
    words = []
    for t in trends or []:
        if isinstance(t, str):
            words.append(t)
        elif isinstance(t, dict):
            for k in ("streamer", "topic", "keyword", "name"):
                if t.get(k):
                    words.append(str(t[k]))
            words += [str(x) for x in t.get("keywords") or []]
    words = [w.strip().lower() for w in words if len(w.strip()) >= 3]
    out = []
    for i in search(""):
        hay = " ".join(str(i.get(k) or "") for k in ("channel", "caption", "transcript")).lower()
        hit = next((w for w in words if w in hay), None)
        if hit:
            out.append((i, hit))
    return out
