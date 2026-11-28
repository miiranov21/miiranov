"""Сам выбирает стримеров для слежки: кто сейчас в эфире и на хайпе (английский Twitch, категории ниши,
любимчики из стратегии «Доктора»). Переписывает streamers.txt — слежка подхватывает список на ходу.
Кого слежка уже ведёт, не выкидываем, пока его эфир не закончился и запись не дорезана."""
from __future__ import annotations

import json
import math
import os
import time

from . import paths

DEFAULT_CATEGORIES = ["Grand Theft Auto VI", "Just Chatting", "IRL"]
KEEP_AFTER_LIVE = 3 * 3600   # после конца эфира держим ещё 3 ч — чтобы дорезать запись
MIN_VIEWERS = 1000            # меньше — моментов и клипов зрителей почти нет
BAD_LABELS = {"SexualThemes", "Gambling"}  # такие эфиры режут площадки — не берём
HEADER = ("# Список ведёт программа сама: выбирает, кто сейчас в эфире и на хайпе.\n"
          "# Выключить — сними галочку «🤖 Сам выбирает стримеров» над списком.\n")


def enabled() -> bool:
    return bool(paths._settings().get("auto_streamers", True))


def _max() -> int:
    try:
        return max(1, int(paths._settings().get("auto_streamers_max") or 6))
    except (TypeError, ValueError):
        return 6


def _strategy() -> dict:
    try:
        from . import strategy
        return strategy.get() or {}
    except Exception:
        return {}


def blocked() -> set:
    """Кого не брать никогда: settings.json → auto_streamers_block."""
    return {str(n).strip().lower().lstrip("@") for n in paths._settings().get("auto_streamers_block") or []}


def favorites(s: dict) -> set:
    """Стримеры, которых «Доктор» и «Трендовик» считают сильными сейчас."""
    ap = s.get("autopilot") or {}
    hb = s.get("hook_bank") or {}
    names = list((ap.get("streamer_mix") or {}).get("priority_streamers") or [])
    names += list(hb.get("male_streamers") or []) + list(hb.get("female_streamers") or [])
    names += [t.get("streamer", "") for t in (s.get("trends") or []) if isinstance(t, dict)]
    return {n.strip().lower().lstrip("@") for n in names if isinstance(n, str) and n.strip()}


def categories(s: dict) -> list:
    c = ((s.get("autopilot") or {}).get("streamer_mix") or {}).get("categories")
    return [x for x in c if isinstance(x, str)] if isinstance(c, list) and c else DEFAULT_CATEGORIES


def live_candidates(cats: list, favs: set) -> dict:
    """{login: {"viewers", "category", "fav"}} — только те, кто сейчас в эфире."""
    from .twitch import _gql
    out: dict = {}
    for cat in cats:
        safe = cat.replace('"', "")
        d = _gql('query{game(name:"%s"){streams(first:20,options:{languages:["EN"]}){edges{node{'
                 'broadcaster{login broadcastSettings{isMature}} viewersCount contentClassificationLabels{id}}}}}}' % safe)
        for e in (((d.get("game") or {}).get("streams") or {}).get("edges") or []):
            n = e.get("node") or {}
            b = n.get("broadcaster") or {}
            login = (b.get("login") or "").lower()
            labels = {x.get("id") for x in (n.get("contentClassificationLabels") or []) if isinstance(x, dict)}
            if login and login not in blocked() and (login in favs or not (labels & BAD_LABELS
                                                                           or (b.get("broadcastSettings") or {}).get("isMature"))):
                out[login] = {"viewers": int(n.get("viewersCount") or 0), "category": cat, "fav": login in favs}
    if favs:
        logins = ",".join('"%s"' % f.replace('"', "") for f in sorted(favs))
        d = _gql("query{users(logins:[%s]){login stream{viewersCount game{name}}}}" % logins)
        for u in d.get("users") or []:
            st = (u or {}).get("stream")
            if st:
                out[u["login"].lower()] = {"viewers": int(st.get("viewersCount") or 0),
                                           "category": ((st.get("game") or {}).get("name") or ""), "fav": True}
    return out


def score(c: dict) -> float:
    s = math.log10(max(10, c["viewers"]))
    if c.get("fav"):
        s += 1.0                       # проверенные стримеры: их клипы у нас уже заходят
    if "grand theft auto" in (c.get("category") or "").lower():
        s += 0.5                       # главная тема канала
    return s


def choose(cands: dict, current: list, state: dict, now: float, max_n: int, offline: list = ()) -> list:
    """Новый список логинов. current — кто сейчас в списке, state — {login: {"last_live": ts}}.
    offline — любимчики не в эфире: ими добираем список, их прошлые стримы режем по кругу."""
    keep = [n for n in current if n in cands or now - float((state.get(n) or {}).get("last_live", 0)) < KEEP_AFTER_LIVE]
    pool = sorted((n for n, c in cands.items() if n not in keep and (c.get("fav") or c["viewers"] >= MIN_VIEWERS)),
                  key=lambda n: -score(cands[n]))
    pool += [n for n in offline if n not in keep and n not in pool]
    return keep + pool[:max(0, max_n - len(keep))]


def queue_past_streams(names: list, log=print) -> None:
    """Кто не в эфире — берём его последний неразобранный стрим и ставим в очередь «прошлых стримов» слежки."""
    from . import progress, twitch
    path = os.path.join(paths.default_work_dir(), "extra_vods.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    vods = [v for v in (data.get("vods") or []) if v.get("url")]
    have = {v.get("channel", "").lower() for v in vods}
    done = progress.load()
    added = []
    for n in names:
        if n in have:
            continue
        try:
            streams = twitch.list_streams("twitch", n, 3)
        except Exception:
            continue
        for v in streams:
            e = done.get(str(v.get("key")))
            sm = progress.summary(e) if e else None
            if sm and sm.get("finished"):
                continue
            vods.append({"url": v["url"], "key": str(v.get("key") or ""), "channel": n, "title": v.get("title") or "",
                         "from": float(sm.get("resume") or 0) if sm else 0.0})
            added.append(f"{n} — {(v.get('title') or '')[:40]}")
            break
    if added:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"vods": vods}, f, ensure_ascii=False, indent=1)
        os.replace(path + ".tmp", path)
        log("🤖 Не в эфире — режу их прошлые стримы: " + "; ".join(added))


def _read(path: str) -> tuple[list, list]:
    tw, other = [], []
    try:
        with open(path, encoding="utf-8-sig") as f:
            for ln in f:
                n = ln.split("#")[0].strip()
                if n.startswith(("@", "yt:")) or "youtu" in n.lower():
                    other.append(n)
                elif n:
                    tw.append(n.lower())
    except OSError:
        pass
    return tw, other


def update(path: str, log=print) -> bool:
    """Пересобрать список; True — если поменяли файл."""
    if not enabled():
        return False
    s = _strategy()
    favs = favorites(s)
    try:
        cands = live_candidates(categories(s), favs)
    except Exception as e:
        log(f"🤖 Не смог узнать, кто сейчас в эфире ({str(e)[:120]}) — список стримеров не меняю")
        return False
    st_path = os.path.join(paths.default_work_dir(), "auto_streamers.json")
    try:
        with open(st_path, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        state = {}
    now = time.time()
    for n in cands:
        state.setdefault(n, {})["last_live"] = now
    tw, other = _read(path)
    ap = (s.get("autopilot") or {}).get("streamer_mix") or {}
    order = [n.lower() for n in ap.get("priority_streamers") or [] if isinstance(n, str)]
    offline = [n for n in order + sorted(favs - set(order)) if n not in cands and n not in blocked()]
    new = choose(cands, tw, state, now, _max(), offline)
    try:
        queue_past_streams([n for n in new if n not in cands], log)
    except Exception as e:
        log(f"🤖 Прошлые стримы не поставил в очередь: {str(e)[:120]}")
    os.makedirs(os.path.dirname(st_path), exist_ok=True)
    with open(st_path, "w", encoding="utf-8") as f:
        json.dump({n: v for n, v in state.items() if now - v.get("last_live", 0) < 7 * 86400}, f)
    if set(new) == set(tw):
        return False
    added, gone = [n for n in new if n not in tw], [n for n in tw if n not in new]
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n# Twitch\n" + "".join(n + "\n" for n in new) + "\n# YouTube\n" + "".join(n + "\n" for n in other))
    os.replace(tmp, path)
    why = ", ".join(f"{n} ({cands[n]['viewers']} зр., {cands[n]['category']})" for n in added if n in cands)
    log("🤖 Сам выбрал стримеров: " + (f"+ {why}" if why else "") + (f"; − {', '.join(gone)}" if gone else ""))
    return True
