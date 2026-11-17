"""Ежедневные папки: <папка>/ДД.ММ.ГГГГ/ с шортсами, отчётом и zip-архивом за день."""
from __future__ import annotations

import json
import os
import shutil
import zipfile
from datetime import datetime


def today_label(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime("%d.%m.%Y")


def day_dir(root: str, label: str | None = None) -> str:
    path = os.path.join(root, label or today_label())
    os.makedirs(path, exist_ok=True)
    return path


STATE_DIR: str | None = None  # служебная папка (задаётся из настроек)


def set_state_dir(path: str) -> None:
    global STATE_DIR
    STATE_DIR = path


def _log_path(folder: str) -> str:
    if STATE_DIR:
        d = os.path.join(STATE_DIR, "days")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, os.path.basename(os.path.normpath(folder)) + ".json")
    return os.path.join(folder, "_day.json")


def _load(folder: str) -> dict:
    p = _log_path(folder)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {"clips": [], "events": []}


def _save(folder: str, data: dict) -> None:
    p = _log_path(folder)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(p + ".tmp", p)


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:40] or "stream"


def deliver_clip(root: str, tmp_file: str, clip: dict, channel: str) -> str:
    """Кладёт готовый шортс в папку сегодняшнего дня (атомарно: сначала файл
    дописывается целиком, потом появляется в папке) и обновляет отчёт."""
    folder = day_dir(root)
    sub = os.path.join(folder, _safe(channel))
    os.makedirs(sub, exist_ok=True)
    n = len([f for f in os.listdir(sub) if f.lower().endswith(".mp4")]) + 1
    sec = int(clip.get("moment", clip.get("start", 0)))
    nice = f"{n:02d}_{sec // 3600}ч{sec % 3600 // 60:02d}м{sec % 60:02d}с.mp4"
    dest = os.path.join(sub, nice)
    while os.path.exists(dest):
        n += 1
        dest = os.path.join(sub, f"{n:02d}_{sec // 3600}ч{sec % 3600 // 60:02d}м{sec % 60:02d}с.mp4")
    tmp_dest = dest + ".part"
    shutil.move(tmp_file, tmp_dest)
    os.replace(tmp_dest, dest)
    data = _load(folder)
    clip = dict(clip, file=os.path.relpath(dest, folder), channel=channel,
                created=datetime.now().strftime("%H:%M"))
    data["clips"].append(clip)
    _save(folder, data)
    write_day_report(folder)
    return dest


def log_event(root: str, text: str) -> None:
    """Записывает событие дня (начало/конец стрима, ошибки) — попадёт в отчёт."""
    folder = day_dir(root)
    data = _load(folder)
    data["events"].append({"time": datetime.now().strftime("%H:%M"), "text": text})
    _save(folder, data)
    write_day_report(folder)


def _fmt(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def write_day_report(folder: str) -> str:
    data = _load(folder)
    label = os.path.basename(os.path.normpath(folder))
    clips = data["clips"]
    by_ch: dict[str, list[dict]] = {}
    for c in clips:
        by_ch.setdefault(c["channel"], []).append(c)

    L = [f"# Отчёт за {label}", "",
         f"Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}", "",
         f"**Всего шортсов: {len(clips)}**", ""]
    for ch, cs in by_ch.items():
        L.append(f"- {ch}: {len(cs)}")
    L.append("")
    for ch, cs in by_ch.items():
        L += [f"## {ch}", ""]
        titles = sorted({c.get("vod_title", "") for c in cs if c.get("vod_title")})
        for t in titles:
            L.append(f"Стрим: *{t}*")
        L += ["", "| # | Создан | Момент на стриме | Длина | Оценка | Файл | Что писал чат |",
              "|---|---|---|---|---|---|---|"]
        for i, c in enumerate(sorted(cs, key=lambda c: (c.get("vod_url", ""), c["start"])), 1):
            moment = _fmt(c.get("moment", c["start"]))
            if c.get("link"):
                moment = f"[{moment}]({c['link']})"
            chat = " · ".join(c.get("top_messages", [])[:4]).replace("|", "/")
            L.append(f"| {i} | {c.get('created', '')} | {moment} | {int(c['end'] - c['start'])} с | "
                     f"{c['score']} | {c['file'].replace(os.sep, '/')} | {chat} |")
        L.append("")
    if data["events"]:
        L += ["## Журнал", ""] + [f"- {e['time']} — {e['text']}" for e in data["events"]] + [""]
    path = os.path.join(folder, f"отчет_{label}.md")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    os.replace(path + ".tmp", path)
    return path


def build_zip(folder: str) -> str | None:
    """Собирает ДД.ММ.ГГГГ.zip со всеми шортсами дня и отчётом."""
    data = _load(folder)
    if not data["clips"]:
        return None
    label = os.path.basename(os.path.normpath(folder))
    report = write_day_report(folder)
    zpath = os.path.join(folder, f"{label}.zip")
    tmp = zpath + ".part"
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_STORED) as z:  # mp4 уже сжаты
        for c in data["clips"]:
            src = os.path.join(folder, c["file"])
            if os.path.exists(src):
                z.write(src, c["file"].replace(os.sep, "/"))
        z.write(report, os.path.basename(report))
    os.replace(tmp, zpath)
    return zpath
