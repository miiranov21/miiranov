"""Сам выбирает стримеров: любимчики и GTA выше, кого ведём — не выкидываем до конца записи, лимит соблюдается,
YouTube-строки не трогаем. Запуск: python tests/test_auto_streamers.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import auto_streamers as a  # noqa: E402

cands = {"kaicenat": {"viewers": 3000, "category": "Grand Theft Auto VI", "fav": True},
         "bigchat": {"viewers": 20000, "category": "Just Chatting", "fav": False},
         "gtaguy": {"viewers": 4000, "category": "Grand Theft Auto VI", "fav": False},
         "tiny": {"viewers": 300, "category": "Grand Theft Auto VI", "fav": False}}
now = 1_000_000.0
state = {"oldlive": {"last_live": now - 3600}, "gone": {"last_live": now - 5 * 3600}}
got = a.choose(cands, ["oldlive", "gone"], state, now, 4)
assert got[0] == "oldlive" and "gone" not in got and "tiny" not in got, got  # эфир кончился час назад — дорезаем
assert got[1] == "kaicenat" and len(got) == 4, got                        # любимчик Доктора выше большого чата

d = tempfile.mkdtemp()
path = os.path.join(d, "streamers.txt")
open(path, "w", encoding="utf-8").write("xqc\n@MrBeast\n")
a.enabled = lambda: True
a._max = lambda: 2
a._strategy = lambda: {"autopilot": {"streamer_mix": {"priority_streamers": ["kaicenat"]}}}
a.live_candidates = lambda cats, favs: cands
a.paths.default_work_dir = lambda: d
assert a.update(path, log=lambda *_: None)
tw, other = a._read(path)
assert tw == ["kaicenat", "bigchat"] and other == ["@MrBeast"], (tw, other)
print("OK")
