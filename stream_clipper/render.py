"""Перевод горизонтального видео в вертикальный формат Shorts 1080x1920."""
from __future__ import annotations

import os
import subprocess

W, H = 1080, 1920


def _run(cmd: list[str], cwd: str | None = None) -> None:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg ошибка:\n" + r.stderr[-2000:])


def cut_segment(src: str, start: float, end: float, out: str) -> str:
    """Вырезает кусок из локального файла (с перекодированием — точный рез)."""
    _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-i", src, "-t", f"{end - start:.2f}",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-c:a", "aac", "-b:a", "192k", out])
    return out


# сколько игры видно по ширине: целиком / крупнее (≈75%) / только центр (≈55%)
GAME_ZOOM = {"full": 1.0, "wide": 1.333, "center": 1.85}
# доля высоты под вебку: когда игра целиком (она невысокая), вебку делаем крупнее
CAM_SHARE = {"full": 0.42, "wide": 0.35, "center": 0.35}


def build_filter(layout: str, facecam: tuple[float, float, float, float] | None = None,
                 zoom: float = 1.0, cam_share: float | None = None, game_view: str | None = None,
                 face_peak: tuple[float, float] | None = None,
                 game_crop: tuple[float, float, float, float] | None = None) -> str:
    z = GAME_ZOOM.get(game_view, zoom) if game_view else zoom
    gc = (f"crop=iw*{game_crop[2]:.4f}:ih*{game_crop[3]:.4f}:iw*{game_crop[0]:.4f}:ih*{game_crop[1]:.4f},"
          if game_crop else "")  # чёрные полосы исходника — срезаем у игры и фона
    cam_share = cam_share or CAM_SHARE.get(game_view, 0.35)
    gw = int(W * z) // 2 * 2
    bg = (f"{gc}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"boxblur=25:2,eq=brightness=-0.08")
    if layout == "crop":  # весь кадр — камера (стрим без игры): вертикальная вырезка по центру лица
        cx = (facecam[0] + facecam[2] / 2) if facecam else 0.5
        return f"[0:v]scale=-2:{H},crop={W}:{H}:'max(0,min(iw-{W},iw*{cx:.3f}-{W // 2}))':0[v]"
    if layout == "facecam":
        if not facecam:
            raise ValueError("для layout=facecam укажи --facecam x,y,w,h (доли кадра 0..1)")
        fx, fy, fw, fh = facecam
        ch = int(H * cam_share) // 2 * 2
        # вебка сверху, под ней игра (нужной ширины), всё остальное — размытый фон
        full = ""
        if face_peak:  # лицо на весь кадр на пике (0,5–1 с)
            a_, b_ = face_peak
            full = (f";[d]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},"
                    f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
                    f"hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.9:5:5:0.0[full];"
                    f"[g2][full]overlay=0:0:enable='between(t,{a_:.2f},{b_:.2f})'[v]")
        return (f"[0:v]split={4 if face_peak else 3}[a][b][c]{'[d]' if face_peak else ''};"
                f"[a]{bg}[bg];"
                f"[b]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},"
                # вебка маленькая — растягиваем качественно (lanczos) и чуть добавляем резкости
                f"scale={W}:{ch}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{ch},"
                f"hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.9:5:5:0.0[cam];"
                f"[c]{gc}scale={gw}:-2:flags=lanczos,crop={W}:'min(ih,{H - ch})'[game];"
                f"[bg][cam]overlay=0:0[t];"
                f"[t][game]overlay=0:{ch}" + ("[g2]" + full if face_peak else "[v]"))
    # blur: игра по центру, сверху/снизу размытый фон
    return (f"[0:v]split=2[a][b];"
            f"[a]{bg}[bg];"
            f"[b]{gc}scale={gw}:-2:flags=lanczos,crop={W}:'min(ih,{H})'[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[v]")


CAPTION_STYLE = ("Style: Caption,Arial,68,&H00111111,&H00111111,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,"
                 "100,100,0,0,3,16,0,5,40,40,0,1")


def _wrap(text: str, width: int = 22) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\\N".join(lines[:3])


def caption_y(layout: str, zoom: float = 1.0, cam_share: float | None = None, game_view: str | None = None) -> int:
    """Где ставить плашку: на стыке вебки и игры, или в размытой полосе над игрой."""
    cam_share = cam_share or CAM_SHARE.get(game_view, 0.35)
    if layout == "facecam":
        return int(H * cam_share) // 2 * 2
    if layout == "blur":
        z = GAME_ZOOM.get(game_view, zoom) if game_view else zoom
        fg_h = W * z * 9 / 16
        # не выше 310: выше стоит подпись автора (y≈170) и вкладки TikTok/Reels (верхние 8%)
        return max(310, int((H - fg_h) / 2 * 0.55))
    return 380


def write_caption_ass(path: str, text: str, y: int, duration: float = 600) -> str:
    from .subtitles import _ts
    safe = text.replace("{", "(").replace("}", ")").replace("\n", " ")
    with open(path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                f"{CAPTION_STYLE}\n\n[Events]\n"
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                f"Dialogue: 1,{_ts(0)},{_ts(duration)},Caption,,0,0,0,,{{\\an5\\pos(540,{y})}}{_wrap(safe)}\n")
    return path


WM_POSITIONS = ("corner", "center", "moving")
# точки, между которыми «плавает» водяной знак (по кругу)
_WM_PATH = [(170, 260), (900, 420), (260, 1250), (880, 1600), (540, 900), (190, 1700), (860, 230)]


def watermark_corner(credit_pos: str = "", caption_y: int | None = None) -> tuple[int, int, int]:
    """Угол для знака: (выравнивание ASS, x, y). Ниже верхних 8% кадра (там вкладки TikTok/Reels), в верхнем углу,
    напротив подписи автора; правую колонку кнопок площадок (середина-низ справа) не трогаем.
    Если надпись-плашка стоит высоко и доходит до этой строки — знак опускаем под неё."""
    an, x = (7, 40) if credit_pos == "top-right" else (9, 1040)
    y = 170
    if caption_y is not None and caption_y - 150 < y + 50:
        y = caption_y + 150
    return an, x, y


def write_watermark_ass(path: str, text: str, pos: str = "moving", opacity: float = 0.4,
                        duration: float = 600, credit_pos: str = "", caption_y: int | None = None) -> str:
    """Текстовый водяной знак (полупрозрачный)."""
    from .subtitles import _ts
    alpha = f"{int(round((1 - max(0.05, min(opacity, 1.0))) * 255)):02X}"
    safe = text.replace("{", "(").replace("}", ")").replace("\n", " ")
    lines = []
    if pos == "corner":
        an, x, y = watermark_corner(credit_pos, caption_y)
        lines.append((0, duration, f"{{\\an{an}\\pos({x},{y})\\fs40}}{safe}"))
    elif pos == "center":
        lines.append((0, duration, f"{{\\an5\\pos(540,1180)}}{safe}"))
    else:  # плавает: каждые 6 секунд плавно переезжает в следующую точку
        step, t, i = 6.0, 0.0, 0
        while t < duration:
            (x1, y1), (x2, y2) = _WM_PATH[i % len(_WM_PATH)], _WM_PATH[(i + 1) % len(_WM_PATH)]
            lines.append((t, t + step, f"{{\\an5\\move({x1},{y1},{x2},{y2})}}{safe}"))
            t += step
            i += 1
    with open(path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Watermark,Arial,52,&H{alpha}FFFFFF,&H{alpha}FFFFFF,&H{alpha}000000,&H{alpha}000000,"
                "-1,0,0,0,100,100,0,0,1,2,0,5,20,20,20,1\n\n[Events]\n"
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a, b, txt in lines:
            f.write(f"Dialogue: 2,{_ts(a)},{_ts(b)},Watermark,,0,0,0,,{txt}\n")
    return path


# top-left / top-right — чуть ниже верхних 8% кадра (там вкладки TikTok и Reels); bottom-left не советуем:
# внизу подпись закрывают ник аккаунта и описание в интерфейсе площадок
CREDIT_POS = {"bottom-left": (1, 40, 1470), "top-left": (7, 40, 170), "top-right": (9, 1040, 170)}
_PLATFORM_COLOR = {"twitch": "&H00FF4691", "youtube": "&H000021FF", "kick": "&H0017FC53"}  # ASS: &HAABBGGRR


def write_credit_ass(path: str, platform: str, name: str, pos: str = "top-left", duration: float = 600,
                     text: str | None = None) -> str:
    """Подпись автора стрима: «Twitch | KaiCenat» — чтобы было видно, чей это контент."""
    from .subtitles import _ts
    an, x, y = CREDIT_POS.get(pos, CREDIT_POS["top-left"])
    if text:  # свой текст подписи (например, от «Доктора»)
        name, platform = text, ""
    plat = (platform or "").strip()
    color = _PLATFORM_COLOR.get(plat.lower(), "&H00FFFFFF")
    safe = name.replace("{", "(").replace("}", ")").replace("\\", "")
    line = f"{{\\an{an}\\pos({x},{y})}}{{\\c{color}}}{plat}{{\\c&H30FFFFFF}}  |  {safe}" if plat else \
        f"{{\\an{an}\\pos({x},{y})}}{safe}"
    with open(path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: Credit,Arial,34,&H30FFFFFF,&H30FFFFFF,&H90000000,&H90000000,-1,0,0,0,"
                "100,100,0,0,3,10,0,1,20,20,20,1\n\n[Events]\n"
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                f"Dialogue: 3,{_ts(0)},{_ts(duration)},Credit,,0,0,0,,{line}\n")
    return path


def _logo_xy(pos: str, with_text: bool = False) -> tuple[str, str]:
    if pos == "corner":  # если есть и текст (он справа) — логотип в левый угол
        return ("40" if with_text else "W-w-40"), "60"
    if pos == "center":  # с текстом — логотип над ним
        return "(W-w)/2", ("(H-h)/2+40" if with_text else "(H-h)/2+180")
    # плавает: медленно ходит по экрану
    return "(W-w)*(0.5+0.42*sin(t*0.45))", "(H-h)*(0.5+0.40*sin(t*0.31+1.3))"


def render_vertical(src: str, out: str, layout: str = "blur", facecam=None, zoom: float = 1.0,
                    ass_paths: list[str] | None = None, preset: str = "medium",
                    logo: str | None = None, logo_pos: str = "moving", logo_opacity: float = 0.4,
                    logo_with_text: bool = False, game_view: str | None = None,
                    face_peak: tuple[float, float] | None = None,
                    game_crop: tuple[float, float, float, float] | None = None) -> str:
    vf = build_filter(layout, facecam, zoom, game_view=game_view, face_peak=face_peak if layout == "facecam" else None,
                      game_crop=game_crop)
    cwd = None
    inputs = ["-i", os.path.abspath(src)]
    if logo and os.path.exists(logo):
        # логотип-картинка: ширина 220 px, полупрозрачный
        inputs += ["-i", os.path.abspath(logo)]
        x, y = _logo_xy(logo_pos, logo_with_text)
        op = max(0.05, min(logo_opacity, 1.0))
        vf = (vf[: -len("[v]")] + f"[vb];[1:v]scale=220:-1,format=rgba,colorchannelmixer=aa={op:.2f}[wm];"
              f"[vb][wm]overlay=x='{x}':y='{y}':format=auto[v]")
    ass_paths = [p for p in (ass_paths or []) if p]
    if ass_paths:
        # ffmpeg плохо переваривает пути с ":" (Windows) в фильтре ass — запускаем из папки субтитров
        cwd = os.path.dirname(os.path.abspath(ass_paths[0]))
        chain = ",".join(f"ass={os.path.basename(p)}" for p in ass_paths)
        vf = vf[: -len("[v]")] + f"[v0];[v0]{chain}[v]"
    _run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", vf,
          "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", preset, "-crf", "18",
          "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
          os.path.abspath(out)], cwd=cwd)
    return out
