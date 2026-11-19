"""Список готовых клипов для окна программы: превью, подписи, отметка «выложено»."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

from . import paths
from .i18n import T


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


def _day_files(date: str | None = None) -> list[tuple[str, str]]:
    """Файлы дневника: [(кто, путь)]. В общей папке — свои и друга, иначе — один файл на день."""
    from . import team
    if team.enabled():
        import glob
        d = os.path.join(team.shared_dir(), "days")
        out = []
        for p in glob.glob(os.path.join(d, (date or "??.??.????") + ".*.json")):
            base = os.path.basename(p)
            out.append((base[11:-5], p))
        return out
    d = os.path.join(_state(), "days")
    if date:
        p = os.path.join(d, date + ".json")
        return [("", p)] if os.path.exists(p) else []
    import glob
    return [("", p) for p in glob.glob(os.path.join(d, "*.json"))]


def day_entries(date: str) -> list[dict]:
    """Все записи клипов за день (свои и друга), с полем «by» — кто нарезал."""
    out = []
    for user, p in _day_files(date):
        try:
            with open(p, encoding="utf-8") as f:
                for c in json.load(f).get("clips", []):
                    out.append(dict(c, by=user))
        except Exception:
            continue
    return out


def list_dates() -> list[str]:
    """Даты (ДД.ММ.ГГГГ), за которые есть клипы, — новые сверху."""
    from . import team
    if team.enabled():
        dates = sorted({os.path.basename(p)[:10] for u, p in _day_files() if day_entries(os.path.basename(p)[:10])})

        def key(s):
            try:
                dd, mm, yy = s.split(".")
                return (int(yy), int(mm), int(dd))
            except ValueError:
                return (0, 0, 0)
        return sorted(dates, key=key, reverse=True)
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


def list_clips(date: str, out_dir: str | None = None, include_missing: bool = False) -> list[dict]:
    """Клипы за день (только те, чьи файлы существуют), новые сверху.
    include_missing=True — и удалённые (у них c["missing"] = True): их можно вернуть из корзины или нарезать заново."""
    data = {"clips": day_entries(date)}
    if not data["clips"]:
        return []
    root = os.path.join(out_dir or paths.default_out_dir(), date)
    posted = load_posted()
    res = []
    seen = set()
    for c in data.get("clips", []):
        path = os.path.normpath(os.path.join(root, c.get("file", "")))
        if path in seen:  # одна и та же запись дважды (например, после продолжения работы) — показываем один раз
            continue
        seen.add(path)
        if not os.path.exists(path):
            if include_missing:
                res.append(dict(c, path=path, posted=posted.get(path, {}), missing=True, date=date))
            continue
        res.append(dict(c, path=path, posted=posted.get(path, {}), date=date))
    res.reverse()
    return res


PLATFORMS = ("youtube", "instagram", "tiktok")
PLATFORM_NAMES = {"youtube": "YouTube", "instagram": "Instagram", "tiktok": "TikTok"}


def _posted_file() -> str:
    return os.path.join(_state(), "posted.json")


def load_posted() -> dict:
    """{путь клипа: {"youtube": True, "instagram": False, ...}}. Старые отметки «выложен» считаем YouTube."""
    from . import team
    if team.enabled():
        return team.load_posted()[0]
    try:
        with open(_posted_file(), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    return {k: (v if isinstance(v, dict) else {"youtube": bool(v)}) for k, v in data.items()}


def posted_by() -> dict:
    """Кто выложил: {путь: {площадка: имя}} (только в общей папке с другом)."""
    from . import team
    return team.load_posted()[1] if team.enabled() else {}


def set_posted(path: str, value, platform: str = "youtube") -> None:
    from . import team
    if team.enabled():
        team.set_posted(path, bool(value), platform)
        return
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
    return os.path.join(paths.default_out_dir(), T("К загрузке"))


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


def update_clip(path: str, fields: dict, out_dir: str | None = None) -> bool:
    """Меняет запись клипа в дневнике (после обрезки/удлинения: новое начало, конец, слова...)."""
    path = os.path.normpath(path)
    root = os.path.normpath(out_dir or paths.default_out_dir())
    rel = os.path.relpath(path, root)
    date = rel.split(os.sep)[0]
    for _, p in _day_files(date):  # в общей папке — в том файле дня, где записан клип (свой или друга)
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for c in data.get("clips", []):
            if os.path.normpath(os.path.join(root, date, c.get("file", ""))) == path:
                c.update(fields)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=1)
                return True
    return False


# ---------- оценки 1–10: ставятся один раз и больше не меняются ----------
def _ratings_file() -> str:
    return os.path.join(_state(), "ratings.json")


def frozen_ratings(clips: list[dict]) -> dict:
    """Оценка каждого клипа «замораживается» при первом показе. Удаление слабых клипов не двигает остальные,
    поэтому хороший клип случайно не «съедет» вниз списка."""
    from . import team
    if team.enabled():
        saved = team.load_merged("ratings")
    else:
        try:
            with open(_ratings_file(), encoding="utf-8") as f:
                saved = json.load(f)
        except Exception:
            saved = {}
    new = [c for c in clips if c["path"] not in saved]
    if new:
        from .caption import display_ratings
        fresh = display_ratings(clips)  # новым клипам — место среди всех (и удалённых тоже)
        for c in new:
            saved[c["path"]] = fresh.get(c["path"], 1)
        if team.enabled():  # оценка ставится один раз — и она одинаковая у вас обоих
            team.put_many("ratings", {c["path"]: saved[c["path"]] for c in new})
        else:
            with open(_ratings_file(), "w", encoding="utf-8") as f:
                json.dump(saved, f, ensure_ascii=False, indent=0)
    return {c["path"]: saved.get(c["path"], 1) for c in clips}


# ---------- корзина: удалённое лежит здесь, пока не очистишь ----------
def trash_dir() -> str:
    return os.path.join(paths.default_work_dir(), "trash")


def _trash_file() -> str:
    return os.path.join(_state(), "trash.json")


def load_trash() -> list[dict]:
    try:
        with open(_trash_file(), encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        return []
    return [t for t in items if os.path.exists(t.get("file", ""))]


def _save_trash(items: list[dict]) -> None:
    with open(_trash_file(), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)


def move_to_trash(clip: dict, score: int | None = None) -> dict:
    import shutil
    import time
    os.makedirs(trash_dir(), exist_ok=True)
    dest = os.path.join(trash_dir(), f"{int(time.time() * 1000)}_{os.path.basename(clip['path'])}")
    shutil.move(clip["path"], dest)
    try:
        os.remove(thumb_path(clip["path"]))
    except OSError:
        pass
    keep = {k: clip.get(k) for k in ("channel", "caption", "moment", "start", "end", "vod_url", "date", "rating",
                                     "ai_score")}
    rec = dict(keep, orig=os.path.normpath(clip["path"]), file=dest, trashed=time.time(), score10=score)
    items = load_trash()
    items.append(rec)
    _save_trash(items)
    return rec


def restore_from_trash(rec: dict) -> str:
    import shutil
    dest = rec["orig"]
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):  # на этом месте уже другой файл (например, нарезали заново) — не затираем
        base, n = dest[:-4], 2
        while os.path.exists(f"{base} ({n}).mp4"):
            n += 1
        dest = f"{base} ({n}).mp4"
    shutil.move(rec["file"], dest)
    _save_trash([t for t in load_trash() if t["file"] != rec["file"]])
    make_thumb(dest)
    return dest


def purge_trash(recs: list[dict]) -> int:
    """Удалить навсегда. Возвращает, сколько байт освободилось."""
    freed = 0
    gone = {r["file"] for r in recs}
    for r in recs:
        try:
            freed += os.path.getsize(r["file"])
            os.remove(r["file"])
        except OSError:
            pass
    _save_trash([t for t in load_trash() if t["file"] not in gone])
    from . import edits
    for r in recs:  # исходники для правок этих клипов больше не нужны
        if not os.path.exists(r.get("orig", "")):
            edits.forget(r.get("orig", ""))
    return freed


# ---------- что реально ушло в публикацию (для «Доктора»: связать видео в аналитике с клипом) ----------
def _published_file() -> str:
    return os.path.join(_state(), "published.json")


def load_published() -> dict:
    from . import team
    if team.enabled():
        return team.load_merged("published", "t")
    try:
        with open(_published_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def record_published(path: str, platform: str, title: str, description: str, post_id: str = "", url: str = "",
                     when: str = "") -> None:
    """when — время, на которое публикацию запланировали в приложении (иначе — сейчас)."""
    import time
    data = load_published()
    rec = {"title": title, "description": description, "time": when or time.strftime("%Y-%m-%dT%H:%M:%S")}
    if when:
        rec["scheduled"] = True
    if post_id:
        rec["id"] = post_id
    if url:
        rec["url"] = url
    from . import team
    if team.enabled():
        cur = team.load_merged("published", "t").get(os.path.normpath(path)) or {}
        cur = dict(cur, t=time.time())
        cur[platform] = dict(rec, by=team.me())
        team.put("published", path, cur)
        return
    data.setdefault(os.path.normpath(path), {})[platform] = rec
    with open(_published_file(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
