"""Громкость звука по секундам (крики стримера, взрывы и т.п.)."""
from __future__ import annotations

import os
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


def scene_per_second(src: str, fps: int = 2) -> np.ndarray:
    """«Насколько резко меняется картинка» для каждой секунды (0..1): взрывы, аварии, внезапные события.
    Считается по уменьшенному видео — быстро."""
    cmd = ["ffmpeg", "-v", "error", "-i", src, "-an",
           "-vf", f"fps={fps},scale=160:-2,select='gte(scene,0)',metadata=print:file=-", "-f", "null", "-"]
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)
    per_sec: dict = {}
    t = None
    for line in r.stdout.splitlines():
        if "pts_time:" in line:
            try:
                t = float(line.split("pts_time:")[1].split()[0])
            except (ValueError, IndexError):
                t = None
        elif line.startswith("lavfi.scene_score=") and t is not None:
            try:
                v = float(line.split("=", 1)[1])
            except ValueError:
                continue
            sec = int(t)
            per_sec[sec] = max(per_sec.get(sec, 0.0), v)
    if not per_sec:
        return np.zeros(0, dtype=np.float32)
    arr = np.zeros(max(per_sec) + 1, dtype=np.float32)
    for sec, v in per_sec.items():
        arr[sec] = v
    return arr
