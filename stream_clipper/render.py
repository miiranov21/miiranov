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


def render_vertical(src: str, out: str, layout: str = "blur", facecam=None, zoom: float = 1.0,
                    ass_path: str | None = None, preset: str = "medium") -> str:
    vf = build_filter(layout, facecam, zoom)
    cwd = None
    if ass_path:
        # ffmpeg плохо переваривает пути с ":" (Windows) в фильтре ass — запускаем из папки субтитров
        cwd = os.path.dirname(os.path.abspath(ass_path))
        vf = vf[: -len("[v]")] + f"[v0];[v0]ass={os.path.basename(ass_path)}[v]"
    _run(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(src), "-filter_complex", vf,
          "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", preset, "-crf", "20",
          "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
          os.path.abspath(out)], cwd=cwd)
    return out
