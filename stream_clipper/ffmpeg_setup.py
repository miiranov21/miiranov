"""Находит ffmpeg, а на Windows при отсутствии — скачивает его в папку программы."""
from __future__ import annotations

import glob
import os
import shutil
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "bin")
URLS = [
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
]


def _add_to_path(d: str) -> None:
    os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")


def _local_dirs() -> list[str]:
    dirs = [BIN, ROOT, os.getcwd()]
    dirs += [os.path.dirname(p) for p in glob.glob(os.path.join(ROOT, "ffmpeg*", "bin", "ffmpeg*"))]
    return dirs


def ensure_ffmpeg(log=print) -> bool:
    if shutil.which("ffmpeg"):
        return True
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    for d in _local_dirs():
        if os.path.isfile(os.path.join(d, exe)):
            _add_to_path(d)
            return True
    if os.name != "nt":
        log("ffmpeg не найден. Установи его: sudo apt install ffmpeg  (или brew install ffmpeg)")
        return False
    os.makedirs(BIN, exist_ok=True)
    zpath = os.path.join(BIN, "ffmpeg.zip")
    for url in URLS:
        try:
            log(f"ffmpeg не найден — скачиваю (~100 МБ, один раз): {url}")
            with urllib.request.urlopen(url, timeout=60) as r, open(zpath, "wb") as f:
                total = int(r.headers.get("Content-Length") or 0)
                got = 0
                while True:
                    buf = r.read(1 << 20)
                    if not buf:
                        break
                    f.write(buf)
                    got += len(buf)
                    if total:
                        print(f"\r  {got * 100 // total}%", end="", flush=True)
            print()
            with zipfile.ZipFile(zpath) as z:
                for name in z.namelist():
                    base = os.path.basename(name)
                    if base in ("ffmpeg.exe", "ffprobe.exe"):
                        with z.open(name) as src, open(os.path.join(BIN, base), "wb") as dst:
                            shutil.copyfileobj(src, dst)
            os.remove(zpath)
            if os.path.isfile(os.path.join(BIN, "ffmpeg.exe")):
                _add_to_path(BIN)
                log("ffmpeg готов.")
                return True
        except Exception as e:
            log(f"  не получилось: {e}")
    log("Не удалось скачать ffmpeg автоматически. Скачай вручную с https://www.gyan.dev/ffmpeg/builds/ "
        "и положи ffmpeg.exe и ffprobe.exe в папку " + BIN)
    return False
