"""Хук подборки: «FAILS» только если все моменты — fail; вчерашний хук не повторяется.
Запуск: python tests/test_compilation_hook.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import compilation as c  # noqa: E402

c._cfg = lambda: {"hooks": ["{s}'S 3 WORST FAILS", "{s}'S CRAZIEST MOMENTS TODAY", "TOP {n} {s} MOMENTS"]}
parts = [{"top_messages": ["lol"]}, {"top_messages": ["kekw"]}]
got = {c.choose_hook("kaicenat", parts)[0] for _ in range(40)}
assert not any("FAIL" in g for g in got), got
last = "{s}'S CRAZIEST MOMENTS TODAY"
assert all(c.choose_hook("kaicenat", parts, last)[1] != last for _ in range(20))
print("OK")
