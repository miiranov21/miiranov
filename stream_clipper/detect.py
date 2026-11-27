"""Поиск интересных моментов: всплески чата + всплески громкости."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, asdict

import numpy as np

from .chat import ChatMessage

# Слова/эмоуты, которые чат спамит в интересные моменты (регистр не важен).
DEFAULT_HYPE = [
    # смех
    "kekw", "lul", "lulw", "omegalul", "lmao", "lol", "xd", "icant", "pepelaugh", "kekl",
    "ахах", "хаха", "ахаха", "ору", "орууу", "лол", "кек", "ржу", "аха",
    # шок / хайп
    "pog", "pogchamp", "poggers", "pogu", "wtf", "omg", "monkas", "monkaw", "nooo", "noway",
    "wow", "sheesh", "gg", "ez", "wait", "what",
    "жесть", "имба", "охренеть", "офигеть", "нифига", "капец", "вау", "ого", "чего", "шо",
    # просьбы клипнуть
    "clip", "clipit", "клип", "клипай", "клипнул", "клипните",
]

_word_re = re.compile(r"[\w']+", re.UNICODE)


@dataclass
class Highlight:
    start: float        # начало клипа (сек VOD)
    end: float          # конец клипа
    peak: float         # момент действия
    score: float
    chat_z: float
    audio_z: float
    top_messages: list[str]
    jump_z: float = 0.0     # резкий скачок звука (крик)
    vis_z: float = 0.0      # резкая смена картинки (взрыв, авария)
    clip_views: int = 0     # сколько просмотров у клипа зрителей на этом месте (0 — клипа нет)

    def to_dict(self):
        return asdict(self)


def _is_hype(text: str, hype: set[str]) -> bool:
    t = text.lower()
    if "???" in t or "!!!" in t:
        return True
    for w in _word_re.findall(t):
        if w in hype:
            return True
        # "ахахахах", "ооооо", "kekwww" — укорачиваем повторы букв
        if re.sub(r"(.)\1+", r"\1", w) in hype or w.startswith(("ахах", "хаха", "кек", "kek", "lul")):
            return True
    return False


def chat_activity(msgs: list[ChatMessage], duration: int, hype_words: list[str],
                  hype_weight: float = 1.5, author_cooldown: float = 4.0) -> np.ndarray:
    """Очки активности чата для каждой секунды. Спам одного человека не считается."""
    hype = {w.lower() for w in hype_words}
    arr = np.zeros(duration + 1, dtype=np.float32)
    last_by_author: dict[str, float] = {}
    for m in msgs:
        if m.t < 0 or m.t > duration:
            continue
        prev = last_by_author.get(m.author)
        if m.author and prev is not None and m.t - prev < author_cooldown:
            continue
        last_by_author[m.author] = m.t
        arr[int(m.t)] += 1.0 + (hype_weight if _is_hype(m.text, hype) else 0.0)
    return arr


def smooth(x: np.ndarray, w: int) -> np.ndarray:
    if w <= 1 or x.size == 0:
        return x.astype(np.float32)
    k = np.ones(w, dtype=np.float32) / w
    return np.convolve(x, k, mode="same").astype(np.float32)


def robust_z(x: np.ndarray, window: int = 600, step: int = 30, min_scale: float = 0.3) -> np.ndarray:
    """Насколько значение выше «обычного» уровня вокруг (скользящая медиана + MAD).
    Так программа подстраивается под онлайн: 50 сообщений/мин у маленького стримера —
    хайп, а у большого — тишина."""
    n = x.size
    if n == 0:
        return x
    centers = np.arange(0, n, step)
    meds = np.empty(len(centers), dtype=np.float32)
    mads = np.empty(len(centers), dtype=np.float32)
    half = window // 2
    for i, c in enumerate(centers):
        seg = x[max(0, c - half): min(n, c + half)]
        med = np.median(seg)
        meds[i] = med
        mads[i] = np.median(np.abs(seg - med))
    idx = np.arange(n)
    med_i = np.interp(idx, centers, meds)
    mad_i = np.interp(idx, centers, mads)
    floor = max(float(np.median(mads)) * 0.5, min_scale / 1.4826)
    z = (x - med_i) / (1.4826 * np.maximum(mad_i, floor))
    return np.clip(z, -20, 20).astype(np.float32)


def find_highlights(msgs: list[ChatMessage], duration: int, *, audio_db: np.ndarray | None = None,
                    visual: np.ndarray | None = None, visual_weight: float = 0.5,
                    top: int = 10, clip_pre: float = 20, clip_post: float = 15, chat_lag: int = 5,
                    audio_weight: float = 0.6, min_score: float = 3.0, min_gap: float | None = None,
                    hype_words: list[str] | None = None, exclude: list[tuple[float, float]] | None = None,
                    clips: list[tuple[float, float, int]] | None = None, log=print) -> list[Highlight]:
    duration = int(duration)
    hype_words = hype_words or DEFAULT_HYPE
    chat = smooth(chat_activity(msgs, duration, hype_words), 8)
    # Чат реагирует с задержкой: сдвигаем на chat_lag секунд назад к моменту действия.
    if chat_lag > 0:
        chat = np.concatenate([chat[chat_lag:], np.zeros(chat_lag, dtype=np.float32)])
    chat_z = robust_z(chat)

    audio_z = np.zeros_like(chat_z)
    if audio_db is not None and audio_db.size:
        a = np.full(chat_z.size, float(np.median(audio_db)), dtype=np.float32)
        m = min(a.size, audio_db.size)
        a[:m] = audio_db[:m]
        audio_z = robust_z(smooth(a, 3), min_scale=2.0)  # dB

    # резкие скачки звука (крик, вскрик стримера) — важнее просто громкого фона
    jump_z = np.zeros_like(chat_z)
    if audio_db is not None and audio_db.size:
        d = np.diff(smooth(a, 2), prepend=float(a[0]))
        jump_z = robust_z(np.clip(d, 0, None), min_scale=1.5)
    # картинка: резкие смены кадра (взрывы, аварии, внезапные события) — работает даже без чата
    vis_z = np.zeros_like(chat_z)
    if visual is not None and visual.size:
        v = np.zeros(chat_z.size, dtype=np.float32)
        m = min(v.size, visual.size)
        v[:m] = visual[:m]
        vis_z = robust_z(smooth(v, 3), min_scale=0.04)

    # клипы зрителей: люди сами вырезали этот момент; чем больше просмотров, тем сильнее (лучший клип ≈ +3)
    clip_sig = np.zeros_like(chat_z)
    views = np.zeros(chat_z.size, dtype=np.int64)
    for off, dur, v in clips or []:
        a, b = max(0, int(off)), min(chat_z.size, int(off + max(dur, 5)) + 1)
        if b > a:
            clip_sig[a:b] = np.maximum(clip_sig[a:b], np.log10(v + 10))
            views[a:b] = np.maximum(views[a:b], v)
    if clip_sig.max() > 0:
        clip_sig = 3.0 * clip_sig / clip_sig.max()
    score = (np.clip(chat_z, 0, None) + audio_weight * np.clip(audio_z, 0, None)
             + 0.4 * np.clip(jump_z, 0, None) + visual_weight * np.clip(vis_z, 0, None) + clip_sig)
    score = smooth(score, 5)

    gap = min_gap if min_gap is not None else (clip_pre + clip_post)
    work = score.copy()
    for s, e in exclude or []:
        work[max(0, int(s)): int(e) + 1] = 0  # уже нарезанные куски

    result: list[Highlight] = []
    while len(result) < top:
        p = int(np.argmax(work)) if work.size else 0
        val = float(work[p]) if work.size else 0.0
        if val < min_score:
            break
        work[max(0, int(p - gap)): int(p + gap) + 1] = 0
        start = max(0.0, p - clip_pre)
        end = min(float(duration), p + clip_post)
        if end - start < 5:
            continue
        # что писал чат в этот момент — подсказка для названия ролика
        texts = [m.text.strip() for m in msgs if start + chat_lag <= m.t <= end + chat_lag and m.text.strip()]
        top_msgs = [t for t, _ in Counter(t.lower()[:60] for t in texts).most_common(8)]
        lo, hi = max(0, p - 6), min(len(chat_z), p + 7)  # действие — в окрестности пика
        result.append(Highlight(start=start, end=end, peak=float(p), score=round(val, 2),
                                chat_z=round(float(chat_z[p]), 2), audio_z=round(float(audio_z[p]), 2),
                                top_messages=top_msgs, jump_z=round(float(jump_z[lo:hi].max()), 2),
                                vis_z=round(float(vis_z[lo:hi].max()), 2),
                                clip_views=int(views[int(start):int(end) + 1].max()) if views.size else 0))
    if not result:
        log(f"  ничего не найдено выше порога {min_score} (попробуй --min-score поменьше)")
    return sorted(result, key=lambda h: h.start)
