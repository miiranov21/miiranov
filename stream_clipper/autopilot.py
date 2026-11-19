"""Автопилот: отбор → ревью (Claude смотрит кадры) → монтаж под площадки → проверка результата → публикация
в окна из стратегии «Доктора шортсов» → негодное в архив. Всё записывается в ленту и exchange/autopilot_log.json.

Работает в фоне из окна программы (переключатель «🤖 Автопилот»; «⏸ Пауза публикаций» останавливает только выкладку).
Без ключа Claude автопилот работает по правилам (без просмотра кадров) — это хуже, но работа не встаёт.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta

from . import archive, exchange, library, paths, strategy

PLATFORMS = ("tiktok", "youtube", "instagram")
MAX_REVIEWS_PER_RUN = 2
FLAGS = 0x08000000 if os.name == "nt" else 0


# ---------- состояние ----------
def _state_file() -> str:
    return os.path.join(paths.default_work_dir(), "autopilot.json")


def load_state() -> dict:
    try:
        with open(_state_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"clips": {}}


def save_state(st: dict) -> None:
    tmp = _state_file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _state_file())


def journal(entry: dict) -> None:
    p = os.path.join(exchange.exchange_dir(), "autopilot_log.json")
    try:
        with open(p, encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        items = []
    items.append(dict(entry, time=datetime.now().isoformat(timespec="seconds")))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(items[-2000:], f, ensure_ascii=False, indent=1)


# ---------- оценка и отбор ----------
def _days_old(c: dict) -> float:
    try:
        d = datetime.strptime(c.get("date", ""), "%d.%m.%Y")
        return max(0.0, (datetime.now() - d).total_seconds() / 86400)
    except ValueError:
        return 0.0


def _dur(c: dict) -> float:
    try:
        return float(c["end"]) - float(c["start"])
    except (KeyError, TypeError, ValueError):
        return 30.0


def score(c: dict, strat: dict) -> float:
    """Итоговая оценка 0–100 по весам из стратегии."""
    sc = strat.get("scoring") or {}
    w = sc.get("weights") or {}
    s = (c.get("score10") or 5) * float(w.get("rating", 6))
    ai = c.get("ai_score")
    s += (float(ai) if isinstance(ai, (int, float)) else (c.get("score10") or 5)) * float(w.get("ai_score", 3))
    if c.get("caption"):
        s += float(w.get("has_hook", 10))
    days = _days_old(c)
    if days > 3:
        s -= (days - 3) * float(w.get("stale_penalty_per_day_over_3", 5))
    else:
        s += (3 - days) * float(w.get("fresh_bonus_per_day_under_3", 0))
    s *= float((sc.get("streamer_weights") or {}).get((c.get("channel") or "").lower(), 1.0))
    d = _dur(c)
    if d < 7 or d > 60:
        s -= 15
    pol = c.get("policy") or {}
    if any(i.get("severity") == "high" for i in pol.get("issues", [])) and not pol.get("fixed"):
        s -= 25
    return max(0.0, min(100.0, s))


def duplicates(clips: list[dict]) -> dict:
    """Один и тот же момент стрима (тот же vod_url, момент ближе 25 с): {проигравший путь: путь победителя}."""
    out = {}
    by_vod: dict = {}
    for c in clips:
        by_vod.setdefault(c.get("vod_url") or c.get("channel"), []).append(c)
    for group in by_vod.values():
        group.sort(key=lambda c: -(c.get("_score") or 0))
        kept = []
        for c in group:
            m = float(c.get("moment", c.get("start", 0)) or 0)
            win = next((k for k in kept if abs(float(k.get("moment", k.get("start", 0)) or 0) - m) < 25), None)
            if win:
                out[c["path"]] = win["path"]
            else:
                kept.append(c)
    return out


# ---------- тексты по правилам «Доктора» ----------
def clean_text(platform: str, title: str, description: str, hashtags: list, clip: dict, strat: dict) -> dict:
    tr = strat.get("text_rules") or {}
    banned = {t.lower() for t in tr.get("banned_hashtags", [])}
    banned |= {t.lower() for t in (tr.get("cross_platform_banned") or {}).get(platform, [])}
    tags, seen = [], set()
    for t in hashtags or []:
        t = "#" + str(t).strip().lstrip("#")
        if len(t) > 1 and t.lower() not in banned and t.lower() not in seen:
            seen.add(t.lower())
            tags.append(t)
    lo, hi = (tr.get("hashtags_count") or {}).get(platform, [3, 5])
    tags = tags[:hi]
    if len(tags) < lo:
        nick = "#" + re.sub(r"\W", "", (clip.get("channel") or "").lower())
        for t in (nick, "#gta6", "#gta"):
            if len(tags) >= lo:
                break
            if t.lower() not in seen and t.lower() not in banned and len(t) > 1:
                tags.append(t)
                seen.add(t.lower())
    # хэштеги из описания тоже чистим (чтобы #fyp не пролез в тексте)
    desc = " ".join(w for w in description.split(" ") if w.lower().strip(".,!?") not in banned)
    tmax = int((tr.get("title_max") or {}).get(platform, 100))
    title = " ".join(w for w in title.split() if w.lower().strip(".,!?") not in banned
                     and not (w.startswith("#") and platform != "youtube"))
    desc = exchange.with_author(desc, clip, platform)
    return {"title": title[:tmax].strip(), "description": desc, "hashtags": tags}


# ---------- Claude: ревью и проверка ----------
def _frames(path: str, n: int = 6) -> list[str]:
    from .montage import duration
    d = duration(path) or 30
    work = os.path.join(paths.default_work_dir(), "autopilot", "frames")
    os.makedirs(work, exist_ok=True)
    out = []
    for i in range(n):
        t = d * (i + 0.5) / n
        p = os.path.join(work, f"f{i}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                        "-vf", "scale=360:-2", "-q:v", "5", p], capture_output=True, creationflags=FLAGS)
        if os.path.exists(p):
            with open(p, "rb") as f:
                out.append(base64.standard_b64encode(f.read()).decode())
    return out


def _claude(system: str, text: str, images: list[str], key: str) -> dict:
    import anthropic
    content: list = []
    for i, b in enumerate(images):
        content.append({"type": "text", "text": f"Frame {i + 1}"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b}})
    content.append({"type": "text", "text": text})
    client = anthropic.Anthropic(api_key=key, max_retries=3)
    resp = client.beta.messages.create(model="claude-opus-5-5", max_tokens=6000, output_config={"effort": "low"},
                                       betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                                       system=system, messages=[{"role": "user", "content": content}])
    if resp.stop_reason == "refusal":
        raise RuntimeError("модель отказалась")
    raw = next((b.text for b in resp.content if b.type == "text"), "")
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise RuntimeError("Claude не прислал план")
    return json.loads(m.group(0))


REVIEW_PROMPT = """You are the autopilot editor of a channel that posts vertical clips from livestreams to TikTok, YouTube Shorts and Instagram Reels.
You get frames of one clip, its transcript and data, plus the channel strategy (platform fit, risk rules, text rules, edit style).
Decide for each platform whether to post, what must be edited, and write the texts. Follow the strategy strictly:
- check every risk rule (copyright music, swearing, nudity/blood/weapons on real people, foreign watermarks/QR/links, unoriginal raw re-upload, clickbait);
  if a risk cannot be fixed with edits — do not post on that platform;
- mandatory edits from the edit style: hook text in the first 0-3 s (only if the clip has no caption plate), word-by-word subtitles
  (only if the clip has no subtitles yet), author credit top-left, loudness -14 LUFS, cut silences > 0.7 s; for promotion add zoom
  punches on peaks, loop_end, progress_bar for clips longer than 30 s; bleep swearing for YouTube and Instagram;
- texts: in the language of the streamer's speech; must include the streamer's nickname and what exactly happened; no banned hashtags,
  no other platforms' tags; hashtag counts and title lengths from text_rules.
Available edits (times in seconds of the original clip): trim{cut_start,cut_end}, cut_silence{min_gap}, speed{t0,t1,rate},
crop_out{box}, blur{t0,t1,box}, zoom{t,scale,dur}, subtitles{style:karaoke|plain,pos:center|lower_center},
replace_hook{text} (replace the caption plate already burned into the clip — use it when that caption is generic, repeats other
clips, mentions the chat/viewers, or contains swearing),
hook{text,seconds,style:plate|outline}, credit{pos,text}, progress_bar{on}, mute{t0,t1}, bleep{t0,t1}, bleep_profanity{all},
replace_audio{t0,t1,sfx:silence|whoosh}, loudness{lufs}, loop_end{crossfade}, cover{t,text}. box = [x,y,w,h] fractions 0..1.
Answer with JSON only:
{"archive": false, "reason": "short reason in Russian if archive",
 "platforms": {"tiktok": {"post": true, "why": "in Russian", "title": "...", "description": "...", "hashtags": ["#..."], "edits": [...]},
               "youtube": {...}, "instagram": {...}}}"""

CHECK_PROMPT = """You check the FINISHED version of a vertical clip before it is published on {platform}.
Look at the frames: is anything from the risk rules still visible or audible (per the transcript), is the hook readable in the first
frames, are subtitles inside safe zones (not in the bottom 20%, not in the right 15%), no black bars, credit visible but not in the way?
Answer with JSON only: {{"ok": true|false, "problems": ["in Russian"], "fix_edits": [ ...extra edits in the same format... ]}}"""


SINGLE = ("cut_silence", "subtitles", "hook", "credit", "progress_bar", "loudness", "loop_end", "cover", "trim")


def merge_edits(ops: list, extra: list) -> list:
    """Исправления после проверки: одиночные приёмы (хук, подпись, субтитры...) ЗАМЕНЯЮТСЯ, а не дублируются."""
    out = list(ops)
    for e in extra:
        if not isinstance(e, dict) or not e.get("type"):
            continue
        if e["type"] in SINGLE:
            out = [o for o in out if o.get("type") != e["type"]]
        out.append(e)
    return out


def ensure_mandatory(ops: list, c: dict, strat: dict, platform: str, duration: float) -> list:
    """Обязательный монтаж из стратегии — даже если план его забыл: подпись автора, громкость,
    хук (если на клипе нет надписи), субтитры (если их нет), запикать мат для YouTube и Instagram."""
    have = {o.get("type") for o in ops}
    add = []
    cr = (strat.get("credit_rules") or {}).get("on_video") or {}
    if cr.get(platform, True) and "credit" not in have:
        add.append({"type": "credit", "pos": cr.get("pos") or "top-left"})
    if "loudness" not in have:
        add.append({"type": "loudness", "lufs": -14})
    if not c.get("caption") and "hook" not in have:
        pass  # текста хука нет — его должен придумать план (Claude); выдумывать не будем
    if not (c.get("words") or c.get("transcript")) and "subtitles" not in have:
        add.append({"type": "subtitles", "style": "karaoke"})
    swear = any(i.get("kind") in ("profanity", "slur") for i in (c.get("policy") or {}).get("issues", []))
    if swear and platform in ("youtube", "instagram") and not have & {"bleep", "bleep_profanity", "mute"}:
        add.append({"type": "bleep_profanity", "all": True})
    from . import shape
    tgt = shape.target_for(platform)
    if tgt and duration > tgt[1] + 0.5 and "trim" not in have:
        # момент длиннее, чем любит площадка — версия короче: режем начало (но не ближе 3 с к пику), остальное — с конца
        excess = duration - tgt[1]
        peak_off = float(c.get("peak", 0) or 0) - float(c.get("start", 0) or 0)
        cut_a = min(excess, max(0.0, peak_off - 3.0)) if peak_off > 0 else excess * 0.5
        add.append({"type": "trim", "cut_start": round(cut_a, 2), "cut_end": round(excess - cut_a, 2)})
    if shape.length_rules().get("cut") and "cut_silence" not in have:
        add.append({"type": "cut_silence", "min_gap": 0.7})
    if duration > 30 and "progress_bar" not in have:
        add.append({"type": "progress_bar", "on": True})
    return list(ops) + add


def _strategy_brief(strat: dict) -> str:
    keep = {k: strat.get(k) for k in ("platform_fit", "risk_rules", "text_rules", "credit_rules", "lessons")}
    return json.dumps(keep, ensure_ascii=False)[:6000] + "\n\nEDIT STYLE:\n" + strategy.edit_style()[:3500]


def review(c: dict, strat: dict, key: str | None) -> dict:
    """План по площадкам. С ключом Claude — по кадрам и речи, без ключа — по правилам."""
    info = {k: c.get(k) for k in ("channel", "caption", "transcript", "lang", "score10", "ai_score")}
    info["duration"] = round(_dur(c), 1)
    info["has_hook"] = bool(c.get("caption"))
    info["has_subs"] = bool(c.get("words") or c.get("transcript"))
    info["policy_issues"] = [{k: i.get(k) for k in ("kind", "t0", "t1", "what")} for i in (c.get("policy") or {}).get("issues", [])]
    if key:
        return _claude(REVIEW_PROMPT, "CLIP:\n" + json.dumps(info, ensure_ascii=False) + "\n\nSTRATEGY:\n" + _strategy_brief(strat),
                       _frames(c["path"], 6), key)
    return rule_plan(c, strat, info)


def rule_plan(c: dict, strat: dict, info: dict) -> dict:
    """Без Claude: обязательный монтаж из EDIT_STYLE и тексты по шаблону."""
    from .caption import free_post
    d = info["duration"]
    spots = (strat.get("scoring") or {}).get("duration_sweet_spot_sec") or {}
    prules = strat.get("platform_rules") or {}
    swear = any(i["kind"] in ("profanity", "slur") for i in info["policy_issues"])
    nude = any(i["kind"] == "nudity" for i in info["policy_issues"])
    peak = None
    if c.get("peak") is not None and c.get("start") is not None:
        peak = float(c["peak"]) - float(c["start"])
    plats = {}
    for pl in PLATFORMS:
        lo, hi = (prules.get(pl) or {}).get("length_sec") or spots.get(pl, [8, 60])
        post = free_post(pl, c.get("channel", ""), c.get("caption", ""), c.get("vod_title", ""), c.get("transcript", ""),
                         c.get("top_messages") or [], c.get("lang") or "en", c.get("words") or [], peak,
                         display=c.get("credit_name") or "")
        edits = [{"type": "cut_silence", "min_gap": 0.7}]
        if not info["has_hook"] and c.get("caption"):
            edits.append({"type": "hook", "text": c["caption"], "seconds": 3})
        if not info["has_subs"]:
            edits.append({"type": "subtitles", "style": "karaoke"})
        edits += [{"type": "credit", "pos": "top-left"}, {"type": "loudness", "lufs": -14}, {"type": "loop_end"}]
        if d > 30:
            edits.append({"type": "progress_bar", "on": True})
        if swear and pl in ("youtube", "instagram"):
            edits.append({"type": "bleep_profanity", "all": True})
        if pl == "instagram" and c.get("caption"):  # обложка с крупным текстом — видна в сетке профиля
            edits.append({"type": "cover", "text": " ".join(c["caption"].split()[:4]),
                          "t": max(0.0, (peak or 3.0))})
        # длиннее, чем любит площадка, — не беда: ensure_mandatory сделает версию короче (trim)
        ok = d >= lo - 3 and not nude
        plats[pl] = {"post": ok, "why": "по правилам (без ключа Claude)" if ok else "не подходит по длине или рискам",
                     "title": post["title"], "description": post["description"],
                     "hashtags": post["hashtags"], "edits": edits}
    return {"archive": not any(p["post"] for p in plats.values()), "reason": "ни одна площадка не подходит",
            "platforms": plats}


def check(render_path: str, platform: str, plan: dict, strat: dict, key: str | None) -> dict:
    """Проверка готовой версии. С Claude — по кадрам; без него — локально (нагота и мат)."""
    if key:
        return _claude(CHECK_PROMPT.format(platform=platform),
                       "PLAN:\n" + json.dumps(plan, ensure_ascii=False)[:3000] + "\n\nRISK RULES:\n"
                       + json.dumps(strat.get("risk_rules"), ensure_ascii=False)[:3000], _frames(render_path, 5), key)
    from . import policy
    found = policy.check_nudity(render_path, log=lambda m: None)
    return {"ok": not found, "problems": ["в кадре найдено обнажённое тело"] if found else [], "fix_edits":
            [{"type": "blur", "t0": i["t0"], "t1": i["t1"], "box": i["box"]} for i in found]}


# ---------- расписание ----------
def _parse(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def next_slot(platform: str, st: dict, strat: dict, now: datetime | None = None) -> datetime:
    """Ближайшее свободное время для площадки: окно публикаций, пауза между постами, не больше N в день,
    сдвиг между площадками (чтобы не выходить везде одновременно)."""
    ap = strat.get("autopilot") or {}
    now = now or datetime.now()
    slots_et = (ap.get("target_slots_et") or {}).get(platform)
    slots = (ap.get("target_slots_msk") or {}).get(platform)
    if slots_et:  # расписание под США: постоянное время аудитории (ET), по Москве сдвигается само
        return _target_slot(platform, slots_et, st, ap, now, zone="et")
    if slots:  # запасной вариант: слоты по московскому времени
        return _target_slot(platform, slots, st, ap, now)
    win = ap.get("post_window_local") or {"from": 12, "to": 23}
    gap = timedelta(hours=float(ap.get("min_gap_hours", 4)))
    stagger = timedelta(minutes=float(ap.get("platform_stagger_minutes", 20)))
    per_day = int((ap.get("posts_per_day") or {}).get(platform, 3))
    taken = []
    for c in st["clips"].values():
        for pl, q in (c.get("queue") or {}).items():
            t = _parse(q.get("when"))
            if t:
                taken.append((pl, t))
    mine = sorted(t for pl, t in taken if pl == platform)
    t = max(now + timedelta(minutes=2), (mine[-1] + gap) if mine else now)
    for _ in range(2000):
        if t.hour < int(win["from"]):
            t = t.replace(hour=int(win["from"]), minute=0, second=0, microsecond=0)
        if t.hour >= int(win["to"]):
            t = (t + timedelta(days=1)).replace(hour=int(win["from"]), minute=0, second=0, microsecond=0)
            continue
        same_day = [x for x in mine if x.date() == t.date()]
        if len(same_day) >= per_day:
            t = (t + timedelta(days=1)).replace(hour=int(win["from"]), minute=0, second=0, microsecond=0)
            continue
        if any(abs((t - x).total_seconds()) < gap.total_seconds() for x in mine):
            t += timedelta(minutes=15)
            continue
        if any(pl != platform and abs((t - x).total_seconds()) < stagger.total_seconds() for pl, x in taken):
            t += timedelta(minutes=5)
            continue
        return t.replace(second=0, microsecond=0)
    return t


def _target_slot(platform: str, slots: list, st: dict, ap: dict, now: datetime, zone: str = "msk") -> datetime:
    """Первый свободный слот площадки. Если публикацию планируют в приложении (schedule_in_app), слот должен быть
    позже следующей дневной отправки пачки в Telegram (+30 мин) — иначе его не успеют запланировать."""
    from . import schedule
    per_day = int((ap.get("posts_per_day") or {}).get(platform, len(slots)))
    slots = list(slots)[:max(1, per_day)]
    earliest = now + timedelta(minutes=2)
    if ap.get("schedule_in_app") and ap.get("telegram_delivery_msk"):
        _, nxt = schedule.deliveries(ap["telegram_delivery_msk"], now)
        if nxt:
            earliest = max(earliest, nxt + timedelta(minutes=30))
    mine = set()
    for c in st["clips"].values():
        q = (c.get("queue") or {}).get(platform)
        t = _parse((q or {}).get("when"))
        if t and (q or {}).get("status") not in ("skipped", "error"):
            mine.add(t.replace(second=0, microsecond=0))
    inst = schedule.slot_instances_et(slots, now, days=30) if zone == "et" else schedule.slot_instances(slots, now, days=30)
    for t in inst:
        if t >= earliest and t.replace(second=0, microsecond=0) not in mine:
            return t.replace(second=0, microsecond=0)
    return earliest.replace(second=0, microsecond=0)


# ---------- один проход ----------
def run_step(key: str | None, paused: bool, say, event, budget: int = MAX_REVIEWS_PER_RUN) -> dict:
    """Один проход автопилота. say(текст) — что делаю сейчас; event(значок, текст, путь|None, вид) — в ленту."""
    strategy.refresh(log=lambda m: None)
    from .caption import claude_allowed
    if not claude_allowed():  # стратегия: бесплатный режим, Claude не трогаем даже при наличии ключа
        key = None
    strat = strategy.get()
    ap = strat.get("autopilot") or {}
    st = load_state()
    stats = {"published": 0, "reviewed": 0, "archived": 0, "queued": 0}
    dates = library.list_dates()
    clips = [c for d in dates for c in library.list_clips(d)]
    pool = [c for d in dates for c in library.list_clips(d, include_missing=True)]
    scores = library.frozen_ratings(pool) if pool else {}
    from . import policy
    pres = policy.load_results()
    for c in clips:
        c["score10"] = scores.get(c["path"], 5)
        c["policy"] = pres.get(os.path.normpath(c["path"])) or {}
        c["_score"] = score(c, strat)
    by_path = {c["path"]: c for c in clips}

    # 0) уже выложенное с серьёзным нарушением — снять: YouTube сами (приватно), TikTok/Instagram — сказать, что удалить вручную
    unpublish_flagged(st, event)

    # 1) публикация того, чему пора (в режиме «через Telegram» выкладку ведёт tg_assist — бот присылает пост в слот)
    from . import tg_assist
    if not paused and ap.get("auto_publish", True) and tg_assist.mode() != "telegram_assist":
        stats["published"] += _publish_due(st, by_path, strat, say, event)

    # 2) отбор
    fresh = [c for c in clips if c["path"] not in st["clips"] and not any(c["posted"].values())]
    up_upload = os.path.normpath(library.upload_dir())
    fresh = [c for c in fresh if not os.path.normpath(c["path"]).startswith(up_upload)]
    if ap.get("auto_delete", True):
        dups = duplicates(fresh)
        for c in list(fresh):
            reason = None
            if c["path"] in dups:
                reason = f"дубликат клипа {os.path.basename(dups[c['path']])[:-4]}"
            elif _dur(c) < 5:
                reason = "короче 5 секунд"
            elif c["_score"] < float(ap.get("archive_below_score", 20)):
                reason = f"оценка {c['_score']:.0f} ниже порога {ap.get('archive_below_score', 20)}"
            elif _days_old(c) > 7:
                reason = "старше 7 дней и не попал в отбор"
            if reason:
                _to_archive(c, reason, st, event)
                fresh.remove(c)
                stats["archived"] += 1
    cands = sorted([c for c in fresh if c["_score"] >= float(ap.get("min_score_to_post", 55))],
                   key=lambda c: -c["_score"])
    for c in cands[:budget]:
        try:
            _process_clip(c, st, strat, key, say, event, stats)
        except Exception as e:
            st["clips"][c["path"]] = {"stage": "failed", "error": str(e)[:300], "time": time.time()}
            event("❌", f"{c.get('channel', '')}: автопилот не справился с клипом — {e}"[:240], None, "error")
            journal({"clip": exchange.clip_id(c["path"]), "action": "error", "why": str(e)[:300]})
        save_state(st)
    save_state(st)
    return stats


def unpublish_flagged(st: dict, event) -> None:
    from . import policy, publisher
    warned = st.setdefault("unpublish_warned", [])
    yt_ok = publisher.connected().get("youtube")
    for f in policy.flagged_posted():
        c, pl = f["clip"], f["platform"]
        key = f"{c['path']}|{pl}"
        name = f"{c.get('channel', '')} {os.path.basename(c['path'])[:-4]}"
        if pl == "youtube" and f["id"] and yt_ok:
            try:
                publisher.youtube_set_privacy(f["id"], "private")
                library.set_posted(c["path"], False, pl)
                event("⛔", f"{name}: снял с YouTube (сделал приватным) — {f['reason']}", c["path"], "warn")
                journal({"clip": exchange.clip_id(c["path"]), "action": "unpublish", "platform": pl, "why": f["reason"],
                         "how": "private"})
                continue
            except Exception as e:
                event("❌", f"{name}: не смог снять с YouTube — {e}"[:220], None, "error")
        if key not in warned:
            warned.append(key)
            how = {"instagram": "удаление через API Instagram недоступно — заархивируй вручную в приложении",
                   "tiktok": "удаления через API TikTok нет — удали вручную в приложении"}.get(
                pl, "удали или сделай приватным в YouTube Studio")
            event("⛔", f"{name}: выложен в {pl}, но в нём нарушение ({f['reason']}) — {how}. Список: «Клипы → Ещё → "
                       f"⛔ Снять с публикации»", c["path"], "error")
            journal({"clip": exchange.clip_id(c["path"]), "action": "unpublish_manual", "platform": pl, "why": f["reason"],
                     "how": how})


def _to_archive(c: dict, reason: str, st: dict, event):
    rec = archive.archive_clip(c, reason, round(c.get("_score") or 0))
    st["clips"][c["path"]] = {"stage": "archived", "reason": reason, "time": time.time()}
    event("🗄", f"{c.get('channel', '')} {os.path.basename(c['path'])[:-4]}: в архив — {reason} "
               f"(освобождено {max(0, rec.get('freed', 0)) / 1e6:.0f} МБ)", None, "info")
    journal({"clip": exchange.clip_id(c["path"]), "action": "archive", "why": reason})


def _process_clip(c: dict, st: dict, strat: dict, key: str | None, say, event, stats: dict):
    from . import edits
    name = c.get("channel", "")
    say(f"🔍 {name}: смотрю клип и решаю, куда и как выкладывать...")
    plan = review(c, strat, key)
    stats["reviewed"] += 1
    rec = {"stage": "reviewed", "plan": plan, "score": round(c["_score"]), "time": time.time(), "queue": {},
           "renders": {}}
    st["clips"][c["path"]] = rec
    if plan.get("archive") or not any((p or {}).get("post") for p in (plan.get("platforms") or {}).values()):
        st["clips"].pop(c["path"], None)
        _to_archive(c, plan.get("reason") or "автопилот: ни одна площадка не подходит", st, event)
        stats["archived"] += 1
        return
    out_dir = os.path.join(paths.default_work_dir(), "autopilot", "renders")
    os.makedirs(out_dir, exist_ok=True)
    for pl, p in (plan.get("platforms") or {}).items():
        if pl not in PLATFORMS or not (p or {}).get("post"):
            continue
        ops = ensure_mandatory(merge_edits([], p.get("edits") or []), c, strat, pl, _dur(c))
        out = os.path.join(out_dir, f"{int(time.time())}_{pl}_{os.path.basename(c['path'])}")
        ok, problems = False, []
        for attempt in range(3):  # первая сборка + не больше 2 переделок
            say(f"✂ {name}: монтаж для {pl}" + (f" (переделка {attempt})" if attempt else "") + "...")
            res = edits.build_variant(c, ops, out, log=lambda m: None, platform=pl)
            say(f"👁 {name}: проверяю готовую версию для {pl}...")
            chk = check(out, pl, p, strat, key)
            if chk.get("ok"):
                ok = True
                break
            problems = chk.get("problems") or ["не прошла проверку"]
            ops = merge_edits(ops, chk.get("fix_edits") or [])
        if not ok:
            event("⚠", f"{name}: версия для {pl} не прошла проверку — {'; '.join(problems)[:150]}", None, "warn")
            journal({"clip": exchange.clip_id(c["path"]), "action": "reject", "platform": pl, "why": "; ".join(problems)})
            continue
        texts = clean_text(pl, p.get("title") or c.get("caption") or "", p.get("description") or "",
                           p.get("hashtags") or [], c, strat)
        when = next_slot(pl, st, strat)
        rec["renders"][pl] = {"path": out, "applied": [a["type"] for a in res.get("applied", [])],
                              "skipped": res.get("skipped", [])}
        rec["queue"][pl] = {"when": when.isoformat(timespec="minutes"), "status": "waiting", "file": out, **texts,
                            "why": p.get("why", "")}
        stats["queued"] += 1
        event("🗓", f"{name}: {pl} — в очередь на {when.strftime('%d.%m %H:%M')} «{texts['title'][:50]}»", out, "clip")
        journal({"clip": exchange.clip_id(c["path"]), "action": "queue", "platform": pl, "when": rec["queue"][pl]["when"],
                 "why": p.get("why", ""), "edits": rec["renders"][pl]["applied"]})
    rec["stage"] = "queued" if rec["queue"] else "rejected"
    if not rec["queue"]:
        st["clips"].pop(c["path"], None)
        _to_archive(c, "ни одна версия не прошла проверку", st, event)
        stats["archived"] += 1
    else:  # видно в колонке «Совет» и в плане «Выложить → По плану»
        exchange.set_decision(c["path"], {pl: {"post": True, "when": q["when"], "title": q["title"],
                                               "description": q["description"], "hashtags": q["hashtags"]}
                                          for pl, q in rec["queue"].items()}, source="autopilot")


def _publish_due(st: dict, by_path: dict, strat: dict, say, event) -> int:
    from . import publisher
    now = datetime.now()
    conn = publisher.connected()
    n = 0
    for path, rec in st["clips"].items():
        for pl, q in (rec.get("queue") or {}).items():
            when = _parse(q.get("when"))
            if q.get("status") != "waiting" or not when or when > now:
                continue
            c = by_path.get(path)
            if c is None or c["posted"].get(pl):
                q["status"] = "skipped"
                continue
            from . import policy
            block = policy.publish_block(path, (rec.get("renders") or {}).get(pl, {}).get("applied"))
            if block:  # жёсткое правило — никакой выкладки с неисправленным серьёзным нарушением
                q["status"] = "blocked"
                event("⛔", f"{c.get('channel', '')}: {pl} — не публикую: {block}", path, "error")
                journal({"clip": exchange.clip_id(path), "action": "blocked", "platform": pl, "why": block})
                continue
            if not conn.get(pl):
                if not q.get("warned"):
                    q["warned"] = True
                    event("📤", f"{c.get('channel', '')}: пора публиковать в {pl}, но площадка не подключена "
                               f"(Настройки → Автопубликация)", None, "warn")
                continue
            say(f"📤 {c.get('channel', '')}: публикую в {pl}...")
            try:
                res = publisher.publish(pl, q["file"], q.get("title", ""), q.get("description", "") +
                                        ("\n\n" + " ".join(q.get("hashtags") or []) if q.get("hashtags") else ""),
                                        q.get("hashtags") or [], log=lambda m: None)
            except Exception as e:
                q["errors"] = q.get("errors", 0) + 1
                q["when"] = (now + timedelta(minutes=30)).isoformat(timespec="minutes")
                if q["errors"] >= 3:
                    q["status"] = "error"
                event("❌", f"{c.get('channel', '')}: не опубликовалось в {pl} — {e}"[:240], None, "error")
                journal({"clip": exchange.clip_id(path), "action": "publish_error", "platform": pl, "why": str(e)[:300]})
                continue
            q["status"] = "published"
            q["result"] = res
            library.set_posted(path, True, pl)
            library.record_published(path, pl, q.get("title", ""), q.get("description", ""), res.get("id", ""),
                                     res.get("url", ""))
            n += 1
            what = "черновик TikTok — открой его в телефоне и нажми «Опубликовать»" if res.get("draft") else (res.get("url") or "")
            event("✅", f"{c.get('channel', '')}: опубликовано в {pl} — {what} {res.get('note', '')}".strip(), path, "clip")
            journal({"clip": exchange.clip_id(path), "action": "publish", "platform": pl, "url": res.get("url", ""),
                     "draft": bool(res.get("draft")), "note": res.get("note", "")})
    save_state(st)
    return n


def queue_overview() -> list[dict]:
    """Очередь автопилота для окна: что, куда и когда."""
    out = []
    for path, rec in load_state()["clips"].items():
        for pl, q in (rec.get("queue") or {}).items():
            out.append({"path": path, "platform": pl, **{k: q.get(k) for k in ("when", "status", "title", "why")}})
    return sorted(out, key=lambda x: x.get("when") or "")
