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

Reply with the caption text only."""


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
        "laugh": ["{s} couldn't stop laughing{g}", "{s}'s funniest moment yet{g}", "{s} lost it{g}",
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


def template_caption(streamer: str, title: str, top_messages: list[str], lang: str,
                     quote: str | None = None) -> str:
    import random
    lang = "ru" if lang == "ru" else "en"
    gta = "gta" in title.lower() or "гта" in title.lower() or "gta" in " ".join(top_messages).lower()
    g = (" в GTA 6" if lang == "ru" else " in GTA 6") if gta else ""
    s = _nice_name(streamer)
    cat = _category(top_messages)  # чат подсказывает только тип момента
    options = [t.format(s=s, g=g) for t in TEMPLATES[lang][cat]]
    used = set(recent_captions(streamer))
    if quote:  # цитата самого стримера — самое живое, что можно поставить без Claude
        q = f"{s}: «{quote}»" if lang == "ru" else f'{s}: "{quote}"'
        if q not in used and random.random() < 0.7:
            return q
    fresh = [o for o in options if o not in used] or options
    return random.choice(fresh)


def make_caption(streamer: str, title: str, top_messages: list[str], transcript: str, lang: str,
                 log=print, frames: list[str] | None = None, quote: str | None = None) -> str:
    key = _api_key()
    text = None
    if key:
        try:
            text = _claude_caption(key, streamer, title, top_messages, transcript, lang, frames or [])
        except Exception as e:
            log(f"    подпись от Claude не получилась ({e}) — ставлю шаблонную")
    if not text:
        text = template_caption(streamer, title, top_messages, lang, quote)
    try:
        remember_caption(streamer, text)
    except Exception:
        pass
    return text


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
            + ("\n".join(f"- {c}" for c in recent_captions(streamer)[-15:]) or "(none yet)"))
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
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("модель отказалась")
    out = next((b.text for b in response.content if b.type == "text"), "").strip()
    out = out.strip('"«»“” \n').splitlines()[0] if out else ""
    if not out:
        raise RuntimeError("пустой ответ")
    return out[:90]


# ---------- описание и хэштеги для публикации (YouTube Shorts / Instagram Reels / TikTok) ----------
POST_PROMPT = """You write the publishing text for a short vertical clip from a livestream (YouTube Shorts, Instagram Reels, TikTok).
Return exactly two parts in this format:
DESCRIPTION: 1-3 short sentences that hook the viewer and say what the streamer does in the clip; may end with a call to action (subscribe/follow). No chat mentions.
HASHTAGS: 10-15 hashtags separated by spaces: the streamer (nickname variants), the game, the genre/moment, plus platform tags like #shorts #reels #fyp; mix popular and specific tags; lowercase is fine.
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
        tags = [tag, "#стрим", "#нарезки", "#моментысостримов", "#twitch", "#shorts", "#reels", "#рекомендации"]
    else:
        desc = f"{caption or s + ' on stream'} 🔥 Daily best moments from {s}'s streams. Follow for more!"
        tags = [tag, "#streamer", "#streamclips", "#twitch", "#shorts", "#reels", "#fyp", "#viral"]
    tags[1:1] = _game_tags(title, lang)
    seen, uniq = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return {"description": desc, "hashtags": " ".join(uniq[:15])}


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
