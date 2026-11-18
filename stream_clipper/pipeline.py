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
        from .caption import make_caption
        text = make_caption(meta.get("streamer", ""), meta.get("title", ""), meta.get("top_messages", []),
                            transcript, meta.get("lang", "en"), log=log)
        log(f"    подпись: {text}")
        ass_files.append(render.write_caption_ass(base + ".caption.ass", text,
                                                  render.caption_y(layout, cfg.zoom, game_view=cfg.game_view)))
    if cfg.watermark_text.strip():
        # знак ставим под надписью-плашкой, чтобы не закрывал её
        ass_files.insert(len(ass_files) - (1 if text else 0),
                         render.write_watermark_ass(base + ".wm.ass", cfg.watermark_text.strip(),
                                                    cfg.watermark_pos, cfg.watermark_opacity))
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
    if changed:
        log("Новые настройки подхвачены: " + ", ".join(changed))


def clip_budget(per_hour: int, seconds: float) -> int:
    """Сколько клипов положено на столько-то секунд стрима («клипов за час стрима»)."""
    import math
    return max(1, math.ceil(per_hour * max(seconds, 0) / 3600))


def _analyze(msgs: list[ChatMessage], duration: float, audio_db, cfg: Settings, done: list[dict], log,
             top: int | None = None):
    log(f"Ищу моменты (длительность {_fmt(duration)}, сообщений {len(msgs)})...")
    hl = detect.find_highlights(
        msgs, int(duration), audio_db=audio_db, top=cfg.top if top is None else top, clip_pre=cfg.clip_pre, clip_post=cfg.clip_post,
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
                on_clip=None, start_at=None, progress: dict | None = None) -> list[dict]:
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
    link = (lambda s: f"https://youtu.be/{vid}?t={int(s)}") if yt else (lambda s: twitch.timestamp_link(url, s))

    # звук качаем параллельно с чатом — анализ не ждёт его
    audio = {"db": None}
    audio_thread = None
    if cfg.audio and not live:
        npy = os.path.join(work, "loudness.npy")
        if os.path.exists(npy):
            audio["db"] = np.load(npy)
        else:
            def load_audio():
                try:
                    a = twitch.download_audio(url, os.path.join(work, "audio"))
                    audio["db"] = loudness_per_second(a)
                    np.save(npy, audio["db"])
                    os.remove(a)
                    log("  громкость проанализирована — дальше учитываю и её")
                except Exception as e:
                    log(f"  громкость не получилась ({e}) — режу только по чату")
            log("  качаю звук для анализа громкости в фоне (можно отключить --no-audio)...")
            audio_thread = threading.Thread(target=load_audio, daemon=True)
            audio_thread.start()

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
    while True:
        refresh_live(cfg, log)
        msgs, finished = download_chat_part(url, cache, None if cfg.dry_run else last + step, log,
                                            start_from=start_at)
        covered = last = msgs[-1].t if msgs else 0
        if finished and not live:
            covered = max(covered, vod_duration)
            if audio_thread:
                audio_thread.join()  # последний проход — уже со звуком
        duration = max(covered, 1)
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
            hl = _analyze(msgs, duration, audio["db"], cfg, skip, log, top=allowed)
            for i, h in enumerate(hl, 1):
                if paths.stop_requested():
                    break
                refresh_live(cfg, log)
                d = dict(h.to_dict(), vod_url=url, vod_title=title, link=link(h.start))
                if not cfg.dry_run:
                    name = f"{vid}_{_fmt(h.start)}"
                    log(f"  [{i}/{len(hl)}] качаю кусок {_fmt(h.start)}...")
                    try:
                        seg = twitch.download_section(url, h.start, h.end, os.path.join(work, name + "_raw"),
                                                      cfg.max_height)
                        tmp = os.path.join(work, name + ".mp4")
                        d["caption"] = _make_short(seg, tmp, cfg, log, {"streamer": channel, "title": title,
                                                                        "top_messages": h.top_messages,
                                                                        "lang": lang or "en"})
                        if not cfg.keep_raw:
                            os.remove(seg)
                        d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, channel)
                        log(f"    готово -> {d['file']}")
                    except Exception as e:
                        log(f"    ошибка: {e}")
                        daily.log_event(cfg.out_dir, f"{channel}: не удалось сделать клип {_fmt(h.start)} — {e}")
                        continue
                new.append(d)
                if on_clip:
                    on_clip(d)
        boundary = next_boundary
        if finished or cfg.dry_run:
            break
        if paths.stop_requested():
            log("  останавливаюсь по просьбе — продолжу с этого места при следующем запуске")
            break

    _finish(cfg, new, work, done + new, title, link, log)
    return new


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
    duration = len(audio_db) if audio_db is not None else (msgs[-1].t if msgs else 0)
    hl = _analyze(msgs, duration, audio_db, cfg, [], log, top=clip_budget(cfg.top, duration))
    from .caption import detect_language
    lang = cfg.language or detect_language([m.text for m in msgs], name)
    clips = []
    for i, h in enumerate(hl, 1):
        d = dict(h.to_dict(), vod_title=name)
        if not cfg.dry_run:
            base = f"{name}_{_fmt(h.start)}"
            seg = render.cut_segment(video, h.start, h.end, os.path.join(work, base + "_raw.mp4"))
            tmp = os.path.join(work, base + ".mp4")
            d["caption"] = _make_short(seg, tmp, cfg, log, {"streamer": name, "title": name,
                                                            "top_messages": h.top_messages, "lang": lang})
            if not cfg.keep_raw:
                os.remove(seg)
            d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, name)
            log(f"  [{i}/{len(hl)}] готово -> {d['file']}")
        clips.append(d)
    _finish(cfg, clips, work, clips, name, None, log)
    return clips
