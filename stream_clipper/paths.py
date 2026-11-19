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


def parse_start(text) -> float | str | None:
    """«2:30» → 9000 сек, «2» → 7200, «сейчас»/«now» → "now", пусто/«0:00» → None (с начала)."""
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text) if text > 0 else None
    from .i18n import untranslate
    t = untranslate(str(text).strip()).lower().split("(")[0].strip()
    if not t or t in ("0", "0:00", "с начала", "начало"):
        return None
    if t in ("сейчас", "now", "с текущего момента"):
        return "now"
    parts = t.replace(".", ":").split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"не понял время «{text}»: пиши часы:минуты, например 1:30")
    sec = nums[0] * 3600 + (nums[1] * 60 if len(nums) > 1 else 0) + (nums[2] if len(nums) > 2 else 0)
    return sec if sec > 0 else None


# ---------- время начала анализа для каждого стримера ----------
def start_times_path() -> str:
    return os.path.join(default_work_dir(), "start_times.json")


def load_start_times() -> dict:
    """{ключ стримера: {"value": "13:00", "mode": "stream"|"clock"}}"""
    import json
    try:
        with open(start_times_path(), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_start_times(data: dict) -> None:
    import json
    os.makedirs(os.path.dirname(start_times_path()), exist_ok=True)
    with open(start_times_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def resolve_start(value, mode: str = "stream", stream_start_ts: float | None = None):
    """Время начала анализа → секунды от начала стрима (или "now"/None).
    mode="stream": «13:00» = 13 часов от начала стрима; mode="clock": «13:00» = 13:00 по часам компьютера."""
    sec = parse_start(value)
    if sec in (None, "now") or mode != "clock":
        return sec
    if not stream_start_ts:
        return None  # не знаем, когда начался стрим — начнём с начала
    import datetime as _dt
    start = _dt.datetime.fromtimestamp(stream_start_ts)
    target = start.replace(hour=int(sec // 3600) % 24, minute=int(sec % 3600 // 60), second=0, microsecond=0)
    if target < start:
        target += _dt.timedelta(days=1)  # «01:00» для стрима, начавшегося вечером, — это уже следующие сутки
    off = (target - start).total_seconds()
    return off if off > 0 else None
