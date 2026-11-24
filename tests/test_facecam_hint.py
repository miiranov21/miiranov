"""Ручная рамка вебки — подсказка: на месте → она, не видно → она, переехала → новое место, «нет вебки» → None.
Запуск: python tests/test_facecam_hint.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import facecam as f  # noqa: E402

store = {}
f.load_store = lambda: dict(store)
f._save_store = lambda d: (store.clear(), store.update(d))
f._save_frame = lambda *a: None
quiet = lambda *a: None

store["kai"] = {"manual": True, "none": False, "region": [0.70, 0.02, 0.28, 0.30]}
f.detect_facecam = lambda *a, **k: (0.71, 0.03, 0.27, 0.29)
assert f.resolve("kai", "x", log=quiet) == (0.70, 0.02, 0.28, 0.30)
f.detect_facecam = lambda *a, **k: None
assert f.resolve("kai", "x", log=quiet) == (0.70, 0.02, 0.28, 0.30)
f.detect_facecam = lambda *a, **k: (0.02, 0.60, 0.28, 0.30)
assert f.resolve("kai", "x", log=quiet) == (0.02, 0.60, 0.28, 0.30)
assert store["kai"]["manual"] and store["kai"]["region"] == [0.02, 0.60, 0.28, 0.30]
store["lacy"] = {"manual": True, "none": True}
assert f.resolve("lacy", "x", log=quiet) is None
print("OK")
