"""Подпись к клипу («Спид первый попробовал GTA 6») и язык стримера."""
from __future__ import annotations

import os
import re

from . import paths

_CYR = re.compile(r"[а-яёА-ЯЁ]")
_LAT = re.compile(r"[a-zA-Z]")

SYSTEM_PROMPT = """You write the on-screen caption for a short vertical video (YouTube Shorts / TikTok) cut from a Twitch or YouTube livestream.

The caption sits in a white box over the video and is the hook that makes people stop scrolling. Write ONE caption:
- 4 to 9 words, at most 60 characters, no hashtags, no quotes around it, at most one emoji;
- name the streamer the way fans call them (a short nickname is fine) and say what happens in this moment, e.g. "Спид первый попробовал сыграть в GTA 6", "xQc lost his mind over the GTA 6 map";
- base it only on the information given: the chat reaction and the transcript show what happened; do not invent events;
- if the details are unclear, describe the reaction instead ("Эвелон не ожидал такого от GTA 6");
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

TEMPLATES = {
    "ru": {
        "laugh": ["{s} рассмешил весь чат{g}", "Чат умер со смеху с {s}{g}", "{s} выдал лучший момент стрима{g}",
                  "Этот момент {s} чат пересматривал 10 раз", "{s} не смог сдержаться{g}", "Чат плачет от смеха{g}"],
        "shock": ["{s} в шоке{g}", "{s} не поверил своим глазам{g}", "Такого {s} точно не ожидал{g}",
                  "Чат в шоке от того, что сделал {s}", "{s}: «ЧТО ЭТО БЫЛО?!»", "Никто не ожидал такого{g}"],
        "hype": ["{s} сделал невозможное{g}", "{s} показал класс{g}", "Самый эпичный момент {s}{g}",
                 "{s} затащил{g}", "Чат взорвался после этого момента{g}"],
        "fail": ["{s} опозорился на весь стрим{g}", "Самый неловкий момент {s}{g}", "{s}, что ты делаешь?!",
                 "Так {s} ещё не ошибался{g}", "Чат не простит {s} этот момент"],
        "clip": ["Чат требовал клипнуть этот момент {s}", "Момент, который все клипнули{g}",
                 "{s} — момент для клипа{g}"],
        "general": ["{s}: момент, который надо видеть{g}", "Лучший момент стрима {s}{g}", "{s} и его реакция{g}",
                    "Вот за это смотрят {s}", "Момент стрима {s}, который обсуждает чат"],
        "quote": ["Чат в один голос: «{q}»", "«{q}» — реакция чата на {s}", "{s}, а чат пишет «{q}»"],
    },
    "en": {
        "laugh": ["{s} had chat crying{g}", "{s} can't stop laughing{g}", "Chat lost it at {s}{g}",
                  "{s}'s funniest moment yet{g}", "This {s} moment broke chat"],
        "shock": ["{s} can't believe this{g}", "{s} was NOT ready for this{g}", "Nobody expected this from {s}",
                  "{s}'s reaction says it all{g}", "Wait... what just happened?!"],
        "hype": ["{s} just did the impossible{g}", "{s} went crazy{g}", "{s}'s cleanest play{g}",
                 "Chat went wild for {s}{g}"],
        "fail": ["{s}'s biggest fail{g}", "{s} will never live this down", "This is so embarrassing for {s}",
                 "{s} really thought this would work"],
        "clip": ["Chat begged to clip this {s} moment", "The moment everyone clipped{g}"],
        "general": ["{s}'s craziest moment{g}", "You have to see this {s} moment", "{s} in a nutshell{g}",
                    "Peak {s} content{g}"],
        "quote": ['Chat spammed "{q}" after this', '"{q}" — chat after this {s} moment'],
    },
}


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


def template_caption(streamer: str, title: str, top_messages: list[str], lang: str) -> str:
    import random
    lang = "ru" if lang == "ru" else "en"
    gta = "gta" in title.lower() or "гта" in title.lower() or "gta" in " ".join(top_messages).lower()
    g = (" в GTA 6" if lang == "ru" else " in GTA 6") if gta else ""
    s = _nice_name(streamer)
    cat = _category(top_messages)
    pool = list(TEMPLATES[lang][cat])
    q = _quote(top_messages) if cat != "general" else None  # цитируем чат, только если это реакция
    if q:
        pool.append(random.choice(TEMPLATES[lang]["quote"]))
    used = set(recent_captions(streamer))
    options = [t.format(s=s, g=g, q=q or "") for t in pool]
    fresh = [o for o in options if o not in used] or options
    return random.choice(fresh)


def make_caption(streamer: str, title: str, top_messages: list[str], transcript: str, lang: str,
                 log=print) -> str:
    key = _api_key()
    text = None
    if key:
        try:
            text = _claude_caption(key, streamer, title, top_messages, transcript, lang)
        except Exception as e:
            log(f"    подпись от Claude не получилась ({e}) — ставлю шаблонную")
    if not text:
        text = template_caption(streamer, title, top_messages, lang)
    try:
        remember_caption(streamer, text)
    except Exception:
        pass
    return text


def _claude_caption(key: str, streamer: str, title: str, top_messages: list[str], transcript: str,
                    lang: str) -> str:
    import anthropic

    language = "Russian" if lang == "ru" else "English (American)"
    user = (f"Language: {language}\n"
            f"Streamer: {streamer}\n"
            f"Stream title: {title}\n"
            f"Most repeated chat messages at this moment: {' | '.join(top_messages[:8]) or '(none)'}\n"
            f"What the streamer says in the clip (auto transcript, may be empty or rough):\n"
            f"{transcript[:1500] or '(no transcript)'}\n"
            f"Captions already used for this streamer — do not repeat them, vary the wording and angle:\n"
            + ("\n".join(f"- {c}" for c in recent_captions(streamer)[-15:]) or "(none yet)"))
    client = anthropic.Anthropic(api_key=key, max_retries=3)
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("модель отказалась")
    text = next((b.text for b in response.content if b.type == "text"), "").strip()
    text = text.strip('"«»“” \n').splitlines()[0] if text else ""
    if not text:
        raise RuntimeError("пустой ответ")
    return text[:90]
