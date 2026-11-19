"""Обмен с «Доктором шортсов» (программа аналитики соцсетей).

Распределение работы:
  * Stream Clipper — нарезает, хранит клипы, делает монтаж, готовит выкладку и ставит галочки «выложено»;
  * «Доктор» — по аналитике (твоей и конкурентов) решает, какой клип куда выкладывать, с какими текстами
    и хэштегами под каждую площадку, какой монтаж нужен под площадку и что лучше удалить.

Папка обмена: <папка программы>/exchange
  catalog.json   — пишет Stream Clipper: все клипы с данными (обновляется сам);
  decisions.json — пишет «Доктор»: решения по клипам. Stream Clipper подхватывает его сам.
Формат описан в EXCHANGE_FORMAT.md рядом с ними (создаётся автоматически).
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime

from . import library, paths

PLATFORMS = ("youtube", "tiktok", "instagram")
EDIT_TYPES = ("trim", "credit", "hook")

FORMAT_DOC = """# Обмен Stream Clipper ⇄ «Доктор шортсов» (версия 1)

## catalog.json — пишет Stream Clipper (только чтение для «Доктора»)
{"version": 1, "generated": "2026-11-26T12:00:00", "clips": [
  {"id": "26.11.2026/kaicenat/01_1ч00м10с.mp4",   // постоянный ключ клипа
   "path": "C:/Users/.../01_1ч00м10с.mp4", "thumb": "...png",
   "streamer": "kaicenat", "source": "twitch", "vod_url": "https://www.twitch.tv/videos/...",
   "date": "26.11.2026", "moment": 3610.0, "duration": 34.8,
   "caption": "надпись-плашка на клипе (хук)", "has_hook": true, "has_subs": true,
   "transcript": "что говорит стример", "lang": "ru",
   "rating": 8,                // 1–10, не меняется со временем
   "ai_score": 7.5,            // оценка Claude, если была
   "policy": {"issues": [{"kind": "profanity", "t0": 2.1, "t1": 2.6, "what": "...", "severity": "medium"}],
              "fixed": false},
   "posted": {"youtube": false, "tiktok": true, "instagram": false},
   "edits": ["Подпись автора"],
   "published": {"tiktok": {"title": "...", "description": "текст с хэштегами, как ушёл", "time": "2026-11-26T18:02:11"}}}
]}

## decisions.json — пишет «Доктор»
{"version": 1, "generated": "2026-11-26T12:05:00", "decisions": [
  {"id": "26.11.2026/kaicenat/01_1ч00м10с.mp4",
   "platforms": {
     "tiktok": {"post": true, "when": "2026-11-26T18:00:00",       // время по часам компьютера, необязательно
                "title": "...", "description": "...", "hashtags": ["#kaicenat", "#gta6", "#gtaonline"],
                "edits": [{"type": "trim", "cut_start": 2.0, "cut_end": 0.0},
                          {"type": "hook", "text": "КАЙ УГНАЛ ТАНК", "seconds": 3},
                          {"type": "credit", "pos": "bottom-left"}]},
     "instagram": {"post": false, "reason": "нет хука в первые 2 секунды"},
     "youtube": {"post": true, "title": "...", "description": "...", "hashtags": ["#kaicenat", "#gta6"]}},
   "delete": false, "reason": "почему",
   "posted": {"tiktok": true}}                                      // видео уже выложено (видно по аналитике)
]}

Монтаж под площадку (edits) применяется к копии клипа для этой площадки, сам клип в папке не меняется:
  trim   — cut_start / cut_end: сколько секунд отрезать в начале / в конце;
  hook   — text, seconds (по умолчанию 3): крупная надпись-хук вверху кадра в первые секунды;
  credit — pos: bottom-left | top-left | top-right: подпись автора «Twitch | ник».
«delete» — только совет: человек подтверждает удаление (клип уходит в корзину).
Галочки «выложено» из «posted» ставятся сразу.
"""


def exchange_dir() -> str:
    d = os.path.join(paths.program_dir(), "exchange")
    os.makedirs(d, exist_ok=True)
    doc = os.path.join(d, "EXCHANGE_FORMAT.md")
    if not os.path.exists(doc):
        with open(doc, "w", encoding="utf-8") as f:
            f.write(FORMAT_DOC)
    return d


def clip_id(path: str) -> str:
    rel = os.path.relpath(os.path.normpath(path), os.path.normpath(paths.default_out_dir()))
    return rel.replace(os.sep, "/")


def _duration(c: dict) -> float:
    try:
        return round(float(c["end"]) - float(c["start"]), 1)
    except (KeyError, TypeError, ValueError):
        return 0.0


def export_catalog(path: str | None = None) -> str:
    """Каталог всех клипов для «Доктора»."""
    from . import credit, edits, policy
    dates = library.list_dates()
    clips = [c for d in dates for c in library.list_clips(d)]
    pool = [c for d in dates for c in library.list_clips(d, include_missing=True)]
    scores = library.frozen_ratings(pool) if pool else {}
    pol = policy.load_results()
    ed = edits.load()
    published = library.load_published()
    out = []
    for c in clips:
        p = os.path.normpath(c["path"])
        res = pol.get(p) or {}
        url = c.get("vod_url") or ""
        out.append({
            "id": clip_id(p), "path": p.replace("\\", "/"), "thumb": library.thumb_path(p).replace("\\", "/"),
            "streamer": c.get("channel", ""), "source": "youtube" if "youtu" in url else "twitch", "vod_url": url,
            "date": c.get("date", ""), "moment": c.get("moment", c.get("start")), "duration": _duration(c),
            "caption": c.get("caption") or "", "has_hook": bool(c.get("caption")),
            "has_subs": bool(c.get("words") or c.get("transcript")),
            "transcript": (c.get("transcript") or "")[:800], "lang": c.get("lang", ""),
            "rating": scores.get(c["path"]), "ai_score": c.get("ai_score"),
            "policy": {"issues": [{k: i.get(k) for k in ("kind", "t0", "t1", "what", "severity")}
                                  for i in res.get("issues", [])], "fixed": bool(res.get("fixed"))},
            "posted": {pl: bool(c["posted"].get(pl)) for pl in PLATFORMS},
            "edits": [edits.label(o) for o in (ed.get(p) or {}).get("ops", [])],
            "credit": credit.state(c) in ("on", "burned"),
            "published": published.get(p, {}),  # что реально ушло в публикацию: {площадка: {title, description, time}}
        })
    path = path or os.path.join(exchange_dir(), "catalog.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "generated": datetime.now().isoformat(timespec="seconds"), "clips": out}, f,
                  ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    return path


# ---------- решения «Доктора» ----------
def _store() -> str:
    return os.path.join(paths.default_work_dir(), "decisions.json")


def load_decisions() -> dict:
    """Решения по клипам: {id: decision} (последнее принятое)."""
    try:
        with open(_store(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _clean_platform(p: dict) -> dict:
    out = {"post": bool(p.get("post"))}
    for k in ("when", "title", "description", "reason"):
        if isinstance(p.get(k), str):
            out[k] = p[k][:5000]
    tags = p.get("hashtags")
    if isinstance(tags, str):
        tags = tags.split()
    if isinstance(tags, list):
        out["hashtags"] = [("#" + str(t).lstrip("#")).strip() for t in tags if str(t).strip()][:30]
    eds = []
    for e in p.get("edits") or []:
        if isinstance(e, dict) and e.get("type") in EDIT_TYPES:
            eds.append({k: e[k] for k in e if k in ("type", "cut_start", "cut_end", "text", "seconds", "pos")})
    if eds:
        out["edits"] = eds
    return out


def import_decisions(path: str | None = None, log=print) -> dict:
    """Читает decisions.json от «Доктора» и применяет то, что можно сразу (галочки «выложено»).
    Возвращает сводку: сколько решений, сколько к выкладке, сколько советов удалить."""
    path = path or os.path.join(exchange_dir(), "decisions.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("decisions") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("в файле нет списка decisions")
    known = {clip_id(c["path"]): c for d in library.list_dates() for c in library.list_clips(d)}
    store = load_decisions()
    summary = {"total": 0, "post": 0, "delete": 0, "posted": 0, "unknown": 0}
    for d in items:
        if not isinstance(d, dict) or not d.get("id"):
            continue
        cid = str(d["id"]).replace("\\", "/")
        c = known.get(cid)
        if not c:
            summary["unknown"] += 1
            continue
        summary["total"] += 1
        dec = {"platforms": {}, "delete": bool(d.get("delete")), "reason": str(d.get("reason") or "")[:500],
               "received": time.time()}
        for pl, p in (d.get("platforms") or {}).items():
            if pl in PLATFORMS and isinstance(p, dict):
                dec["platforms"][pl] = _clean_platform(p)
                summary["post"] += dec["platforms"][pl]["post"]
        summary["delete"] += dec["delete"]
        for pl, v in (d.get("posted") or {}).items():  # «Доктор» видит видео в аналитике — ставим галочку
            if pl in PLATFORMS and v and not c["posted"].get(pl):
                library.set_posted(c["path"], True, pl)
                summary["posted"] += 1
        store[cid] = dec
    with open(_store(), "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=1)
    return summary


def decision_for(clip: dict) -> dict | None:
    return load_decisions().get(clip_id(clip["path"]))


def plan(clips: list[dict]) -> list[tuple[dict, str, dict]]:
    """Что выложить по советам «Доктора»: [(клип, площадка, решение по площадке)] — ещё не выложенное,
    по времени «when» (без времени — в конце, лучшие сначала)."""
    dec = load_decisions()
    todo = []
    for c in clips:
        d = dec.get(clip_id(c["path"]))
        if not d:
            continue
        for pl, p in d.get("platforms", {}).items():
            if p.get("post") and not c["posted"].get(pl):
                todo.append((c, pl, p))

    def key(item):
        w = item[2].get("when") or "9999"
        return (w, -(item[0].get("score10") or 0))
    return sorted(todo, key=key)


def due(clips: list[dict]) -> list[tuple[dict, str, dict]]:
    """Из плана — то, чему пора: время «when» уже наступило (или не указано)."""
    now = datetime.now().isoformat(timespec="seconds")
    return [t for t in plan(clips) if (t[2].get("when") or "") <= now]


def platform_text(p: dict) -> tuple[str, str]:
    """(название, описание с хэштегами) из решения «Доктора»."""
    tags = " ".join(p.get("hashtags") or [])
    desc = "\n\n".join(x for x in (p.get("description") or "", tags) if x)
    return p.get("title") or "", desc


def author_line(clip: dict, platform: str) -> str:
    """Строка про автора в описании (правила «Доктора»): TikTok/Instagram — «🎥 ник (Twitch)», YouTube — «Стрим: ссылка»."""
    from . import credit
    name = credit.author_of(clip)
    src = credit.platform_of(clip)
    if platform == "youtube":
        url = clip.get("vod_url") or ""
        if not url or "twitch.tv/" not in url and "youtu" not in url:
            url = f"https://www.twitch.tv/{name}" if src == "Twitch" else f"https://www.youtube.com/@{name}"
        return f"Стрим: {url}"
    return f"🎥 {name} ({src})"


def with_author(desc: str, clip: dict, platform: str | None) -> str:
    if not platform:
        return desc
    line = author_line(clip, platform)
    return desc if line in desc else (desc.rstrip() + "\n\n" + line).strip()
