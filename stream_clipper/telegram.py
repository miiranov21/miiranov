"""Отправка готовых клипов на телефон через своего Telegram-бота."""
from __future__ import annotations

import json
import os

from . import paths

API = os.environ.get("STREAM_CLIPPER_TG_API", "https://api.telegram.org")
LIMIT = 49 * 1024 * 1024  # бот может отправить файл до 50 МБ


def _cfg_path() -> str:
    return os.path.join(paths.default_work_dir(), "telegram.json")


def load() -> dict:
    try:
        with open(_cfg_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save(cfg: dict) -> None:
    os.makedirs(os.path.dirname(_cfg_path()), exist_ok=True)
    with open(_cfg_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)


def enabled() -> bool:
    c = load()
    return bool(c.get("on") and c.get("token") and c.get("chat_id"))


def _call(token: str, method: str, timeout: float = 30, data: dict | None = None, files: dict | None = None):
    """Запрос к Telegram Bot API на встроенных средствах Python (без сторонних библиотек)."""
    import urllib.error
    import urllib.parse
    import urllib.request
    import uuid
    url = f"{API}/bot{token}/{method}"
    if files:
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in (data or {}).items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, (fname, fobj, ctype) in files.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'
                         f"Content-Type: {ctype}\r\n\r\n".encode() + fobj.read() + b"\r\n")
        body = b"".join(parts) + f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data or {}).encode())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            res = json.load(e)
        except Exception:
            raise RuntimeError(f"HTTP {e.code}")
    if not res.get("ok"):
        desc = res.get("description") or "ошибка"
        if "Unauthorized" in desc or "Not Found" in desc:
            desc = "неверный ключ бота — скопируй его из @BotFather целиком"
        raise RuntimeError(desc)
    return res["result"]


def find_chat(token: str) -> tuple[int, str] | None:
    """Ищет чат с ботом: пользователь должен сначала написать боту /start. Возвращает (chat_id, имя)."""
    me = _call(token, "getMe")
    updates = _call(token, "getUpdates", timeout=30)
    for u in reversed(updates):
        msg = u.get("message") or u.get("edited_message") or {}
        chat = msg.get("chat") or {}
        if chat.get("id"):
            name = chat.get("first_name") or chat.get("title") or chat.get("username") or "чат"
            return chat["id"], name
    raise RuntimeError(f"Бот @{me.get('username')} пока не получил сообщений. Открой его в Telegram, "
                       f"нажми «Старт» (или напиши /start) и попробуй ещё раз")


def send_text(text: str) -> None:
    c = load()
    _call(c["token"], "sendMessage", data={"chat_id": c["chat_id"], "text": text[:4000]})


def send_clip(path: str, clip: dict, channel: str) -> str:
    """Отправляет клип в Telegram. Возвращает короткий итог для журнала."""
    c = load()
    if not (c.get("token") and c.get("chat_id")):
        return "Telegram не подключён"
    sec = int(clip.get("moment", clip.get("start", 0)))
    lines = [f"🎬 {channel} — {sec // 3600}ч{sec % 3600 // 60:02d}м{sec % 60:02d}с"]
    if clip.get("caption"):
        lines.append(f"Надпись: {clip['caption']}")
    if clip.get("link"):
        lines.append(clip["link"])
    caption = "\n".join(lines)[:1000]
    send_path, note = path, "отправлен в Telegram"
    if os.path.getsize(path) > LIMIT:
        send_path = _light_copy(path)  # облегчённая копия 720p — оригинал остаётся на компьютере
        note = "отправлен в Telegram (облегчённая копия 720p — оригинал в папке на компьютере)"
        if not send_path or os.path.getsize(send_path) > LIMIT:
            send_text(caption + "\n\n(клип слишком большой для Telegram — он в папке на компьютере)")
            return "клип больше 50 МБ — отправил только описание"
    try:
        with open(send_path, "rb") as f:
            _call(c["token"], "sendVideo", timeout=600,
                  data={"chat_id": c["chat_id"], "caption": caption, "supports_streaming": "true"},
                  files={"video": (os.path.basename(path), f, "video/mp4")})
    finally:
        if send_path != path:
            try:
                os.remove(send_path)
            except OSError:
                pass
    return note


def _light_copy(path: str) -> str | None:
    import subprocess
    out = os.path.join(paths.default_work_dir(), "tg_upload.mp4")
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", "scale=720:-2:flags=lanczos",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", out], capture_output=True, creationflags=flags)
    return out if r.returncode == 0 and os.path.exists(out) else None
