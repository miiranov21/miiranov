"""Язык окна программы. Русский — родной язык кода; переводы лежат в stream_clipper/lang/<код>.json
(ключ — русская фраза без крайних пробелов, значение — перевод; {0}, {1}... — подставляемые части).

T("фраза")     — перевод фразы окна;
tr_line(line)   — перевод строки журнала, пришедшей от рабочей части (по шаблонам);
untranslate(s)  — обратно на русский (для значений, которые сохраняются в настройки).
Язык выбирается в «Настройках» и применяется после перезапуска окна.
"""
from __future__ import annotations

import json
import os
import re

LANGS = {"ru": "Русский", "az": "Azərbaycanca"}
_HERE = os.path.dirname(os.path.abspath(__file__))
_PH = re.compile(r"\{(\d+)(![rsa])?(:[^{}]*)?\}")
_CYR = re.compile("[А-Яа-яЁё]")


def _detect() -> str:
    lang = os.environ.get("STREAM_CLIPPER_LANG", "")
    if not lang:
        try:
            with open(os.path.join(os.path.dirname(_HERE), "settings.json"), encoding="utf-8") as f:
                lang = json.load(f).get("lang", "")
        except Exception:
            lang = ""
    if not lang:  # язык ещё не выбирали — берём язык Windows (азербайджанский Windows → азербайджанский)
        try:
            import locale
            sys_lang = (locale.getlocale()[0] or "").lower()
            if os.name == "nt":
                import ctypes
                import locale as _l
                sys_lang = (_l.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), "")
                            or sys_lang).lower()
            if sys_lang.startswith(("az", "azerbaijan")):
                lang = "az"
        except Exception:
            pass
    return lang if lang in LANGS else "ru"


def _load(lang: str) -> dict:
    if lang == "ru":
        return {}
    try:
        with open(os.path.join(_HERE, "lang", lang + ".json"), encoding="utf-8") as f:
            data = json.load(f)
        return {k.strip(): v for k, v in data.items() if isinstance(v, str) and v.strip()}
    except Exception:
        return {}


LANG = _detect()
_TR = _load(LANG)
_REV = {v: k for k, v in _TR.items()}
_patterns: list | None = None
_prefixes: list | None = None


def _pad(s: str, core: str, new: str) -> str:
    lead = len(s) - len(s.lstrip())
    trail = len(s) - len(s.rstrip())
    return s[:lead] + new + (s[len(s) - trail:] if trail else "")


def T(s: str) -> str:
    if not _TR or not isinstance(s, str):
        return s
    core = s.strip()
    tr = _TR.get(core)
    return _pad(s, core, tr) if tr is not None else s


def untranslate(s):
    if not _REV or not isinstance(s, str):
        return s
    core = s.strip()
    ru = _REV.get(core)
    return _pad(s, core, ru) if ru is not None else s


def _compile():
    global _patterns, _prefixes
    pats, pref = [], []
    for key, tr in _TR.items():
        if _PH.search(key):
            literal = _PH.sub("", key).replace("{{", "{").replace("}}", "}")
            if len(literal.strip()) < 4:
                continue  # слишком общий шаблон («с {0}») — ловил бы что попало
            rx, pos = "", 0
            for m in _PH.finditer(key):
                rx += re.escape(key[pos:m.start()].replace("{{", "{").replace("}}", "}")) + "(.*?)"
                pos = m.end()
            rx += re.escape(key[pos:].replace("{{", "{").replace("}}", "}"))
            pats.append((len(literal), re.compile(rx, re.S), tr))
        elif len(key) >= 8:
            pref.append((key, tr))
    pats.sort(key=lambda p: -p[0])
    pref.sort(key=lambda p: -len(p[0]))
    _patterns, _prefixes = pats, pref


def _fill(tr: str, groups: tuple) -> str:
    def sub(m):
        i = int(m.group(1))
        return groups[i] if i < len(groups) else m.group(0)
    return _PH.sub(sub, tr).replace("{{", "{").replace("}}", "}")


def tr_line(line: str, _depth: int = 0) -> str:
    """Переводит строку журнала: целиком, по шаблону с подстановками или по известному началу."""
    if not _TR or not line or not _CYR.search(line) or _depth > 3:
        return line
    core = line.strip()
    tr = _TR.get(core)
    if tr is not None:
        return _pad(line, core, tr)
    if _patterns is None:
        _compile()
    for _, rx, tr in _patterns:
        m = rx.fullmatch(core)
        if m:
            groups = tuple(tr_line(g, _depth + 1) for g in m.groups())
            return _pad(line, core, _fill(tr, groups))
    for key, tr in _prefixes:
        if core.startswith(key):
            return _pad(line, core, tr + tr_line(core[len(key):], _depth + 1))
    return line
