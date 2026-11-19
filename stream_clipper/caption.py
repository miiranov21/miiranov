"""Подпись к клипу («Спид первый попробовал GTA 6») и язык стримера."""
from __future__ import annotations

import os
import re

from . import paths

_CYR = re.compile(r"[а-яёА-ЯЁ]")
_LAT = re.compile(r"[a-zA-Z]")

SYSTEM_PROMPT = """You write the on-screen caption for a short vertical video (YouTube Shorts / TikTok) cut from a Twitch or YouTube livestream.

The caption sits in a white box over the video and is the hook that makes people stop scrolling. Write ONE caption:
- 4 to 9 words, at most 60 characters, no hashtags, at most one emoji;
- it is about THE STREAMER: what they do, say or how they react in this exact moment, e.g. "Спид впервые угнал самолёт в GTA 6", "xQc crashed in the first 5 minutes of GTA 6", "Эвелон не поверил своим глазам";
- never mention the chat, viewers, comments or "W"/"L" spam — people watching the Short do not see the chat; the chat reaction is only a hint about the kind of moment (funny, shocking, epic, fail);
- rely first on the frames (what happens on screen) and on what the streamer says (transcript); a short punchy quote of the streamer is great if it fits;
- do not invent events that the frames or transcript do not show; if unsure, describe the streamer's reaction;
- name the streamer the way fans call them (a short nickname is fine);
- write in the language you are told to use.

Reply in exactly this format:
CAPTION: <the caption>
SCORE: <1-10, how likely this clip goes viral as a Short: 9-10 = something wild clearly happens on screen or the streamer reacts huge; 5-6 = decent but ordinary; 1-3 = the streamer just talks and nothing really happens>"""


def detect_language(texts: list[str], title: str = "") -> str:
    """'ru', если чат/название в основном на кириллице, иначе 'en'."""
    sample = " ".join(texts[:3000]) + " " + title * 20
    cyr = len(_CYR.findall(sample))
    lat = len(_LAT.findall(sample))
    return "ru" if cyr > 0.35 * (cyr + lat) and cyr > 20 else "en"


def _api_key() -> str | None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    p = os.path.join(paths.program_dir(), "claude_key.txt")
    if os.path.exists(p):
        key = open(p, encoding="utf-8-sig").read().strip()
        return key or None
    return None


_LAUGH = ("kek", "lul", "lol", "lmao", "ахах", "хаха", "ору", "icant", "xd", "кек", "омегалул", "😂", "🤣")
_SHOCK = ("wtf", "omg", "???", "жесть", "что", "чего", "what", "noway", "капец", "офигеть", "ого", "нифига", "😱")
_HYPE = ("pog", "gg", "ez", "имба", "sheesh", "w ", "красава", "топ", "легенда", "🔥", "clean", "go")
_FAIL = ("f", "rip", "кринж", "l ", "лох", "позор", "упал", "fail", "😭", "💀", "ну ты")
_CLIP = ("clip", "клип")

# надписи — про стримера, а не про чат (чат только подсказывает, какой это момент)
TEMPLATES = {
    "ru": {
        "laugh": ["{s} не смог сдержать смех{g}", "{s} выдал лучший момент стрима{g}", "{s} угарает{g}",
                  "{s} и самый смешной момент дня{g}", "{s} просто лёг от смеха{g}", "{s} такого не ожидал{g}"],
        "shock": ["{s} в шоке{g}", "{s} не поверил своим глазам{g}", "Такого {s} точно не ожидал{g}",
                  "{s}: «ЧТО ЭТО БЫЛО?!»", "{s} потерял дар речи{g}", "Реакция {s} говорит сама за себя"],
        "hype": ["{s} сделал невозможное{g}", "{s} показал класс{g}", "Самый эпичный момент {s}{g}",
                 "{s} затащил{g}", "{s} на максималках{g}"],
        "fail": ["{s} опозорился{g}", "Самый неловкий момент {s}{g}", "{s}, что ты делаешь?!",
                 "Так {s} ещё не ошибался{g}", "{s} пожалел об этом через секунду"],
        "clip": ["{s} — момент, который надо видеть{g}", "{s} и этот момент{g}"],
        "general": ["{s}: момент, который надо видеть{g}", "Лучший момент стрима {s}{g}", "{s} и его реакция{g}",
                    "Вот за это смотрят {s}", "{s} в своём репертуаре{g}"],
    },
    "en": {
        "laugh": ["{s} couldn't stop laughing{g}", "{s}'s funniest moment yet{g}", "{s} can't believe it{g}",
                  "{s} was crying laughing{g}"],
        "shock": ["{s} can't believe this{g}", "{s} was NOT ready for this{g}", "{s}'s reaction says it all{g}",
                  "{s} was speechless{g}"],
        "hype": ["{s} just did the impossible{g}", "{s} went crazy{g}", "{s}'s cleanest play{g}", "Peak {s}{g}"],
        "fail": ["{s}'s biggest fail{g}", "{s} will never live this down", "{s} really thought this would work",
                 "{s} regretted this instantly"],
        "clip": ["You have to see this {s} moment", "{s}'s moment of the day{g}"],
        "general": ["{s}'s craziest moment{g}", "You have to see this {s} moment", "{s} in a nutshell{g}",
                    "Peak {s} content{g}"],
    },
}


def streamer_quote(words: list, center: float, window: float = 5.0) -> str | None:
    """Короткая фраза стримера из самого момента клипа (по субтитрам): 3–8 слов возле пика."""
    near = [w for w in words if center - window <= w[0] <= center + window]
    if len(near) < 3:
        return None
    # берём цельную фразу вокруг слова, ближайшего к пику: тянем влево/вправо, пока нет паузы > 0.7 с
    best = min(range(len(near)), key=lambda i: abs(near[i][0] - center))
    a = b = best
    while a > 0 and near[a][0] - near[a - 1][1] < 0.7 and b - a < 7:
        a -= 1
    while b + 1 < len(near) and near[b + 1][0] - near[b][1] < 0.7 and b - a < 7:
        b += 1
    phrase = " ".join(w[2].strip() for w in near[a:b + 1]).strip(" ,.-")
    if not (3 <= len(phrase.split()) <= 9) or len(phrase) > 48:
        return None
    return phrase


def _nice_name(login: str) -> str:
    import re
    name = re.sub(r"\d{3,}$", "", login or "").strip("_") or login or "стример"
    return name[:1].upper() + name[1:]


def _category(top_messages: list[str]) -> str:
    for msg in top_messages[:2]:  # главная реакция чата: самые частые сообщения решают
        m = f" {msg.lower()} "
        for cat, words in (("shock", _SHOCK), ("laugh", _LAUGH), ("fail", _FAIL), ("hype", _HYPE), ("clip", _CLIP)):
            if any(w in m for w in words):
                return cat
    return "general"


def _quote(top_messages: list[str]) -> str | None:
    import re
    for msg in top_messages[:2]:
        q = re.sub(r"@\S+", "", msg).strip(" .,!")
        if 2 <= len(q) <= 24 and "http" not in q and not q.isdigit():
            return q.upper() if len(q) <= 8 else q
    return None


def _used_path() -> str:
    return os.path.join(paths.default_work_dir(), "captions_used.json")


def recent_captions(streamer: str) -> list[str]:
    try:
        import json
        with open(_used_path(), encoding="utf-8") as f:
            return json.load(f).get(streamer.lower(), [])
    except Exception:
        return []


def remember_caption(streamer: str, text: str) -> None:
    import json
    try:
        with open(_used_path(), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    lst = data.get(streamer.lower(), [])
    lst.append(text)
    data[streamer.lower()] = lst[-40:]
    os.makedirs(os.path.dirname(_used_path()), exist_ok=True)
    with open(_used_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


# ---------- банк хуков «Доктора» (strategy.json → hook_bank) и история выданных надписей ----------
def hook_bank() -> dict:
    try:
        from . import strategy
        hb = strategy.get().get("hook_bank") or {}
        return hb if isinstance(hb, dict) else {}
    except Exception:
        return {}


def short_nick(streamer: str, bank: dict | None = None) -> str:
    """Короткий ник, как зовут фанаты (hook_bank.nicknames), иначе — красиво оформленный логин."""
    bank = hook_bank() if bank is None else bank
    nicks = {k.lower(): v for k, v in (bank.get("nicknames") or {}).items()}
    return nicks.get((streamer or "").lower()) or _nice_name(streamer)


def _history_path() -> str:
    return os.path.join(paths.default_work_dir(), "captions_history.json")


def caption_history() -> list[dict]:
    """Все выданные надписи по порядку (общие для всех стримеров): [{"text", "tpl"}]."""
    try:
        import json
        with open(_history_path(), encoding="utf-8") as f:
            data = json.load(f)
        return [h for h in data if isinstance(h, dict)] if isinstance(data, list) else []
    except Exception:
        return []


def _remember_history(text: str, tpl: str) -> None:
    import json
    hist = caption_history()
    hist.append({"text": text, "tpl": tpl})
    os.makedirs(os.path.dirname(_history_path()), exist_ok=True)
    tmp = _history_path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(hist[-100:], f, ensure_ascii=False, indent=0)
    os.replace(tmp, _history_path())


TEXT_GAP, TPL_GAP = 20, 5  # одна надпись — не чаще раза в 20 клипов, один шаблон — не чаще раза в 5
LAST_TPL: dict = {"value": ""}  # шаблон, по которому сделана последняя надпись (для истории)


def _norm(t: str) -> str:
    return re.sub(r"\W+", " ", (t or "").lower()).strip()


def _bank_category(cat: str, bank_lang: dict) -> list[str]:
    """Тип момента из реакции чата → список хуков банка (для «просто момента» — смесь подходящих типов)."""
    if bank_lang.get(cat):
        return list(bank_lang[cat])
    mix = []
    for c in ("shock", "laugh", "hype"):
        mix += list(bank_lang.get(c) or [])
    return mix


def _pick_fresh(cands: list[tuple[str, str]], spare: list[tuple[str, str]] = ()) -> tuple[str, str] | None:
    """cands: [(готовая надпись, шаблон)] → случайная, которой не было в последних 20 и шаблона — в последних 5.
    Если в своём типе момента свежих не осталось — берём свежую из запасных (соседние типы), и только потом повтор."""
    import random
    hist = caption_history()
    recent_text = {_norm(h.get("text", "")) for h in hist[-TEXT_GAP:]}
    recent_tpl = {h.get("tpl", "") for h in hist[-TPL_GAP:]}

    def fresh(lst):
        return [c for c in lst if _norm(c[0]) not in recent_text and c[1] not in recent_tpl]
    tiers = (fresh(cands), fresh(spare),
             [c for c in cands if _norm(c[0]) not in recent_text],
             [c for c in spare if _norm(c[0]) not in recent_text],
             cands)
    for tier in tiers:
        if tier:
            return random.choice(tier)
    return None


def template_caption(streamer: str, title: str, top_messages: list[str], lang: str,
                     quote: str | None = None) -> str:
    """Надпись без Claude: 1) цензурная цитата стримера 2–6 слов, 2) банк хуков «Доктора», 3) старые шаблоны."""
    lang = "ru" if lang == "ru" else "en"
    bank = hook_bank()
    s = short_nick(streamer, bank)
    cat = _category(top_messages)  # чат подсказывает только тип момента
    hist = [_norm(h.get("text", "")) for h in caption_history()[-TEXT_GAP:]] + \
        [_norm(t) for t in recent_captions(streamer)[-TEXT_GAP:]]
    if quote and 2 <= len(quote.split()) <= 6:  # цитата самого стримера — самое живое
        q = quote.strip(" .,!?").upper()
        q = f"{s}: «{q}»" if lang == "ru" else f'{s}: "{q}"'
        if _norm(q) not in hist and _norm(quote) not in " ".join(hist):
            LAST_TPL["value"] = "quote"
            return q
    hooks = _bank_category(cat, bank.get(lang) or {})
    if hooks:  # хуки банка — заглавными, без «в GTA 6»: игра и так видна
        def fmt(lst):
            out = []
            for t in lst:
                try:
                    out.append((t.format(s=s).upper(), "bank:" + t))
                except (KeyError, IndexError, ValueError):
                    pass
            return out
        bl = bank.get(lang) or {}
        near = [t for c in ("shock", "laugh", "hype") if c != cat for t in (bl.get(c) or []) if t not in hooks]
        got = _pick_fresh(fmt(hooks), fmt(near))
        if got:
            LAST_TPL["value"] = got[1]
            return got[0]
    # запасной вариант — стратегия не скачалась: старые шаблоны, «в GTA 6» не чаще раза в 5 надписей
    gta = "gta" in title.lower() or "гта" in title.lower() or "gta" in " ".join(top_messages).lower()
    gta_recent = any("gta" in h for h in hist[-TPL_GAP + 1:])
    g = (" в GTA 6" if lang == "ru" else " in GTA 6") if gta and not gta_recent else ""
    got = _pick_fresh([(t.format(s=s, g=g), "tpl:" + t) for t in TEMPLATES[lang][cat]])
    LAST_TPL["value"] = got[1]
    return got[0]


LAST_SCORE: dict = {"value": None}  # оценка Claude для последней надписи (1–10)


def make_caption(streamer: str, title: str, top_messages: list[str], transcript: str, lang: str,
                 log=print, frames: list[str] | None = None, quote: str | None = None) -> str:
    key = _api_key()
    text = None
    LAST_SCORE["value"] = None
    LAST_TPL["value"] = ""
    if key:
        try:
            text = _claude_caption(key, streamer, title, top_messages, transcript, lang, frames or [])
        except Exception as e:
            log(f"    подпись от Claude не получилась ({e}) — ставлю шаблонную")
    from .policy import censor_text, word_kind
    if quote and any(word_kind(w) for w in quote.split()):
        quote = None  # цитата с матом в надписи на экране — нельзя
    if not text:
        text = template_caption(streamer, title, top_messages, lang, quote)
    text = censor_text(text)
    try:
        remember_caption(streamer, text)
        _remember_history(text, LAST_TPL["value"] or "claude:" + _norm(text))
    except Exception:
        pass
    return text


def _system_prompt(streamer: str, lang: str) -> str:
    """SYSTEM_PROMPT + правила и 5 случайных примеров из банка хуков «Доктора» (если стратегия скачана)."""
    import random
    bank = hook_bank()
    rules = [r for r in bank.get("rules") or [] if isinstance(r, str)]
    pool = [h for v in (bank.get("ru" if lang == "ru" else "en") or {}).values() if isinstance(v, list) for h in v]
    if not rules and not pool:
        return SYSTEM_PROMPT
    nick = short_nick(streamer, bank)
    extra = "\n\nHouse style for captions (from our strategy, follow it):"
    if rules:
        extra += "\n" + "\n".join(f"- {r}" for r in rules)
    extra += f"\n- call the streamer {nick}; do not add the game name to every caption — the game is visible anyway."
    if pool:
        ex = random.sample(pool, min(5, len(pool)))
        extra += ("\nStyle examples (ALL CAPS, short; write in this style, but your own words for this exact moment):\n"
                  + "\n".join(f"- {e.replace('{s}', nick)}" for e in ex))
    return SYSTEM_PROMPT + extra


def _claude_caption(key: str, streamer: str, title: str, top_messages: list[str], transcript: str,
                    lang: str, frames: list[str] | None = None) -> str:
    import base64
    import anthropic

    language = "Russian" if lang == "ru" else "English (American)"
    text = (f"Language: {language}\n"
            f"Streamer: {streamer}\n"
            f"Stream title: {title}\n"
            f"Kind of moment (hint from chat, do not mention chat): {_category(top_messages)}\n"
            f"What the streamer says in the clip (auto transcript, may be empty or rough):\n"
            f"{transcript[:1500] or '(no transcript)'}\n"
            f"Captions already used for this streamer — do not repeat them, vary the wording and angle:\n"
            + ("\n".join(f"- {c}" for c in recent_captions(streamer)[-15:]) or "(none yet)")
            + "\nLast 20 captions across all clips — do not repeat any of them or their pattern:\n"
            + ("\n".join(f"- {h.get('text', '')}" for h in caption_history()[-TEXT_GAP:]) or "(none yet)"))
    content: list = []
    for p in (frames or [])[:3]:  # кадры момента — Claude видит, что происходит на экране
        try:
            with open(p, "rb") as f:
                content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                            "data": base64.standard_b64encode(f.read()).decode()}})
        except OSError:
            pass
    if content:
        text = "The images are frames from the moment, in order.\n" + text
    content.append({"type": "text", "text": text})
    client = anthropic.Anthropic(api_key=key, max_retries=3)
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=_system_prompt(streamer, lang),
        messages=[{"role": "user", "content": content}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("модель отказалась")
    out = next((b.text for b in response.content if b.type == "text"), "").strip()
    caption, score = out, None
    if "CAPTION:" in out:
        caption = out.split("CAPTION:", 1)[1].split("SCORE:", 1)[0]
    if "SCORE:" in out:
        try:
            score = float(out.split("SCORE:", 1)[1].strip().split()[0].split("/")[0])
        except (ValueError, IndexError):
            score = None
    caption = caption.strip().strip('"«»“” \n').splitlines()[0] if caption.strip() else ""
    if not caption:
        raise RuntimeError("пустой ответ")
    LAST_SCORE["value"] = score
    return caption[:90]


# ---------- описание и хэштеги для публикации (YouTube Shorts / Instagram Reels / TikTok) ----------
POST_PROMPT = """You write the publishing text for a short vertical clip from a livestream (YouTube Shorts, Instagram Reels, TikTok).
Return exactly two parts in this format:
DESCRIPTION: 1-3 short sentences that hook the viewer and say what the streamer does in the clip; may end with a call to action (subscribe/follow). No chat mentions.
HASHTAGS: 3-5 topical hashtags separated by spaces: the streamer's nickname, the game, what happened in the moment. NO generic reach tags (#fyp #foryou #viral #рек #рекомендации) and NO platform names (#shorts #reels #tiktok); lowercase is fine.
The description must contain the words people search for: the streamer's name and what exactly happened (not vague teasers like "wait what just happened").
Write the description in the language you are told to use (hashtags may mix that language and English)."""


def _game_tags(title: str, lang: str) -> list[str]:
    t = title.lower()
    if "gta" in t or "гта" in t:
        return ["#gta6", "#gta", "#gtavi", "#gta6gameplay"] + (["#гта6", "#гта"] if lang == "ru" else [])
    return ["#gaming", "#gameplay"] + (["#игры"] if lang == "ru" else [])


def template_post(streamer: str, caption: str, title: str, lang: str, link: str = "") -> dict:
    s = _nice_name(streamer)
    tag = "#" + "".join(ch for ch in s.lower() if ch.isalnum())
    if lang == "ru":
        desc = f"{caption or s + ' на стриме'} 🔥 Лучшие моменты со стримов {s} — каждый день. Подписывайся!"
        tags = [tag, "#стрим", "#нарезки"]
    else:
        desc = f"{caption or s + ' on stream'} 🔥 Daily best moments from {s}'s streams. Follow for more!"
        tags = [tag, "#streamer", "#streamclips"]
    tags[1:1] = _game_tags(title, lang)
    seen, uniq = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return {"description": desc, "hashtags": " ".join(uniq[:5])}


def make_post(streamer: str, caption: str, title: str, transcript: str, lang: str, link: str = "",
              log=print) -> dict:
    """Описание и хэштеги: через Claude (если есть ключ), иначе по шаблону."""
    key = _api_key()
    if key:
        try:
            import anthropic
            language = "Russian" if lang == "ru" else "English (American)"
            text = (f"Language: {language}\nStreamer: {streamer}\nStream title: {title}\n"
                    f"On-screen caption of the clip: {caption}\n"
                    f"What the streamer says (auto transcript, may be rough): {transcript[:800] or '(none)'}")
            client = anthropic.Anthropic(api_key=key, max_retries=3)
            response = client.beta.messages.create(
                model="claude-opus-5-5", max_tokens=4000, output_config={"effort": "low"},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                system=POST_PROMPT, messages=[{"role": "user", "content": text}])
            if response.stop_reason != "refusal":
                out = next((b.text for b in response.content if b.type == "text"), "")
                desc = out.split("DESCRIPTION:", 1)[-1].split("HASHTAGS:", 1)[0].strip()
                tags = out.split("HASHTAGS:", 1)[-1].strip() if "HASHTAGS:" in out else ""
                if desc and tags:
                    return {"description": desc, "hashtags": " ".join(tags.split())}
        except Exception as e:
            log(f"описание от Claude не получилось ({e}) — делаю по шаблону")
    return template_post(streamer, caption, title, lang, link)



# ---------- оценка клипа: насколько он яркий (0–10) ----------
def rate_clip(d: dict, transcript: str = "") -> float:
    """«Сырая» яркость момента 0–10 (потом в окне она сравнивается со всеми клипами).
    Чем больше настоящего действия (крик, взрыв, резкий поворот) и реакции — тем выше.
    Штраф за «пустую болтовню» — только если звук и картинка реально измерялись и действия не было."""
    chat = max(0.0, float(d.get("chat_z", 0) or 0))
    audio = max(0.0, float(d.get("audio_z", 0) or 0))
    jump = max(0.0, float(d.get("jump_z", 0) or 0))
    vis = max(0.0, float(d.get("vis_z", 0) or 0))
    score = max(0.0, float(d.get("score", 0) or 0))
    r = (1.0 + 0.15 * min(score, 30) + 0.1 * min(chat, 20) + 0.2 * min(audio, 12)
         + 0.35 * min(jump, 10) + 0.4 * min(vis, 10))
    measured = bool(d.get("has_media"))  # звук/картинка для этого клипа реально анализировались
    words = len((transcript or d.get("transcript", "") or "").split())
    if measured and jump + vis < 1.0:
        r -= 2.0 if words > 55 else 1.0  # стример просто разговаривает / на экране тихо
    return round(max(0.0, min(10.0, r)), 2)


def display_ratings(clips: list[dict]) -> dict:
    """Итоговая оценка 1–10 для показа: сравниваем «сырую» яркость со всеми клипами
    (лучшие получают 8–10, средние ~5, слабые 1–3) и добавляем оценку Claude, если она есть."""
    raws = {c["path"]: rate_clip(c) for c in clips}
    ordered = sorted(raws.values())
    n = len(ordered)
    out = {}
    for path, raw in raws.items():
        if n > 1:
            below = sum(1 for v in ordered if v < raw)
            equal = sum(1 for v in ordered if v == raw)
            pct = (below + (equal - 1) / 2) / (n - 1)
        else:
            pct = 0.5
        r = 1 + 9 * (0.65 * pct + 0.35 * raw / 10)
        c = next(x for x in clips if x["path"] == path)
        ai = c.get("ai_score")
        if isinstance(ai, (int, float)) and 0 < ai <= 10:
            r = (r + float(ai)) / 2
        out[path] = max(1, min(10, round(r)))
    return out
