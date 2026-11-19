"""Проверка клипа на нарушения правил YouTube / TikTok / Instagram и исправление.

Что ищем:
  * мат и оскорбления в речи стримера — по распознанной речи (слова с точным временем);
  * язык вражды (слюры) — самое опасное: за это удаляют ролик и дают страйк;
  * чужая музыка — по пометкам распознавания речи («♪», «[музыка]»);
  * с ключом Claude — ещё и картинку: обнажёнка, реальная жестокость, наркотики, личные данные на экране
    (телефон, адрес, почта), символы ненависти. Насилие в самой игре (GTA) нарушением не считается.

Как исправляем:
  * мат/слюры — «запикиваем» (писк вместо слова) и размываем строку субтитров в этот момент;
  * музыка — глушим звук на отрезке (по желанию: это заглушит и голос);
  * картинка — размываем область (или весь кадр) на время нарушения.
Исправленная версия делается отдельным файлом; оригинал не трогаем, пока человек не выберет.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time

from . import paths

# --- слова. Корни, чтобы ловить все формы. Список нарочно короткий: только то, за что реально режут показы. ---
SLURS = [
    r"nigg(?:a|er|ah|as|ers|uh)?s?", r"faggot\w*", r"fag(?:s)?", r"retard(?:ed|s)?", r"tranny", r"chink\w*",
    r"kike\w*", r"spic(?:s)?", r"coon(?:s)?", r"wetback\w*",
    r"пидор\w*", r"пидар\w*", r"педик\w*", r"жид\w*", r"хач\w*", r"чурк\w*", r"ниггер\w*", r"негритос\w*",
    r"даун(?:ы|ов)?", r"хохл\w*", r"кацап\w*",
]
PROFANITY = [
    r"\w*fuck\w*", r"shit\w*", r"bullshit", r"bitch\w*", r"cunt\w*", r"motherf\w*", r"asshole\w*", r"dick(?:head)?s?",
    r"puss(?:y|ies)", r"whore\w*", r"slut\w*",
    # русский мат: корни с типичными приставками (а не «где угодно в слове» — иначе ловились «мебель», «страхуй»)
    r"(?:на|по|о|от|за|рас|до|при|пере|ни|об|под|вы|у)?ху[йяеёию]\w*",
    r"(?:рас|за|на|вы|от|по|с|при|у|под|об|рас)?пи[зс][дж]\w*", r"пздц\w*", r"пзд\w*",
    r"(?:за|от|вы|у|на|по|под|раз|рас|про|при|до|пере|недо|об|съ|въ|подъ|отъ|изъ|разъ|объ|долбо|долба)?ъ?[её]б"
    r"(?:а|ал|ан|ат|ет|ёт|ис|ись|ло|лан|ля|ну|ут|ыв|уч|ош|ок|ук|ен|ар|ит|им|ли|лу|ей|у)\w*",
    r"(?:долбо|долба)[её]б\w*", r"бля\w*", r"сук[аиуеоё]\w*", r"суч(?:ка|ки|ке|ку|кой|ара|ары|ий|ья|ье)\w*",
    r"мудак\w*", r"мудил\w*", r"муди\w*", r"г[ао]ндон\w*", r"залуп\w*", r"шлюх\w*", r"дроч\w*",
    r"(?:на|по|ни|до)?хер(?:а|ня|ни|не|ню|ов|ово|овый|овая|овое|ь)?", r"[её]п(?:т|та|ть|тать|онский)?",
    r"манд(?:а|ы|е|у|ой|ёж|еж)", r"говн\w*", r"дерьм\w*", r"срань", r"сран\w*", r"мраз(?:ь|и|ота|ей)", r"жоп\w*",
]
# слова, которые похожи на мат по корню, но им не являются
NOT_BAD = {"себя", "небо", "небе", "неба", "ребят", "ребята", "ребенок", "ребёнок", "хлеба", "требую", "требует",
           "требовать", "погиб", "гибель", "колеба", "колебания", "вебка", "вебку", "вебке", "dickens", "скипидар",
           "застрахуй", "сукно", "dicks", "ебэй", "херсон", "хересе", "сучок", "сучки_дерева", "мудрый",
           "мудрость", "мудрец", "мудро", "муди", "ехать", "епископ"}

_SLUR_RX = re.compile(r"^(?:" + "|".join(SLURS) + r")$", re.I)
_PROF_RX = re.compile(r"^(?:" + "|".join(PROFANITY) + r")$", re.I)
_MUSIC_RX = re.compile(r"[♪♫]|\[(?:music|музыка)\]|\((?:music|музыка)\)", re.I)

# что грозит на каждой площадке
RULES = {
    "slur": ("Оскорбление / язык вражды", "high",
             {"YouTube": "удаление ролика и страйк", "TikTok": "удаление, бан аккаунта", "Instagram": "удаление"}),
    "profanity": ("Мат", "medium",
                  {"YouTube": "меньше рекламы (особенно мат в первые 7 секунд)", "TikTok": "могут урезать показы",
                   "Instagram": "не попадёт в рекомендации"}),
    "music": ("Возможно, чужая музыка", "medium",
              {"YouTube": "блокировка или заявка по авторским правам", "TikTok": "звук заглушат",
               "Instagram": "звук заглушат или ролик скроют"}),
    "nudity": ("Обнажённое тело / откровенное", "high",
               {"YouTube": "удаление", "TikTok": "удаление", "Instagram": "удаление"}),
    "gore": ("Кровь, жестокость (реальная)", "high",
             {"YouTube": "ограничение 18+ или удаление", "TikTok": "удаление", "Instagram": "скрытие (деликатный контент)"}),
    "drugs": ("Наркотики / опасные действия", "medium",
              {"YouTube": "ограничение 18+", "TikTok": "удаление", "Instagram": "не попадёт в рекомендации"}),
    "personal_info": ("Личные данные на экране", "high",
                      {"YouTube": "удаление (нарушение приватности)", "TikTok": "удаление", "Instagram": "удаление"}),
    "hate_symbol": ("Символ ненависти", "high",
                    {"YouTube": "удаление и страйк", "TikTok": "удаление", "Instagram": "удаление"}),
    "manual": ("Размыть вручную", "medium", {"YouTube": "закрыто вручную", "TikTok": "закрыто вручную",
                                             "Instagram": "закрыто вручную"}),
    "other": ("Другое нарушение", "medium", {"YouTube": "риск ограничений", "TikTok": "риск ограничений",
                                             "Instagram": "риск ограничений"}),
}
FIX_FOR = {"manual": "blur", "slur": "bleep", "profanity": "bleep", "music": "mute", "nudity": "blur", "gore": "blur",
           "drugs": "blur", "personal_info": "blur", "hate_symbol": "blur", "other": "blur"}

# строка субтитров в кадре 1080x1920 (стиль Default: внизу по центру, отступ 560) — размываем её на время писка
SUBS_BOX = (40, 1150, 1000, 250)


def _clean(word: str) -> str:
    return re.sub(r"[^\w]", "", word.lower().replace("ё", "е")) if word else ""


def word_kind(word: str) -> str | None:
    w = _clean(word)
    if not w or w in NOT_BAD:
        return None
    if _SLUR_RX.match(w):
        return "slur"
    if _PROF_RX.match(w):
        return "profanity"
    return None


def censor_text(text: str) -> str:
    """Для субтитров: мат и оскорбления заменяем звёздочками (первая буква остаётся)."""
    def rep(m):
        w = m.group(0)
        return w[0] + "*" * (len(w) - 1) if word_kind(w) else w
    return re.sub(r"[\w']+", rep, text)


def _issue(kind: str, t0: float, t1: float, what: str, box=None, source: str = "speech") -> dict:
    title, sev, plats = RULES.get(kind, RULES["other"])
    return {"kind": kind, "t0": round(max(0.0, t0), 2), "t1": round(t1, 2), "what": what, "title": title,
            "severity": sev, "platforms": plats, "fix": FIX_FOR.get(kind, "blur"), "box": box, "source": source}


def check_words(words: list) -> list[dict]:
    """words: [(начало, конец, слово), ...] → нарушения в речи."""
    out = []
    for item in words or []:
        try:
            s, e, w = float(item[0]), float(item[1]), str(item[2])
        except (TypeError, ValueError, IndexError):
            continue
        if _MUSIC_RX.search(w):
            out.append(_issue("music", s, e, "♪"))
            continue
        if "*" in w and re.search(r"[A-Za-zА-Яа-яЁё]", w):
            out.append(_issue("profanity", s - 0.05, e + 0.05, w.strip()))
            continue
        for token in re.findall(r"[\w']+", w):
            kind = word_kind(token)
            if kind:
                out.append(_issue(kind, s - 0.05, e + 0.05, token))
                break
    return _merge_music(out)


def _merge_music(issues: list) -> list:
    music = sorted((i for i in issues if i["kind"] == "music"), key=lambda i: i["t0"])
    rest = [i for i in issues if i["kind"] != "music"]
    merged: list = []
    for m in music:
        if merged and m["t0"] - merged[-1]["t1"] < 3:
            merged[-1]["t1"] = max(merged[-1]["t1"], m["t1"])
        else:
            merged.append(dict(m))
    return sorted(rest + merged, key=lambda i: i["t0"])


# ---------- распознавание речи для старых клипов (где слова не сохранены) ----------
def transcribe_words(clip: str, model: str = "small") -> list:
    from . import subtitles
    m = subtitles._get_model(model)
    audio = subtitles._load_audio(clip)
    try:
        segs, _ = m.transcribe(audio, word_timestamps=True, vad_filter=False)
        segs = list(segs)
    except Exception:
        return []
    return [(float(w.start), float(w.end), w.word) for s in segs for w in (s.words or []) if w.word.strip()]


# ---------- картинка и смысл речи — через Claude (если есть ключ) ----------
VISION_PROMPT = """You check a short vertical gaming-stream clip (1080x1920) against YouTube, TikTok and Instagram community guidelines before it is uploaded.
You get frames taken at the listed times and the auto transcript of what the streamer says.

Flag ONLY clear, real risks:
- nudity: nudity or sexually explicit content — ALSO for video-game characters: exposed buttocks (e.g. a character in a
  shower or naked), exposed breasts or genitals count even in a game; give a tight box around the exposed body part
- gore: realistic graphic gore or real-world violence (NOT ordinary video-game shooting/fighting — GTA violence is allowed)
- drugs: real drug use or clearly dangerous real-life acts
- personal_info: readable phone numbers, home addresses, emails, passwords, ID documents on screen
- hate_symbol: swastikas or other hate symbols
- slur: hateful slurs or hate speech in the transcript (quote the exact words)
Do not flag swearing (handled separately), game violence, guns in the game, or anything you are unsure about.

Answer with JSON only, no other text:
{"issues": [{"kind": "...", "frame": <index of the frame where it is visible, or null for speech>,
  "box": [x, y, w, h] as fractions 0..1 of the frame covering the problem area (generous), or null for the whole frame,
  "what": "short description in Russian"}]}
Return {"issues": []} if the clip is fine."""


def _frames(clip: str, work: str, every: float = 2.5, limit: int = 14) -> list[tuple[float, str]]:
    flags = 0x08000000 if os.name == "nt" else 0
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip],
                           capture_output=True, text=True, creationflags=flags)
        dur = float(r.stdout.strip())
    except Exception:
        dur = 30.0
    n = max(1, min(limit, int(dur / every) + 1))
    out = []
    os.makedirs(work, exist_ok=True)
    for i in range(n):
        t = min(dur - 0.2, (i + 0.5) * dur / n)
        p = os.path.join(work, f"pol_{i}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", clip, "-frames:v", "1",
                        "-vf", "scale=432:-2", "-q:v", "5", p], capture_output=True, creationflags=flags)
        if os.path.exists(p):
            out.append((t, p))
    return out


def check_visual(clip: str, words: list, key: str, log=print) -> list[dict]:
    import base64
    import anthropic
    work = os.path.join(paths.default_work_dir(), "policy_frames")
    frames = _frames(clip, work)
    step = (frames[1][0] - frames[0][0]) if len(frames) > 1 else 3.0
    content: list = []
    for i, (t, p) in enumerate(frames):
        with open(p, "rb") as f:
            content.append({"type": "text", "text": f"Frame {i} at {t:.1f}s"})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                        "data": base64.standard_b64encode(f.read()).decode()}})
    transcript = " ".join(f"[{float(s):.1f}s] {w.strip()}" for s, e, w in words)[:3000] if words else "(no speech)"
    content.append({"type": "text", "text": "Transcript with times:\n" + transcript})
    client = anthropic.Anthropic(api_key=key, max_retries=3)
    resp = client.beta.messages.create(
        model="claude-opus-5-5", max_tokens=3000, output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        system=VISION_PROMPT, messages=[{"role": "user", "content": content}])
    for _, p in frames:
        try:
            os.remove(p)
        except OSError:
            pass
    text = next((b.text for b in resp.content if b.type == "text"), "")
    m = re.search(r"\{.*\}", text, re.S)
    try:
        data = json.loads(m.group(0)) if m else {}
    except ValueError:
        data = {}
    out = []
    for it in data.get("issues") or []:
        kind = it.get("kind") if it.get("kind") in RULES else "other"
        fr = it.get("frame")
        box = it.get("box")
        if isinstance(box, list) and len(box) == 4:
            try:
                box = [max(0.0, min(1.0, float(v))) for v in box]
            except (TypeError, ValueError):
                box = None
        else:
            box = None
        if isinstance(fr, int) and 0 <= fr < len(frames):
            t = frames[fr][0]
            out.append(_issue(kind, t - step, t + step, str(it.get("what") or ""), box, source="video"))
        elif kind == "slur":
            continue  # слюры в речи уже ловим по словам с точным временем
        else:
            out.append(_issue(kind, 0, 10 ** 6, str(it.get("what") or ""), box, source="video"))
    return out


NUDITY_NOTE: dict = {}  # последняя проблема поиска обнажёнки (например, не скачалась модель)


def check_nudity(clip: str, log=print) -> list[dict]:
    """Обнажёнка в кадре — локальная модель, без интернета и без Claude (каждые полсекунды)."""
    NUDITY_NOTE.pop("text", None)
    try:
        from . import nudity
        if not nudity.ensure_model(log):
            NUDITY_NOTE["text"] = "поиск обнажёнки не работает: не скачалась модель (проверь интернет/VPN)"
            return []
        found = nudity.scan_clip(clip, log=log)
    except Exception as e:
        NUDITY_NOTE["text"] = f"поиск обнажёнки не удался: {type(e).__name__}: {e}"
        log(NUDITY_NOTE["text"])
        return []
    return [_issue("nudity", f["t0"], f["t1"], f["what"], f["box"], source="video") for f in found]


# ---------- проверка целиком + память результатов ----------
def _store() -> str:
    return os.path.join(paths.default_work_dir(), "policy.json")


def load_results() -> dict:
    try:
        with open(_store(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_result(clip: str, result: dict) -> None:
    data = load_results()
    data[os.path.normpath(clip)] = result
    os.makedirs(os.path.dirname(_store()), exist_ok=True)
    with open(_store(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def check_clip(clip: dict, key: str | None = None, log=print, whisper_model: str = "small") -> dict:
    """clip — запись клипа из библиотеки (path, words?, ...). Возвращает {'issues': [...], 'visual': bool, ...}."""
    path = clip["path"]
    words = clip.get("words")
    note = ""
    if not words:
        from . import subtitles
        if subtitles.available():
            log("Распознаю речь клипа...")
            words = transcribe_words(path, whisper_model)
        else:
            note = "речь не проверена: не установлено распознавание речи (install_subs.bat)"
    issues = check_words(words or [])
    log("Ищу обнажёнку в кадре...")
    issues += check_nudity(path, log)
    if NUDITY_NOTE.get("text"):
        note = (note + "; " if note else "") + NUDITY_NOTE["text"]
    visual = False
    if key:
        log("Claude смотрит картинку клипа...")
        try:
            local = [i for i in issues if i["kind"] == "nudity"]
            for v in check_visual(path, words or [], key, log):
                if v["kind"] == "nudity" and any(v["t0"] < i["t1"] and v["t1"] > i["t0"] for i in local):
                    continue
                issues.append(v)
            visual = True
        except Exception as e:
            note = (note + "; " if note else "") + f"картинка не проверена: {type(e).__name__}: {e}"
    else:
        note = (note + "; " if note else "") + "картинка не проверена: нет ключа Claude"
    issues.sort(key=lambda i: i["t0"])
    res = {"issues": issues, "visual": visual, "note": note, "checked": time.time(), "nudity_v": 2,
           "fixed": bool(clip.get("_fixed")), "words": words or []}
    save_result(path, res)
    return res


# ---------- исправление ----------
def _between(spans) -> str:
    return "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in spans)


def _duration(path: str) -> float:
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=flags)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 60.0


def subtitle_lines(words: list, words_per_line: int = 3) -> list[tuple[float, float, str]]:
    """Строки субтитров ровно так, как их нарезает subtitles.make_ass: (начало, конец, текст)."""
    ws = []
    for item in words or []:
        try:
            ws.append((float(item[0]), float(item[1]), str(item[2])))
        except (TypeError, ValueError, IndexError):
            continue
    ws = [w for w in ws if w[2].strip()]
    lines, cur = [], []
    for w in ws:
        if cur and (len(cur) >= words_per_line or w[0] - cur[-1][1] > 0.6):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    out = []
    for i, ln in enumerate(lines):
        start, end = ln[0][0], ln[-1][1] + 0.15
        if i + 1 < len(lines):
            end = min(end, lines[i + 1][0][0])
        out.append((start, end, " ".join(w[2].strip() for w in ln)))
    return out


def _subs_cover(issues: list, words: list | None, dur: float) -> tuple[list, list]:
    """Какие строки субтитров надо закрыть: [(начало, конец)] для размытия и [(начало, конец, текст со звёздочками)]."""
    speech = [i for i in issues if i.get("kind") in ("profanity", "slur") and i.get("fix") in ("bleep", "mute")]
    if not speech:
        return [], []
    lines = subtitle_lines(words or [])
    spans, redraw = [], []
    for i in speech:
        hit = [ln for ln in lines if ln[0] < i["t1"] + 0.05 and ln[1] > i["t0"] - 0.05]
        if not hit:  # слов нет (старый клип) — закрываем с запасом вокруг слова
            spans.append((max(0.0, i["t0"] - 1.2), min(dur, i["t1"] + 1.2)))
            continue
        for a, b, text in hit:
            span = (max(0.0, a - 0.1), min(dur, b + 0.1))
            if span not in spans:
                spans.append(span)
                redraw.append((a, b, censor_text(text)))
    return spans, redraw


def _rect(box, W, H, pad=0.04):
    if not box:
        return (0, 0, W, H)
    x, y, w, h = box
    x0, y0 = max(0.0, x - pad), max(0.0, y - pad)  # с запасом: модель и Claude указывают область примерно
    x1, y1 = min(1.0, x + w + pad), min(1.0, y + h + pad)
    return (int(x0 * W) // 2 * 2, int(y0 * H) // 2 * 2, max(16, int((x1 - x0) * W) // 2 * 2),
            max(16, int((y1 - y0) * H) // 2 * 2))


def _overlap(r1, r2) -> bool:
    return r1[0] < r2[0] + r2[2] and r2[0] < r1[0] + r1[2] and r1[1] < r2[1] + r2[3] and r2[1] < r1[1] + r1[3]


def detect_text_plates(path: str) -> list[tuple[int, int, int, int]]:
    """Где в клипе белая плашка-надпись (она стоит весь клип): прямоугольники, которые нельзя размывать."""
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    found = []
    for frac in (0.25, 0.5, 0.75):
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(n * frac)))
        ok, fr = cap.read()
        if not ok:
            continue
        H, W = fr.shape[:2]
        mask = (fr.min(axis=2) > 225).astype(np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        cnt, _, stats, _ = cv2.connectedComponentsWithStats(mask)
        rects = []
        for x, y, w, h, area in stats[1:cnt]:
            if w > 0.2 * W and 25 < h < 0.2 * H and area > 0.55 * w * h:
                rects.append((int(x), int(y), int(w), int(h)))
        found.append(rects)
    cap.release()
    out = []
    for r in (found[0] if found else []):  # плашка неподвижна: должна быть на всех проверенных кадрах
        if all(any(abs(r[0] - q[0]) < 30 and abs(r[1] - q[1]) < 30 for q in other) for other in found[1:]):
            out.append((max(0, r[0] - 8), max(0, r[1] - 8), r[2] + 16, r[3] + 16))
    return out


def build_fix_filters(issues: list, size=(1080, 1920), subs_burned: bool = True, dur: float = 60.0,
                      words: list | None = None, redraw_ass: str | None = None, plates: list | None = None):
    """Фильтры ffmpeg для исправления: (видео-фильтр, аудио-фильтр).
    plates — плашки-надписи: после размытия картинки их возвращаем чёткими (надпись не должна размываться);
    redraw_ass — строки субтитров, которые рисуются поверх заново (со звёздочками вместо мата)."""
    W, H = size
    bleep = [(i["t0"], min(i["t1"], dur)) for i in issues if i.get("fix") == "bleep"]
    mute = [(i["t0"], min(i["t1"], dur)) for i in issues if i.get("fix") == "mute"]
    video = [(_rect(i.get("box"), W, H), (i["t0"], min(i["t1"], dur))) for i in issues if i.get("fix") == "blur"]
    subs = [(SUBS_BOX, span) for span in (_subs_cover(issues, words, dur)[0] if subs_burned else [])]
    plates = [p for p in (plates or []) if any(_overlap(p, r) for r, _ in video)]
    vf = None
    if video or subs:
        chain = []
        cur = "0:v"
        if plates:
            chain.append(f"[0:v]split={len(plates) + 1}[src]" + "".join(f"[keep{k}]" for k in range(len(plates))))
            cur = "src"
        n = 0
        for (x, y, w, h), (a, b) in video:
            r = max(2, min(40, min(w, h) // 4 - 1))
            chain.append(f"[{cur}]split[m{n}][c{n}];[c{n}]crop={w}:{h}:{x}:{y},boxblur={r}:4[b{n}];"
                         f"[m{n}][b{n}]overlay={x}:{y}:enable='between(t,{a:.2f},{b:.2f})'[v{n}]")
            cur, n = f"v{n}", n + 1
        for k, (x, y, w, h) in enumerate(plates):  # надпись-плашку возвращаем чёткой поверх размытия
            chain.append(f"[keep{k}]crop={w}:{h}:{x}:{y}[p{k}];[{cur}][p{k}]overlay={x}:{y}[pv{k}]")
            cur = f"pv{k}"
        for (x, y, w, h), (a, b) in subs:  # строка субтитров с матом — размыта всё время показа
            chain.append(f"[{cur}]split[m{n}][c{n}];[c{n}]crop={w}:{h}:{x}:{y},boxblur=40:4[b{n}];"
                         f"[m{n}][b{n}]overlay={x}:{y}:enable='between(t,{a:.2f},{b:.2f})'[v{n}]")
            cur, n = f"v{n}", n + 1
        if redraw_ass:
            chain.append(f"[{cur}]ass={redraw_ass}[vr]")
            cur = "vr"
        vf = ";".join(chain).rsplit(f"[{cur}]", 1)[0] + "[v]"
    af = None
    if bleep or mute:
        silent = _between(bleep + mute)
        af = f"[0:a]volume=0:enable='{silent}'[a0]"
        if bleep:
            af += (f";sine=frequency=1000:sample_rate=48000,volume=0.35,"
                   f"volume=0:enable='not({_between(bleep)})'[tone];[a0][tone]amix=inputs=2:duration=first:"
                   f"normalize=0[a]")
        else:
            af = af.replace("[a0]", "[a]")
    return vf, af


def fix_clip(src: str, out: str, issues: list, subs_burned: bool = True, words: list | None = None) -> str:
    dur = _duration(src)
    W, H = 1080, 1920
    ass_name, cwd = None, None
    redraw = []
    video = [(_rect(i.get("box"), W, H), i["t0"], i["t1"]) for i in issues if i.get("fix") == "blur"]
    if subs_burned:
        _, redraw = _subs_cover(issues, words, dur)
        # строки субтитров, на которые попало размытие картинки, рисуем заново поверх — текст остаётся чётким
        for a, b, text in subtitle_lines(words or []):
            if any(_overlap(r, SUBS_BOX) and a < t1 and b > t0 for r, t0, t1 in video) \
                    and not any(abs(a - x[0]) < 0.01 for x in redraw):
                redraw.append((a, b, censor_text(text)))
    if redraw:
        from .subtitles import ASS_HEADER, _ts
        cwd = os.path.join(paths.default_work_dir(), "fixed")
        os.makedirs(cwd, exist_ok=True)
        ass_name = f"redraw_{int(time.time() * 1000)}.ass"
        with open(os.path.join(cwd, ass_name), "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
            for a, b, text in sorted(redraw):
                text = text.upper().replace("{", "(").replace("}", ")")
                f.write(f"Dialogue: 0,{_ts(a)},{_ts(b)},Default,,0,0,0,,{text}\n")
    plates = detect_text_plates(src) if video else []
    vf, af = build_fix_filters(issues, subs_burned=subs_burned, dur=dur, words=words, redraw_ass=ass_name,
                               plates=plates)
    if not vf and not af:
        raise ValueError("нечего исправлять")
    graph = ";".join(x for x in (vf, af) if x)
    src, out = os.path.abspath(src), os.path.abspath(out)  # ffmpeg запускается из папки субтитров (пути с «:»)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", graph,
           "-map", "[v]" if vf else "0:v", "-map", "[a]" if af else "0:a?"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"] if vf else ["-c:v", "copy"]
    cmd += ["-c:a", "aac", "-b:a", "160k"] if af else ["-c:a", "copy"]
    cmd += ["-movflags", "+faststart", out]
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags, cwd=cwd)
    if ass_name:
        try:
            os.remove(os.path.join(cwd, ass_name))
        except OSError:
            pass
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[-600:])
    return out


def originals_dir() -> str:
    return os.path.join(paths.default_work_dir(), "originals")


FIXES_FOR = {"nudity": ("blur",), "gore": ("blur",), "personal_info": ("blur", "crop_out"), "hate_symbol": ("blur", "crop_out"),
             "slur": ("bleep", "bleep_profanity", "mute"), "drugs": ("blur",), "manual": ("blur",)}


def publish_block(clip_path: str, applied: list | None = None) -> str | None:
    """Жёсткое правило: клип с серьёзным (high) неисправленным нарушением НЕ публикуется никаким способом.
    applied — приёмы, применённые в версии под площадку (размытие/запикивание в ней тоже считается исправлением).
    Возвращает причину запрета или None."""
    res = load_results().get(os.path.normpath(clip_path)) or {}
    done = {a.get("type") if isinstance(a, dict) else a for a in (applied or [])}
    left = []
    for i in res.get("issues") or []:
        if i.get("severity") != "high":
            continue
        if done & set(FIXES_FOR.get(i.get("kind"), ())):
            continue
        left.append(i)
    if not left:
        return None
    kinds = sorted({RULES.get(i.get("kind"), RULES["other"])[0] for i in left})
    return "неисправленное серьёзное нарушение: " + ", ".join(kinds) + " — сначала «Исправить нарушение»"


def flagged_posted() -> list[dict]:
    """Уже выложенные клипы, в которых есть неисправленное серьёзное нарушение: их надо снять с публикации."""
    from . import library
    pub = library.load_published()
    out = []
    for d in library.list_dates():
        for c in library.list_clips(d):
            reason = publish_block(c["path"])
            if not reason:
                continue
            for pl, on in (c.get("posted") or {}).items():
                if on:
                    info = (pub.get(os.path.normpath(c["path"])) or {}).get(pl) or {}
                    out.append({"clip": c, "platform": pl, "reason": reason, "id": info.get("id", ""),
                                "url": info.get("url", "")})
    return out
