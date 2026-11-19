"""Подпись автора на отдельном клипе — по желанию, галочкой в списке клипов.

Подпись («Twitch | KaiCenat») накладывается на уже готовый клип. Чистая версия (без подписи) сохраняется
в служебной папке, поэтому галочку можно снять — клип вернётся как был.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

from . import paths, render


def _store() -> str:
    return os.path.join(paths.default_work_dir(), "credits.json")


def load() -> dict:
    try:
        with open(_store(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(_store()), exist_ok=True)
    with open(_store(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def state(clip: dict, data: dict | None = None) -> str:
    """'on' — подписан (можно снять), 'burned' — вшита при нарезке (снять нельзя), 'off' — без подписи,
    'unknown' — старый клип, неизвестно."""
    rec = (data if data is not None else load()).get(os.path.normpath(clip["path"]))
    if rec and rec.get("on"):
        return "on"
    if clip.get("credit_burned"):
        return "burned"
    if "credit_burned" not in clip:
        return "unknown"  # клип нарезан до этой функции: подпись могла вшиться (раньше она ставилась всем)
    return "off"


def platform_of(clip: dict) -> str:
    if clip.get("platform"):
        return clip["platform"]
    url = (clip.get("vod_url") or clip.get("link") or "").lower()
    if "youtu" in url:
        return "YouTube"
    if "kick.com" in url:
        return "Kick"
    return "Twitch"


def author_of(clip: dict) -> str:
    return (clip.get("credit_name") or clip.get("channel") or "").lstrip("@")


def _run(cmd: list, cwd: str | None = None) -> None:
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, creationflags=flags)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[-500:])


def add(clip: dict, pos: str = "bottom-left") -> None:
    """Накладывает подпись на клип; чистую версию откладывает, чтобы потом можно было снять."""
    path = os.path.normpath(clip["path"])
    work = os.path.join(paths.default_work_dir(), "credit_clean")
    os.makedirs(work, exist_ok=True)
    stamp = str(abs(hash(path)) % 10 ** 10)
    clean = os.path.join(work, f"{stamp}_{os.path.basename(path)}")
    ass = f"credit_{stamp}.ass"
    render.write_credit_ass(os.path.join(work, ass), platform_of(clip), author_of(clip), pos)
    tmp = os.path.join(work, f"{stamp}_new.mp4")
    _run(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(path), "-vf", f"ass={ass}", "-c:v", "libx264",
          "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
          os.path.abspath(tmp)], cwd=work)
    os.remove(os.path.join(work, ass))
    shutil.move(path, clean)
    shutil.move(tmp, path)
    data = load()
    data[path] = {"on": True, "clean": clean, "mtime": os.path.getmtime(path), "pos": pos}
    _save(data)


def remove(clip: dict) -> None:
    """Снимает подпись: возвращает чистую версию клипа."""
    path = os.path.normpath(clip["path"])
    data = load()
    rec = data.get(path)
    if not rec or not rec.get("on"):
        raise ValueError("подпись вшита при нарезке — снять её нельзя")
    if not os.path.exists(rec.get("clean", "")):
        raise ValueError("чистая версия клипа не найдена")
    if abs(os.path.getmtime(path) - float(rec.get("mtime", 0))) > 2:
        raise ValueError("клип менялся после подписи (например, исправляли нарушения) — снять подпись нельзя")
    os.remove(path)
    shutil.move(rec["clean"], path)
    data.pop(path, None)
    _save(data)
