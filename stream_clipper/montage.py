"""Монтаж клипа под площадку по заданию «Доктора шортсов» (или автопилота).

Приёмы (edits) применяются в постоянном порядке:
  trim → cut_silence → speed → crop_out → blur → zoom → subtitles → hook → credit → progress_bar →
  звук (mute / bleep / bleep_profanity / replace_audio) → loudness → loop_end → cover
Время в заданиях — по исходному клипу (до монтажа). После вырезания пауз и ускорений оно само
пересчитывается («карта времени»), поэтому зум или писк попадают в нужный момент.
Неизвестные приёмы пропускаются и записываются в журнал — ничего не ломается.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time

ORDER = ["trim", "cut_silence", "speed", "layout", "crop_out", "blur", "zoom", "subtitles", "hook", "credit",
         "progress_bar", "mute", "bleep", "bleep_profanity", "replace_audio", "loudness", "loop_end", "cover"]
AUDIO = ("mute", "bleep", "bleep_profanity", "replace_audio")
W, H = 1080, 1920
FLAGS = 0x08000000 if os.name == "nt" else 0


def _run(cmd: list, cwd: str | None = None) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, creationflags=FLAGS)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[-700:])
    return r.stderr


def duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=FLAGS)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _enc(final: bool) -> list:
    """Промежуточные шаги — быстро и почти без потерь; финал — по требованиям площадок (H.264 High, AAC 192k)."""
    if final:
        return ["-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "18", "-maxrate", "12M",
                "-bufsize", "24M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart"]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
            "-ar", "48000"]


# ---------- карта времени: исходный клип → текущая версия ----------
class TimeMap:
    def __init__(self, dur: float):
        self.pieces = [(0.0, dur, 0.0, dur)]  # (исх. от, исх. до, тек. от, тек. до)

    def map(self, t: float) -> float | None:
        for s0, s1, c0, c1 in self.pieces:
            if s0 <= t <= s1:
                return c0 + (t - s0) * ((c1 - c0) / (s1 - s0) if s1 > s0 else 0)
        return None

    def map_span(self, a: float, b: float) -> tuple[float, float] | None:
        out = []
        for s0, s1, c0, c1 in self.pieces:
            lo, hi = max(a, s0), min(b, s1)
            if hi > lo:
                k = (c1 - c0) / (s1 - s0) if s1 > s0 else 0
                out.append((c0 + (lo - s0) * k, c0 + (hi - s0) * k))
        if not out:
            return None
        return min(x[0] for x in out), max(x[1] for x in out)

    def apply(self, keep: list[tuple[float, float, float]]):
        """keep — куски ТЕКУЩЕЙ версии, которые остаются: (от, до, скорость). Склеиваются подряд."""
        new, pos = [], 0.0
        for k0, k1, rate in keep:
            for s0, s1, c0, c1 in self.pieces:
                lo, hi = max(k0, c0), min(k1, c1)
                if hi <= lo or c1 <= c0:
                    continue
                o0 = s0 + (lo - c0) * (s1 - s0) / (c1 - c0)
                o1 = s0 + (hi - c0) * (s1 - s0) / (c1 - c0)
                n0 = pos + (lo - k0) / rate
                new.append((o0, o1, n0, n0 + (hi - lo) / rate))
            pos += (k1 - k0) / rate
        self.pieces = new or self.pieces


# ---------- приёмы ----------
def _trim(cur, out, op, tm, dur):
    a, b = max(0.0, float(op.get("cut_start") or 0)), max(0.0, float(op.get("cut_end") or 0))
    if dur - a - b < 1:
        raise ValueError("после обрезки клип короче секунды")
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-ss", f"{a:.3f}", "-to", f"{dur - b:.3f}", *_enc(False), out])
    tm.apply([(a, dur - b, 1.0)])


def silences(path: str, min_gap: float = 0.7, noise: str = "-35dB") -> list[tuple[float, float]]:
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", f"silencedetect=noise={noise}:d={min_gap}",
                          "-f", "null", "-"], capture_output=True, text=True, creationflags=FLAGS).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends + [duration(path)] * (len(starts) - len(ends))))


def _keep_render(cur, out, keep):
    expr = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b, _ in keep)
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-vf", f"select='{expr}',setpts=N/FRAME_RATE/TB",
          "-af", f"aselect='{expr}',asetpts=N/SR/TB", *_enc(False), out])


def _cut_silence(cur, out, op, tm, dur):
    gap = float(op.get("min_gap") or 0.7)
    pad = 0.15  # чуть тишины по краям — чтобы слова не обрубались
    cuts = [(s + pad, e - pad) for s, e in silences(cur, gap) if e - s - 2 * pad > 0.2]
    if not cuts:
        raise _Skip("пауз длиннее %.1f с нет" % gap)
    keep, pos = [], 0.0
    for s, e in cuts:
        if s > pos:
            keep.append((pos, s, 1.0))
        pos = max(pos, e)
    if pos < dur:
        keep.append((pos, dur, 1.0))
    _keep_render(cur, out, keep)
    tm.apply(keep)


def _atempo(rate: float) -> str:
    parts = []
    while rate > 2.0:
        parts.append("atempo=2.0")
        rate /= 2.0
    while rate < 0.5:
        parts.append("atempo=0.5")
        rate /= 0.5
    parts.append(f"atempo={rate:.4f}")
    return ",".join(parts)


def _speed(cur, out, op, tm, dur):
    rate = max(0.5, min(3.0, float(op.get("rate") or 1.25)))
    span = tm.map_span(float(op.get("t0", 0)), float(op.get("t1", dur)))
    if not span or span[1] - span[0] < 0.3:
        raise _Skip("отрезок для ускорения вырезан раньше")
    a, b = span
    parts = [(0.0, a, 1.0), (a, b, rate), (b, dur, 1.0)]
    parts = [p for p in parts if p[1] - p[0] > 0.05]
    v, au, labels = [], [], ""
    for i, (s, e, r) in enumerate(parts):
        v.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=(PTS-STARTPTS)/{r}[v{i}]")
        au.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,{_atempo(r)}[a{i}]")
        labels += f"[v{i}][a{i}]"
    graph = ";".join(v + au) + f";{labels}concat=n={len(parts)}:v=1:a=1[v][a]"
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
          *_enc(False), out])
    tm.apply(parts)


def _px_box(box) -> tuple[int, int, int, int]:
    x, y, w, h = (max(0.0, min(1.0, float(v))) for v in box)
    X, Y = int(x * W), int(y * H)
    return max(1, X), max(1, Y), max(8, min(W - X - 2, int(w * W))), max(8, min(H - Y - 2, int(h * H)))


def _crop_out(cur, out, op, tm, dur):
    """Убрать чужую плашку / алерт доната / чат: область «затирается» по соседним пикселям."""
    if not op.get("box"):
        raise _Skip("не указана область")
    x, y, w, h = _px_box(op["box"])
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-vf", f"delogo=x={x}:y={y}:w={w}:h={h}", *_enc(False), out])


def _blur(cur, out, op, tm, dur):
    from . import policy
    span = tm.map_span(float(op.get("t0", 0)), float(op.get("t1", dur)))
    if not span:
        raise _Skip("отрезок вырезан раньше")
    issue = policy._issue("manual", span[0], span[1], "монтаж", op.get("box"), source="video")
    policy.fix_clip(cur, out, [issue], subs_burned=False)


def _zoom(cur, out, ops, tm, dur):
    """Зум-панчи: быстрый наезд (×1.1–1.3) на ударном моменте и плавный возврат."""
    terms = []
    for op in ops:
        t = tm.map(float(op.get("t", 0)))
        if t is None:
            continue
        s = max(1.02, min(1.5, float(op.get("scale") or 1.2)))
        d = max(0.2, min(3.0, float(op.get("dur") or 0.6)))
        a, b = t, t + d
        ramp = 0.12
        # 0 → 1 за ramp секунд, держим, обратно за ramp секунд
        env = (f"between(t,{a:.3f},{b:.3f})*min(1,min((t-{a:.3f})/{ramp},({b:.3f}-t)/{ramp}))")
        terms.append(f"{s - 1:.3f}*{env}")
    if not terms:
        raise _Skip("моменты для зума вырезаны раньше")
    z = "1+" + "+".join(terms)
    vf = (f"scale=w='trunc(iw*({z})/2)*2':h='trunc(ih*({z})/2)*2':eval=frame,"
          f"crop={W}:{H}:'(iw-{W})/2':'(ih-{H})/2'")
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-vf", vf, *_enc(False), out])


ASS_HEAD = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
            "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n{styles}\n\n[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")


def _ts(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _burn_ass(cur, out, ass_text: str):
    work = os.path.dirname(os.path.abspath(out))
    name = f"m_{int(time.time() * 1000)}.ass"
    with open(os.path.join(work, name), "w", encoding="utf-8") as f:
        f.write(ass_text)
    try:
        _run(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(cur), "-vf", f"ass={name}", *_enc(False),
              os.path.abspath(out)], cwd=work)
    finally:
        try:
            os.remove(os.path.join(work, name))
        except OSError:
            pass


def _words_now(cur, words, tm, log):
    """Слова с временем в ТЕКУЩЕЙ версии: из сохранённых (через карту времени) или распознаём заново."""
    out = []
    for w in words or []:
        try:
            a, b = tm.map(float(w[0])), tm.map(float(w[1]))
        except (TypeError, ValueError, IndexError):
            continue
        if a is not None and b is not None and b > a:
            out.append((a, b, str(w[2]).strip()))
    if out:
        return out
    try:
        from . import policy, subtitles
        if subtitles.available():
            log("распознаю речь для субтитров...")
            return [(a, b, str(t).strip()) for a, b, t in policy.transcribe_words(cur)]
    except Exception:
        pass
    return []


def _subtitles(cur, out, op, tm, dur, words, log):
    """Пословные субтитры: караоке (текущее слово подсвечено) или обычные; по центру чуть ниже середины."""
    from .policy import censor_text
    ws = _words_now(cur, words, tm, log)
    if not ws:
        raise _Skip("нет распознанной речи")
    y = 1350 if op.get("pos") == "lower_center" else 1150  # не в нижних 20% кадра
    karaoke = op.get("style", "karaoke") != "plain"
    styles = ("Style: Sub,Arial,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,5,90,90,0,1")
    lines, curl = [], []
    for w in ws:
        if curl and (len(curl) >= 3 or w[0] - curl[-1][1] > 0.6):
            lines.append(curl)
            curl = []
        curl.append(w)
    if curl:
        lines.append(curl)
    ev = []
    for li, ln in enumerate(lines):
        end_line = min(ln[-1][1] + 0.15, lines[li + 1][0][0]) if li + 1 < len(lines) else ln[-1][1] + 0.3
        texts = [censor_text(w[2]).upper().replace("{", "(").replace("}", ")") for w in ln]
        if not karaoke:
            ev.append(f"Dialogue: 0,{_ts(ln[0][0])},{_ts(end_line)},Sub,,0,0,0,,{{\\an5\\pos(540,{y})}}{' '.join(texts)}")
            continue
        for wi, w in enumerate(ln):
            a = w[0]
            b = ln[wi + 1][0] if wi + 1 < len(ln) else end_line
            parts = [("{\\c&H0000E5FF&}" + t + "{\\c&H00FFFFFF&}") if j == wi else t for j, t in enumerate(texts)]
            ev.append(f"Dialogue: 0,{_ts(a)},{_ts(b)},Sub,,0,0,0,,{{\\an5\\pos(540,{y})}}{' '.join(parts)}")
    _burn_ass(cur, out, ASS_HEAD.format(styles=styles) + "\n".join(ev) + "\n")


def _hook(cur, out, op, tm, dur):
    """Хук-текст в первые секунды: верхняя треть кадра, до 6 слов ЗАГЛАВНЫМИ; плашка или обводка."""
    text = (op.get("text") or "").strip()
    if not text:
        raise _Skip("нет текста хука")
    text = " ".join(text.upper().split()[:8]).replace("{", "(").replace("}", ")")
    secs = max(1.0, min(10.0, float(op.get("seconds") or 3)))
    if op.get("style") == "outline":
        style = "Style: Hook,Arial,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,3,8,80,80,0,1"
    else:
        style = "Style: Hook,Arial,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H28000000,-1,0,0,0,100,100,0,0,3,18,0,8,80,80,0,1"
    ev = f"Dialogue: 2,{_ts(0)},{_ts(secs)},Hook,,0,0,0,,{{\\an8\\pos(540,300)\\fad(0,250)}}{text}"
    _burn_ass(cur, out, ASS_HEAD.format(styles=style) + ev + "\n")


def _credit(cur, out, op, tm, dur, clip):
    from . import credit, render
    work = os.path.dirname(os.path.abspath(out))
    name = f"m_{int(time.time() * 1000)}_credit.ass"
    render.write_credit_ass(os.path.join(work, name), credit.platform_of(clip or {}), credit.author_of(clip or {}),
                            op.get("pos") or "top-left", text=op.get("text") or None)
    try:
        _run(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(cur), "-vf", f"ass={name}", *_enc(False),
              os.path.abspath(out)], cwd=work)
    finally:
        os.remove(os.path.join(work, name))


def _progress_bar(cur, out, op, tm, dur):
    """Полоска прогресса сверху: растёт от 0 до конца клипа."""
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-f", "lavfi", "-i", f"color=c=0xFFD400:s={W}x10:r=30",
          "-filter_complex", f"[0:v][1:v]overlay=x='-w+w*t/{dur:.3f}':y=0:shortest=1[v]",
          "-map", "[v]", "-map", "0:a?", *_enc(False), out])


def _audio(cur, out, ops, tm, dur, words, log):
    """Звук за один проход: заглушить, запикать (отрезки или весь мат), заменить звуком «свуш» или тишиной."""
    from . import policy
    silent, bleeps, whoosh = [], [], []
    for op in ops:
        t = op["type"]
        if t == "bleep_profanity":
            for i in policy.check_words([(a, b, w) for a, b, w in _words_now(cur, words, tm, log)]):
                if i["kind"] in ("profanity", "slur"):
                    bleeps.append((i["t0"], i["t1"]))
            continue
        span = tm.map_span(float(op.get("t0", 0)), float(op.get("t1", 0)))
        if not span:
            continue
        if t == "bleep":
            bleeps.append(span)
        elif t == "mute":
            silent.append(span)
        elif t == "replace_audio":
            silent.append(span)
            if op.get("sfx") == "whoosh":
                whoosh.append(span[0])
    if not (silent or bleeps or whoosh):
        raise _Skip("нечего менять в звуке (мата не найдено)")
    between = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in silent + bleeps) or "0"
    graph = f"[0:a]volume=0:enable='{between}'[base]"
    mix, n = ["[base]"], 1
    if bleeps:
        on = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in bleeps)
        graph += f";sine=frequency=1000:sample_rate=48000,volume=0.35,volume=0:enable='not({on})'[bl]"
        mix.append("[bl]")
        n += 1
    for k, t0 in enumerate(whoosh):  # «свуш» — сгенерированный шум, без авторских прав
        ms = int(t0 * 1000)
        graph += (f";anoisesrc=d=0.45:c=pink:a=0.6:r=48000,highpass=f=400,lowpass=f=6000,"
                  f"afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.25,adelay={ms}|{ms}[w{k}]")
        mix.append(f"[w{k}]")
        n += 1
    graph += f";{''.join(mix)}amix=inputs={n}:duration=first:normalize=0[a]"
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-filter_complex", graph, "-map", "0:v", "-map", "[a]",
          "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", out])


def _loudness(cur, out, op, tm, dur):
    lufs = max(-24.0, min(-9.0, float(op.get("lufs") or -14)))
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11", "-c:v", "copy",
          "-c:a", "aac", "-b:a", "256k", "-ar", "48000", out])


def _loop_end(cur, out, op, tm, dur):
    """Петля: последние доли секунды плавно переходят в первый кадр — видео хочется смотреть по кругу."""
    x = max(0.1, min(1.0, float(op.get("crossfade") or 0.3)))
    graph = (f"[0:v]split[m][f];[f]trim=0:0.05,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={x}[first];"
             f"[m][first]xfade=transition=fade:duration={x}:offset={max(0.1, dur - x):.3f}[v];"
             f"[0:a]afade=t=out:st={max(0.0, dur - x):.3f}:d={x}[a]")
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
          *_enc(False), out])


def _cover(cur, op, tm, dur, cover_path):
    """Обложка: кадр на пике эмоции + 2–4 слова."""
    t = tm.map(float(op.get("t", 0))) or 0.0
    text = (op.get("text") or "").strip().upper().replace("{", "(").replace("}", ")")
    work = os.path.dirname(os.path.abspath(cover_path))
    name = f"m_{int(time.time() * 1000)}_cover.ass"
    style = "Style: C,Arial,110,&H00FFFFFF,&H00FFFFFF,&H00000000,&H50000000,-1,0,0,0,100,100,0,0,3,20,0,5,60,60,0,1"
    with open(os.path.join(work, name), "w", encoding="utf-8") as f:
        f.write(ASS_HEAD.format(styles=style) + (f"Dialogue: 0,0:00:00.00,0:00:10.00,C,,0,0,0,,{{\\an5\\pos(540,700)}}{text}\n"
                                                 if text else ""))
    try:
        _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{min(t, max(0.0, dur - 0.1)):.2f}", "-i", os.path.abspath(cur),
              "-frames:v", "1", "-vf", f"ass={name}", "-q:v", "3", os.path.abspath(cover_path)], cwd=work)
    finally:
        os.remove(os.path.join(work, name))
    return t


class _Skip(Exception):
    pass


def render_plan(src: str, out: str, ops: list, words: list | None = None, clip: dict | None = None,
                log=print) -> dict:
    """Монтаж по списку приёмов. Возвращает {"applied": [...], "skipped": [...], "cover": путь или None, ...}."""
    work = os.path.join(os.path.dirname(os.path.abspath(out)), f"_m_{int(time.time() * 1000)}")
    os.makedirs(work, exist_ok=True)
    applied, skipped = [], []
    known = [o for o in ops if isinstance(o, dict) and o.get("type") in ORDER]
    for o in ops:
        if not isinstance(o, dict) or o.get("type") not in ORDER:
            skipped.append({"type": (o or {}).get("type") if isinstance(o, dict) else str(o),
                            "why": "неизвестный приём — пропущен"})
            log(f"монтаж: приём «{(o or {}).get('type') if isinstance(o, dict) else o}» неизвестен — пропускаю")
    known.sort(key=lambda o: ORDER.index(o["type"]))
    cur = src
    tm = TimeMap(duration(src))
    step = 0
    cover = None
    cover_t = None

    def nxt():
        nonlocal step
        step += 1
        return os.path.join(work, f"s{step}.mp4")

    i = 0
    while i < len(known):
        op = known[i]
        t = op["type"]
        group = [op]
        if t in ("zoom",) + AUDIO:  # все зумы и все звуковые правки — одним проходом
            kinds = ("zoom",) if t == "zoom" else AUDIO
            while i + 1 < len(known) and known[i + 1]["type"] in kinds:
                i += 1
                group.append(known[i])
        i += 1
        dur = duration(cur)
        dst = nxt()
        try:
            if t == "trim":
                _trim(cur, dst, op, tm, dur)
            elif t == "cut_silence":
                _cut_silence(cur, dst, op, tm, dur)
            elif t == "speed":
                _speed(cur, dst, op, tm, dur)
            elif t == "layout":
                raise _Skip("компоновку меняет только перенарезка из записи стрима (будет позже)")
            elif t == "crop_out":
                _crop_out(cur, dst, op, tm, dur)
            elif t == "blur":
                _blur(cur, dst, op, tm, dur)
            elif t == "zoom":
                _zoom(cur, dst, group, tm, dur)
            elif t == "subtitles":
                _subtitles(cur, dst, op, tm, dur, words, log)
            elif t == "hook":
                _hook(cur, dst, op, tm, dur)
            elif t == "credit":
                _credit(cur, dst, op, tm, dur, clip)
            elif t == "progress_bar":
                if op.get("on", True) is False:
                    raise _Skip("выключено")
                _progress_bar(cur, dst, op, tm, dur)
            elif t in AUDIO:
                _audio(cur, dst, group, tm, dur, words, log)
            elif t == "loudness":
                _loudness(cur, dst, op, tm, dur)
            elif t == "loop_end":
                _loop_end(cur, dst, op, tm, dur)
            elif t == "cover":
                cover_t = _cover(cur, op, tm, dur, os.path.splitext(out)[0] + "_cover.jpg")
                cover = os.path.splitext(out)[0] + "_cover.jpg"
                applied.append(dict(op))
                continue
            for g in group:
                applied.append(dict(g))
            cur = dst
        except _Skip as e:
            for g in group:
                skipped.append({"type": g["type"], "why": str(e)})
            log(f"монтаж: «{t}» пропущен — {e}")
        except Exception as e:
            for g in group:
                skipped.append({"type": g["type"], "why": f"ошибка: {e}"[:300]})
            log(f"монтаж: «{t}» не получился — {e}")
    # финальный экспорт по требованиям площадок
    _run(["ffmpeg", "-y", "-v", "error", "-i", cur, *_enc(True), os.path.abspath(out)])
    shutil.rmtree(work, ignore_errors=True)
    return {"applied": applied, "skipped": skipped, "cover": cover, "cover_t": cover_t, "duration": duration(out)}
