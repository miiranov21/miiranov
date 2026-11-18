"""Работа с Twitch и YouTube через yt-dlp: инфо, проверка эфира, скачивание кусков."""
from __future__ import annotations

import glob
import os

import yt_dlp
from yt_dlp.utils import DownloadError, download_range_func

class _QuietLogger:
    """yt-dlp не печатает свои ошибки — программа сама пишет понятное сообщение."""
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


_BASE = {"quiet": True, "no_warnings": True, "noprogress": True, "logger": _QuietLogger()}


def _setup_js_runtime() -> None:
    """С конца 2025 года YouTube защищает видео проверкой на JavaScript — yt-dlp проходит её
    через движок Deno (ставится через pip как пакет «deno») и пакет yt-dlp-ejs."""
    try:
        import deno
        path = deno.find_deno_bin()
        if path and os.path.exists(path):
            _BASE["js_runtimes"] = {"deno": {"path": path}}
    except Exception:
        pass


_setup_js_runtime()


def set_cookies_browser(browser: str | None) -> None:
    """Брать куки из браузера (chrome/firefox/edge...) — помогает, если YouTube просит
    «подтвердить, что вы не бот»."""
    if browser:
        _BASE["cookiesfrombrowser"] = (browser,)


def export_cookies(path: str) -> bool:
    """Сохраняет куки из выбранного браузера в файл (нужен загрузчику живого чата YouTube)."""
    if "cookiesfrombrowser" not in _BASE:
        return False
    try:
        with yt_dlp.YoutubeDL(dict(_BASE)) as ydl:
            ydl.cookiejar.save(path, ignore_discard=True, ignore_expires=True)
        return os.path.exists(path)
    except Exception:
        return False


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
        kind, text = explain_youtube_error(e)
        if kind == "offline":
            return False  # канал не в эфире
        raise RuntimeError(text)
    return info.get("live_status") == "is_live" or bool(info.get("is_live"))


_OFFLINE_MARKERS = ("not currently live", "is offline", "does not exist", "not live", "no video formats")
_YT_OFFLINE = ("will begin", "premieres", "this live event", "has not started", "is upcoming",
               "does not have a live", "no live stream", "not currently live", "is offline")
_NETWORK = ("ssl", "timed out", "timeout", "connection", "getaddrinfo", "proxy", "eof occurred",
            "name resolution", "network is unreachable", "remote end closed")


def explain_youtube_error(e: Exception) -> tuple[str, str]:
    """Понятная причина ошибки YouTube: ('offline'|'bot'|'network'|'missing'|'other', текст)."""
    msg = str(e).replace("ERROR: ", "")
    low = msg.lower()
    if any(m in low for m in _YT_OFFLINE):
        return "offline", "не в эфире"
    if "not a bot" in low or "sign in to confirm" in low or "confirm your age" in low or "cookies" in low:
        return "bot", ("YouTube просит подтвердить, что ты не бот (так бывает через VPN). "
                       "В окне программы выбери «Вход в YouTube через браузер» (лучше Firefox) "
                       "и войди в YouTube в этом браузере")
    if "does not exist" in low or "404" in low or "not found" in low or "unable to recognize tab" in low:
        return "missing", "канал не найден — проверь ник (лучше вставь ссылку на канал из адресной строки)"
    if "no video formats" in low or "javascript" in low or "js runtime" in low or "challenge" in low:
        return "jsruntime", ("YouTube не отдаёт видео: не хватает компонента для проверки YouTube (Deno). "
                             "Нажми «Проверить обновления» — программа поставит его сама "
                             "(или выполни: python -m pip install deno yt-dlp-ejs)")
    if any(m in low for m in _NETWORK):
        return "network", "нет связи с YouTube — проверь интернет и VPN"
    return "other", "YouTube ответил ошибкой: " + msg[:180]


def _is_offline_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(m in msg for m in _OFFLINE_MARKERS)


LAST_LIVE_INFO: dict = {}  # логин -> инфо о текущем эфире (время начала и т.п.)


def is_live(channel: str) -> bool:
    try:
        info = get_info(f"https://www.twitch.tv/{channel}")
        LAST_LIVE_INFO[channel] = info
        return bool(info.get("is_live"))
    except DownloadError as e:
        if _is_offline_error(e):
            return False  # канал оффлайн
        raise RuntimeError("нет связи с Twitch — проверь интернет и VPN (сервер, на котором открывается Twitch)")


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
        # без force_keyframes_at_cuts: кусок копируется как есть, без лишнего пережатия (качество выше);
        # начало может сдвинуться на 1–2 секунды к ближайшему ключевому кадру — это не страшно
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
