"""Вход TikTok: если приложение не приняло формат code_challenge, программа сама входит второй раз в другом формате
и запоминает подошедший. Запуск: python tests/test_tiktok_pkce.py"""
import base64
import hashlib
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from stream_clipper import publisher as p  # noqa: E402

store = {}
p.load = lambda: dict(store)
p._update = lambda **kw: store.update(kw)
sent = {}


def fake_open(url):
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
    sent.update(challenge=q["code_challenge"], state=q["state"])


def fake_http(url, data=None, *a, **k):  # «TikTok», принимающий только base64url
    want = base64.urlsafe_b64encode(hashlib.sha256(data["code_verifier"].encode()).digest()).rstrip(b"=").decode()
    if want == sent["challenge"]:
        return 200, {}, {"access_token": "A", "refresh_token": "R", "expires_in": 3600}
    return 400, {}, {"error": "invalid_request", "error_description": "Code verifier or code challenge is invalid."}


p.webbrowser.open = fake_open
p._wait_code = lambda port: {"code": "c", "state": sent["state"]}
p._http = fake_http
store["tiktok"] = {"pkce": "hex"}  # раньше запомнили неверный формат
assert p.tiktok_connect("k", "s", log=lambda *_: None) == "ok"
assert store["tiktok"]["pkce"] == "b64" and store["tiktok"]["access_token"] == "A", store
# подмена state — отказ
p._wait_code = lambda port: {"code": "c", "state": "чужой"}
try:
    p.tiktok_connect("k", "s", log=lambda *_: None)
    raise SystemExit("state не проверен")
except RuntimeError as e:
    assert "state" in str(e)
print("OK")
