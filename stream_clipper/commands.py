"""Разовые команды «Доктора» из strategy.json → "commands": [...]. Каждая выполняется один раз (по id).

Сейчас умеет:
  {"id": "reset-2026-11-19", "type": "reset_posted",
   "keep": [{"clip": "19.11.2026/IShowSpeed/61_17ч03м13с.mp4", "platforms": ["tiktok"]}]}
  — пользователь удалил видео с площадок: снимаем отметки «выложено» у всех клипов, кроме перечисленных
    (клип — путь относительно папки клипов, как "id" в catalog.json), и даём им заново попасть в план.
"""
from __future__ import annotations

import json
import os
import time

from . import exchange, library, paths


def _done_file() -> str:
    return os.path.join(paths.default_work_dir(), "commands_done.json")


def _done() -> dict:
    try:
        with open(_done_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _mark(cid: str, result: str) -> None:
    d = _done()
    d[cid] = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "result": result}
    os.makedirs(os.path.dirname(_done_file()), exist_ok=True)
    with open(_done_file(), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def reset_posted(keep: list, log=print) -> str:
    from . import autopilot, tg_assist
    keep_map: dict = {}
    for k in keep or []:
        if isinstance(k, dict) and k.get("clip"):
            keep_map[str(k["clip"]).replace("\\", "/")] = set(k.get("platforms") or [])
    clips = [c for d in library.list_dates() for c in library.list_clips(d, include_missing=True)]
    unset, touched = 0, set()
    for c in clips:
        cid = exchange.clip_id(c["path"])
        kept = keep_map.get(cid, set())
        for pl, on in (c.get("posted") or {}).items():
            if on and pl not in kept:
                library.set_posted(c["path"], False, pl)
                unset += 1
                touched.add(os.path.normpath(c["path"]))
    # записи о публикации (что, когда, где) — тоже убираем, кроме оставленных
    pub = library.load_published()
    changed = False
    for path in list(pub):
        kept = keep_map.get(exchange.clip_id(path), set())
        for pl in list(pub[path]):
            if pl in exchange.PLATFORMS and pl not in kept:
                pub[path].pop(pl)
                changed = True
        if not any(pl in exchange.PLATFORMS for pl in pub[path]):
            pub.pop(path)
    if changed:
        try:
            from . import team
            if not team.enabled():
                with open(library._published_file(), "w", encoding="utf-8") as f:
                    json.dump(pub, f, ensure_ascii=False, indent=1)
        except Exception:
            pass
    # автопилот и Telegram: забываем старые решения по клипам — они заново пройдут отбор
    st = autopilot.load_state()
    for path in list(st.get("clips", {})):
        kept = keep_map.get(exchange.clip_id(path), set())
        if not kept:
            st["clips"].pop(path)
        else:
            q = st["clips"][path].get("queue") or {}
            for pl in list(q):
                if pl not in kept:
                    q.pop(pl)
    autopilot.save_state(st)
    tst = tg_assist.load()
    for jid, job in list(tst.get("jobs", {}).items()):
        if job.get("platform") not in keep_map.get(exchange.clip_id(job.get("path", "")), set()):
            tst["jobs"].pop(jid)
    tg_assist.save(tst)
    msg = f"снял отметки «выложено»: {unset} (у {len(touched)} клипов), оставил: " + \
        (", ".join(f"{k} ({', '.join(sorted(v))})" for k, v in keep_map.items()) or "ничего")
    log(msg)
    return msg


def run(event=None) -> int:
    """Выполнить новые команды из стратегии. Возвращает, сколько выполнено."""
    from . import strategy
    cmds = strategy.get().get("commands") or []
    done = _done()
    n = 0
    for cmd in cmds if isinstance(cmds, list) else []:
        if not isinstance(cmd, dict) or not cmd.get("id") or cmd["id"] in done:
            continue
        try:
            if cmd.get("type") == "reset_posted":
                res = reset_posted(cmd.get("keep") or [], log=lambda m: None)
            else:
                res = f"неизвестная команда {cmd.get('type')}"
            _mark(cmd["id"], res)
            n += 1
            if event:
                event("🩺", f"Команда «Доктора» выполнена: {res}", None, "info")
        except Exception as e:
            if event:
                event("❌", f"Команда «Доктора» не выполнилась: {e}", None, "error")
    return n
