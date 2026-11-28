"""Сам выбирает, что резать: всё про GTA 6, где есть просмотры и охват.
• В эфире: английский Twitch в категории GTA 6 (и любимчики «Доктора», если играют в GTA 6) → streamers.txt,
  слежка подхватывает список на ходу; кого ведёт — не выкидываем, пока эфир не дорезан.
• Прошлые стримы: самые просматриваемые записи про GTA 6 (любые — хоть первый стрим IShowSpeed) →
  очередь «прошлых стримов» слежки, режутся по кругу."""
from __future__ import annotations

import json
import math
import re
import os
import time

from . import paths

DEFAULT_CATEGORIES = ["Grand Theft Auto VI"]
TOPIC = re.compile(r"\bgta\s*-?\s*(6|vi)\b|grand theft auto vi\b", re.I)  # стрим про GTA 6 по названию
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
            game = ((st or {}).get("game") or {}).get("name") or ""
            if st and any(c.lower() == game.lower() for c in cats):  # любимчик в эфире, но не в GTA 6 — не берём
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


def choose(cands: dict, current: list, state: dict, now: float, max_n: int) -> list:
    """Новый список логинов. current — кто сейчас в списке, state — {login: {"last_live": ts}}."""
    keep = [n for n in current if n in cands or now - float((state.get(n) or {}).get("last_live", 0)) < KEEP_AFTER_LIVE]
    pool = sorted((n for n, c in cands.items() if n not in keep and (c.get("fav") or c["viewers"] >= MIN_VIEWERS)),
                  key=lambda n: -score(cands[n]))
    return keep + pool[:max(0, max_n - len(keep))]


def top_past(cats: list, favs: set) -> list:
    """Самые просматриваемые записи про GTA 6: [{url, key, channel, title, views}], сильные — первыми."""
    from .twitch import _gql
    vids: dict = {}

    def add(node, login):
        vid = str(node.get("id") or "")
        title = node.get("title") or ""
        game = ((node.get("game") or {}).get("name") or "")
        if vid and login and login not in blocked() and (TOPIC.search(title) or any(c.lower() == game.lower() for c in cats)):
            views = int(node.get("viewCount") or 0) * (3 if login in favs else 1)  # любимчики «Доктора» — выше
            vids[vid] = {"url": f"https://www.twitch.tv/videos/{vid}", "key": vid, "channel": login,
                         "title": title, "views": views}
    for cat in cats:
        d = _gql('query{game(name:"%s"){videos(first:30,languages:["en"],sort:VIEWS){edges{node{'
                 'id title viewCount game{name} owner{login}}}}}}' % cat.replace('"', ""))
        for e in (((d.get("game") or {}).get("videos") or {}).get("edges") or []):
            n = e.get("node") or {}
            add(n, ((n.get("owner") or {}).get("login") or "").lower())
    for f in sorted(favs):
        d = _gql('query{user(login:"%s"){videos(first:15,type:ARCHIVE,sort:VIEWS){edges{node{'
                 'id title viewCount game{name}}}}}}' % f.replace('"', ""))
        for e in ((((d.get("user") or {}).get("videos") or {}).get("edges")) or []):
            add(e.get("node") or {}, f)
    return sorted(vids.values(), key=lambda v: -v["views"])


def queue_past_streams(videos: list, want: int, log=print) -> None:
    """Дополняем очередь «прошлых стримов» слежки до want записей: самые сильные, ещё не разобранные."""
    from . import progress
    path = os.path.join(paths.default_work_dir(), "extra_vods.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    vods = [v for v in (data.get("vods") or []) if v.get("url")]
    have = {str(v.get("key") or v.get("url")) for v in vods}
    done = progress.load()
    added = []
    for v in videos:
        if len(vods) >= want:
            break
        if v["key"] in have:
            continue
        e = done.get(v["key"])
        sm = progress.summary(e) if e else None
        if sm and sm.get("finished"):
            continue
        vods.append({"url": v["url"], "key": v["key"], "channel": v["channel"], "title": v["title"],
                     "from": float(sm.get("resume") or 0) if sm else 0.0})
        added.append(f"{v['channel']} — {v['title'][:40]}")
    if added:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"vods": vods}, f, ensure_ascii=False, indent=1)
        os.replace(path + ".tmp", path)
        log("🤖 Режу самые просматриваемые стримы про GTA 6: " + "; ".join(added))


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
    new = choose(cands, tw, state, now, _max())
    try:  # прошлые стримы про GTA 6: всегда в работе пара сильных записей, ночью (мало эфиров) — больше
        queue_past_streams(top_past(categories(s), favs), max(2, _max() - len(new)), log)
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
