"""Список готовых клипов для окна программы: превью, подписи, отметка «выложено»."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

from . import paths


def _state() -> str:
    d = paths.default_work_dir()
    os.makedirs(d, exist_ok=True)
    return d


def thumb_path(clip: str) -> str:
    h = hashlib.md5(os.path.abspath(clip).encode("utf-8")).hexdigest()[:16]
    d = os.path.join(_state(), "thumbs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, h + ".png")


def make_thumb(clip: str, height: int = 128) -> str | None:
    """Картинка-превью (кадр с 2-й секунды) для списка клипов."""
    out = thumb_path(clip)
    if os.path.exists(out):
        return out
    flags = 0x08000000 if os.name == "nt" else 0
    try:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2", "-i", clip, "-frames:v", "1",
                        "-vf", f"scale=-2:{height}", out], capture_output=True, timeout=60, creationflags=flags)
    except Exception:
        return None
    return out if os.path.exists(out) else None


def list_dates() -> list[str]:
    """Даты (ДД.ММ.ГГГГ), за которые есть клипы, — новые сверху."""
    d = os.path.join(_state(), "days")
    if not os.path.isdir(d):
        return []
    dates = []
    for f in os.listdir(d):
        if not f.endswith(".json"):
            continue
        try:  # только дни, где есть клипы (а не одни события вроде «стрим начался»)
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                if json.load(fh).get("clips"):
                    dates.append(f[:-5])
        except Exception:
            continue

    def key(s):
        try:
            dd, mm, yy = s.split(".")
            return (int(yy), int(mm), int(dd))
        except ValueError:
            return (0, 0, 0)
    return sorted(dates, key=key, reverse=True)


def list_clips(date: str, out_dir: str | None = None) -> list[dict]:
    """Клипы за день (только те, чьи файлы существуют), новые сверху."""
    p = os.path.join(_state(), "days", date + ".json")
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    root = os.path.join(out_dir or paths.default_out_dir(), date)
    posted = load_posted()
    res = []
    for c in data.get("clips", []):
        path = os.path.normpath(os.path.join(root, c.get("file", "")))
        if not os.path.exists(path):
            continue
        res.append(dict(c, path=path, posted=posted.get(path, {})))
    res.reverse()
    return res


PLATFORMS = ("youtube", "instagram", "tiktok")
PLATFORM_NAMES = {"youtube": "YouTube", "instagram": "Instagram", "tiktok": "TikTok"}


def _posted_file() -> str:
    return os.path.join(_state(), "posted.json")


def load_posted() -> dict:
    """{путь клипа: {"youtube": True, "instagram": False, ...}}. Старые отметки «выложен» считаем YouTube."""
    try:
        with open(_posted_file(), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    return {k: (v if isinstance(v, dict) else {"youtube": bool(v)}) for k, v in data.items()}


def set_posted(path: str, value, platform: str = "youtube") -> None:
    data = load_posted()
    entry = data.get(path, {})
    if value:
        entry[platform] = True
    else:
        entry.pop(platform, None)
    if entry:
        data[path] = entry
    else:
        data.pop(path, None)
    with open(_posted_file(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def forget(path: str) -> None:
    data = load_posted()
    if data.pop(path, None) is not None:
        with open(_posted_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)


UPLOAD_PAGES = {"youtube": "https://www.youtube.com/upload",
                "instagram": "https://www.instagram.com/",
                "tiktok": "https://www.tiktok.com/tiktokstudio/upload"}


def upload_dir() -> str:
    """Рабочий стол\\YouTube\\К загрузке — тут всегда лежит только клип, который сейчас выкладываешь."""
    return os.path.join(paths.default_out_dir(), "К загрузке")


def _safe_name(text: str, limit: int = 90) -> str:
    bad = '<>:"/\\|?*\n\r\t'
    name = "".join("_" if ch in bad else ch for ch in text).strip(" .")
    return name[:limit].rstrip(" .") or "clip"


def stage_for_upload(clip: dict) -> str:
    """Кладёт клип в папку «К загрузке» под понятным именем (= название ролика: YouTube берёт его из имени файла).
    Используется жёсткая ссылка — места на диске не занимает; если не вышло — обычная копия.
    Прежние файлы из папки убираются (кроме тех, что браузер ещё загружает и не даёт удалить)."""
    d = upload_dir()
    os.makedirs(d, exist_ok=True)
    name = _safe_name(clip.get("caption") or f"{clip.get('channel', '')} {os.path.basename(clip['path'])[:-4]}") + ".mp4"
    dest = os.path.join(d, name)
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p) and p != dest:
            try:
                os.remove(p)
            except OSError:
                pass
    if os.path.exists(dest):
        try:
            if os.path.samefile(dest, clip["path"]):
                return dest
            os.remove(dest)
        except OSError:
            base, n = dest[:-4], 2
            while os.path.exists(f"{base} ({n}).mp4"):
                n += 1
            dest = f"{base} ({n}).mp4"
    try:
        os.link(clip["path"], dest)
    except OSError:
        import shutil
        shutil.copy2(clip["path"], dest)
    return dest
