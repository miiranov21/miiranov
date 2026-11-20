"""💾 Хранитель данных: раз в неделю сохраняет данные программы в отдельную папку.

Что входит в копию: все служебные файлы программы (план, отметки «выложено», история надписей, решения
автопилота, архив-указатель, разобранные стримы, стратегия «Доктора», настройки, список стримеров, обмен
с «Доктором»). Сами клипы — только если включено «копировать и клипы» (они большие).
Хранится несколько последних копий; старые удаляются. Если аккаунт заблокируют или компьютер сломается —
данные восстанавливаются из копии (кнопка «Восстановить из копии…»).
"""
from __future__ import annotations

import json
import os
import shutil
import time

from . import paths

EVERY_DAYS = 7
KEEP = 8
SKIP_DIRS = {"frames", "models", "policy_frames", "build", "tg_assist", "recut", "fixed"}  # архив и корзина: указатели берём, видео — нет
SKIP_EXT = {".mp4", ".ts", ".mkv", ".webm", ".part", ".ass", ".wav", ".jpg", ".png", ".onnx", ".npy", ".tmp"}


def _cfg_path() -> str:
    return os.path.join(paths.default_work_dir(), "backup.json")


def load() -> dict:
    try:
        with open(_cfg_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save(cfg: dict) -> None:
    os.makedirs(os.path.dirname(_cfg_path()), exist_ok=True)
    with open(_cfg_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)


def default_dir() -> str:
    return os.path.join(paths.desktop_dir(), "StreamClipper — резервные копии")


def target_dir() -> str:
    return load().get("dir") or default_dir()


def due() -> bool:
    last = float(load().get("last") or 0)
    return time.time() - last >= EVERY_DAYS * 86400


def _copy_tree(src: str, dst: str, skip_dirs=SKIP_DIRS, skip_ext=SKIP_EXT) -> tuple[int, int]:
    files = size = 0
    for root, dirs, names in os.walk(src):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
        for n in names:
            if os.path.splitext(n)[1].lower() in skip_ext:
                continue
            s = os.path.join(root, n)
            d = os.path.join(dst, os.path.relpath(s, src))
            try:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)
                files += 1
                size += os.path.getsize(s)
            except OSError:
                pass
    return files, size


def make_backup(log=print, with_clips: bool | None = None) -> dict:
    """Сделать копию сейчас. Возвращает {"path", "files", "mb", "clips"}."""
    cfg = load()
    with_clips = cfg.get("with_clips", False) if with_clips is None else with_clips
    base = target_dir()
    stamp = time.strftime("%Y-%m-%d_%H-%M")
    out = os.path.join(base, f"копия_{stamp}")
    os.makedirs(out, exist_ok=True)
    files, size = _copy_tree(paths.default_work_dir(), os.path.join(out, "данные_программы"))
    prog = paths.program_dir()
    for name in ("settings.json", "streamers.txt", "claude_key.txt"):
        p = os.path.join(prog, name)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(out, name))
            files += 1
    exch = os.path.join(prog, "exchange")
    if os.path.isdir(exch):
        f2, s2 = _copy_tree(exch, os.path.join(out, "exchange"))
        files, size = files + f2, size + s2
    team = paths.team_dir()
    if team and os.path.isdir(os.path.join(team, ".team")):  # общая папка с другом: общие отметки и дневники
        f2, s2 = _copy_tree(os.path.join(team, ".team"), os.path.join(out, "общая_папка_team"))
        files, size = files + f2, size + s2
    clips = 0
    clip_list = []
    try:
        from . import library
        for d in library.list_dates():
            for c in library.list_clips(d):
                clip_list.append({k: c.get(k) for k in ("path", "channel", "caption", "date", "posted", "vod_url", "start", "end")})
    except Exception:
        pass
    with open(os.path.join(out, "список_клипов.json"), "w", encoding="utf-8") as f:
        json.dump(clip_list, f, ensure_ascii=False, indent=1, default=str)
    if with_clips:  # сами клипы — полная копия папки клипов
        f2, s2 = _copy_tree(paths.default_out_dir(), os.path.join(out, "клипы"), skip_dirs=set(), skip_ext={".tmp", ".part"})
        clips, size = f2, size + s2
    with open(os.path.join(out, "ПРОЧТИ.txt"), "w", encoding="utf-8") as f:
        f.write("Резервная копия Stream Clipper от " + time.strftime("%d.%m.%Y %H:%M") + "\n\n"
                "Восстановить: в программе «Настройки» → «💾 Хранитель данных» → «Восстановить из копии…» и выбрать эту папку.\n"
                "Внутри: данные программы (план, отметки, разобранные стримы, стратегия), настройки, список стримеров,\n"
                "список клипов" + (" и сами клипы." if with_clips else ". Сами клипы в эту копию не входят.") + "\n"
                "В копии есть ключи (бот Telegram, площадки) — не выкладывай её в общий доступ.\n")
    # старые копии — прочь, оставляем последние KEEP
    olds = sorted(d for d in os.listdir(base) if d.startswith("копия_") and os.path.isdir(os.path.join(base, d)))
    for d in olds[:-KEEP]:
        shutil.rmtree(os.path.join(base, d), ignore_errors=True)
    cfg.update(last=time.time(), last_path=out, last_files=files, last_mb=round(size / 1e6, 1))
    save(cfg)
    log(f"💾 Хранитель данных: резервная копия готова — {files} файлов, {size / 1e6:.0f} МБ → {out}")
    return {"path": out, "files": files, "mb": round(size / 1e6, 1), "clips": clips}


def restore(src: str, log=print) -> int:
    """Вернуть данные из копии (служебные файлы и настройки). Текущие данные перед этим сохраняются в копию."""
    data = os.path.join(src, "данные_программы")
    if not os.path.isdir(data):
        raise RuntimeError("в этой папке нет копии Stream Clipper (нет папки «данные_программы»)")
    make_backup(log=lambda m: None, with_clips=False)  # на всякий случай — снимок текущего состояния
    n, _ = _copy_tree(data, paths.default_work_dir(), skip_dirs=set(), skip_ext=set())
    prog = paths.program_dir()
    for name in ("settings.json", "streamers.txt"):
        p = os.path.join(src, name)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(prog, name))
            n += 1
    log(f"💾 Хранитель данных: восстановлено файлов — {n}. Перезапусти программу.")
    return n


def wipe_all(log=print, forget_streams: bool = True) -> dict:
    """«🧹 Начать с чистого листа»: сначала резервная копия, потом ВСЕ клипы — в корзину (вернуть можно,
    пока корзину не очистили), архив, план, очередь Telegram, отметки «выложено», решения автопилота и «Доктора»
    очищаются; forget_streams — ещё и память «что разобрано» (стримы разберутся заново)."""
    from . import archive, autopilot, exchange, library, progress, tg_assist
    snap = make_backup(log=lambda m: None, with_clips=False)
    moved = 0
    for d in library.list_dates():
        for c in library.list_clips(d):
            try:
                library.move_to_trash(c, c.get("score10"))
                moved += 1
            except OSError:
                pass
    # архив: сжатые копии — в корзину программы, указатель — пустой
    arch = 0
    trash = library.trash_dir()
    os.makedirs(trash, exist_ok=True)
    for rec in archive.load():
        for k in ("small", "thumb"):
            p = rec.get(k)
            if p and os.path.exists(p):
                try:
                    shutil.move(p, os.path.join(trash, f"arch_{int(time.time() * 1000)}_{os.path.basename(p)}"))
                except OSError:
                    pass
        arch += 1
    archive._save([])
    # план, очередь, отметки, решения
    st = autopilot.load_state()
    st["clips"] = {}
    st.pop("quality_checked", None)
    autopilot.save_state(st)
    tst = tg_assist.load()
    tst["jobs"] = {}
    tst.pop("replace", None)
    tg_assist.save(tst)
    work = paths.default_work_dir()
    for name in ("posted.json", "published.json", "decisions.json", "renders.json", "captions_history.json",
                 "captions_used.json", "extra_vods.json"):
        for base in (work, library._state()):
            p = os.path.join(base, name)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
    try:
        from . import team
        if team.enabled():
            for kind in ("posted", "published"):
                team.write_own(kind, {})
    except Exception:
        pass
    if forget_streams:  # дневник клипов (иначе те же моменты стримов не нарежутся заново) — он есть в копии
        for ddir in (os.path.join(library._state(), "days"),):
            if os.path.isdir(ddir):
                for fn in os.listdir(ddir):
                    if fn.endswith(".json"):
                        try:
                            os.remove(os.path.join(ddir, fn))
                        except OSError:
                            pass
        try:
            from . import team
            if team.enabled():
                me = team._safe(team.me())
                tdir = os.path.join(team.shared_dir(), "days")
                for fn in os.listdir(tdir) if os.path.isdir(tdir) else []:
                    if fn.endswith(f".{me}.json"):
                        os.remove(os.path.join(tdir, fn))
        except Exception:
            pass
        try:
            with progress._lock:
                progress._save({})
        except Exception:
            pass
        for name in ("watch_state.json", "vod_state.json"):
            p = os.path.join(work, name)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
    log(f"🧹 Чистый лист: клипов в корзину — {moved}, из архива — {arch}; план, очередь, отметки очищены. "
        f"Копия до очистки: {snap['path']}")
    return {"clips": moved, "archive": arch, "backup": snap["path"]}
