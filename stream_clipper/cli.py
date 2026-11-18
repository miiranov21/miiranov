"""Командная строка."""
from __future__ import annotations

import argparse
import sys

from . import paths
from .pipeline import Settings, process_local, process_vod


def _common(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("поиск моментов")
    g.add_argument("-n", "--top", type=int, default=3, help="сколько клипов на каждый час стрима (по умолч. 3)")
    g.add_argument("--pre", type=float, default=20, help="секунд ДО пика (по умолч. 20)")
    g.add_argument("--post", type=float, default=15, help="секунд ПОСЛЕ пика (по умолч. 15)")
    g.add_argument("--lag", type=int, default=5, help="задержка реакции чата, сек (по умолч. 5)")
    g.add_argument("--min-score", type=float, default=3.0, help="порог «интересности» (меньше = больше клипов)")
    g.add_argument("--no-audio", action="store_true", help="не анализировать громкость (только чат, быстрее)")
    g.add_argument("--audio-weight", type=float, default=0.6, help="вес громкости относительно чата")
    g.add_argument("--keywords", help="файл со своими словами-триггерами (по одному в строке), добавляются к стандартным")
    g = p.add_argument_group("видео")
    g.add_argument("--layout", choices=["auto", "blur", "crop", "facecam"], default="auto",
                   help="auto = сама ищет вебку стримера и ставит её сверху (иначе blur); blur = игра на размытом фоне; "
                        "crop = обрезка по центру; facecam = вебка сверху по координатам --facecam")
    g.add_argument("--no-caption", action="store_true", help="без плашки с подписью")
    g.add_argument("--watermark-text", default="", help="водяной знак текстом, например @мой_канал")
    g.add_argument("--watermark-image", default="", help="водяной знак картинкой (PNG с прозрачностью)")
    g.add_argument("--watermark-pos", choices=["corner", "center", "moving"], default="moving",
                   help="где знак: corner — в углу, center — по центру, moving — плавает по экрану")
    g.add_argument("--watermark-opacity", type=float, default=0.4, help="непрозрачность знака 0.1–1 (по умолч. 0.4)")
    g.add_argument("--facecam", help="где вебка на исходнике, доли кадра: x,y,w,h (например 0.75,0.70,0.25,0.30)")
    g.add_argument("--zoom", type=float, default=1.0, help="(устарело, см. --game-view) увеличение игры")
    g.add_argument("--game-view", choices=["full", "wide", "center"], default="full",
                   help="сколько игры видно: full — целиком, wide — крупнее (≈75%% ширины), center — только центр")
    g.add_argument("--subs", action="store_true", default=None,
                   help="авто-субтитры (по умолчанию включаются сами, если установлен faster-whisper)")
    g.add_argument("--no-subs", dest="subs", action="store_false", help="без субтитров")
    g.add_argument("--whisper-model", default="small", help="tiny/base/small/medium/large-v3")
    g.add_argument("--lang", default=None, help="язык речи (ru, en...). По умолчанию — автоопределение")
    g.add_argument("--preset", default="medium", help="скорость кодирования x264: ultrafast..slow (быстрее = файл больше)")
    g.add_argument("--max-height", type=int, default=1080, help="макс. качество исходника (720/1080)")
    p.add_argument("-o", "--out", default=None,
                   help="куда складывать клипы (по умолчанию Рабочий стол\\YouTube): папки ДД.ММ.ГГГГ\\стример\\клипы")
    p.add_argument("--cookies-browser", help="брать куки из браузера (chrome/firefox/edge) — если YouTube просит войти")
    p.add_argument("--dry-run", action="store_true", help="только найти моменты и сделать отчёт, без нарезки")
    p.add_argument("--keep-raw", action="store_true", help="не удалять исходные горизонтальные куски")


def _settings(a) -> Settings:
    cfg = Settings(out_dir=a.out or paths.default_out_dir(), top=a.top, clip_pre=a.pre, clip_post=a.post, chat_lag=a.lag,
                   min_score=a.min_score, audio=not a.no_audio, audio_weight=a.audio_weight,
                   layout=a.layout, zoom=a.zoom, subs=a.subs, whisper_model=a.whisper_model,
                   language=a.lang, max_height=a.max_height, dry_run=a.dry_run, keep_raw=a.keep_raw,
                   preset=a.preset, caption=not a.no_caption, game_view=a.game_view,
                   watermark_text=a.watermark_text, watermark_image=a.watermark_image,
                   watermark_pos=a.watermark_pos, watermark_opacity=a.watermark_opacity)
    if a.facecam:
        try:
            cfg.facecam = tuple(float(x) for x in a.facecam.split(","))
            assert len(cfg.facecam) == 4
        except Exception:
            sys.exit("--facecam: нужно 4 числа через запятую, например 0.75,0.70,0.25,0.30")
    if cfg.layout == "facecam" and not cfg.facecam:
        sys.exit("для --layout facecam укажи --facecam x,y,w,h")
    if a.keywords:
        with open(a.keywords, encoding="utf-8") as f:
            cfg.hype_words += [w.strip().lower() for w in f if w.strip()]
    return cfg


def _vod_with_memory(url: str, cfg) -> None:
    """Нарезка по ссылке с памятью: после перезапуска уже готовые клипы не режутся заново."""
    import json
    import os
    path = os.path.join(cfg.work_dir, "vod_state.json")
    try:
        state = json.load(open(path, encoding="utf-8"))
    except Exception:
        state = {}
    done = state.get(url, [])
    if done:
        print(f"Продолжаю: по этой ссылке уже готово клипов: {len(done)}")

    def on_clip(d):
        state.setdefault(url, []).append(d)
        os.makedirs(cfg.work_dir, exist_ok=True)
        if not cfg.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False)
    state.setdefault(url, list(done))
    process_vod(url, cfg, done=done, on_clip=on_clip)


def _channels_from_file() -> list[str]:
    """streamers.txt в папке программы: по одному стримеру в строке, # — комментарий."""
    import os
    for path in (os.path.join(paths.program_dir(), "streamers.txt"),
                 os.path.join(paths.default_work_dir(), "streamers.txt")):  # запасная копия
        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as f:
                names = [ln.split("#")[0].strip() for ln in f if ln.split("#")[0].strip()]
            if names:
                return names
    return []


def main(argv=None) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(prog="python -m stream_clipper",
                                description="Автонарезка хайлайтов из Twitch-стримов в YouTube Shorts")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("vod", help="обработать запись стрима (twitch.tv/videos/... или youtube.com/watch?v=...)")
    v.add_argument("urls", nargs="+")
    _common(v)

    w = sub.add_parser("watch", help="следить за каналами и резать автоматически")
    w.add_argument("channels", nargs="*",
                   help="Twitch: логин (kaicenat). YouTube: @handle или ссылка на канал (@MrBeast, https://www.youtube.com/@xyz)")
    w.add_argument("--record", action="store_true",
                   help="Twitch: записывать эфир самим (для стримеров, которые не сохраняют VOD)")
    w.add_argument("--poll", type=int, default=120, help="проверять эфир каждые N сек")
    w.add_argument("--live-every", type=int, default=15,
                   help="резать во время эфира каждые N минут (0 = только после стрима)")
    _common(w)

    l = sub.add_parser("local", help="обработать скачанное видео + файл чата")
    l.add_argument("video")
    l.add_argument("chat", help="JSON чата (TwitchDownloader или формат этой программы)")
    _common(l)

    r = sub.add_parser("report", help="пересобрать отчёт и zip за день")
    r.add_argument("date", nargs="?", help="ДД.ММ.ГГГГ (по умолчанию сегодня)")
    r.add_argument("-o", "--out", default=None)

    a = p.parse_args(argv)
    from . import daily
    daily.set_state_dir(paths.default_work_dir())
    if a.cmd == "report":
        folder = daily.day_dir(a.out or paths.default_out_dir(), a.date)
        print("Отчёт:", daily.write_day_report(folder))
        print("Архив:", daily.build_zip(folder) or "нет шортсов за этот день")
        return
    cfg = _settings(a)
    print(f"Клипы будут здесь: {cfg.out_dir}")
    from .ffmpeg_setup import ensure_ffmpeg
    if not ensure_ffmpeg():
        sys.exit(1)
    if a.cookies_browser:
        from . import twitch
        twitch.set_cookies_browser(a.cookies_browser)
    try:
        import os
        for p in (paths.stop_request_path(), paths.live_settings_path()):
            try:
                os.remove(p)  # старые сигналы/настройки от прошлого запуска не должны мешать
            except OSError:
                pass
        if a.cmd == "vod":
            for u in a.urls:
                _vod_with_memory(u, cfg)
                if paths.stop_requested():
                    break
        elif a.cmd == "watch":
            from .watch import watch
            channels = a.channels or _channels_from_file()
            if not channels:
                sys.exit("Не указаны стримеры. Впиши их в streamers.txt (по одному в строке)")
            import os
            reload_file = None if a.channels else os.path.join(paths.program_dir(), "streamers.txt")
            watch(channels, cfg, poll=a.poll, live_interval=a.live_every * 60, record_twitch=a.record,
                  reload_file=reload_file)
        else:
            process_local(a.video, a.chat, cfg)
    except KeyboardInterrupt:
        print("\nОстановлено.")
    except Exception as e:
        msg = str(e).replace("ERROR: ", "")
        hint = ""
        low = msg.lower()
        if any(w in low for w in ("ssl", "proxy", "connection", "timed out", "eof occurred", "getaddrinfo")):
            hint = "\nПохоже, нет связи с сайтом: проверь интернет и VPN (сервер, на котором открывается Twitch)."
        print(f"\nОШИБКА: {msg[:400]}{hint}")
        sys.exit(1)


if __name__ == "__main__":
    main()
