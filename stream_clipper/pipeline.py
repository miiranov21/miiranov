"""Полный цикл: чат -> звук -> поиск моментов -> скачивание кусков -> вертикальные Shorts."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from . import daily, detect, paths, render
from .paths import parse_start  # noqa: F401  (используется в cli/watch через pipeline)
from .chat import ChatMessage, download_chat, load_chat_file


@dataclass
class Settings:
    out_dir: str = field(default_factory=lambda: paths.default_out_dir())
    work_dir: str = field(default_factory=lambda: paths.default_work_dir())
    top: int = 3              # клипов на каждый час стрима
    clip_pre: float = 20
    clip_post: float = 15
    chat_lag: int = 5
    min_score: float = 3.0
    audio: bool = True
    audio_weight: float = 0.6
    layout: str = "auto"      # auto = вебка сверху, если найдена, иначе blur
    facecam: tuple | None = None
    zoom: float = 1.0
    subs: bool | None = None  # None = включать сами, если установлен faster-whisper
    whisper_model: str = "small"
    language: str | None = None
    max_height: int = 1080
    dry_run: bool = False
    keep_raw: bool = False
    preset: str = "medium"
    caption: bool = True      # плашка с подписью к моменту
    game_view: str = "full"   # игра в кадре: full — целиком, wide — крупнее, center — только центр
    start_from: str | None = None  # с какого места стрима начать анализ: «1:30», «сейчас» или пусто — с начала
    credit: bool = False      # сразу вшивать подпись автора «Twitch | KaiCenat» (иначе — галочкой на нужных клипах)
    credit_pos: str = "bottom-left"  # bottom-left | top-left | top-right
    watermark_text: str = ""  # водяной знак текстом, например "@мой_канал"
    watermark_image: str = "" # водяной знак картинкой (PNG)
    watermark_pos: str = "moving"   # corner | center | moving
    watermark_opacity: float = 0.4
    hype_words: list = field(default_factory=lambda: list(detect.DEFAULT_HYPE))


def _fmt(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:d}h{s % 3600 // 60:02d}m{s % 60:02d}s"


def _overlaps(h, done: list[dict], thr: float = 0.5) -> bool:
    for d in done:
        inter = min(h.end, d["end"]) - max(h.start, d["start"])
        if inter > thr * min(h.end - h.start, d["end"] - d["start"]):
            return True
    return False


def write_report(folder: str, clips: list[dict], source: str, link_fn=None) -> None:
    lines = [f"# Хайлайты: {source}\n"]
    for i, c in enumerate(sorted(clips, key=lambda c: c["start"]), 1):
        lines.append(f"## {i}. {_fmt(c['start'])} – {_fmt(c['end'])}  (score {c['score']})")
        if link_fn:
            lines.append(f"- Twitch: {link_fn(c['start'])}")
        if c.get("file"):
            lines.append(f"- Файл: {os.path.basename(c['file'])}")
        lines.append(f"- чат z={c['chat_z']}, звук z={c['audio_z']}")
        if c.get("top_messages"):
            lines.append("- Что писал чат: " + " | ".join(c["top_messages"]))
        lines.append("")
    with open(os.path.join(folder, "highlights.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(folder, "highlights.json"), "w", encoding="utf-8") as f:
        json.dump(clips, f, ensure_ascii=False, indent=2)


def _make_short(segment: str, out: str, cfg: Settings, log, meta: dict | None = None) -> str:
    """Собирает вертикальный клип. Возвращает подпись (или '')."""
    meta = meta or {}
    layout, facecam = cfg.layout, cfg.facecam
    if layout == "auto":
        from .facecam import resolve
        try:
            facecam = cfg.facecam or resolve(meta.get("streamer", ""), segment, log=log)
        except Exception as e:
            log(f"    поиск вебки не удался: {e}")
            facecam = None
        layout = "facecam" if facecam else "blur"
        log(f"    вебка {'найдена — ставлю её сверху' if facecam else 'не найдена — игра на размытом фоне'}")
    base = os.path.splitext(out)[0]
    ass_files, transcript = [], ""
    use_subs = cfg.subs
    if use_subs is None:
        from .subtitles import available
        use_subs = available()
    if use_subs:
        log("    распознаю речь для субтитров...")
        try:
            transcript = render_subs(segment, base + ".ass", cfg)
            if transcript:
                ass_files.append(base + ".ass")
                log(f"    субтитры готовы ({len(transcript.split())} слов)")
            else:
                log("    субтитры: в клипе не нашлось речи (стример молчит или музыка заглушает)")
        except Exception as e:  # субтитры — не критично
            log(f"    субтитры не получились: {type(e).__name__}: {e}")
    elif cfg.subs is None:
        log("    субтитры выключены: не установлено распознавание речи (запусти install_subs.bat)")
    text = ""
    if cfg.caption:
        from .caption import _api_key, make_caption, streamer_quote
        center = float(cfg.clip_pre)  # пик момента — примерно через clip_pre секунд от начала клипа
        quote = None
        if transcript:
            from . import subtitles
            quote = streamer_quote(subtitles.LAST_WORDS, center)
        keep_text = meta.get("caption_text")  # перерезка клипа: надпись оставляем ту же
        frames = _moment_frames(segment, center, base) if _api_key() and not keep_text else []
        text = keep_text or make_caption(meta.get("streamer", ""), meta.get("title", ""), meta.get("top_messages", []),
                                         transcript, meta.get("lang", "en"), log=log, frames=frames, quote=quote)
        for p in frames:
            try:
                os.remove(p)
            except OSError:
                pass
        log(f"    подпись: {text}")
        ass_files.append(render.write_caption_ass(base + ".caption.ass", text,
                                                  render.caption_y(layout, cfg.zoom, game_view=cfg.game_view)))
    if cfg.credit and meta.get("credit_name"):
        # чей это стрим — платформа и ник автора (уважение к автору и правилам площадок)
        ass_files.insert(0, render.write_credit_ass(base + ".credit.ass", meta.get("platform", ""),
                                                    meta["credit_name"], cfg.credit_pos))
    if cfg.watermark_text.strip():
        # знак ставим под надписью-плашкой, чтобы не закрывал её
        ass_files.insert(len(ass_files) - (1 if text else 0),
                         render.write_watermark_ass(base + ".wm.ass", cfg.watermark_text.strip(),
                                                    cfg.watermark_pos, cfg.watermark_opacity))
    meta["transcript"] = transcript[:800]
    if transcript:
        from . import subtitles as _subs
        meta["words"] = [[round(a, 2), round(b, 2), w] for a, b, w in _subs.LAST_WORDS]
    if cfg.caption:
        from .caption import LAST_SCORE
        meta["ai_score"] = LAST_SCORE.get("value")
    render.render_vertical(segment, out, layout, facecam, cfg.zoom, ass_files, cfg.preset,
                           logo=cfg.watermark_image or None, logo_pos=cfg.watermark_pos,
                           logo_opacity=cfg.watermark_opacity, logo_with_text=bool(cfg.watermark_text.strip()),
                           game_view=cfg.game_view)
    for p in ass_files:
        try:
            os.remove(p)
        except OSError:
            pass
    return text


def _moment_frames(segment: str, center: float, base: str) -> list[str]:
    """3 кадра из момента (до, пик, после) — Claude по ним видит, что происходит на экране."""
    import subprocess
    out = []
    flags = 0x08000000 if os.name == "nt" else 0
    try:  # длина клипа — чтобы не просить кадры за его концом (короткие клипы)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", segment],
                           capture_output=True, text=True, creationflags=flags)
        dur = float(r.stdout.strip())
        if center > dur - 1:
            center = dur * 0.6
    except Exception:
        dur = None
    step = 3 if not dur or dur > 12 else max(0.5, dur / 5)
    for i, t in enumerate((center - step, center, center + step)):
        p = f"{base}.frame{i}.jpg"
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", segment,
                            "-frames:v", "1", "-vf", "scale=768:-2", "-q:v", "4", p],
                           capture_output=True, creationflags=flags)
        if r.returncode == 0 and os.path.exists(p):
            out.append(p)
    return out


def render_subs(segment: str, ass: str, cfg: Settings) -> str:
    from .subtitles import make_ass
    return make_ass(segment, ass, cfg.whisper_model, cfg.language)


def refresh_live(cfg: Settings, log=print) -> None:
    """Подхватываем настройки, изменённые в окне во время работы (клипов в час, длина клипа)."""
    try:
        with open(paths.live_settings_path(), encoding="utf-8") as f:
            live = json.load(f)
    except Exception:
        return
    changed = []
    top = live.get("top")
    if isinstance(top, int) and top > 0 and top != cfg.top:
        cfg.top = top
        changed.append(f"клипов за час: {top}")
    pre, post = live.get("pre"), live.get("post")
    if isinstance(pre, (int, float)) and isinstance(post, (int, float)) and pre > 0 and post > 0 \
            and (pre, post) != (cfg.clip_pre, cfg.clip_post):
        cfg.clip_pre, cfg.clip_post = float(pre), float(post)
        changed.append(f"длина клипа: {int(pre + post)} с")
    credit, cpos = live.get("credit"), live.get("credit_pos")
    if isinstance(credit, bool) and credit != cfg.credit:
        cfg.credit = credit
        changed.append("подпись автора: " + ("вкл" if credit else "выкл"))
    if cpos in render.CREDIT_POS and cpos != cfg.credit_pos:
        cfg.credit_pos = cpos
        changed.append("подпись автора перенесена")
    if changed:
        log("Новые настройки подхвачены: " + ", ".join(changed))


class MediaAnalysis:
    """Громкость и «резкость смены картинки» по секундам стрима, собираемые кусками по ходу работы."""
    CHUNK = 1800

    def __init__(self, url: str, work: str, log=print):
        self.url, self.work, self.log = url, work, log
        self.a = np.full(0, np.nan, dtype=np.float32)
        self.v = np.full(0, np.nan, dtype=np.float32)
        self.done_chunks: set = set()
        self.failed = 0
        self.announced = False

    def _grow(self, n: int):
        if n > self.a.size:
            self.a = np.concatenate([self.a, np.full(n - self.a.size, np.nan, dtype=np.float32)])
            self.v = np.concatenate([self.v, np.full(n - self.v.size, np.nan, dtype=np.float32)])

    def put(self, offset: int, audio, visual):
        for arr_name, data in (("a", audio), ("v", visual)):
            if data is None or not len(data):
                continue
            self._grow(offset + len(data))
            getattr(self, arr_name)[offset:offset + len(data)] = data

    def cover(self, lo: float, hi: float):
        """Убедиться, что для отрезка [lo, hi] звук и картинка посчитаны (качает недостающие куски)."""
        from . import twitch
        from .audio import loudness_per_second, scene_per_second
        if self.failed >= 3:
            return
        for c in range(int(max(0, lo)) // self.CHUNK, int(hi) // self.CHUNK + 1):
            s, e = c * self.CHUNK, min((c + 1) * self.CHUNK, int(hi))
            full = e == (c + 1) * self.CHUNK
            if (c, full) in self.done_chunks or e - s < 60:
                continue
            npz = os.path.join(self.work, f"media_{s}_{e}.npz")
            try:
                if os.path.exists(npz):
                    d = np.load(npz)
                    aud, vis = d["a"], d["v"]
                else:
                    if not self.announced:
                        self.log("  анализирую звук и картинку стрима (облегчённое видео, по кускам)...")
                        self.announced = True
                    f = twitch.download_analysis_section(self.url, s, e, os.path.join(self.work, f"media_{s}_{e}"))
                    aud, vis = loudness_per_second(f), scene_per_second(f)
                    os.remove(f)
                    if full:
                        np.savez(npz, a=aud, v=vis)
                self.put(s, aud, vis)
                self.done_chunks.add((c, full))
            except Exception as e:
                self.failed += 1
                self.log(f"  звук/картинка для {s // 60}–{e // 60} мин не получились ({e}) — режу по чату")

    def _filled(self, arr, n: int):
        if not np.isfinite(arr).any():
            return None
        out = np.full(n, np.nanmedian(arr), dtype=np.float32)
        m = min(n, arr.size)
        seg = arr[:m]
        out[:m] = np.where(np.isfinite(seg), seg, out[:m])
        return out

    def audio(self, n: int):
        return self._filled(self.a, int(n) + 1)

    def visual(self, n: int):
        v = self._filled(self.v, int(n) + 1)
        return v


def clip_budget(per_hour: int, seconds: float) -> int:
    """Сколько клипов положено на столько-то секунд стрима («клипов за час стрима»)."""
    import math
    return max(1, math.ceil(per_hour * max(seconds, 0) / 3600))


def _analyze(msgs: list[ChatMessage], duration: float, audio_db, cfg: Settings, done: list[dict], log,
             top: int | None = None, visual=None):
    log(f"Ищу моменты (длительность {_fmt(duration)}, сообщений {len(msgs)})...")
    hl = detect.find_highlights(
        msgs, int(duration), audio_db=audio_db, visual=visual, top=cfg.top if top is None else top, clip_pre=cfg.clip_pre, clip_post=cfg.clip_post,
        chat_lag=cfg.chat_lag, audio_weight=cfg.audio_weight, min_score=cfg.min_score,
        hype_words=cfg.hype_words, exclude=[(d["start"], d["end"]) for d in done], log=log)
    hl = [h for h in hl if not _overlaps(h, done)]
    for h in hl:
        log(f"  * {_fmt(h.start)} – {_fmt(h.end)}  score={h.score}  ({' | '.join(h.top_messages[:3])})")
    return hl


def _finish(cfg: Settings, new: list[dict], work: str, all_clips: list[dict], title: str, link_fn, log) -> None:
    write_report(work, all_clips, title, link_fn)  # служебный отчёт по стриму
    if cfg.dry_run:
        log(f"Найденные моменты (без нарезки): {os.path.join(work, 'highlights.md')}")
        return
    folder = daily.day_dir(cfg.out_dir)
    if new:
        z = daily.build_zip(folder)
        log(f"Архив дня обновлён: {z}")
    log(f"Отчёт за день: {daily.write_day_report(folder)}")


def process_vod(url: str, cfg: Settings, done: list[dict] | None = None, live: bool = False, log=print,
                on_clip=None, start_at=None, progress: dict | None = None, jump: bool = False) -> list[dict]:
    """Обрабатывает запись стрима (Twitch/YouTube). Клипы режутся ПО ХОДУ загрузки чата:
    скачали очередные 30 минут стрима — сразу нарезали лучшие моменты оттуда.
    done — уже нарезанные клипы (чтобы не повторяться); live=True — запись ещё идёт (эфир);
    on_clip(d) — вызывается сразу после каждого готового клипа."""
    import threading
    from . import twitch
    from .audio import loudness_per_second
    from .caption import detect_language
    from .chat import download_chat_part

    done = list(done or [])
    log(f"VOD {url}{'  (идёт эфир)' if live else ''}")
    info = twitch.get_info(url)
    yt = twitch.is_youtube(url)
    vid = (str(info.get("id") or "") if yt else twitch.vod_id(url)) or twitch.vod_id(url)
    work = os.path.join(cfg.work_dir, vid)
    os.makedirs(work, exist_ok=True)
    title = info.get("title") or vid
    channel = (info.get("uploader_id") or info.get("channel") or info.get("uploader") or "stream").lstrip("@")
    vod_duration = float(info.get("duration") or 0)
    log(f"▶ {channel}: начинаю работу{' (стрим идёт)' if live else ''} — «{title[:60]}»")
    link = (lambda s: f"https://youtu.be/{vid}?t={int(s)}") if yt else (lambda s: twitch.timestamp_link(url, s))

    # звук и картинка: качаем облегчённое видео кусками (по ходу) и считаем громкость + смены кадра.
    # Так моменты находятся даже когда чат молчит, и для идущих стримов тоже.
    media = MediaAnalysis(url, work, log) if cfg.audio else None
    old_npy = os.path.join(work, "loudness.npy")  # совместимость: звук, посчитанный старой версией
    if media and os.path.exists(old_npy):
        media.put(0, np.load(old_npy), None)

    cache = os.path.join(work, "chat.json")
    step = 1800  # режем после каждых 30 минут стрима
    new: list[dict] = []
    lang = cfg.language
    # с какого места стрима начинать анализ (выбирается в окне; «now» — с текущего момента)
    if start_at == "now":
        start_at = vod_duration or (_last_t(cache) or 0)
        log(f"  начинаю с текущего момента стрима: {_fmt(start_at)} — всё, что было раньше, пропускаю")
    start_at = float(start_at or 0)
    if start_at and progress is not None:
        progress["start_at"] = start_at
    if start_at and start_at != (progress or {}).get("announced"):
        log(f"  анализирую стрим с {_fmt(start_at)}")
    last = max(_last_t(cache) or 0, start_at)
    if last > 60 or done:
        log(f"  продолжаю с того места, где остановились: чат уже скачан до {_fmt(last)}, "
            f"готово клипов — {len(done)}")
    # с какой секунды стрима ещё не искали моменты (при повторном проходе — после уже нарезанного)
    boundary = 0.0 if not live else max([d["end"] for d in done], default=0.0) - cfg.clip_post - cfg.clip_pre
    boundary = max(0.0, boundary, start_at)
    if jump and start_at:
        # пользователь сам выбрал «начать с» — начинаем именно оттуда (готовые клипы всё равно не повторятся)
        boundary = start_at
        if done:
            log(f"  начинаю с {_fmt(start_at)}, как выбрано; уже готовые клипы ({len(done)}) не повторятся")
    from . import progress as prog
    stream_ts = info.get("release_timestamp") or info.get("timestamp")
    page_url = info.get("webpage_url") or url
    counted_clips = 0
    while True:
        refresh_live(cfg, log)
        stopped = False
        msgs, finished = download_chat_part(url, cache, None if cfg.dry_run else last + step, log,
                                            start_from=start_at)
        covered = last = msgs[-1].t if msgs else 0
        if finished and not live:
            covered = max(covered, vod_duration)
        duration = max(covered, 1)
        if media:
            media.cover(max(start_at, boundary - 60), duration)
        if not lang and len(msgs) > 200 or (finished and not lang):
            lang = detect_language([m.text for m in msgs], title)
        skip = done + new
        if boundary > 0:
            # уже разобранную часть стрима не трогаем — смотрим только новый кусок
            skip = skip + [{"start": 0.0, "end": boundary}]
        tail = cfg.clip_post + cfg.chat_lag + 60
        if not (finished and not live):
            # хвост ещё не «отреагирован» чатом — возьмём на следующем шаге
            skip = skip + [{"start": max(0.0, duration - tail), "end": duration + 10 ** 6}]
        next_boundary = max(boundary, duration - tail)
        counted = [d for d in done + new if d.get("start", 0) >= start_at - 1]
        allowed = clip_budget(cfg.top, duration - start_at) - len(counted)
        if allowed > 0:
            hl = _analyze(msgs, duration, media.audio(duration) if media else None, cfg, skip, log, top=allowed,
                          visual=media.visual(duration) if media else None)
            for i, h in enumerate(hl, 1):
                if paths.stop_requested():
                    stopped = True
                    break
                refresh_live(cfg, log)
                d = dict(h.to_dict(), vod_url=url, vod_title=title, link=link(h.start))
                d["has_media"] = bool(media and np.isfinite(media.v).any())
                if not cfg.dry_run:
                    name = f"{vid}_{_fmt(h.start)}"
                    log(f"  [{i}/{len(hl)}] качаю кусок {_fmt(h.start)}...")
                    try:
                        seg = twitch.download_section(url, h.start, h.end, os.path.join(work, name + "_raw"),
                                                      cfg.max_height)
                        tmp = os.path.join(work, name + ".mp4")
                        meta = {"streamer": channel, "title": title, "top_messages": h.top_messages,
                                "lang": lang or "en", "platform": "YouTube" if yt else "Twitch",
                                "credit_name": (info.get("uploader") or channel)}
                        d["caption"] = _make_short(seg, tmp, cfg, log, meta)
                        d["transcript"], d["lang"] = meta.get("transcript", ""), lang or "en"
                        d["rating"] = _final_rating(d, meta)
                        if not cfg.keep_raw:
                            os.remove(seg)
                        d["words"] = meta.get("words") or []
                        d["platform"], d["credit_name"] = meta["platform"], meta["credit_name"]
                        d["credit_burned"] = bool(cfg.credit)
                        d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, channel)
                        _quick_policy(d, log)
                        log(f"    готово -> {d['file']}")
                        log(f"✅ {channel}: клип {_clip_no(d['file'])} готов — «{d.get('caption') or ''}»")
                    except Exception as e:
                        log(f"    ошибка: {e}")
                        daily.log_event(cfg.out_dir, f"{channel}: не удалось сделать клип {_fmt(h.start)} — {e}")
                        continue
                new.append(d)
                if on_clip:
                    on_clip(d)
        if not cfg.dry_run:
            # запоминаем, какой кусок стрима разобран — видно во вкладке «Стримы»
            upto = max(duration, vod_duration) if finished and not live else next_boundary
            prog.record(vid, boundary, boundary if stopped else upto, channel=channel,
                        platform="YouTube" if yt else "Twitch", title=title, url=page_url, stream_ts=stream_ts,
                        duration=max(vod_duration, covered), live=live, clips=len(new) - counted_clips)
            counted_clips = len(new)
        boundary = next_boundary
        if finished or cfg.dry_run:
            break
        if paths.stop_requested():
            log("  останавливаюсь по просьбе — продолжу с этого места при следующем запуске")
            break

    _finish(cfg, new, work, done + new, title, link, log)
    return new


def recut(job: dict, cfg: Settings, log=print) -> dict:
    """Перерезать готовый клип с новыми границами (удлинить/сдвинуть): снова качаем кусок записи стрима
    и собираем клип теми же настройками, с той же надписью. job: url, start, end, out, meta."""
    from . import twitch
    work = os.path.join(cfg.work_dir, "recut")
    os.makedirs(work, exist_ok=True)
    start, end = max(0.0, float(job["start"])), float(job["end"])
    log(f"Качаю кусок стрима {_fmt(start)}–{_fmt(end)}...")
    # своё имя на каждую задачу: иначе «уже скачанный» кусок от ДРУГОГО клипа подхватывался вместо нужного
    import glob
    import time as _time
    for old in glob.glob(os.path.join(work, "recut_raw*")):  # хвосты старой версии с общим именем файла
        try:
            os.remove(old)
        except OSError:
            pass
    base = os.path.join(work, f"raw_{int(_time.time() * 1000)}_{int(start)}_{int(end)}")
    seg = twitch.download_section(job["url"], start, end, base, cfg.max_height)
    meta = dict(job.get("meta") or {})
    cfg.clip_pre = min(cfg.clip_pre, max(1.0, (end - start) * 0.57))
    log("Собираю клип...")
    try:
        _make_short(seg, job["out"], cfg, log, meta)
    finally:
        for f in glob.glob(glob.escape(base) + "*"):
            try:
                os.remove(f)
            except OSError:
                pass
    return {"file": job["out"], "words": meta.get("words") or [], "transcript": meta.get("transcript", ""),
            "start": start, "end": end}


def _quick_policy(d: dict, log=print) -> None:
    """Быстрая проверка речи на мат/оскорбления/музыку сразу после нарезки (без Claude, мгновенно)."""
    try:
        from . import policy
        issues = policy.check_words(d.get("words") or []) + policy.check_nudity(d["file"], log)
        policy.save_result(d["file"], {"issues": issues, "visual": False, "checked": __import__("time").time(),
                                       "nudity_v": 2,
                                       "note": "" if d.get("words") else "речи нет или субтитры выключены",
                                       "words": d.get("words") or []})
        if issues:
            kinds = {}
            for i in issues:
                kinds[i["title"]] = kinds.get(i["title"], 0) + 1
            log(f"⚠ клип {_clip_no(d['file'])}: возможные нарушения правил — "
                + ", ".join(f"{k} ×{v}" for k, v in kinds.items()) + " (вкладка «Клипы» → «Исправить нарушение»)")
    except Exception as e:
        log(f"    проверка правил не удалась: {e}")


def _final_rating(d: dict, meta: dict) -> float:
    """Сохраняем «сырую» яркость и оценку Claude отдельно — итог считается в окне, в сравнении со всеми клипами."""
    from .caption import rate_clip
    ai = meta.get("ai_score")
    if isinstance(ai, (int, float)) and 0 < ai <= 10:
        d["ai_score"] = float(ai)
    return rate_clip(d, meta.get("transcript", ""))


def _clip_no(path: str) -> str:
    """Номер клипа из имени файла «03_1ч12м05с.mp4» → «3»."""
    base = os.path.basename(path or "")
    num = base.split("_")[0]
    return str(int(num)) if num.isdigit() else "?"


def _last_t(cache: str) -> float | None:
    try:
        m = load_chat_file(cache)
        return m[-1].t if m else None
    except Exception:
        return None


def process_local(video: str, chat_path: str, cfg: Settings, log=print) -> list[dict]:
    """Обрабатывает уже скачанное видео + файл чата (наш JSON или TwitchDownloader)."""
    from .audio import loudness_per_second

    name = os.path.splitext(os.path.basename(video))[0]
    work = os.path.join(cfg.work_dir, name)
    os.makedirs(work, exist_ok=True)
    msgs = load_chat_file(chat_path)
    audio_db = None
    if cfg.audio:
        log("Анализирую громкость...")
        audio_db = loudness_per_second(video)
        from .audio import scene_per_second
        visual_local = scene_per_second(video)
    duration = len(audio_db) if audio_db is not None else (msgs[-1].t if msgs else 0)
    hl = _analyze(msgs, duration, audio_db, cfg, [], log, top=clip_budget(cfg.top, duration),
                  visual=visual_local if cfg.audio else None)
    from .caption import detect_language
    lang = cfg.language or detect_language([m.text for m in msgs], name)
    clips = []
    for i, h in enumerate(hl, 1):
        d = dict(h.to_dict(), vod_title=name)
        d["has_media"] = bool(cfg.audio)
        if not cfg.dry_run:
            base = f"{name}_{_fmt(h.start)}"
            seg = render.cut_segment(video, h.start, h.end, os.path.join(work, base + "_raw.mp4"))
            tmp = os.path.join(work, base + ".mp4")
            meta = {"streamer": name, "title": name, "top_messages": h.top_messages, "lang": lang}
            d["caption"] = _make_short(seg, tmp, cfg, log, meta)
            d["transcript"], d["lang"] = meta.get("transcript", ""), lang
            d["rating"] = _final_rating(d, meta)
            if not cfg.keep_raw:
                os.remove(seg)
            d["words"] = meta.get("words") or []
            d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, name)
            _quick_policy(d, log)
            log(f"  [{i}/{len(hl)}] готово -> {d['file']}")
            log(f"✅ {name}: клип {_clip_no(d['file'])} готов — «{d.get('caption') or ''}»")
        clips.append(d)
    _finish(cfg, clips, work, clips, name, None, log)
    return clips
