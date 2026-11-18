"""Загрузка и чтение чата Twitch (реплей чата VOD)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict

from . import paths


@dataclass
class ChatMessage:
    t: float       # секунда от начала VOD
    author: str
    text: str


def _save(msgs: list[ChatMessage], path: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump([asdict(m) for m in msgs], f, ensure_ascii=False)
    os.replace(tmp, path)


def load_chat_file(path: str) -> list[ChatMessage]:
    """Читает чат из JSON. Поддерживает формат этой программы и формат TwitchDownloader."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    msgs: list[ChatMessage] = []
    if isinstance(data, dict) and "comments" in data:  # TwitchDownloader
        for c in data["comments"]:
            msgs.append(ChatMessage(
                t=float(c.get("content_offset_seconds", 0)),
                author=(c.get("commenter") or {}).get("display_name", "") or "",
                text=(c.get("message") or {}).get("body", "") or "",
            ))
    else:
        for m in data:
            msgs.append(ChatMessage(t=float(m["t"]), author=m.get("author", ""), text=m.get("text", "")))
    msgs.sort(key=lambda m: m.t)
    return msgs


GQL_URL = "https://gql.twitch.tv/gql"
GQL_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"  # публичный client-id веб-плеера Twitch
COMMENTS_HASH = "b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a"


def _twitch_video_id(url: str) -> str | None:
    import re
    m = re.search(r"twitch\.tv/(?:[^/]+/)?(?:videos?|v)/(\d+)", url)
    return m.group(1) if m else None


def iter_twitch_vod_chat(video_id: str, start: float = 0, log=print, session=None):
    """Реплей чата Twitch VOD через GQL (как TwitchDownloader). Отдаёт ChatMessage по порядку.
    Сначала листает по курсору; если Twitch требует integrity — листает по смещению в секундах."""
    import time
    import requests

    sess = session or requests.Session()
    headers = {"Client-Id": GQL_CLIENT_ID, "Content-Type": "text/plain;charset=UTF-8"}

    def query(variables):
        body = [{"operationName": "VideoCommentsByOffsetOrCursor", "variables": variables,
                 "extensions": {"persistedQuery": {"version": 1, "sha256Hash": COMMENTS_HASH}}}]
        for attempt in range(6):
            try:
                r = sess.post(GQL_URL, json=body, headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
                data = data[0] if isinstance(data, list) else data
                if data.get("errors"):
                    raise RuntimeError(data["errors"][0].get("message", str(data["errors"])))
                video = (data.get("data") or {}).get("video")
                if video is None:
                    raise RuntimeError("Twitch не отдал видео (удалено или только для сабов?)")
                return video.get("comments") or {"edges": [], "pageInfo": {}}
            except RuntimeError:
                raise
            except Exception as e:
                wait = 2 * (attempt + 1)
                log(f"    сеть: {e} — повтор через {wait} с")
                time.sleep(wait)
        raise RuntimeError("не удалось получить чат Twitch после 6 попыток (проверь VPN)")

    def parse(edge):
        n = edge.get("node") or {}
        frags = (n.get("message") or {}).get("fragments") or []
        text = "".join(f.get("text", "") for f in frags)
        who = (n.get("commenter") or {}).get("displayName") or ""
        return n.get("id"), ChatMessage(t=float(n.get("contentOffsetSeconds") or 0), author=who, text=text)

    seen: set = set()
    use_cursor = True
    cursor = None
    offset = int(start)
    while True:
        if use_cursor and cursor:
            try:
                comments = query({"videoID": video_id, "cursor": cursor})
            except RuntimeError as e:
                if "integrity" in str(e).lower():
                    log("    Twitch не даёт листать по курсору — переключаюсь на смещение")
                    use_cursor = False
                    continue
                raise
        else:
            comments = query({"videoID": video_id, "contentOffsetSeconds": offset})
        edges = comments.get("edges") or []
        max_t = None
        for e in edges:
            cid, m = parse(e)
            max_t = m.t if max_t is None else max(max_t, m.t)
            if cid in seen or m.t < start:
                continue
            seen.add(cid)
            yield m
        if not edges:
            return
        has_next = (comments.get("pageInfo") or {}).get("hasNextPage")
        if use_cursor:
            cursor = edges[-1].get("cursor")
            if not has_next or not cursor:
                return
        else:
            nxt = int(max_t)
            if nxt <= offset:
                nxt = offset + 1
            if not has_next and nxt <= offset + 1 and len(edges) < 2:
                return
            offset = nxt


def download_chat(url: str, cache_path: str, refresh: bool = False, log=print) -> list[ChatMessage]:
    """Скачивает реплей чата VOD целиком (с кэшем). refresh=True докачивает новые сообщения."""
    if os.path.exists(cache_path) and not refresh:
        msgs = load_chat_file(cache_path)
        log(f"  чат из кэша: {len(msgs)} сообщений")
        return msgs
    return download_chat_part(url, cache_path, None, log)[0]


def download_chat_part(url: str, cache_path: str, stop_at: float | None = None,
                       log=print, start_from: float = 0) -> tuple[list[ChatMessage], bool]:
    """Докачивает чат с места, где остановились (но не раньше start_from), до секунды stop_at стрима
    (None — до конца). Возвращает (все сообщения, дошли ли до конца чата)."""
    import time
    msgs: list[ChatMessage] = load_chat_file(cache_path) if os.path.exists(cache_path) else []
    start = max(msgs[-1].t if msgs else 0, start_from or 0)
    if stop_at is not None and start >= stop_at:
        return msgs, False
    seen = {(m.t, m.author, m.text) for m in msgs if m.t >= start}
    log(f"  скачиваю чат с {int(start // 3600)}ч{int(start % 3600 // 60):02d}м"
        + (f" до {int(stop_at // 3600)}ч{int(stop_at % 3600 // 60):02d}м..." if stop_at else "..."))
    vid = _twitch_video_id(url)
    source = iter_twitch_vod_chat(vid, start, log=log) if vid else _iter_chat_downloader(url, start)
    new = 0
    last_log = time.time()
    finished = True
    if stop_at is None:
        log("    (нажми Ctrl+C один раз, чтобы перестать качать чат и резать из уже скачанного)")
    try:
        for m in source:
            key = (m.t, m.author, m.text)
            if key in seen:
                continue
            seen.add(key)
            msgs.append(m)
            new += 1
            if stop_at is not None and m.t > stop_at:
                finished = False  # дошли до нужного места — дальше докачаем в следующий раз
                break
            if new % 500 == 0 and paths.stop_requested():
                finished = False  # просят остановиться — сохраняем, что скачали, и выходим
                break
            if time.time() - last_log > 10:  # прогресс раз в 10 секунд
                last_log = time.time()
                log(f"    ...{new} сообщений, позиция {int(m.t // 3600)}ч{int(m.t % 3600 // 60):02d}м")
                _save(msgs, cache_path)  # промежуточное сохранение
    except KeyboardInterrupt:
        if not msgs:
            raise
        t = msgs[-1].t
        log(f"  Ctrl+C: останавливаю загрузку чата на {int(t // 3600)}ч{int(t % 3600 // 60):02d}м, "
            f"режу из того, что есть (ещё раз Ctrl+C — полный выход)")
        finished = True
    finally:
        close = getattr(source, "close", None)
        if close:
            close()
    msgs.sort(key=lambda m: m.t)
    _save(msgs, cache_path)
    log(f"  чат: {len(msgs)} сообщений (+{new} новых)")
    return msgs, finished


def _iter_chat_downloader(url: str, start: float):
    """YouTube и прочее — через пакет chat-downloader."""
    from chat_downloader import ChatDownloader
    for item in ChatDownloader().get_chat(url, start_time=start if start > 0 else None):
        t = item.get("time_in_seconds")
        if t is None:
            continue
        yield ChatMessage(t=float(t), author=(item.get("author") or {}).get("name", "") or "",
                          text=item.get("message", "") or "")
