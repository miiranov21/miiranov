"""Работа с Twitch и YouTube через yt-dlp: инфо, проверка эфира, скачивание кусков."""
from __future__ import annotations

import glob
import os

import yt_dlp
from yt_dlp.utils import DownloadError, download_range_func

_BASE = {"quiet": True, "no_warnings": True, "noprogress": True}


def set_cookies_browser(browser: str | None) -> None:
    """Брать куки из браузера (chrome/firefox/edge...) — помогает, если YouTube просит
    «подтвердить, что вы не бот»."""
    if browser:
        _BASE["cookiesfrombrowser"] = (browser,)


def is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def get_info(url: str, extra: dict | None = None) -> dict:
    with yt_dlp.YoutubeDL(dict(_BASE, **(extra or {}))) as ydl:
        return ydl.extract_info(url, download=False)


def youtube_live_url(spec: str) -> str:
    """@handle / ссылка на канал -> https://www.youtube.com/@handle/live"""
    s = spec.strip()
    if s.startswith("yt:"):
        s = s[3:]
    if s.startswith("@"):
        return f"https://www.youtube.com/{s}/live"
    if "watch?v=" in s or "youtu.be/" in s or s.rstrip("/").endswith("/live"):
        return s
    return s.rstrip("/") + "/live"


def youtube_is_live(live_url: str) -> bool:
    try:
        info = get_info(live_url)
    except DownloadError as e:
        if _is_offline_error(e) or "will begin" in str(e).lower() or "premieres" in str(e).lower():
            return False  # канал не в эфире
        raise RuntimeError("нет связи с YouTube: " + str(e)[:200])
    return info.get("live_status") == "is_live" or bool(info.get("is_live"))


_OFFLINE_MARKERS = ("not currently live", "is offline", "does not exist", "not live", "no video formats")


def _is_offline_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(m in msg for m in _OFFLINE_MARKERS)


def is_live(channel: str) -> bool:
    try:
        info = get_info(f"https://www.twitch.tv/{channel}")
        return bool(info.get("is_live"))
    except DownloadError as e:
        if _is_offline_error(e):
            return False  # канал оффлайн
        raise RuntimeError("нет связи с Twitch (провайдер блокирует? включи VPN): " + str(e)[:200])


def latest_vod_url(channel: str) -> str | None:
    opts = dict(_BASE, extract_flat=True, playlistend=1)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://www.twitch.tv/{channel}/videos?filter=archives&sort=time", download=False)
    entries = list(info.get("entries") or [])
    if not entries:
        return None
    e = entries[0]
    return e.get("url") or f"https://www.twitch.tv/videos/{str(e.get('id')).lstrip('v')}"


def _download(url: str, out_base: str, extra: dict) -> str:
    for f in glob.glob(glob.escape(out_base) + ".*"):
        if not f.endswith((".part", ".ytdl")):
            return f  # уже скачано
    opts = dict(_BASE, outtmpl=out_base + ".%(ext)s", **extra)
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    files = [f for f in glob.glob(glob.escape(out_base) + ".*") if not f.endswith((".part", ".ytdl"))]
    if not files:
        raise RuntimeError(f"не удалось скачать {url}")
    return files[0]


def download_section(url: str, start: float, end: float, out_base: str, max_height: int = 1080) -> str:
    """Скачивает только нужный кусок VOD (не весь 6-часовой стрим)."""
    fmt = (f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b" if is_youtube(url)
           else f"best[height<={max_height}]/best")
    return _download(url, out_base, {
        "format": fmt,
        "merge_output_format": "mp4",
        "download_ranges": download_range_func(None, [(start, end)]),
        "force_keyframes_at_cuts": True,
    })


def download_audio(url: str, out_base: str) -> str:
    """Скачивает только звук VOD (~70 МБ/час) для анализа громкости."""
    return _download(url, out_base, {"format": "bestaudio/audio_only/worst"})


def vod_id(url: str) -> str:
    tail = url.rstrip("/").split("/")[-1].split("?")[0]
    return tail.lstrip("v") or "vod"


def timestamp_link(url: str, sec: float) -> str:
    s = int(sec)
    base = url.split("?")[0]
    return f"{base}?t={s // 3600}h{s % 3600 // 60}m{s % 60}s"
