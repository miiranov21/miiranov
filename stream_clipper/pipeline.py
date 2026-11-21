"""Полный цикл: чат -> звук -> поиск моментов -> скачивание кусков -> вертикальные Shorts."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from . import daily, detect, paths, render
from .paths import parse_start  # noqa: F401  (используется в cli/watch через pipeline)
from .chat import ChatMessage, download_chat, load_chat_file


@dataclass
class Settings:
    out_dir: str = field(default_factory=lambda: paths.default_out_dir())
    work_dir: str = field(default_factory=lambda: paths.default_work_dir())
    top: int = 3              # клипов на каждый час стрима
    clip_pre: float = 20
    clip_post: float = 15
    chat_lag: int = 5
    min_score: float = 3.0
    audio: bool = True
    audio_weight: float = 0.6
    layout: str = "auto"      # auto = вебка сверху, если найдена, иначе blur
    facecam: tuple | None = None
    zoom: float = 1.0
    subs: bool | None = None  # None = включать сами, если установлен faster-whisper
    whisper_model: str = "small"
    language: str | None = None
    max_height: int = 1080
    dry_run: bool = False
    keep_raw: bool = False
    preset: str = "medium"
    caption: bool = True      # плашка с подписью к моменту
    game_view: str = "full"   # игра в кадре: full — целиком, wide — крупнее, center — только центр, auto — по кадрам
    start_from: str | None = None  # с какого места стрима начать анализ: «1:30», «сейчас» или пусто — с начала
    auto_length: bool = False  # длина под момент (12–45 с): клип идёт, пока длится реакция
    credit: bool = False      # сразу вшивать подпись автора «Twitch | KaiCenat» (иначе — галочкой на нужных клипах)
    credit_pos: str = "top-left"  # top-left | top-right | bottom-left (внизу её закрывает интерфейс площадок)
    watermark_text: str = ""  # водяной знак текстом, например "@мой_канал"
    watermark_image: str = "" # водяной знак картинкой (PNG)
    watermark_pos: str = "moving"   # corner | center | moving
    watermark_opacity: float = 0.4
    per_streamer: dict = field(default_factory=dict)  # настройки «Доктора» под конкретного стримера (по нику)
    no_facecam_fallback: dict = field(default_factory=dict)  # что менять, если вебка не найдена (от «Доктора»)
    hype_words: list = field(default_factory=lambda: list(detect.DEFAULT_HYPE))


def _fmt(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:d}h{s % 3600 // 60:02d}m{s % 60:02d}s"


def _overlaps(h, done: list[dict], thr: float = 0.5) -> bool:
    for d in done:
        inter = min(h.end, d["end"]) - max(h.start, d["start"])
        if inter > thr * min(h.end - h.start, d["end"] - d["start"]):
            return True
    return False


def write_report(folder: str, clips: list[dict], source: str, link_fn=None) -> None:
    lines = [f"# Хайлайты: {source}\n"]
    for i, c in enumerate(sorted(clips, key=lambda c: c["start"]), 1):
        lines.append(f"## {i}. {_fmt(c['start'])} – {_fmt(c['end'])}  (score {c['score']})")
        if link_fn:
            lines.append(f"- Twitch: {link_fn(c['start'])}")
        if c.get("file"):
            lines.append(f"- Файл: {os.path.basename(c['file'])}")
        lines.append(f"- чат z={c['chat_z']}, звук z={c['audio_z']}")
        if c.get("top_messages"):
            lines.append("- Что писал чат: " + " | ".join(c["top_messages"]))
        lines.append("")
    with open(os.path.join(folder, "highlights.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(folder, "highlights.json"), "w", encoding="utf-8") as f:
        json.dump(clips, f, ensure_ascii=False, indent=2)


def _make_short(segment: str, out: str, cfg: Settings, log, meta: dict | None = None) -> str:
    """Собирает вертикальный клип. Возвращает подпись (или '')."""
    meta = meta or {}
    cfg = _for_streamer(cfg, meta.get("streamer", ""), log)
    peak = float(cfg.clip_pre) + float((meta.get("pad") or (0, 0))[0])  # где пик момента внутри куска
    trimmed = None
    if cfg.auto_length and meta.get("pad"):
        # длина под момент: начало и конец — в паузы речи (не с середины фразы и не на середине слова)
        from . import shape
        try:
            pa, pb = meta["pad"]
            a, b = shape.snap_bounds(segment, pa, pb)
            if a > 0.05 or b < shape._duration(segment) - 0.05:
                trimmed = shape.trim(segment, a, b, os.path.splitext(segment)[0] + "_trim.mp4")
                segment = trimmed
                meta["trim"] = (a, b)
                peak -= a
        except Exception as e:
            log(f"    границы по паузам не поставились ({e}) — оставляю как есть")
    if meta.get("check_quality", True) and not meta.get("caption_text"):
        try:  # настоящий пик — самая громкая реакция стримера рядом с всплеском чата (чат запаздывает)
            from .shape import voice_energy
            e = voice_energy(segment)
            i0, i1 = max(0, int((peak - 2.0) / 0.05)), min(e.size, int((peak + 3.0) / 0.05))
            if i1 - i0 > 10:
                loud = (i0 + int(np.argmax(e[i0:i1]))) * 0.05
                if abs(loud - peak) > 0.2:
                    meta["peak_shift"] = round(loud - peak, 2)
                    peak = loud
        except Exception:
            pass
        from . import quality as _q0
        from .shape import defaults as _cd
        why = _q0.first_seconds_check(segment, peak, _cd().get("cold_open") is True)
        if why:
            raise ClipRejected(why)
    meta["peak_off"] = peak
    layout, facecam = cfg.layout, cfg.facecam
    if layout == "auto":
        from .facecam import resolve
        try:
            facecam = cfg.facecam or resolve(meta.get("streamer", ""), segment, log=log)
        except Exception as e:
            log(f"    поиск вебки не удался: {e}")
            facecam = None
        layout = "facecam" if facecam else "blur"
        log(f"    вебка {'найдена — ставлю её сверху' if facecam else 'не найдена — игра на размытом фоне'}")
        if not facecam and cfg.no_facecam_fallback:
            import copy
            cfg = copy.copy(cfg)
            fb = {k: v for k, v in cfg.no_facecam_fallback.items() if k not in ("layout", "facecam")}
            ch = apply_settings(cfg, fb)
            if ch:
                log("    без вебки — по совету «Доктора»: " + ", ".join(ch))
    base = os.path.splitext(out)[0]
    q_vis = None
    if meta.get("check_quality", True) and not meta.get("caption_text"):
        from . import quality as _q
        lag = _q.lag_check(segment)  # стоп-кадры (лаг стрима, реклама, рваная запись) — такой клип не нужен
        if lag:
            raise ClipRejected(lag)
        from . import quality
        if quality.enabled():
            q_vis = quality.visual_metrics(segment, facecam if layout == "facecam" else None)
            will_subs = cfg.subs if cfg.subs is not None else __import__("stream_clipper.subtitles",
                                                                             fromlist=["available"]).available()
            if not will_subs:  # без субтитров решаем сразу — по голосовой полосе
                v = quality.voice_ratio_energy(segment)
                why = quality.verdict(q_vis, v, layout == "facecam", by_energy=True)
                if why:
                    raise ClipRejected(f"{why} (голос {v:.0%})")
                q_vis = None
    if cfg.game_view not in ("full", "wide", "center"):  # auto — выбираем по кадрам этого момента
        import copy
        from . import shape
        from .caption import _api_key
        key = _api_key()
        fr = _moment_frames(segment, peak, base + ".gv") if key else []
        try:
            gv, why = shape.choose_view(segment, peak, key, fr, facecam if layout == "facecam" else None, log)
        finally:
            for p_ in fr:
                try:
                    os.remove(p_)
                except OSError:
                    pass
        cfg = copy.copy(cfg)
        cfg.game_view = gv
        log(f"    кадр: {shape.VIEW_NAMES.get(gv, gv)} — {why}")
    ass_files, transcript = [], ""
    use_subs = cfg.subs
    if use_subs is None:
        from .subtitles import available
        use_subs = available()
    if use_subs:
        log("    распознаю речь для субтитров...")
        try:
            transcript = render_subs(segment, base + ".ass", cfg)
            if transcript:
                ass_files.append(base + ".ass")
                log(f"    субтитры готовы ({len(transcript.split())} слов)")
            else:
                log("    субтитры: в клипе не нашлось речи (стример молчит или музыка заглушает)")
        except Exception as e:  # субтитры — не критично
            log(f"    субтитры не получились: {type(e).__name__}: {e}")
    elif cfg.subs is None:
        log("    субтитры выключены: не установлено распознавание речи (запусти install_subs.bat)")
    if q_vis is not None:  # есть субтитры — голос стримера считаем по словам (озвучка донатов не в счёт)
        from . import quality, subtitles as _sb
        words_now = list(_sb.LAST_WORDS) if transcript else []
        v = quality.voice_ratio_words(words_now, quality.duration(segment)) if words_now else \
            quality.voice_ratio_energy(segment) * 0.5
        why = quality.verdict(q_vis, v, layout == "facecam", by_energy=not words_now)
        if why:
            for p_ in ass_files:
                try:
                    os.remove(p_)
                except OSError:
                    pass
            raise ClipRejected(f"{why} (голос {v:.0%})")
    if meta.get("check_quality", True) and not meta.get("caption_text"):
        from . import quality, subtitles as _sb2
        if quality.enabled():  # вторая, строгая проверка: сумма признаков сна (темно, всё стоит, лицо неподвижно…)
            why, _m = quality.deep_check(segment, list(_sb2.LAST_WORDS) if transcript else [],
                                         meta.get("title", ""), meta.get("top_messages") or [])
            if why:
                for p_ in ass_files:
                    try:
                        os.remove(p_)
                    except OSError:
                        pass
                raise ClipRejected(why)
    text = ""
    if cfg.caption:
        from .caption import _api_key, make_caption, streamer_quote
        center = peak  # пик момента внутри клипа
        quote = None
        if transcript:
            from . import subtitles
            quote = streamer_quote(subtitles.LAST_WORDS, center)
        keep_text = meta.get("caption_text")  # перерезка клипа: надпись оставляем ту же
        frames = _moment_frames(segment, center, base) if _api_key() and not keep_text else []
        from . import shape as _sh
        try:
            pfrac = peak / max(1.0, _sh._duration(segment))
        except Exception:
            pfrac = None
        cdef = _sh.defaults()
        text = keep_text or make_caption(meta.get("streamer", ""), meta.get("title", ""), meta.get("top_messages", []),
                                         transcript, meta.get("lang", "en"), log=log, frames=frames, quote=quote,
                                         peak_frac=pfrac, cold_open=cdef.get("cold_open") is True,
                                         question=bool(cdef.get("question_overlay")))
        for p in frames:
            try:
                os.remove(p)
            except OSError:
                pass
        log(f"    подпись: {text}")
        ass_files.append(render.write_caption_ass(base + ".caption.ass", text,
                                                  render.caption_y(layout, cfg.zoom, game_view=cfg.game_view)))
    if cfg.credit and meta.get("credit_name"):
        # чей это стрим — платформа и ник автора (уважение к автору и правилам площадок)
        ass_files.insert(0, render.write_credit_ass(base + ".credit.ass", meta.get("platform", ""),
                                                    meta["credit_name"], cfg.credit_pos))
    if cfg.watermark_text.strip():
        # знак ставим под надписью-плашкой, чтобы не закрывал её
        ass_files.insert(len(ass_files) - (1 if text else 0),
                         render.write_watermark_ass(base + ".wm.ass", cfg.watermark_text.strip(),
                                                    cfg.watermark_pos, cfg.watermark_opacity,
                                                    credit_pos=cfg.credit_pos if cfg.credit else "",
                                                    caption_y=render.caption_y(layout, cfg.zoom,
                                                                               game_view=cfg.game_view)
                                                    if text else None))
    meta["transcript"] = transcript[:800]
    if transcript:
        from . import subtitles as _subs
        meta["words"] = [[round(a, 2), round(b, 2), w] for a, b, w in _subs.LAST_WORDS]
    if cfg.caption:
        from .caption import LAST_SCORE
        meta["ai_score"] = LAST_SCORE.get("value")
    face_peak = None
    try:
        from .shape import trick
        if layout == "facecam" and trick("face_fullscreen_on_peak") and peak > 0.3:
            face_peak = (max(0.0, peak - 0.1), peak + 0.7)  # лицо на весь кадр на пике
            meta["face_peak"] = True
    except Exception:
        pass
    render.render_vertical(segment, out, layout, facecam, cfg.zoom, ass_files, cfg.preset,
                           logo=cfg.watermark_image or None, logo_pos=cfg.watermark_pos,
                           logo_opacity=cfg.watermark_opacity, logo_with_text=bool(cfg.watermark_text.strip()),
                           game_view=cfg.game_view, face_peak=face_peak)
    for p in ass_files + ([trimmed] if trimmed else []):
        try:
            os.remove(p)
        except OSError:
            pass
    try:
        from . import shape
        log(f"📐 длина {round(shape._duration(out))} с, кадр: {shape.VIEW_NAMES.get(cfg.game_view, cfg.game_view)}")
    except Exception:
        pass
    return text


def _apply_trim(d: dict, meta: dict) -> None:
    """Границы клипа сдвинулись в паузы речи — поправляем время клипа в записи стрима (для перерезки и ссылок)."""
    if meta.get("peak_shift") and d.get("peak") is not None:
        d["peak"] = round(float(d["peak"]) + float(meta["peak_shift"]), 2)
    tr = meta.get("trim")
    if tr:
        s0 = float(d.get("start", 0))
        d["start"], d["end"] = round(s0 + tr[0], 2), round(s0 + tr[1], 2)


def _moment_frames(segment: str, center: float, base: str) -> list[str]:
    """3 кадра из момента (до, пик, после) — Claude по ним видит, что происходит на экране."""
    import subprocess
    out = []
    flags = 0x08000000 if os.name == "nt" else 0
    try:  # длина клипа — чтобы не просить кадры за его концом (короткие клипы)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", segment],
                           capture_output=True, text=True, creationflags=flags)
        dur = float(r.stdout.strip())
        if center > dur - 1:
            center = dur * 0.6
    except Exception:
        dur = None
    step = 3 if not dur or dur > 12 else max(0.5, dur / 5)
    for i, t in enumerate((center - step, center, center + step)):
        p = f"{base}.frame{i}.jpg"
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", segment,
                            "-frames:v", "1", "-vf", "scale=768:-2", "-q:v", "4", p],
                           capture_output=True, creationflags=flags)
        if r.returncode == 0 and os.path.exists(p):
            out.append(p)
    return out


def render_subs(segment: str, ass: str, cfg: Settings) -> str:
    from .subtitles import make_ass
    return make_ass(segment, ass, cfg.whisper_model, cfg.language)


def apply_settings(cfg: Settings, live: dict) -> list[str]:
    """Применяет словарь настроек (из окна или от «Доктора») к cfg. Возвращает, что поменялось (по-русски)."""
    changed = []
    top = live.get("top")
    if isinstance(top, int) and not isinstance(top, bool) and top > 0 and top != cfg.top:
        cfg.top = top
        changed.append(f"клипов за час: {top}")
    pre, post = live.get("pre"), live.get("post")
    length = live.get("length")
    if (pre is None or post is None) and isinstance(length, (int, float)) and not isinstance(length, bool) \
            and length > 0:
        pre = max(2, round(length * 0.57))
        post = max(2, length - pre)
    if isinstance(pre, (int, float)) and isinstance(post, (int, float)) and pre > 0 and post > 0 \
            and (pre, post) != (cfg.clip_pre, cfg.clip_post):
        cfg.clip_pre, cfg.clip_post = float(pre), float(post)
        changed.append(f"длина клипа: {int(pre + post)} с")
    credit, cpos = live.get("credit"), live.get("credit_pos")
    if isinstance(credit, bool) and credit != cfg.credit:
        cfg.credit = credit
        changed.append("подпись автора: " + ("вкл" if credit else "выкл"))
    if cpos in render.CREDIT_POS and cpos != cfg.credit_pos:
        cfg.credit_pos = cpos
        changed.append("подпись автора перенесена")
    names = {"subs": "субтитры", "caption": "надпись-плашка", "audio": "поиск по звуку и картинке"}
    for key, name in names.items():
        val = live.get(key)
        if isinstance(val, bool) and val != bool(getattr(cfg, key)):
            setattr(cfg, key, val)
            changed.append(f"{name}: {'вкл' if val else 'выкл'}")
    fc = live.get("facecam")
    lay = live.get("layout")
    if lay in ("auto", "blur", "crop") and lay != cfg.layout:
        cfg.layout = lay
        changed.append(f"раскладка: {lay}")
    elif isinstance(fc, bool) and lay is None and fc != (cfg.layout != "blur"):
        cfg.layout = "auto" if fc else "blur"
        changed.append(f"вебка сверху: {'вкл' if fc else 'выкл'}")
    al = live.get("auto_length")
    if isinstance(al, bool) and al != cfg.auto_length:
        cfg.auto_length = al
        changed.append(f"длина под момент: {'вкл' if al else 'выкл'}")
    gv = live.get("game_view")
    if gv in ("full", "wide", "center", "auto") and gv != cfg.game_view:
        cfg.game_view = gv
        changed.append(f"игра в кадре: {gv}")
    q = live.get("quality")
    if isinstance(q, int) and q in (720, 1080) and q != cfg.max_height:
        cfg.max_height = q
        changed.append(f"качество: {q}")
    if "watermark_text" in live and isinstance(live["watermark_text"], str) \
            and live["watermark_text"].strip() != cfg.watermark_text.strip():
        cfg.watermark_text = live["watermark_text"].strip()
        changed.append(f"водяной знак: {cfg.watermark_text or 'выкл'}")
    wp = live.get("watermark_pos")
    if wp in render.WM_POSITIONS and wp != cfg.watermark_pos:
        cfg.watermark_pos = wp
        changed.append(f"знак: {wp}")
    wo = live.get("watermark_opacity")
    if isinstance(wo, (int, float)) and not isinstance(wo, bool) and 0.05 <= wo <= 1 \
            and abs(wo - cfg.watermark_opacity) > 1e-3:
        cfg.watermark_opacity = float(wo)
        changed.append(f"заметность знака: {wo}")
    return changed


def refresh_live(cfg: Settings, log=print) -> None:
    """Подхватываем настройки, изменённые в окне во время работы (или выбранные «Доктором»)."""
    try:
        with open(paths.live_settings_path(), encoding="utf-8") as f:
            live = json.load(f)
    except Exception:
        return
    changed = apply_settings(cfg, live)
    ps = live.get("per_streamer")
    ps = {str(k).lower().lstrip("@"): v for k, v in ps.items() if isinstance(v, dict)} if isinstance(ps, dict) else {}
    if ps != cfg.per_streamer:
        cfg.per_streamer = ps
        if ps:
            changed.append("свои настройки для: " + ", ".join(ps))
    fb = live.get("no_facecam_fallback")
    fb = fb if isinstance(fb, dict) else ({"game_view": fb} if fb in ("full", "wide", "center", "auto") else {})
    if fb != cfg.no_facecam_fallback:
        cfg.no_facecam_fallback = fb
    if changed:
        log("Новые настройки подхвачены: " + ", ".join(changed))


def _for_streamer(cfg: Settings, streamer: str, log=print) -> Settings:
    """Копия настроек с переопределениями «Доктора» для этого стримера (если есть)."""
    over = (cfg.per_streamer or {}).get((streamer or "").lower().lstrip("@"))
    if not over:
        return cfg
    import copy
    c = copy.copy(cfg)
    ch = apply_settings(c, over)
    if ch:
        log(f"    для {streamer} — свои настройки: " + ", ".join(ch))
    return c


class MediaAnalysis:
    """Громкость и «резкость смены картинки» по секундам стрима, собираемые кусками по ходу работы."""
    CHUNK = 1800

    def __init__(self, url: str, work: str, log=print):
        self.url, self.work, self.log = url, work, log
        self.a = np.full(0, np.nan, dtype=np.float32)
        self.v = np.full(0, np.nan, dtype=np.float32)
        self.done_chunks: set = set()
        self.failed = 0
        self.announced = False

    def _grow(self, n: int):
        if n > self.a.size:
            self.a = np.concatenate([self.a, np.full(n - self.a.size, np.nan, dtype=np.float32)])
            self.v = np.concatenate([self.v, np.full(n - self.v.size, np.nan, dtype=np.float32)])

    def put(self, offset: int, audio, visual):
        for arr_name, data in (("a", audio), ("v", visual)):
            if data is None or not len(data):
                continue
            self._grow(offset + len(data))
            getattr(self, arr_name)[offset:offset + len(data)] = data

    def cover(self, lo: float, hi: float):
        """Убедиться, что для отрезка [lo, hi] звук и картинка посчитаны (качает недостающие куски)."""
        from . import twitch
        from .audio import loudness_per_second, scene_per_second
        if self.failed >= 3:
            return
        for c in range(int(max(0, lo)) // self.CHUNK, int(hi) // self.CHUNK + 1):
            s, e = c * self.CHUNK, min((c + 1) * self.CHUNK, int(hi))
            full = e == (c + 1) * self.CHUNK
            if (c, full) in self.done_chunks or e - s < 60:
                continue
            npz = os.path.join(self.work, f"media_{s}_{e}.npz")
            try:
                if os.path.exists(npz):
                    d = np.load(npz)
                    aud, vis = d["a"], d["v"]
                else:
                    if not self.announced:
                        self.log("  анализирую звук и картинку стрима (облегчённое видео, по кускам)...")
                        self.announced = True
                    f = twitch.download_analysis_section(self.url, s, e, os.path.join(self.work, f"media_{s}_{e}"))
                    aud, vis = loudness_per_second(f), scene_per_second(f)
                    os.remove(f)
                    if full:
                        np.savez(npz, a=aud, v=vis)
                self.put(s, aud, vis)
                self.done_chunks.add((c, full))
            except Exception as e:
                self.failed += 1
                self.log(f"  звук/картинка для {s // 60}–{e // 60} мин не получились ({e}) — режу по чату")

    def _filled(self, arr, n: int):
        if not np.isfinite(arr).any():
            return None
        out = np.full(n, np.nanmedian(arr), dtype=np.float32)
        m = min(n, arr.size)
        seg = arr[:m]
        out[:m] = np.where(np.isfinite(seg), seg, out[:m])
        return out

    def audio(self, n: int):
        return self._filled(self.a, int(n) + 1)

    def visual(self, n: int):
        v = self._filled(self.v, int(n) + 1)
        return v


def clip_budget(per_hour: int, seconds: float) -> int:
    """Сколько клипов положено на столько-то секунд стрима («клипов за час стрима»)."""
    import math
    return max(1, math.ceil(per_hour * max(seconds, 0) / 3600))


class ClipRejected(Exception):
    """Момент не прошёл фильтры качества (стример спит, отошёл, молчит при неподвижной картинке)."""


def _analyze(msgs: list[ChatMessage], duration: float, audio_db, cfg: Settings, done: list[dict], log,
             top: int | None = None, visual=None, title: str = "", channel: str = ""):
    log(f"Ищу моменты (длительность {_fmt(duration)}, сообщений {len(msgs)})...")
    hl = detect.find_highlights(
        msgs, int(duration), audio_db=audio_db, visual=visual, top=cfg.top if top is None else top, clip_pre=cfg.clip_pre, clip_post=cfg.clip_post,
        chat_lag=cfg.chat_lag, audio_weight=cfg.audio_weight, min_score=cfg.min_score,
        hype_words=cfg.hype_words, exclude=[(d["start"], d["end"]) for d in done], log=log)
    hl = [h for h in hl if not _overlaps(h, done)]
    from . import quality
    if quality.enabled():  # чат про сон («wake up», «zzz») — такие моменты не берём
        hl = quality.filter_highlights(hl, msgs, title, channel, cfg.chat_lag, log)
    hl = quality.strong_moments(hl, audio_db is not None, log)  # скучные моменты — мимо: только яркие
    if cfg.auto_length:
        _auto_length(hl, msgs, audio_db, duration)
    for h in hl:
        log(f"  * {_fmt(h.start)} – {_fmt(h.end)}  score={h.score}  ({' | '.join(h.top_messages[:3])})")
    return hl


def _auto_length(hl, msgs, audio_db, duration: float, lo: float | None = None, hi: float | None = None) -> None:
    """Длина под момент: продлеваем клип, пока чат ещё реагирует или стример громко говорит/кричит
    (границы — из правил «Доктора», по умолчанию 10–60 с), +1 с после конца реакции.
    Кусок берём с запасом по 2 с с каждой стороны — точные границы потом ставятся в паузы речи."""
    from . import shape
    lo_, hi_ = shape.min_max()
    lo, hi = lo or lo_, hi or hi_
    n = int(duration) + 6
    counts = np.zeros(n, dtype=np.float32)
    for m in msgs:
        if 0 <= m.t < n:
            counts[int(m.t)] += 1
    base = float(np.median(counts[counts > 0])) if (counts > 0).any() else 0.0
    thresh = max(1.0, base * 1.6)
    loud = None
    if audio_db is not None and len(audio_db):
        a = np.asarray(audio_db, dtype=np.float32)
        ok = np.isfinite(a)
        if ok.any():
            loud = (a, float(np.median(a[ok])) + 4.0)
    for h in hl:
        end = float(h.end)
        while end - h.start < hi and end + 1 < duration:
            i = int(end)
            busy = counts[i:i + 5].mean() > thresh
            if loud is not None and i + 5 <= len(loud[0]):
                seg = loud[0][i:i + 5]
                seg = seg[np.isfinite(seg)]
                busy = busy or (len(seg) and float(seg.mean()) > loud[1])
            if not busy:
                break
            end += 1.0
        end = min(duration, end + 1.0, h.start + hi)
        if end - h.start < lo:
            end = min(duration, h.start + lo)
        pa = min(shape.PAD, max(0.0, float(h.start)))
        pb = min(shape.PAD, max(0.0, duration - end))
        h.start = round(float(h.start) - pa, 1)
        h.end = round(end + pb, 1)
        h.pad = (round(pa, 1), round(pb, 1))


def _finish(cfg: Settings, new: list[dict], work: str, all_clips: list[dict], title: str, link_fn, log) -> None:
    write_report(work, all_clips, title, link_fn)  # служебный отчёт по стриму
    if cfg.dry_run:
        log(f"Найденные моменты (без нарезки): {os.path.join(work, 'highlights.md')}")
        return
    folder = daily.day_dir(cfg.out_dir)
    if new:
        z = daily.build_zip(folder)
        log(f"Архив дня обновлён: {z}")
    log(f"Отчёт за день: {daily.write_day_report(folder)}")


def process_vod(url: str, cfg: Settings, done: list[dict] | None = None, live: bool = False, log=print,
                on_clip=None, start_at=None, progress: dict | None = None, jump: bool = False,
                slice_sec: float | None = None) -> list[dict]:
    """Обрабатывает запись стрима (Twitch/YouTube). Клипы режутся ПО ХОДУ загрузки чата:
    скачали очередные 30 минут стрима — сразу нарезали лучшие моменты оттуда.
    done — уже нарезанные клипы (чтобы не повторяться); live=True — запись ещё идёт (эфир);
    on_clip(d) — вызывается сразу после каждого готового клипа."""
    import threading
    from . import twitch
    from .audio import loudness_per_second
    from .caption import detect_language
    from .chat import download_chat_part

    done = list(done or [])
    import time as _t
    t_slice = _t.time()  # «по кругу»: разбираем кусок не дольше slice_sec и уступаем следующему стримеру
    if progress is not None:
        progress["unfinished"] = False
    log(f"VOD {url}{'  (идёт эфир)' if live else ''}")
    info = twitch.get_info(url)
    yt = twitch.is_youtube(url)
    vid = (str(info.get("id") or "") if yt else twitch.vod_id(url)) or twitch.vod_id(url)
    work = os.path.join(cfg.work_dir, vid)
    os.makedirs(work, exist_ok=True)
    title = info.get("title") or vid
    channel = (info.get("uploader_id") or info.get("channel") or info.get("uploader") or "stream").lstrip("@")
    vod_duration = float(info.get("duration") or 0)
    log(f"▶ {channel}: начинаю работу{' (стрим идёт)' if live else ''} — «{title[:60]}»")
    link = (lambda s: f"https://youtu.be/{vid}?t={int(s)}") if yt else (lambda s: twitch.timestamp_link(url, s))

    # звук и картинка: качаем облегчённое видео кусками (по ходу) и считаем громкость + смены кадра.
    # Так моменты находятся даже когда чат молчит, и для идущих стримов тоже.
    media = MediaAnalysis(url, work, log) if cfg.audio else None
    old_npy = os.path.join(work, "loudness.npy")  # совместимость: звук, посчитанный старой версией
    if media and os.path.exists(old_npy):
        media.put(0, np.load(old_npy), None)

    cache = os.path.join(work, "chat.json")
    step = 1800  # режем после каждых 30 минут стрима
    new: list[dict] = []
    lang = cfg.language
    # с какого места стрима начинать анализ (выбирается в окне; «now» — с текущего момента)
    if start_at == "now":
        start_at = vod_duration or (_last_t(cache) or 0)
        log(f"  начинаю с текущего момента стрима: {_fmt(start_at)} — всё, что было раньше, пропускаю")
    start_at = float(start_at or 0)
    if start_at and progress is not None:
        progress["start_at"] = start_at
    if start_at and start_at != (progress or {}).get("announced"):
        log(f"  анализирую стрим с {_fmt(start_at)}")
    last = max(_last_t(cache) or 0, start_at)
    if last > 60 or done:
        log(f"  продолжаю с того места, где остановились: чат уже скачан до {_fmt(last)}, "
            f"готово клипов — {len(done)}")
    # с какой секунды стрима ещё не искали моменты (при повторном проходе — после уже нарезанного)
    boundary = 0.0 if not live else max([d["end"] for d in done], default=0.0) - cfg.clip_post - cfg.clip_pre
    boundary = max(0.0, boundary, start_at)
    if jump and start_at:
        # пользователь сам выбрал «начать с» — начинаем именно оттуда (готовые клипы всё равно не повторятся)
        boundary = start_at
        if done:
            log(f"  начинаю с {_fmt(start_at)}, как выбрано; уже готовые клипы ({len(done)}) не повторятся")
    from . import progress as prog
    stream_ts = info.get("release_timestamp") or info.get("timestamp")
    page_url = info.get("webpage_url") or url
    counted_clips = 0
    while True:
        refresh_live(cfg, log)
        stopped = False
        msgs, finished = download_chat_part(url, cache, None if cfg.dry_run else last + step, log,
                                            start_from=start_at)
        covered = last = msgs[-1].t if msgs else 0
        if finished and not live:
            covered = max(covered, vod_duration)
        duration = max(covered, 1)
        if cfg.audio and media is None:  # «искать по звуку и картинке» включили во время работы
            media = MediaAnalysis(url, work, log)
        if media and cfg.audio:
            media.cover(max(start_at, boundary - 60), duration)
        if not lang and len(msgs) > 200 or (finished and not lang):
            lang = detect_language([m.text for m in msgs], title)
        if lang and not cfg.language:
            from .caption import lang_allowed
            if not lang_allowed(channel, lang, log):
                break
        skip = done + new
        if boundary > 0:
            # уже разобранную часть стрима не трогаем — смотрим только новый кусок
            skip = skip + [{"start": 0.0, "end": boundary}]
        tail = cfg.clip_post + cfg.chat_lag + 60
        if not (finished and not live):
            # хвост ещё не «отреагирован» чатом — возьмём на следующем шаге
            skip = skip + [{"start": max(0.0, duration - tail), "end": duration + 10 ** 6}]
        next_boundary = max(boundary, duration - tail)
        counted = [d for d in done + new if d.get("start", 0) >= start_at - 1]
        allowed = clip_budget(cfg.top, duration - start_at) - len(counted)
        if allowed > 0:
            use = media if (media and cfg.audio) else None
            hl = _analyze(msgs, duration, use.audio(duration) if use else None, cfg, skip, log, top=allowed,
                          visual=use.visual(duration) if use else None, title=title, channel=channel)
            for i, h in enumerate(hl, 1):
                if paths.stop_requested():
                    stopped = True
                    break
                refresh_live(cfg, log)
                if daily.similar_moment(cfg.out_dir, channel, (h.start + h.end) / 2):
                    log(f"  {_fmt(h.start)}: этот момент у {channel} уже нарезан — пропускаю")
                    continue
                d = dict(h.to_dict(), vod_url=url, vod_title=title, link=link(h.start))
                d["has_media"] = bool(media and np.isfinite(media.v).any())
                if not cfg.dry_run:
                    name = f"{vid}_{_fmt(h.start)}"
                    log(f"  [{i}/{len(hl)}] качаю кусок {_fmt(h.start)}...")
                    try:
                        seg = twitch.download_section(url, h.start, h.end, os.path.join(work, name + "_raw"),
                                                      cfg.max_height)
                        tmp = os.path.join(work, name + ".mp4")
                        meta = {"streamer": channel, "title": title, "top_messages": h.top_messages,
                                "lang": lang or "en", "platform": "YouTube" if yt else "Twitch",
                                "credit_name": (info.get("uploader") or channel), "pad": getattr(h, "pad", None)}
                        d["caption"] = _make_short(seg, tmp, cfg, log, meta)
                        _apply_trim(d, meta)
                        d["transcript"], d["lang"] = meta.get("transcript", ""), lang or "en"
                        d["rating"] = _final_rating(d, meta)
                        if not cfg.keep_raw:
                            os.remove(seg)
                        d["words"] = meta.get("words") or []
                        d["platform"], d["credit_name"] = meta["platform"], meta["credit_name"]
                        d["credit_burned"] = bool(cfg.credit)
                        d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, channel)
                        _quick_policy(d, log)
                        log(f"    готово -> {d['file']}")
                        log(f"✅ {channel}: клип {_clip_no(d['file'])} готов — «{d.get('caption') or ''}»")
                    except ClipRejected as e:
                        log(f"💤 пропущен момент {_fmt(h.peak)} у {channel} — {e}")
                        skip.append({"start": h.start, "end": h.end})
                        continue
                    except Exception as e:
                        log(f"    ошибка: {e}")
                        daily.log_event(cfg.out_dir, f"{channel}: не удалось сделать клип {_fmt(h.start)} — {e}")
                        continue
                new.append(d)
                if on_clip:
                    on_clip(d)
        if not cfg.dry_run:
            # запоминаем, какой кусок стрима разобран — видно во вкладке «Стримы»
            upto = max(duration, vod_duration) if finished and not live else next_boundary
            prog.record(vid, boundary, boundary if stopped else upto, channel=channel,
                        platform="YouTube" if yt else "Twitch", title=title, url=page_url, stream_ts=stream_ts,
                        duration=max(vod_duration, covered), live=live, clips=len(new) - counted_clips)
            counted_clips = len(new)
        boundary = next_boundary
        if finished or cfg.dry_run:
            break
        if paths.stop_requested():
            log("  останавливаюсь по просьбе — продолжу с этого места при следующем запуске")
            break
        if slice_sec and _t.time() - t_slice >= slice_sec:
            if progress is not None:
                progress["unfinished"] = True
            log(f"⏸ {channel}: разобрал до {_fmt(covered)} — перехожу к следующему стримеру, вернусь по кругу")
            break

    _finish(cfg, new, work, done + new, title, link, log)
    return new


def recut(job: dict, cfg: Settings, log=print) -> dict:
    """Перерезать готовый клип с новыми границами (удлинить/сдвинуть): снова качаем кусок записи стрима
    и собираем клип теми же настройками, с той же надписью. job: url, start, end, out, meta."""
    from . import twitch
    work = os.path.join(cfg.work_dir, "recut")
    os.makedirs(work, exist_ok=True)
    start, end = max(0.0, float(job["start"])), float(job["end"])
    log(f"Качаю кусок стрима {_fmt(start)}–{_fmt(end)}...")
    # своё имя на каждую задачу: иначе «уже скачанный» кусок от ДРУГОГО клипа подхватывался вместо нужного
    import glob
    import time as _time
    for old in glob.glob(os.path.join(work, "recut_raw*")):  # хвосты старой версии с общим именем файла
        try:
            os.remove(old)
        except OSError:
            pass
    base = os.path.join(work, f"raw_{int(_time.time() * 1000)}_{int(start)}_{int(end)}")
    seg = twitch.download_section(job["url"], start, end, base, cfg.max_height)
    meta = dict(job.get("meta") or {})
    meta["check_quality"] = False  # перерезка по просьбе пользователя — фильтры не применяем
    cfg.clip_pre = min(cfg.clip_pre, max(1.0, (end - start) * 0.57))
    log("Собираю клип...")
    try:
        _make_short(seg, job["out"], cfg, log, meta)
    finally:
        for f in glob.glob(glob.escape(base) + "*"):
            try:
                os.remove(f)
            except OSError:
                pass
    return {"file": job["out"], "words": meta.get("words") or [], "transcript": meta.get("transcript", ""),
            "start": start, "end": end}


def _quick_policy(d: dict, log=print) -> None:
    """Быстрая проверка речи на мат/оскорбления/музыку сразу после нарезки (без Claude, мгновенно)."""
    try:
        from . import policy
        issues = policy.check_words(d.get("words") or []) + policy.check_nudity(d["file"], log)
        policy.save_result(d["file"], {"issues": issues, "visual": False, "checked": __import__("time").time(),
                                       "nudity_v": 2,
                                       "note": "" if d.get("words") else "речи нет или субтитры выключены",
                                       "words": d.get("words") or []})
        if issues:
            kinds = {}
            for i in issues:
                kinds[i["title"]] = kinds.get(i["title"], 0) + 1
            log(f"⚠ клип {_clip_no(d['file'])}: возможные нарушения правил — "
                + ", ".join(f"{k} ×{v}" for k, v in kinds.items()) + " (вкладка «Клипы» → «Исправить нарушение»)")
    except Exception as e:
        log(f"    проверка правил не удалась: {e}")


def _final_rating(d: dict, meta: dict) -> float:
    """Сохраняем «сырую» яркость и оценку Claude отдельно — итог считается в окне, в сравнении со всеми клипами."""
    from .caption import rate_clip
    ai = meta.get("ai_score")
    if isinstance(ai, (int, float)) and 0 < ai <= 10:
        d["ai_score"] = float(ai)
    return rate_clip(d, meta.get("transcript", ""))


def _clip_no(path: str) -> str:
    """Номер клипа из имени файла «03_1ч12м05с.mp4» → «3»."""
    base = os.path.basename(path or "")
    num = base.split("_")[0]
    return str(int(num)) if num.isdigit() else "?"


def _last_t(cache: str) -> float | None:
    try:
        m = load_chat_file(cache)
        return m[-1].t if m else None
    except Exception:
        return None


def process_local(video: str, chat_path: str, cfg: Settings, log=print) -> list[dict]:
    """Обрабатывает уже скачанное видео + файл чата (наш JSON или TwitchDownloader)."""
    from .audio import loudness_per_second

    name = os.path.splitext(os.path.basename(video))[0]
    work = os.path.join(cfg.work_dir, name)
    os.makedirs(work, exist_ok=True)
    msgs = load_chat_file(chat_path)
    audio_db = None
    if cfg.audio:
        log("Анализирую громкость...")
        audio_db = loudness_per_second(video)
        from .audio import scene_per_second
        visual_local = scene_per_second(video)
    duration = len(audio_db) if audio_db is not None else (msgs[-1].t if msgs else 0)
    hl = _analyze(msgs, duration, audio_db, cfg, [], log, top=clip_budget(cfg.top, duration), title=name, channel=name,
                  visual=visual_local if cfg.audio else None)
    from .caption import detect_language
    lang = cfg.language or detect_language([m.text for m in msgs], name)
    from .caption import lang_allowed
    if not cfg.language and not lang_allowed(name, lang, log):
        return []
    clips = []
    for i, h in enumerate(hl, 1):
        d = dict(h.to_dict(), vod_title=name)
        d["has_media"] = bool(cfg.audio)
        if not cfg.dry_run:
            base = f"{name}_{_fmt(h.start)}"
            seg = render.cut_segment(video, h.start, h.end, os.path.join(work, base + "_raw.mp4"))
            tmp = os.path.join(work, base + ".mp4")
            meta = {"streamer": name, "title": name, "top_messages": h.top_messages, "lang": lang,
                    "pad": getattr(h, "pad", None)}
            try:
                d["caption"] = _make_short(seg, tmp, cfg, log, meta)
            except ClipRejected as e:
                log(f"💤 пропущен момент {_fmt(h.peak)} у {name} — {e}")
                if not cfg.keep_raw and os.path.exists(seg):
                    os.remove(seg)
                continue
            _apply_trim(d, meta)
            d["transcript"], d["lang"] = meta.get("transcript", ""), lang
            d["rating"] = _final_rating(d, meta)
            if not cfg.keep_raw:
                os.remove(seg)
            d["words"] = meta.get("words") or []
            d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, name)
            _quick_policy(d, log)
            log(f"  [{i}/{len(hl)}] готово -> {d['file']}")
            log(f"✅ {name}: клип {_clip_no(d['file'])} готов — «{d.get('caption') or ''}»")
        clips.append(d)
    _finish(cfg, clips, work, clips, name, None, log)
    return clips
