"""Публикация через официальные API площадок (без кликов в браузере — за автоматизацию кликами банят).

  YouTube   — YouTube Data API v3 (videos.insert, загрузка частями). Один раз: свой OAuth-клиент Google
              («Приложение для компьютера», файл client_secret.json) и вход в аккаунт в браузере.
              Пока Google не проверил такое приложение, YouTube делает загруженные через API видео ПРИВАТНЫМИ.
  Instagram — Instagram Graph API (аккаунт Business/Creator): Reels, загрузка из файла (resumable upload).
              Один раз: ID аккаунта Instagram и долгосрочный токен доступа приложения Meta.
  TikTok    — Content Posting API. Пока приложение TikTok не прошло их проверку, публиковать напрямую можно только
              приватно, поэтому видео отправляется в ЧЕРНОВИКИ TikTok (в приложении приходит уведомление — останется
              нажать «Опубликовать» в телефоне). Один раз: client key / secret своего приложения TikTok и вход.
Ключи хранятся только на этом компьютере: <служебная папка>/publish.json.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import time
import urllib.parse
import urllib.request
import webbrowser

from . import paths

GOOGLE_AUTH = os.environ.get("SC_GOOGLE_AUTH", "https://accounts.google.com/o/oauth2/v2/auth")
GOOGLE_TOKEN = os.environ.get("SC_GOOGLE_TOKEN", "https://oauth2.googleapis.com/token")
YT_UPLOAD = os.environ.get("SC_YT_UPLOAD", "https://www.googleapis.com/upload/youtube/v3/videos")
FB_GRAPH = os.environ.get("SC_FB_GRAPH", "https://graph.facebook.com/v21.0")
IG_GRAPH = os.environ.get("SC_IG_GRAPH", "https://graph.instagram.com/v21.0")
TT_AUTH = os.environ.get("SC_TT_AUTH", "https://www.tiktok.com/v2/auth/authorize/")
TT_API = os.environ.get("SC_TT_API", "https://open.tiktokapis.com")
TT_PORT = 8723
TT_REDIRECT = f"http://localhost:{TT_PORT}/callback/"


def _file() -> str:
    return os.path.join(paths.default_work_dir(), "publish.json")


def load() -> dict:
    try:
        with open(_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save(cfg: dict) -> None:
    os.makedirs(os.path.dirname(_file()), exist_ok=True)
    with open(_file(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)


def _update(**kw) -> dict:
    cfg = load()
    for k, v in kw.items():
        cfg.setdefault(k, {}).update(v) if isinstance(v, dict) else cfg.__setitem__(k, v)
    save(cfg)
    return cfg


def _http(url: str, data=None, headers: dict | None = None, method: str | None = None, timeout: float = 120):
    """Запрос → (код, заголовки, тело как dict или текст)."""
    body = data
    if isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode()
        headers = dict(headers or {}, **{"Content-Type": "application/x-www-form-urlencoded"})
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw, code, hdrs = r.read(), r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        raw, code, hdrs = e.read(), e.code, dict(e.headers or {})
    try:
        return code, hdrs, json.loads(raw.decode("utf-8") or "{}")
    except ValueError:
        return code, hdrs, raw.decode("utf-8", errors="replace")


def _json(url: str, payload: dict, token: str, method: str = "POST", extra: dict | None = None):
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"}
    h.update(extra or {})
    return _http(url, json.dumps(payload).encode("utf-8"), h, method)


# ---------- вход через браузер (OAuth с локальным адресом) ----------
def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def _wait_code(port: int, path_prefix: str = "/", timeout: float = 300) -> dict:
    """Ждём, пока браузер вернётся на http://localhost:port с ?code=... (вход выполнен)."""
    got: dict = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Готово — можно закрыть эту вкладку и вернуться в Stream Clipper." if "code" in got else \
                "Вход не выполнен: " + got.get("error", "?")
            self.wfile.write(f"<html><body style='font-family:sans-serif'><h2>{msg}</h2></body></html>".encode())

        def log_message(self, *a):
            pass
    srv = http.server.HTTPServer(("127.0.0.1", port), H)
    srv.timeout = 1
    end = time.time() + timeout
    while not got and time.time() < end:
        srv.handle_request()
    srv.server_close()
    if "code" not in got:
        raise RuntimeError("вход не завершён: " + got.get("error", "время вышло"))
    return got


def _free_port() -> int:
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# ---------- YouTube ----------
def youtube_connect(client_secret_path: str, log=print) -> str:
    """Один раз: файл client_secret.json (OAuth-клиент «Приложение для компьютера») + вход в браузере."""
    with open(client_secret_path, encoding="utf-8") as f:
        cs = json.load(f)
    c = cs.get("installed") or cs.get("web") or cs
    client_id, secret = c["client_id"], c.get("client_secret", "")
    port = _free_port()
    redirect = f"http://127.0.0.1:{port}"
    verifier, challenge = _pkce()
    url = GOOGLE_AUTH + "?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
        # youtube — загрузка, а также «сделать приватным», удалить и менять описание канала (по просьбе пользователя)
        "scope": "https://www.googleapis.com/auth/youtube",
        "access_type": "offline", "prompt": "consent", "code_challenge": challenge, "code_challenge_method": "S256"})
    log("Открываю вход в Google в браузере...")
    webbrowser.open(url)
    code = _wait_code(port)["code"]
    st, _, tok = _http(GOOGLE_TOKEN, {"code": code, "client_id": client_id, "client_secret": secret,
                                      "redirect_uri": redirect, "grant_type": "authorization_code",
                                      "code_verifier": verifier})
    if st != 200 or not isinstance(tok, dict) or "refresh_token" not in tok:
        raise RuntimeError(f"Google не выдал доступ: {tok}")
    _update(youtube={"client_id": client_id, "client_secret": secret, "refresh_token": tok["refresh_token"],
                     "connected": time.strftime("%Y-%m-%d %H:%M")})
    return "ok"


def _yt_token() -> str:
    y = load().get("youtube") or {}
    if not y.get("refresh_token"):
        raise RuntimeError("YouTube не подключён (Настройки → Автопубликация)")
    st, _, tok = _http(GOOGLE_TOKEN, {"client_id": y["client_id"], "client_secret": y.get("client_secret", ""),
                                      "refresh_token": y["refresh_token"], "grant_type": "refresh_token"})
    if st != 200 or "access_token" not in tok:
        raise RuntimeError(f"YouTube: не удалось обновить вход ({tok})")
    return tok["access_token"]


def youtube_upload(file: str, title: str, description: str, tags: list, log=print) -> dict:
    token = _yt_token()
    size = os.path.getsize(file)
    meta = {"snippet": {"title": title[:100], "description": description[:4900],
                        "tags": [t.lstrip("#") for t in tags][:30], "categoryId": "20"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    st, hdrs, body = _json(YT_UPLOAD + "?uploadType=resumable&part=snippet,status", meta, token,
                           extra={"X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"})
    loc = hdrs.get("Location") or hdrs.get("location")
    if st not in (200, 201) or not loc:
        raise RuntimeError(f"YouTube: не начал загрузку ({st}: {body})")
    log("Загружаю видео на YouTube...")
    with open(file, "rb") as f:
        st, _, body = _http(loc, f.read(), {"Authorization": f"Bearer {token}", "Content-Type": "video/mp4",
                                            "Content-Length": str(size)}, "PUT", timeout=1800)
    if st not in (200, 201) or not isinstance(body, dict) or "id" not in body:
        raise RuntimeError(f"YouTube: загрузка не удалась ({st}: {body})")
    privacy = (body.get("status") or {}).get("privacyStatus", "public")
    return {"id": body["id"], "url": f"https://youtube.com/shorts/{body['id']}", "privacy": privacy,
            "note": "YouTube сделал видео приватным: приложение Google ещё не проверено" if privacy == "private" else ""}


YT_API = os.environ.get("SC_YT_API", "https://www.googleapis.com/youtube/v3")


def youtube_set_privacy(video_id: str, privacy: str = "private") -> None:
    token = _yt_token()
    st, _, body = _json(f"{YT_API}/videos?part=status", {"id": video_id, "status": {"privacyStatus": privacy,
                                                                                     "selfDeclaredMadeForKids": False}},
                        token, method="PUT")
    if st != 200:
        raise RuntimeError(f"YouTube: не удалось сменить доступ ({st}: {body})")


def youtube_delete(video_id: str) -> None:
    token = _yt_token()
    st, _, body = _http(f"{YT_API}/videos?id={urllib.parse.quote(video_id)}", None,
                        {"Authorization": f"Bearer {token}"}, "DELETE")
    if st not in (200, 204):
        raise RuntimeError(f"YouTube: не удалось удалить ({st}: {body})")


def youtube_channel_description(text: str) -> None:
    """Описание канала (channels.update → brandingSettings)."""
    token = _yt_token()
    st, _, body = _http(f"{YT_API}/channels?part=brandingSettings&mine=true", None, {"Authorization": f"Bearer {token}"})
    items = (body or {}).get("items") if isinstance(body, dict) else None
    if st != 200 or not items:
        raise RuntimeError(f"YouTube: не нашёл канал ({st}: {body})")
    ch = items[0]
    branding = ch.get("brandingSettings") or {}
    branding.setdefault("channel", {})["description"] = text[:1000]
    st, _, body = _json(f"{YT_API}/channels?part=brandingSettings", {"id": ch["id"], "brandingSettings": branding},
                        token, method="PUT")
    if st != 200:
        raise RuntimeError(f"YouTube: описание канала не обновилось ({st}: {body})")


# ---------- Instagram ----------
def instagram_connect(user_id: str, token: str) -> str:
    base = IG_GRAPH if token.startswith("IG") else FB_GRAPH
    st, _, body = _http(f"{base}/{user_id}?fields=username&access_token={urllib.parse.quote(token)}")
    if st != 200 or not isinstance(body, dict) or "username" not in body:
        raise RuntimeError(f"Instagram не принял ID/токен: {body}")
    _update(instagram={"user_id": user_id, "token": token, "username": body["username"],
                       "connected": time.strftime("%Y-%m-%d %H:%M")})
    return body["username"]


def instagram_upload(file: str, caption: str, log=print, wait: float = 600) -> dict:
    ig = load().get("instagram") or {}
    if not ig.get("token"):
        raise RuntimeError("Instagram не подключён (Настройки → Автопубликация)")
    uid, token = ig["user_id"], ig["token"]
    base = IG_GRAPH if token.startswith("IG") else FB_GRAPH
    st, _, cont = _http(f"{base}/{uid}/media", {"media_type": "REELS", "upload_type": "resumable",
                                                 "caption": caption[:2200], "share_to_feed": "true",
                                                 "access_token": token})
    if st != 200 or not isinstance(cont, dict) or "id" not in cont:
        raise RuntimeError(f"Instagram: не создал публикацию ({cont})")
    cid = cont["id"]
    uri = cont.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v21.0/{cid}"
    size = os.path.getsize(file)
    log("Загружаю Reels в Instagram...")
    with open(file, "rb") as f:
        st, _, up = _http(uri, f.read(), {"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size),
                                          "Content-Type": "application/octet-stream"}, "POST", timeout=1800)
    if st != 200:
        raise RuntimeError(f"Instagram: файл не загрузился ({st}: {up})")
    end = time.time() + wait
    while True:  # Instagram обрабатывает видео — ждём готовности
        st, _, s = _http(f"{base}/{cid}?fields=status_code,status&access_token={urllib.parse.quote(token)}")
        code = (s or {}).get("status_code") if isinstance(s, dict) else None
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED") or time.time() > end:
            raise RuntimeError(f"Instagram: видео не обработалось ({s})")
        time.sleep(5)
    st, _, pub = _http(f"{base}/{uid}/media_publish", {"creation_id": cid, "access_token": token})
    if st != 200 or "id" not in pub:
        raise RuntimeError(f"Instagram: не опубликовал ({pub})")
    st, _, info = _http(f"{base}/{pub['id']}?fields=permalink&access_token={urllib.parse.quote(token)}")
    return {"id": pub["id"], "url": (info or {}).get("permalink", "") if isinstance(info, dict) else ""}


# ---------- TikTok (черновики) ----------
def tiktok_connect(client_key: str, client_secret: str, log=print) -> str:
    """Один раз: ключи своего приложения TikTok (Login Kit + Content Posting API, адрес возврата TT_REDIRECT) и вход."""
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(16)
    url = TT_AUTH + "?" + urllib.parse.urlencode({
        "client_key": client_key, "scope": "user.info.basic,video.upload,video.publish", "response_type": "code",
        "redirect_uri": TT_REDIRECT, "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
    log("Открываю вход в TikTok в браузере...")
    webbrowser.open(url)
    got = _wait_code(TT_PORT)
    st, _, tok = _http(TT_API + "/v2/oauth/token/", {"client_key": client_key, "client_secret": client_secret,
                                                      "code": got["code"], "grant_type": "authorization_code",
                                                      "redirect_uri": TT_REDIRECT, "code_verifier": verifier})
    if st != 200 or not isinstance(tok, dict) or "access_token" not in tok:
        raise RuntimeError(f"TikTok не выдал доступ: {tok}")
    _update(tiktok={"client_key": client_key, "client_secret": client_secret, "access_token": tok["access_token"],
                    "refresh_token": tok.get("refresh_token", ""), "expires": time.time() + float(tok.get("expires_in", 0)),
                    "connected": time.strftime("%Y-%m-%d %H:%M")})
    return "ok"


def _tt_token() -> str:
    t = load().get("tiktok") or {}
    if not t.get("access_token"):
        raise RuntimeError("TikTok не подключён (Настройки → Автопубликация)")
    if time.time() < float(t.get("expires", 0)) - 120 or not t.get("refresh_token"):
        return t["access_token"]
    st, _, tok = _http(TT_API + "/v2/oauth/token/", {"client_key": t["client_key"], "client_secret": t["client_secret"],
                                                      "grant_type": "refresh_token", "refresh_token": t["refresh_token"]})
    if st != 200 or "access_token" not in tok:
        raise RuntimeError(f"TikTok: не удалось обновить вход ({tok})")
    _update(tiktok={"access_token": tok["access_token"], "refresh_token": tok.get("refresh_token", t["refresh_token"]),
                    "expires": time.time() + float(tok.get("expires_in", 0))})
    return tok["access_token"]


def tiktok_draft(file: str, log=print) -> dict:
    """Видео → в черновики TikTok (в приложении придёт уведомление; описание вставляется там)."""
    token = _tt_token()
    size = os.path.getsize(file)
    st, _, body = _json(TT_API + "/v2/post/publish/inbox/video/init/",
                        {"source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size,
                                         "total_chunk_count": 1}}, token)
    data = (body or {}).get("data") or {} if isinstance(body, dict) else {}
    if st != 200 or not data.get("upload_url"):
        raise RuntimeError(f"TikTok: не начал загрузку ({body})")
    log("Отправляю видео в черновики TikTok...")
    with open(file, "rb") as f:
        st, _, up = _http(data["upload_url"], f.read(), {"Content-Type": "video/mp4", "Content-Length": str(size),
                                                         "Content-Range": f"bytes 0-{size - 1}/{size}"}, "PUT",
                          timeout=1800)
    if st not in (200, 201):
        raise RuntimeError(f"TikTok: файл не загрузился ({st}: {up})")
    return {"id": data.get("publish_id", ""), "url": "", "draft": True}


def tiktok_post(file: str, caption: str, log=print) -> dict:
    """Сразу опубликовать в TikTok (Direct Post). Работает, когда приложение TikTok прошло их проверку;
    до проверки TikTok разрешает только приватные посты — тогда видео идёт черновиком (tiktok_draft)."""
    token = _tt_token()
    size = os.path.getsize(file)
    st, _, body = _json(TT_API + "/v2/post/publish/video/init/",
                        {"post_info": {"title": caption[:2200], "privacy_level": "PUBLIC_TO_EVERYONE",
                                       "disable_duet": False, "disable_comment": False, "disable_stitch": False,
                                       "video_cover_timestamp_ms": 500},
                         "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size,
                                         "total_chunk_count": 1}}, token)
    data = (body or {}).get("data") or {} if isinstance(body, dict) else {}
    if st != 200 or not data.get("upload_url"):
        raise RuntimeError(f"TikTok: не начал публикацию ({body})")
    log("Публикую видео в TikTok...")
    with open(file, "rb") as f:
        st, _, up = _http(data["upload_url"], f.read(), {"Content-Type": "video/mp4", "Content-Length": str(size),
                                                         "Content-Range": f"bytes 0-{size - 1}/{size}"}, "PUT",
                          timeout=1800)
    if st not in (200, 201):
        raise RuntimeError(f"TikTok: файл не загрузился ({st}: {up})")
    return {"id": data.get("publish_id", ""), "url": "", "draft": False}


def connected() -> dict:
    cfg = load()
    return {"youtube": bool((cfg.get("youtube") or {}).get("refresh_token")),
            "instagram": bool((cfg.get("instagram") or {}).get("token")),
            "tiktok": bool((cfg.get("tiktok") or {}).get("access_token"))}


def direct_platforms() -> set:
    """Площадки, куда «Выпускающий» публикует сам (подключены в Настройках). TikTok — только когда приложение
    прошло проверку TikTok (tiktok.direct); до этого TikTok идёт через Telegram, чтобы не плодить черновики."""
    c = connected()
    cfg = load()
    out = {p for p in ("youtube", "instagram") if c.get(p)}
    if (cfg.get("youtube") or {}).get("private_lock") and not (cfg.get("youtube") or {}).get("audited"):
        out.discard("youtube")  # Google ещё не проверил приложение — видео выходили бы закрытыми, пока через Telegram
    if c.get("tiktok") and (load().get("tiktok") or {}).get("direct"):
        out.add("tiktok")
    return out


def publish(platform: str, file: str, title: str, description: str, tags: list, log=print) -> dict:
    """Опубликовать на площадке. Возвращает {"id", "url", ...}; ошибки — исключением с понятным текстом."""
    if platform == "youtube":
        res = youtube_upload(file, title, description, tags, log)
        y = load().get("youtube") or {}
        if res.get("privacy") == "private" and not y.get("audited"):
            # приложение Google не проверено: YouTube закрыл видео. Убираем закрытую копию и временно возвращаем
            # YouTube в Telegram — видео не пропадёт. После проверки Google — галочка в Настройках.
            try:
                youtube_delete(res["id"])
            except Exception:
                pass
            _update(youtube={"private_lock": True})
            raise RuntimeError("YouTube делает видео закрытыми, пока Google не проверил приложение — "
                               "до проверки YouTube снова идёт через Telegram")
        return res
    if platform == "instagram":
        return instagram_upload(file, description, log)
    if platform == "tiktok" and (load().get("tiktok") or {}).get("direct"):
        return tiktok_post(file, description, log)
    if platform == "tiktok":
        res = tiktok_draft(file, log)
        try:  # описание в черновик через API не передаётся — шлём его в Telegram, чтобы вставить в телефоне
            from . import telegram
            if telegram.enabled():
                telegram.send_text("🎬 В TikTok ждёт черновик. Описание для него:\n\n" + description)
        except Exception:
            pass
        return res
    raise ValueError(f"неизвестная площадка {platform}")
