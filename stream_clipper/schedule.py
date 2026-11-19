"""Время публикаций под аудиторию США при компьютере в Москве.

МСК — всегда UTC+3 (без перехода на летнее время). Восточное время США (ET) — UTC−5 зимой и UTC−4 летом
(со второго воскресенья марта до первого воскресенья ноября). Считаем сами, без базы часовых поясов:
на Windows её может не быть.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

MSK = timezone(timedelta(hours=3), "MSK")


def _nth_sunday(year: int, month: int, n: int) -> datetime:
    d = datetime(year, month, 1)
    d += timedelta(days=(6 - d.weekday()) % 7)  # первое воскресенье
    return d + timedelta(weeks=n - 1)


def et_offset(utc: datetime) -> timedelta:
    """Смещение ET от UTC в этот момент (−4 летом, −5 зимой)."""
    y = utc.year
    start = _nth_sunday(y, 3, 2).replace(hour=7)   # 2:00 EST = 7:00 UTC
    end = _nth_sunday(y, 11, 1).replace(hour=6)    # 2:00 EDT = 6:00 UTC
    naive = utc.replace(tzinfo=None)
    return timedelta(hours=-4) if start <= naive < end else timedelta(hours=-5)


def _aware_local(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.astimezone()  # наивное время — это время компьютера


def to_local(dt: datetime) -> datetime:
    """Любое время → наивное время компьютера (так хранится очередь)."""
    return _aware_local(dt).astimezone().replace(tzinfo=None)


def msk(dt: datetime) -> datetime:
    return _aware_local(dt).astimezone(MSK)


def et(dt: datetime) -> datetime:
    u = _aware_local(dt).astimezone(timezone.utc)
    return (u + et_offset(u)).replace(tzinfo=None)


def label(dt: datetime) -> str:
    """«03:00 МСК (19:00 ET)» — как показывать время слота."""
    return f"{msk(dt):%H:%M} МСК ({et(dt):%H:%M} ET)"


def day_label(dt: datetime) -> str:
    return f"{msk(dt):%d.%m}"


def _hm(s: str) -> tuple[int, int] | None:
    try:
        h, m = str(s).strip().split(":")
        return int(h) % 24, int(m) % 60
    except (ValueError, AttributeError):
        return None


def slot_instances(times_msk: list, now: datetime, days: int = 14) -> list[datetime]:
    """Все будущие слоты (время МСК из стратегии) на ближайшие дни — в наивном времени компьютера, по порядку."""
    base = msk(now).replace(hour=0, minute=0, second=0, microsecond=0)
    out = []
    for d in range(-1, days + 1):
        day = base + timedelta(days=d)
        for t in times_msk or []:
            hm = _hm(t)
            if hm:
                out.append(to_local(day.replace(hour=hm[0], minute=hm[1])))
    return sorted(set(out))


def deliveries(times_msk: list, now: datetime) -> tuple[datetime | None, datetime | None]:
    """(последняя прошедшая, следующая) отправка пачки в Telegram — в наивном времени компьютера."""
    inst = slot_instances(times_msk, now, days=2)
    now_l = to_local(now)
    past = [t for t in inst if t <= now_l]
    fut = [t for t in inst if t > now_l]
    return (past[-1] if past else None), (fut[0] if fut else None)
