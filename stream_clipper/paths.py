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


def program_dir() -> str:
    """Папка программы (где лежат START.bat и streamers.txt)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stop_request_path() -> str:
    """Файл-сигнал «остановись аккуратно» (окно программы создаёт его перед обновлением)."""
    return os.path.join(default_work_dir(), "stop.request")


def stop_requested() -> bool:
    return os.path.exists(stop_request_path())


def live_settings_path() -> str:
    """Настройки, которые окно меняет на ходу (клипов в час, длина клипа) — работа подхватывает их сразу."""
    return os.path.join(default_work_dir(), "live_settings.json")


def priority_path() -> str:
    """Порядок стримеров (общий для Twitch и YouTube): кто выше — того обрабатываем первым."""
    return os.path.join(default_work_dir(), "priority.json")


def priority_key(spec: str) -> str:
    """Ключ стримера для очереди: twitch-логин или @ник/ссылка YouTube (без учёта регистра)."""
    s = spec.strip()
    if s.startswith("yt:"):
        s = s[3:]
    return s.lower()


def recording_dir() -> str:
    """Отметки «сейчас идёт запись эфира» — пока они есть, автообновление ждёт."""
    d = os.path.join(default_work_dir(), "recording")
    os.makedirs(d, exist_ok=True)
    return d


def recordings_active(max_age: float = 180) -> list[str]:
    """Кого сейчас записываем (свежие отметки; старые — от упавшей программы — не считаем)."""
    import time
    d = recording_dir()
    now = time.time()
    names = []
    for f in os.listdir(d):
        p = os.path.join(d, f)
        try:
            if now - os.path.getmtime(p) < max_age:
                names.append(os.path.splitext(f)[0])
        except OSError:
            pass
    return names
