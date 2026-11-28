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

# никто подходящий не в эфире: добираем любимчиками и ставим их прошлые стримы в очередь (разобранный — пропускаем)
assert a.choose({}, [], {}, now, 3, ["kaicenat", "jynxzi"]) == ["kaicenat", "jynxzi"]
a.twitch_streams = {"kaicenat": [{"key": "v2", "url": "u2", "title": "GTA 6 day 3"}, {"key": "v1", "url": "u1"}],
                    "jynxzi": [{"key": "v9", "url": "u9", "title": "done one"}]}
from stream_clipper import progress, twitch  # noqa: E402
twitch.list_streams = lambda kind, n, k: a.twitch_streams[n]
progress.load = lambda: {"v2": {"x": 1}, "v9": {"x": 1}}
progress.summary = lambda e: {"finished": True}
msgs = []
a.queue_past_streams(["kaicenat", "jynxzi"], log=msgs.append)
import json  # noqa: E402
q = json.load(open(os.path.join(d, "extra_vods.json"), encoding="utf-8"))["vods"]
assert [v["url"] for v in q] == ["u1"] and q[0]["channel"] == "kaicenat", q
a.queue_past_streams(["kaicenat"], log=msgs.append)  # уже в очереди — второй раз не ставим
assert len(json.load(open(os.path.join(d, "extra_vods.json"), encoding="utf-8"))["vods"]) == 1
print("OK offline")
