"""Обрезка и удлинение готового клипа.

Обрезать можно всегда (быстро, прямо из готового файла). Удлинить — только если есть запись стрима:
тогда программа заново качает кусок с новыми границами и собирает клип с той же надписью.
"""
from __future__ import annotations

import os
import subprocess


def source_range(clip: dict) -> tuple[str, float, float] | None:
    """Где взять исходник клипа: (ссылка на запись, начало, конец в секундах записи) или None."""
    url = clip.get("vod_url") or ""
    try:
        start, end = float(clip["start"]), float(clip["end"])
    except (KeyError, TypeError, ValueError):
        return None
    if "/videos/" in url:  # запись Twitch: время клипа — это время записи
        return url, start, end
    if "watch?v=" in url or "youtu.be/" in url or "/live/" in url:
        if "moment" in clip:  # клип из эфира YouTube: запись появится с тем же адресом, время — от начала эфира
            m = float(clip["moment"])
            return url, m, m + (end - start)
        return url, start, end
    return None  # эфир Twitch без сохранённой записи — удлинять неоткуда


def duration(path: str) -> float:
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, creationflags=flags)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def trim_local(src: str, out: str, cut_start: float, cut_end: float) -> str:
    """Обрезать cut_start секунд в начале и cut_end в конце (из готового клипа, без интернета)."""
    dur = duration(src)
    a, b = max(0.0, cut_start), max(0.0, dur - max(0.0, cut_end))
    if b - a < 1:
        raise ValueError("клип получится короче секунды")
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out],
                       capture_output=True, text=True, creationflags=flags)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[-500:])
    return out


def shift_words(words: list, cut_start: float, new_len: float) -> list:
    """Слова субтитров после обрезки: сдвигаем по времени и убираем вырезанные."""
    out = []
    for w in words or []:
        try:
            a, b, t = float(w[0]) - cut_start, float(w[1]) - cut_start, w[2]
        except (TypeError, ValueError, IndexError):
            continue
        if b > 0 and a < new_len:
            out.append([round(max(0.0, a), 2), round(min(new_len, b), 2), t])
    return out
