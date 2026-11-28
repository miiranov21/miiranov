"""YouTube закрыл видео (Google не проверил приложение): копия удаляется, ошибка PublishRefused, никаких
переключений на Telegram — YouTube остаётся «выкладывает сам». Запуск: python tests/test_publish_refused.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import publisher as p  # noqa: E402

gone = []
p.youtube_upload = lambda *a, **k: {"id": "v1", "privacy": "private"}
p.youtube_delete = gone.append
p.load = lambda: {"youtube": {"token": "x"}}
p.connected = lambda: {"youtube": True}
try:
    p.publish("youtube", "f.mp4", "t", "d", [])
    raise SystemExit("ошибки нет")
except p.PublishRefused:
    pass
assert gone == ["v1"] and "youtube" in p.direct_platforms()
print("OK")
