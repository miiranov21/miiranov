"""Режим слежки: ждёт эфир канала и сам режет хайлайты, пока ты спишь."""
from __future__ import annotations

import json
import os
import time

from . import twitch
from .pipeline import Settings, process_vod


def _load(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def watch(channels: list[str], cfg: Settings, poll: int = 120, live_interval: int = 1800, log=print) -> None:
    """poll — как часто проверять эфир (сек); live_interval — как часто резать во время эфира
    (0 = только после окончания стрима)."""
    os.makedirs(cfg.out_dir, exist_ok=True)
    state_path = os.path.join(cfg.out_dir, "watch_state.json")
    state = _load(state_path)  # {vod_id: [clips...]}
    was_live = {c: False for c in channels}
    last_run = {c: 0.0 for c in channels}
    log(f"Слежу за: {', '.join(channels)}. Ctrl+C — выход.")

    def run(channel, live):
        url = twitch.latest_vod_url(channel)
        if not url:
            log(f"[{channel}] VOD не найден (возможно, стример отключил сохранение записей)")
            return
        vid = twitch.vod_id(url)
        done = state.get(vid, [])
        try:
            new = process_vod(url, cfg, done=done, live=live, log=log)
        except Exception as e:
            log(f"[{channel}] ошибка обработки: {e}")
            return
        state[vid] = done + new
        _save(state_path, state)
        log(f"[{channel}] новых шортсов: {len(new)}")

    while True:
        for ch in channels:
            try:
                live = twitch.is_live(ch)
            except Exception as e:
                log(f"[{ch}] не смог проверить эфир: {e}")
                continue
            now = time.time()
            if live:
                if not was_live[ch]:
                    log(f"[{ch}] В ЭФИРЕ!")
                    last_run[ch] = now  # первая нарезка через live_interval
                elif live_interval and now - last_run[ch] >= live_interval:
                    log(f"[{ch}] промежуточная нарезка во время эфира")
                    run(ch, live=True)
                    last_run[ch] = time.time()
            elif was_live[ch]:
                log(f"[{ch}] стрим закончился — финальная нарезка")
                time.sleep(60)  # даём Twitch дописать VOD
                run(ch, live=False)
            was_live[ch] = live
        time.sleep(poll)
