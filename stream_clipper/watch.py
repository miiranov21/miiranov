"""Режим слежки: ждёт эфир каналов (Twitch и YouTube) и сам режет хайлайты."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

from . import daily, paths, twitch
from .pipeline import Settings, process_vod


@dataclass
class Source:
    kind: str      # "twitch" | "youtube"
    name: str      # для логов
    target: str    # twitch: логин; youtube: ссылка .../live
    spec: str = "" # как записан в списке — по нему ищем место в очереди


def parse_source(spec: str) -> Source:
    s = spec.strip()
    if twitch.is_youtube(s) or s.startswith(("@", "yt:")):
        url = twitch.youtube_live_url(s)
        name = s[3:] if s.startswith("yt:") else s
        if "v=" in name:
            name = "yt_" + name.split("v=")[1].split("&")[0]
        elif "youtube.com/" in name:
            name = name.split("youtube.com/")[1].split("/")[0]
        return Source("youtube", name.lstrip("@") or "youtube", url, spec)
    login = s.lower().rstrip("/").split("/")[-1]
    return Source("twitch", login, login, login)


def _load(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_priority() -> list[str]:
    try:
        with open(paths.priority_path(), encoding="utf-8") as f:
            return [paths.priority_key(x) for x in json.load(f)]
    except Exception:
        return []


def order_by_priority(sources: list) -> list:
    """Сортируем стримеров по очереди из окна программы (кого нет в очереди — в конец, как были)."""
    prio = load_priority()
    rank = {k: i for i, k in enumerate(prio)}
    return sorted(sources, key=lambda s: (rank.get(paths.priority_key(s.spec or s.target), len(rank)),
                                          sources.index(s)))


def read_channels_file(path: str) -> list[str]:
    """streamers.txt: по одному стримеру в строке, # — комментарий."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            return [ln.split("#")[0].strip() for ln in f if ln.split("#")[0].strip()]
    except OSError:
        return []


def watch(channels: list[str], cfg: Settings, poll: int = 120, live_interval: int = 900,
          record_twitch: bool = False, log=print, reload_file: str | None = None) -> None:
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
    file_mtime = os.path.getmtime(reload_file) if reload_file and os.path.exists(reload_file) else None

    def reload_sources():
        """Список стримеров поменяли на ходу — добавляем новых, убираем удалённых."""
        nonlocal file_mtime
        if not reload_file or not os.path.exists(reload_file):
            return
        mtime = os.path.getmtime(reload_file)
        if mtime == file_mtime:
            return
        file_mtime = mtime
        wanted = [parse_source(c) for c in read_channels_file(reload_file)]
        have = {s.name for s in sources}
        for src in wanted:
            if src.name not in have:
                sources.append(src)
                was_live[src.name], first_check[src.name], last_run[src.name] = False, True, 0.0
                log(f"+ добавлен стример: {src.name} ({src.kind})")
        keep = {s.name for s in wanted}
        for src in [s for s in sources if s.name not in keep]:
            sources.remove(src)
            log(f"- убран стример: {src.name}")
            sess = sessions.pop(src.name, None)
            if sess:  # шла запись эфира — дорезаем записанное
                sess.stop()
                try:
                    sess.process(final=True)
                except Exception as e:
                    log(f"[{src.name}] ошибка: {e}")
                sess.cleanup()
            for d in (was_live, first_check, last_run, rec_mode, vod_checked):
                d.pop(src.name, None)

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
        saved = list(done)

        def on_clip(d):  # сохраняем сразу, чтобы после сбоя не резать то же самое ещё раз
            saved.append(d)
            state[vid] = saved
            if not cfg.dry_run:
                _save(state_path, state)
        # с какого места анализировать этот стрим: выбранное в окне запоминаем для всех следующих проходов
        from .pipeline import parse_start
        key = f"{vid}__from"
        start_at = state.get(key)
        if start_at is None and cfg.start_from and not done:
            start_at = parse_start(cfg.start_from)
        progress: dict = {}
        try:
            new = process_vod(url, cfg, done=done, live=live, log=log, on_clip=on_clip,
                              start_at=start_at, progress=progress)
            if progress.get("start_at") and state.get(key) is None:
                state[key] = progress["start_at"]
                if not cfg.dry_run:
                    _save(state_path, state)
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
            return True
        except Exception as e:
            reason = twitch.explain_youtube_error(e)[1] if src.kind == "youtube" else str(e)[:200]
            log(f"[{src.name}] не смог начать запись: {reason}. Попробую снова через пару минут")
            daily.log_event(cfg.out_dir, f"{src.name}: не смог начать запись — {reason}")
            return False

    try:
        while True:
            reload_sources()
            from .pipeline import refresh_live
            refresh_live(cfg, log)
            ordered = order_by_priority(sources)
            if [x.name for x in ordered] != [x.name for x in sources]:
                log("Порядок обработки: " + " → ".join(x.name for x in ordered))
                sources[:] = ordered
            for src in list(sources):
                if paths.stop_requested():
                    log("Останавливаюсь аккуратно: дорезаю начатое...")
                    raise KeyboardInterrupt
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
                            if start_recorder(src):
                                log(f"[{src.name}] запись идёт с этого момента; первые шортсы — через "
                                    f"{live_interval // 60} мин")
                        elif first_check[src.name]:
                            log(f"[{src.name}] стрим уже идёт — режу то, что было до этого момента")
                            vod_checked[src.name] = True
                            run_vod(src, live=True)
                            last_run[src.name] = time.time()
                    elif rec and src.name not in sessions:
                        if start_recorder(src):  # повторная попытка, если запись не стартовала
                            log(f"[{src.name}] запись началась; первые шортсы — через {live_interval // 60} мин")
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
            # ждём до следующей проверки, но список стримеров ловим сразу
            waited = 0
            while waited < poll:
                if paths.stop_requested():
                    log("Останавливаюсь аккуратно: дорезаю начатое...")
                    raise KeyboardInterrupt
                time.sleep(5)
                waited += 5
                if reload_file and os.path.exists(reload_file) and os.path.getmtime(reload_file) != file_mtime:
                    break
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
