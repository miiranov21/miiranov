"""Полный цикл: чат -> звук -> поиск моментов -> скачивание кусков -> вертикальные Shorts."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from . import daily, detect, paths, render
from .chat import ChatMessage, download_chat, load_chat_file


@dataclass
class Settings:
    out_dir: str = field(default_factory=lambda: paths.default_out_dir())
    work_dir: str = field(default_factory=lambda: paths.default_work_dir())
    top: int = 10
    clip_pre: float = 20
    clip_post: float = 15
    chat_lag: int = 5
    min_score: float = 3.0
    audio: bool = True
    audio_weight: float = 0.6
    layout: str = "blur"
    facecam: tuple | None = None
    zoom: float = 1.0
    subs: bool = False
    whisper_model: str = "small"
    language: str | None = None
    max_height: int = 1080
    dry_run: bool = False
    keep_raw: bool = False
    preset: str = "medium"
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


def _make_short(segment: str, out: str, cfg: Settings, log) -> None:
    ass = None
    if cfg.subs:
        ass = os.path.splitext(out)[0] + ".ass"
        try:
            if not render_subs(segment, ass, cfg):
                ass = None
        except Exception as e:  # субтитры — не критично
            log(f"    субтитры не получились: {e}")
            ass = None
    render.render_vertical(segment, out, cfg.layout, cfg.facecam, cfg.zoom, ass, cfg.preset)


def render_subs(segment: str, ass: str, cfg: Settings) -> bool:
    from .subtitles import make_ass
    return make_ass(segment, ass, cfg.whisper_model, cfg.language)


def _analyze(msgs: list[ChatMessage], duration: float, audio_db, cfg: Settings, done: list[dict], log):
    log(f"Ищу моменты (длительность {_fmt(duration)}, сообщений {len(msgs)})...")
    hl = detect.find_highlights(
        msgs, int(duration), audio_db=audio_db, top=cfg.top, clip_pre=cfg.clip_pre, clip_post=cfg.clip_post,
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


def process_vod(url: str, cfg: Settings, done: list[dict] | None = None, live: bool = False, log=print) -> list[dict]:
    """Обрабатывает Twitch VOD. done — уже нарезанные клипы (чтобы не повторяться).
    live=True — запись ещё идёт (стрим в эфире): докачиваем чат и не трогаем последние минуты."""
    from . import twitch
    from .audio import loudness_per_second

    done = list(done or [])
    log(f"VOD {url}{'  (идёт эфир)' if live else ''}")
    info = twitch.get_info(url)
    yt = twitch.is_youtube(url)
    vid = str(info.get("id") or "") if yt else twitch.vod_id(url)
    vid = vid or twitch.vod_id(url)
    work = os.path.join(cfg.work_dir, vid)
    os.makedirs(work, exist_ok=True)
    title = info.get("title") or vid
    channel = (info.get("uploader_id") or info.get("channel") or info.get("uploader") or "stream").lstrip("@")
    msgs = download_chat(url, os.path.join(work, "chat.json"), refresh=live, log=log)
    duration = float(info.get("duration") or 0) or (msgs[-1].t if msgs else 0)
    if live and msgs:
        duration = max(duration, msgs[-1].t)

    audio_db = None
    if cfg.audio and not live:
        npy = os.path.join(work, "loudness.npy")
        if os.path.exists(npy):
            audio_db = np.load(npy)
        else:
            log("  качаю звук для анализа громкости (можно отключить --no-audio)...")
            a = twitch.download_audio(url, os.path.join(work, "audio"))
            audio_db = loudness_per_second(a)
            np.save(npy, audio_db)
            os.remove(a)

    skip = list(done)
    if live:
        # Последние минуты эфира ещё не «отреагированы» чатом и могут отсутствовать в записи —
        # их возьмём на следующем проходе.
        tail = cfg.clip_post + cfg.chat_lag + 60
        skip.append({"start": max(0.0, duration - tail), "end": duration + tail})
    hl = _analyze(msgs, duration, audio_db, cfg, skip, log)
    new = []
    if yt:
        link = lambda s: f"https://youtu.be/{vid}?t={int(s)}"
    else:
        link = lambda s: twitch.timestamp_link(url, s)
    for i, h in enumerate(hl, 1):
        d = dict(h.to_dict(), vod_url=url, vod_title=title, link=link(h.start))
        if not cfg.dry_run:
            name = f"{vid}_{_fmt(h.start)}"
            log(f"  [{i}/{len(hl)}] качаю кусок {_fmt(h.start)}...")
            try:
                seg = twitch.download_section(url, h.start, h.end, os.path.join(work, name + "_raw"), cfg.max_height)
                tmp = os.path.join(work, name + ".mp4")
                _make_short(seg, tmp, cfg, log)
                if not cfg.keep_raw:
                    os.remove(seg)
                d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, channel)
                log(f"    готово -> {d['file']}")
            except Exception as e:
                log(f"    ошибка: {e}")
                daily.log_event(cfg.out_dir, f"{channel}: не удалось сделать клип {_fmt(h.start)} — {e}")
                continue
        new.append(d)

    _finish(cfg, new, work, done + new, title, link, log)
    return new


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
    duration = len(audio_db) if audio_db is not None else (msgs[-1].t if msgs else 0)
    hl = _analyze(msgs, duration, audio_db, cfg, [], log)
    clips = []
    for i, h in enumerate(hl, 1):
        d = dict(h.to_dict(), vod_title=name)
        if not cfg.dry_run:
            base = f"{name}_{_fmt(h.start)}"
            seg = render.cut_segment(video, h.start, h.end, os.path.join(work, base + "_raw.mp4"))
            tmp = os.path.join(work, base + ".mp4")
            _make_short(seg, tmp, cfg, log)
            if not cfg.keep_raw:
                os.remove(seg)
            d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, name)
            log(f"  [{i}/{len(hl)}] готово -> {d['file']}")
        clips.append(d)
    _finish(cfg, clips, work, clips, name, None, log)
    return clips
