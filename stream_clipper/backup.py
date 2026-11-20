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
