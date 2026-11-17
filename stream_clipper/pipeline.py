"""Полный цикл: чат -> звук -> поиск моментов -> скачивание кусков -> вертикальные Shorts."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from . import detect, render
from .chat import ChatMessage, download_chat, load_chat_file


@dataclass
class Settings:
    out_dir: str = "output"
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


def process_vod(url: str, cfg: Settings, done: list[dict] | None = None, live: bool = False, log=print) -> list[dict]:
    """Обрабатывает Twitch VOD. done — уже нарезанные клипы (чтобы не повторяться)."""
    from . import twitch
    from .audio import loudness_per_second

    done = list(done or [])
    vid = twitch.vod_id(url)
    folder = os.path.join(cfg.out_dir, vid)
    work = os.path.join(folder, "_work")
    os.makedirs(work, exist_ok=True)

    log(f"VOD {url}")
    info = twitch.get_info(url)
    title = info.get("title") or vid
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

    hl = _analyze(msgs, duration, audio_db, cfg, done, log)
    new = []
    for i, h in enumerate(hl, 1):
        d = h.to_dict()
        if not cfg.dry_run:
            name = f"short_{_fmt(h.start)}"
            log(f"  [{i}/{len(hl)}] качаю кусок {_fmt(h.start)}...")
            try:
                seg = twitch.download_section(url, h.start, h.end, os.path.join(work, name), cfg.max_height)
                out = os.path.join(folder, name + ".mp4")
                _make_short(seg, out, cfg, log)
                d["file"] = out
                if not cfg.keep_raw:
                    os.remove(seg)
                log(f"    готово: {out}")
            except Exception as e:
                log(f"    ошибка: {e}")
                continue
        new.append(d)

    all_clips = done + new
    write_report(folder, all_clips, title, lambda s: twitch.timestamp_link(url, s))
    log(f"Отчёт: {os.path.join(folder, 'highlights.md')}")
    return new


def process_local(video: str, chat_path: str, cfg: Settings, log=print) -> list[dict]:
    """Обрабатывает уже скачанное видео + файл чата (наш JSON или TwitchDownloader)."""
    from .audio import loudness_per_second

    name = os.path.splitext(os.path.basename(video))[0]
    folder = os.path.join(cfg.out_dir, name)
    work = os.path.join(folder, "_work")
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
        d = h.to_dict()
        if not cfg.dry_run:
            base = f"short_{_fmt(h.start)}"
            seg = render.cut_segment(video, h.start, h.end, os.path.join(work, base + "_raw.mp4"))
            out = os.path.join(folder, base + ".mp4")
            _make_short(seg, out, cfg, log)
            if not cfg.keep_raw:
                os.remove(seg)
            d["file"] = out
            log(f"  [{i}/{len(hl)}] готово: {out}")
        clips.append(d)
    write_report(folder, clips, name)
    log(f"Отчёт: {os.path.join(folder, 'highlights.md')}")
    return clips
