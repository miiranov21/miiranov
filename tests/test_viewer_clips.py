"""Клип зрителей поднимает момент, даже если чат и звук ровные; число просмотров попадает в Highlight.
Запуск: python tests/test_viewer_clips.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import detect  # noqa: E402
from stream_clipper.chat import ChatMessage  # noqa: E402

msgs = [ChatMessage(t=float(t), author=f"u{t % 7}", text="hi") for t in range(0, 1200, 3)]  # ровный чат
quiet = lambda *a: None

base = detect.find_highlights(msgs, 1200, top=3, min_score=1.0, log=quiet)
assert not any(400 <= h.peak <= 460 for h in base), "без клипа этот кусок ничем не выделяется"

hl = detect.find_highlights(msgs, 1200, top=3, min_score=1.0, clips=[(420.0, 25.0, 34000)], log=quiet)
hit = [h for h in hl if 400 <= h.peak <= 460]
assert hit, "клип зрителей должен дать момент"
assert hit[0].clip_views == 34000
print("OK")
