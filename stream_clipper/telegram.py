"""Отправка готовых клипов на телефон через своего Telegram-бота."""
from __future__ import annotations

import json
import os

from . import paths
from .i18n import T

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


def all_clips() -> bool:
    """Присылать КАЖДЫЙ готовый клип (по умолчанию нет — в Telegram приходят только видео, которые надо выложить)."""
    c = load()
    return bool(c.get("all_clips") and c.get("token") and c.get("chat_id"))


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
    import time as _time
    res = None
    for attempt in range(3):  # обрыв связи (VPN, провайдер) — переподключаемся сами: через 1 и 3 секунды
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = json.load(r)
            break
        except urllib.error.HTTPError as e:
            try:
                res = json.load(e)
            except Exception:
                raise RuntimeError(f"HTTP {e.code}")
            break
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            if attempt == 2:
                raise RuntimeError(T("нет связи с Telegram (обрыв соединения — проверь интернет или VPN)")) from e
            _time.sleep(1 + attempt * 2)
    if not res.get("ok"):
        desc = res.get("description") or T("ошибка")
        if "Unauthorized" in desc or "Not Found" in desc:
            desc = T("неверный ключ бота — скопируй его из @BotFather целиком")
        raise RuntimeError(desc)
    out = res["result"]
    if method.startswith("send") and isinstance(out, dict) and out.get("message_id"):
        _log_sent((data or {}).get("chat_id") or (out.get("chat") or {}).get("id"), out["message_id"])
    return out


def _sent_path() -> str:
    return os.path.join(paths.default_work_dir(), "tg_sent.json")


def _log_sent(chat, mid) -> None:
    """Что бот отправил (чат, номер сообщения, время) — чтобы потом можно было убрать всё из чата."""
    import time
    try:
        try:
            with open(_sent_path(), encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = []
        log.append([str(chat), int(mid), time.time()])
        log = [x for x in log if time.time() - x[2] < 3 * 86400][-5000:]
        with open(_sent_path(), "w", encoding="utf-8") as f:
            json.dump(log, f)
    except Exception:
        pass


def sent_log() -> list:
    try:
        with open(_sent_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def clear_sent_log() -> None:
    try:
        os.remove(_sent_path())
    except OSError:
        pass


def find_chat(token: str) -> tuple[int, str, bool]:
    """Ищет чат для клипов: группа с темами (лучше — темы работают как папки по датам) или личный чат с ботом.
    Возвращает (chat_id, название, это_группа_с_темами)."""
    me = _call(token, "getMe")
    updates = _call(token, "getUpdates", timeout=30)
    chats = []
    for u in reversed(updates):
        msg = u.get("message") or u.get("edited_message") or u.get("my_chat_member") or {}
        chat = msg.get("chat") or {}
        if chat.get("id") and chat["id"] not in [c["id"] for c in chats]:
            chats.append(chat)
    if not chats:
        raise RuntimeError(T('Бот @{0} пока не получил сообщений. Открой его в Telegram, нажми «Старт» (или напиши что-нибудь в группе с ботом) и попробуй ещё раз').format(me.get('username')))
    for chat in chats:  # группа с темами важнее личного чата
        if chat.get("type") == "supergroup":
            try:
                info = _call(token, "getChat", data={"chat_id": chat["id"]})
            except Exception:
                info = chat
            if info.get("is_forum"):
                return chat["id"], chat.get("title") or T("группа"), True
    chat = chats[0]
    name = chat.get("first_name") or chat.get("title") or chat.get("username") or T("чат")
    return chat["id"], name, False


def _date_label() -> str:
    from datetime import datetime
    return datetime.now().strftime("%d.%m.%Y")


def _day_target(c: dict) -> dict:
    """Куда класть клипы сегодняшнего дня: тема «📁 ДД.ММ.ГГГГ» в группе или заголовок дня в личном чате."""
    date = _date_label()
    if c.get("forum"):
        topics = c.setdefault("topics", {})
        if date not in topics:
            try:
                t = _call(c["token"], "createForumTopic", data={"chat_id": c["chat_id"], "name": f"📁 {date}"})
                topics[date] = t["message_thread_id"]
                save(c)
            except Exception as e:
                raise RuntimeError(T('не смог создать тему-папку «{0}» — дай боту в группе права администратора с пунктом «Управление темами» ({1})').format(date, e))
        return {"message_thread_id": topics[date]}
    if c.get("last_day") != date:  # личный чат: отделяем дни заголовком
        _call(c["token"], "sendMessage", data={"chat_id": c["chat_id"], "text": T('📁 Клипы за {0}').format(date)})
        c["last_day"] = date
        save(c)
    return {}


def send_text(text: str) -> None:
    c = load()
    _call(c["token"], "sendMessage", data={"chat_id": c["chat_id"], "text": text[:4000]})


def send_clip(path: str, clip: dict, channel: str) -> str:
    """Отправляет клип ФАЙЛОМ (без пережатия Telegram — качество как на компьютере) в папку-тему дня."""
    c = load()
    if not (c.get("token") and c.get("chat_id")):
        return T("Telegram не подключён")
    sec = int(clip.get("moment", clip.get("start", 0)))
    lines = [T('🎬 {0} — {1}ч{2:02d}м{3:02d}с').format(channel, sec // 3600, sec % 3600 // 60, sec % 60)]
    if clip.get("caption"):
        lines.append(T('Надпись: {0}').format(clip['caption']))
    if clip.get("link"):
        lines.append(clip["link"])
    caption = "\n".join(lines)[:1000]
    target = _day_target(c)
    send_path, note = path, T("отправлен в Telegram файлом")
    if os.path.getsize(path) > LIMIT:
        send_path = _light_copy(path)  # боты не могут отправлять файлы больше 50 МБ
        note = T("в Telegram — копия 1080p с меньшим битрейтом (клип больше 50 МБ; оригинал в папке на компьютере)")
        caption += T("\n(копия под лимит Telegram 50 МБ: оригинал лежит в папке на компьютере)")
        if not send_path or os.path.getsize(send_path) > LIMIT:
            _call(c["token"], "sendMessage",
                  data={"chat_id": c["chat_id"], "text": caption + T("\n\n(клип слишком большой для Telegram)"), **target})
            return T("клип больше 50 МБ — отправил только описание")
    safe = "".join(ch if ch.isascii() and (ch.isalnum() or ch in "-_") else "_" for ch in channel) or "clip"
    name = f"{safe}_{sec // 3600}h{sec % 3600 // 60:02d}m{sec % 60:02d}s.mp4"  # латиницей — везде читается
    try:
        with open(send_path, "rb") as f:
            res = _call(c["token"], "sendDocument", timeout=600,
                        data={"chat_id": c["chat_id"], "caption": caption, "disable_content_type_detection": "true",
                              **target},
                        files={"document": (name, f, "application/octet-stream")})
        fid = ((res or {}).get("document") or {}).get("file_id")
        for e in c.get("extra_chats") or []:  # тот же клип — и другим получателям (без повторной загрузки)
            if fid and e.get("id") and e["id"] != c["chat_id"]:
                try:
                    _call(c["token"], "sendDocument", timeout=120,
                          data={"chat_id": e["id"], "caption": caption, "document": fid})
                except Exception:
                    pass
    finally:
        if send_path != path:
            try:
                os.remove(send_path)
            except OSError:
                pass
    return note


def fit_1080(path: str, out: str) -> str | None:
    """Файл больше лимита бота (50 МБ) — ужимаем ТОЛЬКО битрейт под ~47 МБ, разрешение 1080×1920 сохраняем.
    Если и так не влезает (очень длинный клип) — в последнюю очередь 720p."""
    import subprocess
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=flags)
    try:
        dur = max(1.0, float(r.stdout.strip()))
    except ValueError:
        dur = 60.0
    kbps = int((47 * 1024 * 1024 * 8) / dur / 1000) - 160
    for k, scale in ((1.0, None), (0.88, None), (0.75, None), (0.75, "720:-2")):
        vb = max(800, int(kbps * k))
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", path]
        if scale:
            cmd += ["-vf", f"scale={scale}:flags=lanczos"]
        cmd += ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vb}k", "-maxrate", f"{int(vb * 1.3)}k",
                "-bufsize", f"{vb * 2}k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True, creationflags=flags)
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) <= LIMIT:
            return out
    return None


def _light_copy(path: str) -> str | None:
    return fit_1080(path, os.path.join(paths.default_work_dir(), "tg_upload.mp4"))
