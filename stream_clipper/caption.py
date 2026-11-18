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


_LAUGH = ("kek", "lul", "lol", "lmao", "ахах", "хаха", "ору", "icant", "xd", "кек")
_SHOCK = ("wtf", "omg", "pog", "???", "жесть", "что", "чего", "what", "noway", "капец", "офигеть")


def template_caption(streamer: str, title: str, top_messages: list[str], lang: str) -> str:
    joined = " ".join(top_messages).lower()
    gta = "gta" in title.lower() or "гта" in title.lower() or "gta" in joined
    game_ru = " в GTA 6" if gta else ""
    game_en = " in GTA 6" if gta else ""
    if any(w in joined for w in _LAUGH):
        return f"{streamer} рассмешил весь чат{game_ru}" if lang == "ru" else f"{streamer} had chat crying{game_en}"
    if any(w in joined for w in _SHOCK):
        return f"{streamer} в шоке{game_ru}" if lang == "ru" else f"{streamer} can't believe this{game_en}"
    return f"{streamer}: момент, который надо видеть" if lang == "ru" else f"{streamer}'s craziest moment{game_en}"


def make_caption(streamer: str, title: str, top_messages: list[str], transcript: str, lang: str,
                 log=print) -> str:
    key = _api_key()
    if key:
        try:
            return _claude_caption(key, streamer, title, top_messages, transcript, lang)
        except Exception as e:
            log(f"    подпись от Claude не получилась ({e}) — ставлю шаблонную")
    return template_caption(streamer, title, top_messages, lang)


def _claude_caption(key: str, streamer: str, title: str, top_messages: list[str], transcript: str,
                    lang: str) -> str:
    import anthropic

    language = "Russian" if lang == "ru" else "English (American)"
    user = (f"Language: {language}\n"
            f"Streamer: {streamer}\n"
            f"Stream title: {title}\n"
            f"Most repeated chat messages at this moment: {' | '.join(top_messages[:8]) or '(none)'}\n"
            f"What the streamer says in the clip (auto transcript, may be empty or rough):\n"
            f"{transcript[:1500] or '(no transcript)'}")
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
