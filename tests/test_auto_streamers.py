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
a.top_past = lambda cats, favs: []
a.paths.default_work_dir = lambda: d
assert a.update(path, log=lambda *_: None)
tw, other = a._read(path)
assert tw == ["kaicenat", "bigchat"] and other == ["@MrBeast"], (tw, other)
print("OK")

# прошлые стримы: самые просматриваемые про GTA 6, разобранные — пропускаем, очередь не раздуваем
assert a.TOPIC.search("🔴PLAYING GTA 6 EARLY ACCESS") and a.TOPIC.search("Grand Theft Auto VI day 2") and not a.TOPIC.search("RONALDO RETIRED")
from stream_clipper import progress  # noqa: E402
progress.load = lambda: {"v2": {"x": 1}}
progress.summary = lambda e: {"finished": True}
vids = [{"url": "u2", "key": "v2", "channel": "ishowspeed", "title": "GTA 6 first", "views": 9},
        {"url": "u3", "key": "v3", "channel": "caseoh_", "title": "LOSING MY MIND", "views": 8},
        {"url": "u4", "key": "v4", "channel": "lacy", "title": "GTA 6 marathon", "views": 7}]
a.queue_past_streams(vids, 1, log=lambda *_: None)
import json  # noqa: E402
q = json.load(open(os.path.join(d, "extra_vods.json"), encoding="utf-8"))["vods"]
assert [v["key"] for v in q] == ["v3"], q          # v2 уже разобран, лимит очереди — 1
a.queue_past_streams(vids, 2, log=lambda *_: None)
assert [v["key"] for v in json.load(open(os.path.join(d, "extra_vods.json"), encoding="utf-8"))["vods"]] == ["v3", "v4"]
print("OK past")
