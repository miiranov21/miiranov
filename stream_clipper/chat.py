"""Загрузка и чтение чата Twitch (реплей чата VOD)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict


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


def download_chat(url: str, cache_path: str, refresh: bool = False, log=print) -> list[ChatMessage]:
    """Скачивает реплей чата VOD (с кэшем). refresh=True докачивает новые сообщения
    (нужно для VOD, который ещё идёт в прямом эфире)."""
    msgs: list[ChatMessage] = []
    if os.path.exists(cache_path):
        msgs = load_chat_file(cache_path)
        if not refresh:
            log(f"  чат из кэша: {len(msgs)} сообщений")
            return msgs

    from chat_downloader import ChatDownloader  # импорт тут, чтобы локальный режим работал без пакета

    start = msgs[-1].t if msgs else 0
    seen = {(m.t, m.author, m.text) for m in msgs if m.t >= start}
    log(f"  скачиваю чат с {int(start)} сек...")
    chat = ChatDownloader().get_chat(url, start_time=start if start > 0 else None)
    new = 0
    for item in chat:
        t = item.get("time_in_seconds")
        if t is None:
            continue
        m = ChatMessage(
            t=float(t),
            author=(item.get("author") or {}).get("name", "") or "",
            text=item.get("message", "") or "",
        )
        key = (m.t, m.author, m.text)
        if key in seen:
            continue
        seen.add(key)
        msgs.append(m)
        new += 1
        if new % 5000 == 0:
            log(f"    ...{new} сообщений, позиция {int(m.t // 3600)}ч{int(m.t % 3600 // 60):02d}м")
            _save(msgs, cache_path)  # промежуточное сохранение
    msgs.sort(key=lambda m: m.t)
    _save(msgs, cache_path)
    log(f"  чат: {len(msgs)} сообщений (+{new} новых)")
    return msgs
