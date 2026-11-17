"""Где лежат результаты и служебные файлы."""
from __future__ import annotations

import os


def desktop_dir() -> str:
    """Настоящий путь к рабочему столу (учитывает перенос в OneDrive и т.п.)."""
    if os.name == "nt":
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(260)
            if ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buf) == 0 and buf.value:
                return buf.value  # CSIDL_DESKTOPDIRECTORY
        except Exception:
            pass
    home = os.path.expanduser("~")
    for name in ("Desktop", "Рабочий стол"):
        p = os.path.join(home, name)
        if os.path.isdir(p):
            return p
    return home


def default_out_dir() -> str:
    """Рабочий стол\\YouTube — сюда складываются папки по датам."""
    return os.path.join(desktop_dir(), "YouTube")


def default_work_dir() -> str:
    """Служебные файлы (кэш чата, записи эфира, состояние) — вне папки с клипами."""
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return os.path.join(os.environ["LOCALAPPDATA"], "StreamClipper")
    return os.path.join(os.path.expanduser("~"), ".stream_clipper")
