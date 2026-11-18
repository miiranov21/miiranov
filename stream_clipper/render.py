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
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", out])
    return out


def build_filter(layout: str, facecam: tuple[float, float, float, float] | None = None,
                 zoom: float = 1.0, cam_share: float = 0.35) -> str:
    if layout == "crop":
        return f"[0:v]scale=-2:{H},crop={W}:{H}[v]"
    if layout == "facecam":
        if not facecam:
            raise ValueError("для layout=facecam укажи --facecam x,y,w,h (доли кадра 0..1)")
        fx, fy, fw, fh = facecam
        ch = int(H * cam_share) // 2 * 2
        gh = H - ch
        return (f"[0:v]split=2[a][b];"
                f"[a]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},"
                f"scale={W}:{ch}:force_original_aspect_ratio=increase,crop={W}:{ch}[cam];"
                f"[b]scale=-2:{gh},crop={W}:{gh}[game];"
                f"[cam][game]vstack=inputs=2[v]")
    # blur (по умолчанию): игра по центру, сверху/снизу размытый фон
    fgw = int(W * zoom) // 2 * 2
    return (f"[0:v]split=2[a][b];"
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=25:2,eq=brightness=-0.08[bg];"
            f"[b]scale={fgw}:-2,crop={W}:ih[fg];"
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


def caption_y(layout: str, zoom: float = 1.0, cam_share: float = 0.35) -> int:
    """Где ставить плашку: на стыке вебки и игры, или в размытой полосе над игрой."""
    if layout == "facecam":
        return int(H * cam_share) // 2 * 2
    if layout == "blur":
        fg_h = W * zoom * 9 / 16
        return int((H - fg_h) / 2 * 0.55)
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


def render_vertical(src: str, out: str, layout: str = "blur", facecam=None, zoom: float = 1.0,
                    ass_paths: list[str] | None = None, preset: str = "medium") -> str:
    vf = build_filter(layout, facecam, zoom)
    cwd = None
    ass_paths = [p for p in (ass_paths or []) if p]
    if ass_paths:
        # ffmpeg плохо переваривает пути с ":" (Windows) в фильтре ass — запускаем из папки субтитров
        cwd = os.path.dirname(os.path.abspath(ass_paths[0]))
        chain = ",".join(f"ass={os.path.basename(p)}" for p in ass_paths)
        vf = vf[: -len("[v]")] + f"[v0];[v0]{chain}[v]"
    _run(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(src), "-filter_complex", vf,
          "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", preset, "-crf", "20",
          "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
          os.path.abspath(out)], cwd=cwd)
    return out
