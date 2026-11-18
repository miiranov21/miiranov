"""Режим слежки: ждёт эфир каналов (Twitch и YouTube) и сам режет хайлайты."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

from . import daily, twitch
from .pipeline import Settings, process_vod


@dataclass
class Source:
    kind: str      # "twitch" | "youtube"
    name: str      # для логов
    target: str    # twitch: логин; youtube: ссылка .../live


def parse_source(spec: str) -> Source:
    s = spec.strip()
    if twitch.is_youtube(s) or s.startswith(("@", "yt:")):
        url = twitch.youtube_live_url(s)
        name = s[3:] if s.startswith("yt:") else s
        if "v=" in name:
            name = "yt_" + name.split("v=")[1].split("&")[0]
        elif "youtube.com/" in name:
            name = name.split("youtube.com/")[1].split("/")[0]
        return Source("youtube", name.lstrip("@") or "youtube", url)
    login = s.lower().rstrip("/").split("/")[-1]
    return Source("twitch", login, login)


def _load(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def watch(channels: list[str], cfg: Settings, poll: int = 120, live_interval: int = 900,
          record_twitch: bool = False, log=print) -> None:
    """poll — как часто проверять эфир (сек); live_interval — как часто резать во время эфира
    (0 = только после окончания). record_twitch — писать Twitch-эфир самим (если стример не сохраняет VOD)."""
    sources = [parse_source(c) for c in channels]
    os.makedirs(cfg.work_dir, exist_ok=True)
    state_path = os.path.join(cfg.work_dir, "watch_state.json")
    state = _load(state_path)  # Twitch: {vod_id: [clips...]}
    was_live = {s.name: False for s in sources}
    first_check = {s.name: True for s in sources}
    last_run = {s.name: 0.0 for s in sources}
    sessions: dict = {}  # name -> LiveSession (запись эфира)
    rec_mode: dict = {}  # Twitch-стримеры без записей VOD — пишем их эфир сами
    vod_checked: dict = {}  # проверили ли, что у текущего эфира есть запись
    log("Слежу за: " + ", ".join(f"{s.name} ({s.kind})" for s in sources) + ". Ctrl+C — выход.")

    def uses_recorder(src: Source) -> bool:
        return src.kind == "youtube" or record_twitch or rec_mode.get(src.name, False)

    def current_vod(src: Source, live: bool) -> str | None:
        """Запись ИМЕННО этого эфира (а не старая, если стример отключил сохранение)."""
        try:
            url = twitch.latest_vod_url(src.target)
        except Exception:
            url = None
        if url and live:
            started = (twitch.LAST_LIVE_INFO.get(src.target) or {}).get("timestamp")
            try:
                created = twitch.get_info(url).get("timestamp")
            except Exception:
                created = None
            if started and created and abs(created - started) > 1800:
                return None  # последняя запись — от старого стрима
        return url

    def run_vod(src: Source, live: bool):
        url = current_vod(src, live)
        if not url:
            if live:
                log(f"[{src.name}] стример не сохраняет записи — записываю эфир сам (с этого момента)")
                daily.log_event(cfg.out_dir, f"{src.name}: нет записи стрима, пишу эфир сам")
                rec_mode[src.name] = True
                start_recorder(src)
            else:
                log(f"[{src.name}] запись стрима не найдена")
            return
        vid = twitch.vod_id(url)
        done = state.get(vid, [])
        try:
            new = process_vod(url, cfg, done=done, live=live, log=log)
        except Exception as e:
            log(f"[{src.name}] ошибка обработки: {e}")
            daily.log_event(cfg.out_dir, f"{src.name}: ошибка обработки — {e}")
            return
        state[vid] = done + new
        if not cfg.dry_run:
            _save(state_path, state)
        _report(src, new, live)

    def run_rec(src: Source, final: bool):
        sess = sessions.get(src.name)
        if not sess:
            return
        try:
            new = sess.process(final=final)
        except Exception as e:
            log(f"[{src.name}] ошибка обработки: {e}")
            daily.log_event(cfg.out_dir, f"{src.name}: ошибка обработки — {e}")
            return
        _report(src, new, not final)

    def _report(src, new, live):
        log(f"[{src.name}] новых шортсов: {len(new)}")
        daily.log_event(cfg.out_dir, f"{src.name}: {'проход во время эфира' if live else 'финальный проход'}, "
                                     f"новых шортсов: {len(new)}")

    def start_recorder(src: Source):
        from .live import LiveSession
        url = src.target if src.kind == "youtube" else f"https://www.twitch.tv/{src.target}"
        sess = LiveSession(url, cfg, log=log, max_height=min(cfg.max_height, 1080))
        try:
            sess.start()
            sessions[src.name] = sess
        except Exception as e:
            log(f"[{src.name}] не смог начать запись: {e}")
            daily.log_event(cfg.out_dir, f"{src.name}: не смог начать запись — {e}")

    try:
        while True:
            for src in sources:
                try:
                    live = twitch.youtube_is_live(src.target) if src.kind == "youtube" else twitch.is_live(src.target)
                except Exception as e:
                    log(f"[{src.name}] не смог проверить эфир: {e}")
                    continue
                now = time.time()
                rec = uses_recorder(src)
                if live:
                    if not was_live[src.name]:
                        log(f"[{src.name}] В ЭФИРЕ!")
                        daily.log_event(cfg.out_dir, f"{src.name}: стрим начался"
                                        + (" (запущено посреди эфира)" if first_check[src.name] else ""))
                        last_run[src.name] = now
                        if rec:
                            start_recorder(src)
                            if first_check[src.name]:
                                log(f"[{src.name}] запись идёт с этого момента; первые шортсы — через "
                                    f"{live_interval // 60} мин")
                        elif first_check[src.name]:
                            log(f"[{src.name}] стрим уже идёт — режу то, что было до этого момента")
                            vod_checked[src.name] = True
                            run_vod(src, live=True)
                            last_run[src.name] = time.time()
                    elif rec and src.name not in sessions:
                        start_recorder(src)  # повторная попытка, если запись не стартовала
                    elif not rec and not vod_checked.get(src.name):
                        # через пару минут после начала эфира проверяем, пишет ли Twitch запись
                        vod_checked[src.name] = True
                        if not current_vod(src, True):
                            run_vod(src, live=True)  # переключится на запись эфира
                    elif live_interval and now - last_run[src.name] >= live_interval:
                        log(f"[{src.name}] промежуточная нарезка во время эфира")
                        run_rec(src, final=False) if rec else run_vod(src, live=True)
                        last_run[src.name] = time.time()
                elif was_live[src.name]:
                    log(f"[{src.name}] стрим закончился — финальная нарезка")
                    daily.log_event(cfg.out_dir, f"{src.name}: стрим закончился")
                    if rec:
                        sess = sessions.get(src.name)
                        if sess:
                            sess.stop()
                            run_rec(src, final=True)
                            sess.cleanup()
                            sessions.pop(src.name, None)
                        rec_mode.pop(src.name, None)  # следующий стрим снова пробуем через VOD
                    else:
                        time.sleep(60)  # даём Twitch дописать VOD
                        run_vod(src, live=False)
                    vod_checked.pop(src.name, None)
                was_live[src.name] = live
                first_check[src.name] = False
            time.sleep(poll)
    finally:
        # Ctrl+C посреди эфира: дорезаем то, что записали
        for name, sess in list(sessions.items()):
            log(f"[{name}] останавливаю запись, дорезаю записанное...")
            sess.stop()
            try:
                sess.process(final=True)
            except Exception as e:
                log(f"[{name}] ошибка: {e}")
            sess.cleanup()
