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


def claude_allowed() -> bool:
    """Стратегия может выключить Claude целиком (ai_mode.claude_key = false — пока нет дохода): всё бесплатно."""
    try:
        from . import strategy
        return (strategy.get().get("ai_mode") or {}).get("claude_key", True) is not False
    except Exception:
        return True


def account_lang(default: str | None = None) -> str | None:
    """Язык канала из стратегии (account.language): надписи и тексты — только на нём."""
    try:
        from . import strategy
        lang = ((strategy.get().get("account") or {}).get("language") or "").strip().lower()
        return lang if lang in ("ru", "en") else default
    except Exception:
        return default


def _langs_path() -> str:
    return os.path.join(paths.default_work_dir(), "streamer_langs.json")


def streamer_langs() -> dict:
    """{ник: язык} — какой язык программа увидела у стримера (по чату)."""
    try:
        import json
        with open(_langs_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


LANG_NAMES = {"ru": "русскоязычный", "en": "англоязычный"}
_warned: set = set()


def lang_allowed(channel: str, lang: str, log=print) -> bool:
    """Канал под один язык (account.streamers_language): стримера на другом языке не режем и предупреждаем."""
    import json
    key = (channel or "").lower().lstrip("@")
    data = streamer_langs()
    if key and data.get(key) != lang:
        data[key] = lang
        try:
            os.makedirs(os.path.dirname(_langs_path()), exist_ok=True)
            with open(_langs_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
        except OSError:
            pass
    try:
        from . import strategy
        acc = strategy.get().get("account") or {}
        need = (acc.get("streamers_language") or acc.get("language") or "").strip().lower()
    except Exception:
        need = ""
    if not need or lang == need:
        return True
    if key not in _warned:
        _warned.add(key)
        log(f"🌐 {channel}: стример {LANG_NAMES.get(lang, lang)}, а канал {LANG_NAMES.get(need, need)} — "
            f"для этого стримера нужен отдельный канал. Не нарезаю.")
    return False


def _api_key() -> str | None:
    if not claude_allowed():
        return None
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


def _remember_history(text: str, tpl: str, kind: str = "") -> None:
    import json
    hist = caption_history()
    hist.append({"text": text, "tpl": tpl, "type": kind})
    os.makedirs(os.path.dirname(_history_path()), exist_ok=True)
    tmp = _history_path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(hist[-100:], f, ensure_ascii=False, indent=0)
    os.replace(tmp, _history_path())


TEXT_GAP, TPL_GAP = 20, 5  # одна надпись — не чаще раза в 20 клипов, один шаблон — не чаще раза в 5
LAST_TPL: dict = {"value": "", "type": ""}  # шаблон и тип последней надписи (для истории и ротации)
_PRON_M = re.compile(r"\b(HE|HIS|HIM|HIMSELF|HE'S)\b", re.I)
_PRON_F = re.compile(r"\b(SHE|HER|HERS|HERSELF|SHE'S)\b", re.I)


def _pronoun_ok(tpl: str, streamer: str, bank: dict) -> bool:
    """HE/HIS — только для стримеров-мужчин, SHE/HER — только для женщин, для остальных — хуки без местоимений
    (hook_bank.male_streamers / female_streamers)."""
    low = (streamer or "").lower().lstrip("@")
    males = {str(x).lower() for x in bank.get("male_streamers") or []}
    females = {str(x).lower() for x in bank.get("female_streamers") or []}
    if _PRON_M.search(tpl) and low not in males:
        return False
    if _PRON_F.search(tpl) and low not in females:
        return False
    return True


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


def _pick_fresh(cands: list[tuple[str, str]], spare: list[tuple[str, str]] = (), nick: str = "") -> tuple[str, str] | None:
    """cands: [(готовая надпись, шаблон)] → свежая (надписи не было в последних 20, шаблона — в последних 5),
    из свежих — одна из двух сильнейших по оценке хука (hookscore), чтобы не всегда одна и та же.
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
    from .hookscore import score
    for tier in tiers:
        if tier:
            best = sorted(tier, key=lambda c: -score(c[0], nick))[:2]
            return random.choice(best)
    return None


_PROMISE = re.compile(r"\b(WAIT FOR|AT THE END|TILL|UNTIL|WATCH TILL)\b|ЖДИ КОНЦОВКУ|ДО КОНЦА|В КОНЦЕ", re.I)
_QUESTION = re.compile(r"^\s*(\{s\}\s+)?(WILL|CAN|DOES|DID|IS|СМОЖЕТ|ПОЛУЧИТСЯ)\b|\?\s*$", re.I)


def _hook_ok(tpl: str, cat: str, peak_frac: float | None, cold_open: bool) -> bool:
    """Правила банка хуков: обещание «WAIT FOR / AT THE END / TILL» — только если пик в последней трети и без
    холодного старта (иначе обещание не сбудется); вопросы «WILL/CAN…?» — только для hype и fail."""
    if _PROMISE.search(tpl) and (cold_open or peak_frac is None or peak_frac < 2 / 3):
        return False
    if _QUESTION.search(tpl) and cat not in ("hype", "fail"):
        return False
    return True


def template_caption(streamer: str, title: str, top_messages: list[str], lang: str,
                     quote: str | None = None, peak_frac: float | None = None, cold_open: bool = False,
                     question: bool = False) -> str:
    """Надпись без Claude: 1) цензурная цитата стримера 2–6 слов, 2) банк хуков «Доктора», 3) старые шаблоны."""
    lang = "ru" if lang == "ru" else "en"
    bank = hook_bank()
    s = short_nick(streamer, bank)
    cat = _category(top_messages)  # чат подсказывает только тип момента
    hist = [_norm(h.get("text", "")) for h in caption_history()[-TEXT_GAP:]] + \
        [_norm(t) for t in recent_captions(streamer)[-TEXT_GAP:]]
    last_type = (caption_history()[-1:] or [{}])[0].get("type", "")
    # ротация (hook_bank.rotation): тот же тип подряд не ставим — цитата, смех, шок, хайп чередуются по кругу
    if quote and 2 <= len(quote.split()) <= 6 and last_type != "quote":  # цитата самого стримера — самое живое
        q = quote.strip(" .,!?").upper()
        q = f"{s}: «{q}»" if lang == "ru" else f'{s}: "{q}"'
        if _norm(q) not in hist and _norm(quote) not in " ".join(hist):
            LAST_TPL["value"], LAST_TPL["type"] = "quote", "quote"
            return q
    bl0 = bank.get(lang) or {}
    if cat == last_type or (cat not in bl0 and cat != "talk"):
        cycle = [c for c in ("laugh", "shock", "hype") + (("fail",) if cat == "fail" else ()) if bl0.get(c)]
        if cycle:
            i = cycle.index(last_type) if last_type in cycle else -1
            cat = next((c for c in cycle[i + 1:] + cycle[:i + 1] if c != last_type), cat)
    ok = lambda t, c: _hook_ok(t, c, peak_frac, cold_open) and _pronoun_ok(t, streamer, bank)
    hooks = [t for t in _bank_category(cat, bl0) if ok(t, cat)]
    if question and cat in ("hype", "fail"):  # question_overlay: для hype/fail — хук-вопрос, ответ даёт сам клип
        qs = [t for t in hooks if _QUESTION.search(t)]
        hooks = qs or hooks
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
        near = [t for c in ("shock", "laugh", "hype") if c != cat for t in (bl.get(c) or [])
                if t not in hooks and ok(t, c)]
        got = _pick_fresh(fmt(hooks), fmt(near), s)
        if got:
            LAST_TPL["value"] = got[1]
            LAST_TPL["type"] = next((c for c, lst in bl.items() if isinstance(lst, list) and got[1][5:] in lst), cat)
            return got[0]
    # запасной вариант — стратегия не скачалась: старые шаблоны, «в GTA 6» не чаще раза в 5 надписей
    gta = "gta" in title.lower() or "гта" in title.lower() or "gta" in " ".join(top_messages).lower()
    gta_recent = any("gta" in h for h in hist[-TPL_GAP + 1:])
    g = (" в GTA 6" if lang == "ru" else " in GTA 6") if gta and not gta_recent else ""
    got = _pick_fresh([(t.format(s=s, g=g), "tpl:" + t) for t in TEMPLATES[lang].get(cat) or TEMPLATES[lang]["general"]])
    LAST_TPL["value"], LAST_TPL["type"] = got[1], cat
    return got[0]


LAST_SCORE: dict = {"value": None}  # оценка Claude для последней надписи (1–10)


def make_caption(streamer: str, title: str, top_messages: list[str], transcript: str, lang: str,
                 log=print, frames: list[str] | None = None, quote: str | None = None,
                 peak_frac: float | None = None, cold_open: bool = False, question: bool = False) -> str:
    lang = account_lang(lang) or lang
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
        text = template_caption(streamer, title, top_messages, lang, quote, peak_frac, cold_open, question)
    text = censor_text(text)
    try:
        remember_caption(streamer, text)
        _remember_history(text, LAST_TPL["value"] or "claude:" + _norm(text), LAST_TPL.get("type", ""))
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


# ---------- тексты публикаций без Claude: из ника, надписи-хука, расшифровки и правил «Доктора» ----------
_EMOJI = {"laugh": "😂", "shock": "😳", "hype": "🔥", "fail": "💀", "talk": "🎙", "clip": "🎬", "general": "🎬"}
_MOMENT_TAGS = {"laugh": ["#funny", "#funnymoments"], "shock": ["#reaction", "#shocking"], "hype": ["#clutch", "#insane"],
                "fail": ["#fail", "#funnyfails"], "talk": ["#storytime", "#podcastclips"],
                "clip": ["#streamclips"], "general": ["#streamclips"]}
_CTA = {"en": {"tiktok": "Follow for daily {s} clips 🔔", "youtube": "Subscribe for daily {s} moments 🔔",
               "instagram": "Send this to a friend who needs to see it 👀 Follow for daily {s} clips"},
        "ru": {"tiktok": "Подписывайся — {s} каждый день 🔔", "youtube": "Подписывайся на лучшие моменты {s} 🔔",
               "instagram": "Перешли другу, который должен это увидеть 👀"}}


def _game(title: str) -> str:
    t = (title or "").lower()
    if "gta" in t or "гта" in t:
        return "GTA 6" if ("6" in t or "vi" in t.split()) else "GTA"
    return ""


def _sentence(hook: str, nick: str) -> str:
    """«SPEED CAN'T STOP LAUGHING» → «Speed can't stop laughing» (ник с большой буквы)."""
    h = re.sub(r"\s+", " ", (hook or "").strip())
    if not h:
        return ""
    if h.isupper() or sum(ch.isupper() for ch in h) > len(h) * 0.6:
        h = h.lower()
        h = h[:1].upper() + h[1:]
        if nick:
            h = re.sub(re.escape(nick.lower()), nick, h, flags=re.I)
    return h


_FRAGMENT_END = {"the", "a", "an", "and", "or", "but", "so", "to", "of", "in", "on", "what", "kind", "like", "that",
                 "is", "was", "i", "you", "we", "my", "your", "nick", "y"}


def _whole_phrase(q: str) -> bool:
    """Цитата в описание — только целая понятная фраза (text_rules.quote_rule): ≥4 слов, без обрывков
    вроде «kind of what y 'all Nick what the»."""
    ws = q.replace("’", "'").split()
    if len(ws) < 4 or any(w.startswith("'") for w in ws):
        return False
    if ws[-1][-1:] in ".!?":  # законченная фраза
        return True
    last = re.sub(r"[^\w']", "", ws[-1].lower())
    return last not in _FRAGMENT_END


def free_post(platform: str, streamer: str, hook: str, title: str, transcript: str = "",
              top_messages: list | None = None, lang: str = "en", words: list | None = None,
              peak: float | None = None, display: str = "") -> dict:
    """{title, description, hashtags[]} под площадку — по шаблонам и правилам text_rules (без Claude)."""
    from .policy import censor_text, word_kind
    lang = account_lang(lang) or ("ru" if lang == "ru" else "en")
    bank = hook_bank()
    nick_caps = short_nick(streamer, bank)
    nick = nick_caps.title() if nick_caps.isupper() else nick_caps  # SPEED → Speed (как зовут фанаты)
    full = (display or "").lstrip("@") or _nice_name(streamer)  # как ник пишется на канале (KaiCenat)
    cat = _category(top_messages or [])
    game = _game(title)
    sent = _sentence(hook, nick) or (f"{nick} on stream" if lang == "en" else f"{nick} на стриме")
    if nick.lower() not in sent.lower() and full.lower() not in sent.lower():
        sent = f"{full}: {sent}"
    # цитата стримера (цензурная) — то, что ищут и что цепляет в тексте
    quote = None
    if words and peak is not None:
        q = streamer_quote(words, peak, window=6.0)
        if q and not any(word_kind(w) for w in q.split()) and _whole_phrase(q):
            quote = q
    if not quote and transcript:
        for part in re.split(r"(?<=[.!?])\s+", transcript.strip()):
            part = part.strip(" -,")
            if 4 <= len(part.split()) <= 12 and not any(word_kind(w) for w in part.split()) and _whole_phrase(part):
                quote = part
                break
    tmax = int(((strategy_rules().get("title_max") or {}).get(platform)) or (60 if platform == "youtube" else 100))
    if platform == "youtube":  # ник и игра в начале, до 60 символов
        t = sent if not game else f"{sent} | {game}"
        if len(t) > tmax:
            t = sent
    else:
        t = sent
    t = t[:tmax].rstrip()
    lines = [f"{sent} {_EMOJI.get(cat, '')}".strip()]
    if quote:
        lines.append(f"“{censor_text(quote)}” — {nick}")
    src = "Twitch"
    if lang == "en":
        lines.append(f"{full} {'playing ' + game if game else 'live'} on {src}")
    else:
        lines.append(f"{full} {'в ' + game if game else 'на стриме'} ({src})")
    lines.append(_CTA["en" if lang == "en" else "ru"][platform if platform in _CTA["en"] else "tiktok"].format(s=nick))
    try:  # text_rules.description_max_words: коротко; лишнее убираем с конца по важности (цитата, игра, призыв)
        maxw = int(strategy_rules().get("description_max_words") or 0)
    except (TypeError, ValueError):
        maxw = 0
    if maxw:
        drop = [l for l in (lines[1] if quote else None, lines[-2], lines[-1]) if l]
        while sum(len(l.split()) for l in lines) > maxw and drop:
            lines.remove(drop.pop(0))
    desc = "\n".join(dict.fromkeys(l for l in lines if l))
    tag_nick = "#" + "".join(ch for ch in full.lower() if ch.isalnum())
    tmpl = (strategy_rules().get("hashtag_templates") or {}).get(platform)
    if isinstance(tmpl, list) and tmpl:  # шаблоны «Доктора» по площадкам: {streamer} = ник без пробелов
        bare = tag_nick[1:]
        tags = []
        for t in tmpl:
            t = str(t).replace("{streamer}", bare)
            if not game and "gta" in t.lower():
                continue  # игру ставим, только если это правда она
            tags.append(t if t.startswith("#") else "#" + t)
        if tag_nick not in tags:
            tags.insert(0, tag_nick)
    else:
        tags = [tag_nick]
        if game:
            tags += ["#gta6", "#gta"] if "6" in game else ["#gta"]
    tags += _MOMENT_TAGS.get(cat, ["#streamclips"])
    tags += ["#twitchclips" if lang == "en" else "#стрим", "#streamer"]
    return {"title": t, "description": desc, "hashtags": list(dict.fromkeys(tags))}


def strategy_rules() -> dict:
    try:
        from . import strategy
        return strategy.get().get("text_rules") or {}
    except Exception:
        return {}


def make_post(streamer: str, caption: str, title: str, transcript: str, lang: str, link: str = "",
              log=print, platform: str = "tiktok", top_messages: list | None = None) -> dict:
    """Описание и хэштеги: через Claude (если есть ключ), иначе по шаблонам и правилам «Доктора»."""
    lang = account_lang(lang) or lang
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
    p = free_post(platform, streamer, caption, title, transcript, top_messages, lang)
    return {"description": p["description"], "hashtags": " ".join(p["hashtags"][:5]), "title": p["title"]}



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
