"""Командная строка."""
from __future__ import annotations

import argparse
import sys

from .pipeline import Settings, process_local, process_vod


def _common(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("поиск моментов")
    g.add_argument("-n", "--top", type=int, default=10, help="сколько шортсов максимум (по умолч. 10)")
    g.add_argument("--pre", type=float, default=20, help="секунд ДО пика (по умолч. 20)")
    g.add_argument("--post", type=float, default=15, help="секунд ПОСЛЕ пика (по умолч. 15)")
    g.add_argument("--lag", type=int, default=5, help="задержка реакции чата, сек (по умолч. 5)")
    g.add_argument("--min-score", type=float, default=3.0, help="порог «интересности» (меньше = больше клипов)")
    g.add_argument("--no-audio", action="store_true", help="не анализировать громкость (только чат, быстрее)")
    g.add_argument("--audio-weight", type=float, default=0.6, help="вес громкости относительно чата")
    g.add_argument("--keywords", help="файл со своими словами-триггерами (по одному в строке), добавляются к стандартным")
    g = p.add_argument_group("видео")
    g.add_argument("--layout", choices=["blur", "crop", "facecam"], default="blur",
                   help="blur = игра по центру + размытый фон; crop = обрезка по центру; facecam = вебка сверху, игра снизу")
    g.add_argument("--facecam", help="где вебка на исходнике, доли кадра: x,y,w,h (например 0.75,0.70,0.25,0.30)")
    g.add_argument("--zoom", type=float, default=1.0, help="увеличение игры в режиме blur (например 1.4)")
    g.add_argument("--subs", action="store_true", help="авто-субтитры (нужен faster-whisper)")
    g.add_argument("--whisper-model", default="small", help="tiny/base/small/medium/large-v3")
    g.add_argument("--lang", default=None, help="язык речи (ru, en...). По умолчанию — автоопределение")
    g.add_argument("--preset", default="medium", help="скорость кодирования x264: ultrafast..slow (быстрее = файл больше)")
    g.add_argument("--max-height", type=int, default=1080, help="макс. качество исходника (720/1080)")
    p.add_argument("-o", "--out", default="output",
                   help="корневая папка: внутри создаются папки по датам ДД.ММ.ГГГГ с шортсами, отчётом и zip")
    p.add_argument("--cookies-browser", help="брать куки из браузера (chrome/firefox/edge) — если YouTube просит войти")
    p.add_argument("--dry-run", action="store_true", help="только найти моменты и сделать отчёт, без нарезки")
    p.add_argument("--keep-raw", action="store_true", help="не удалять исходные горизонтальные куски")


def _settings(a) -> Settings:
    cfg = Settings(out_dir=a.out, top=a.top, clip_pre=a.pre, clip_post=a.post, chat_lag=a.lag,
                   min_score=a.min_score, audio=not a.no_audio, audio_weight=a.audio_weight,
                   layout=a.layout, zoom=a.zoom, subs=a.subs, whisper_model=a.whisper_model,
                   language=a.lang, max_height=a.max_height, dry_run=a.dry_run, keep_raw=a.keep_raw,
                   preset=a.preset)
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
    w.add_argument("channels", nargs="+",
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
    r.add_argument("-o", "--out", default="output")

    a = p.parse_args(argv)
    if a.cmd == "report":
        from . import daily
        folder = daily.day_dir(a.out, a.date)
        print("Отчёт:", daily.write_day_report(folder))
        print("Архив:", daily.build_zip(folder) or "нет шортсов за этот день")
        return
    cfg = _settings(a)
    if a.cookies_browser:
        from . import twitch
        twitch.set_cookies_browser(a.cookies_browser)
    try:
        if a.cmd == "vod":
            for u in a.urls:
                process_vod(u, cfg)
        elif a.cmd == "watch":
            from .watch import watch
            watch(a.channels, cfg, poll=a.poll, live_interval=a.live_every * 60, record_twitch=a.record)
        else:
            process_local(a.video, a.chat, cfg)
    except KeyboardInterrupt:
        print("\nОстановлено.")


if __name__ == "__main__":
    main()
