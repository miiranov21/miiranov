"""Подписи: HE/HIS только для мужчин, тип хука не повторяется подряд, цитата не идёт два раза подряд,
обрывки цитат не попадают в описание, описание не длиннее description_max_words.
Запуск: python tests/test_captions.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import caption as cap  # noqa: E402

BANK = {"male_streamers": ["kaicenat"], "female_streamers": ["missmikkaa"], "nicknames": {"missmikkaa": "MIKKAA", "kaicenat": "KAI"},
        "en": {"laugh": ["{s} FELL OUT HIS CHAIR", "{s} CAN'T STOP LAUGHING"], "shock": ["{s} FROZE", "WATCH HER FACE"],
               "hype": ["{s} DID IT", "ONLY {s} CAN DO THIS"]}}
hist = []
cap.hook_bank = lambda: BANK
cap.caption_history = lambda: list(hist)
cap.recent_captions = lambda s: []
cap.account_lang = lambda lang=None: "en"
cap.strategy_rules = lambda: {"description_max_words": 20}


def make(streamer, msgs=("lol", "kekw"), quote=None):
    t = cap.template_caption(streamer, "GTA", list(msgs), "en", quote)
    hist.append({"text": t, "tpl": cap.LAST_TPL["value"], "type": cap.LAST_TPL["type"]})
    return t


for _ in range(12):  # у неизвестных и у женщин — ни одного HIS/HE
    t = make("missmikkaa")
    assert " HIS " not in f" {t} ", t
    t = make("jynxzi")
    assert not cap._PRON_M.search(t) and not cap._PRON_F.search(t), t
types = [h["type"] for h in hist]
assert all(a != b for a, b in zip(types, types[1:])), types  # тип подряд не повторяется

hist.clear()
q1 = make("kaicenat", quote="bro what is that")
q2 = make("kaicenat", quote="no way this happened")
assert q1.startswith("KAI:") and not q2.startswith("KAI:"), (q1, q2)  # цитата не два раза подряд

assert not cap._whole_phrase("kind of what y 'all Nick what the")
assert cap._whole_phrase("I can't believe he did that!")
post = cap.free_post("tiktok", "kaicenat", "KAI DID IT", "GTA 6 stream", "kind of what y 'all Nick what the",
                     ["lol"], "en", [], None, "KaiCenat")
assert "y 'all" not in post["description"], post["description"]
assert len(post["description"].split()) <= 20, post["description"]
print("OK")

# оценка хука: конкретный хук сильнее пустого; из свежих берётся один из двух сильнейших
from stream_clipper import hookscore  # noqa: E402
assert hookscore.score("KAI STOLE A TANK AND WRECKED IT IN 3 SECONDS", "KAI") > hookscore.score("KAI DID IT", "KAI")
hist.clear()
BANK["en"]["hype"] = ["{s} DID IT", "{s} WON $10K IN 3 MINUTES", "{s} DID IT AGAIN"]
picked = {cap.template_caption("kaicenat", "GTA", ["pog"], "en") for _ in range(20)}
assert "KAI WON $10K IN 3 MINUTES" in picked and "KAI DID IT" not in picked, picked
print("OK hookscore")

# пост без машинного следа и с правильными хэштегами
post = cap.free_post("tiktok", "kaicenat", "KAI DID IT", "GTA 6 stream", "", ["lol"], "en", [], None, "KaiCenat")
assert "—" not in post["description"] and "​" not in post["description"], post["description"]
assert len(post["hashtags"]) <= 5 and not {"#fyp", "#viral", "#shorts"} & set(post["hashtags"]), post["hashtags"]
print("OK caption lint")

# заголовок YouTube — хук текстом + тег + #shorts, а не один хэштег (баг 13 Shorts)
cap.strategy_rules = lambda: {"hashtag_templates": {"youtube": ["#{streamer}", "#gta6", "#shorts"]}}
yt = cap.free_post("youtube", "kaicenat", "KAI HAD TO WALK AWAY", "GTA 6", "", ["lol"], "en", [], None, "KaiCenat")
assert yt["title"].lower().startswith("kai had to walk away") and "#shorts" in yt["title"], yt["title"]
assert "#shorts" in yt["hashtags"], yt["hashtags"]
assert cap.good_title("#ishowspeedclips", "Speed had to walk away 😂\nmore", "youtube") == "Speed had to walk away 😂 #ishowspeedclips #shorts"
print("OK youtube title")
