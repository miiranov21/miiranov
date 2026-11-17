"""Громкость звука по секундам (крики стримера, взрывы и т.п.)."""
from __future__ import annotations

import subprocess

import numpy as np


def loudness_per_second(src: str, sr: int = 8000) -> np.ndarray:
    """Возвращает громкость (dBFS RMS) для каждой секунды медиафайла."""
    cmd = ["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    chunk = sr * 2  # 1 секунда int16
    vals: list[float] = []
    assert proc.stdout is not None
    while True:
        buf = proc.stdout.read(chunk)
        if not buf:
            break
        a = np.frombuffer(buf[: len(buf) // 2 * 2], dtype=np.int16).astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(a * a))) if a.size else 0.0
        vals.append(20 * np.log10(rms + 1e-6))
    proc.wait()
    if proc.returncode != 0 and not vals:
        raise RuntimeError(f"ffmpeg не смог прочитать звук из {src}")
    return np.array(vals, dtype=np.float32)
