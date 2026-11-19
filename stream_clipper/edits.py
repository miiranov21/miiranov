"""Правки клипа, которые можно отменить.

Для каждого клипа храним ИСХОДНИК (как его нарезала программа) и список правок. Готовый файл в папке
каждый раз собирается заново: исходник → исправления нарушений → подпись автора → обрезка.
Поэтому любую правку можно убрать отдельно (например, размытие), не трогая остальные.

Правки (ops):
  fix     — исправления нарушений: issues со временем ОТ НАЧАЛА ИСХОДНИКА
  credit  — подпись автора
  trim    — обрезка: cut_start / cut_end секунд
  recut   — удлинение: новый исходник, скачанный заново (file, range, shift — на сколько сдвинулось время)
  frozen  — версия, сделанная до этой функции (её нельзя разобрать на части — только убрать целиком)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

from . import paths


def _store() -> str:
    return os.path.join(paths.default_work_dir(), "edits.json")


def _dir() -> str:
    d = os.path.join(paths.default_work_dir(), "edits")
    os.makedirs(d, exist_ok=True)
    return d


def load() -> dict:
    try:
        with open(_store(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict) -> None:
    with open(_store(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def get(clip: dict) -> dict | None:
    return load().get(os.path.normpath(clip["path"]))


def ensure(clip: dict) -> dict:
    """Запись правок клипа; при первой правке сохраняем исходник (и переносим правки, сделанные раньше)."""
    path = os.path.normpath(clip["path"])
    data = load()
    rec = data.get(path)
    if rec and os.path.exists(rec.get("base", "")):
        return rec
    stamp = f"{int(time.time() * 1000)}"
    rec = {"ops": [], "words": clip.get("words") or [], "next": 1,
           "range": [clip.get("start"), clip.get("end")], "moment": clip.get("moment")}
    from . import credit, policy
    legacy_credit = credit.load().get(path)
    legacy_fix = (policy.load_results().get(path) or {}).get("original")
    if legacy_fix and os.path.exists(legacy_fix):
        # клип исправляли до этой функции: исходник — сохранённый оригинал, а текущий файл — «замороженная» версия
        rec["base"] = os.path.join(_dir(), f"{stamp}_base.mp4")
        shutil.copy2(legacy_fix, rec["base"])
        frozen = os.path.join(_dir(), f"{stamp}_frozen.mp4")
        shutil.copy2(path, frozen)
        rec["ops"].append({"id": 1, "type": "frozen", "file": frozen, "label": "исправление нарушений (сделано раньше)"})
        rec["next"] = 2
    elif legacy_credit and legacy_credit.get("on") and os.path.exists(legacy_credit.get("clean", "")):
        rec["base"] = os.path.join(_dir(), f"{stamp}_base.mp4")
        shutil.move(legacy_credit["clean"], rec["base"])
        rec["ops"].append({"id": 1, "type": "credit", "pos": legacy_credit.get("pos", "bottom-left"),
                           "label": "подпись автора"})
        rec["next"] = 2
        cd = credit.load()
        cd.pop(path, None)
        credit._save(cd)
    else:
        rec["base"] = os.path.join(_dir(), f"{stamp}_base.mp4")
        shutil.copy2(path, rec["base"])
    data[path] = rec
    _save(data)
    return rec


def total_cut(rec: dict) -> tuple[float, float]:
    a = sum(float(o.get("cut_start", 0)) for o in rec["ops"] if o["type"] == "trim")
    b = sum(float(o.get("cut_end", 0)) for o in rec["ops"] if o["type"] == "trim")
    return a, b


def to_base_time(rec: dict, t: float) -> float:
    """Время в текущем клипе → время в исходнике (обрезка начала сдвигает время)."""
    return t + total_cut(rec)[0]


def source(rec: dict) -> tuple[str, float]:
    """Файл-исходник (с учётом удлинения) и сдвиг времени относительно первоначального исходника."""
    recuts = [o for o in rec["ops"] if o["type"] == "recut" and os.path.exists(o.get("file", ""))]
    if recuts:
        return recuts[-1]["file"], float(recuts[-1].get("shift", 0))
    return rec["base"], 0.0


def label(op: dict) -> str:
    from .i18n import T
    t = op["type"]
    if t == "fix":
        kinds = sorted({T(i.get("title", "")) for i in op.get("issues", [])})
        return T("Исправление нарушений: {0}").format(", ".join(kinds) or "—")
    if t == "credit":
        return T("Подпись автора")
    if t == "trim":
        return T("Обрезка: начало −{0:.1f} с, конец −{1:.1f} с").format(op.get("cut_start", 0), op.get("cut_end", 0))
    if t == "hook":
        return T("Хук-надпись: «{0}»").format(op.get("text", ""))
    if t == "recut":
        r = op.get("range") or [0, 0]
        return T("Удлинение (новые границы {0:.0f}–{1:.0f} с стрима)").format(r[0], r[1])
    return T(op.get("label", t))


def _ffmpeg(cmd: list, cwd: str | None = None) -> None:
    flags = 0x08000000 if os.name == "nt" else 0
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, creationflags=flags)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[-500:])


def build(clip: dict, rec: dict, out: str, log=print) -> dict:
    """Собирает клип из исходника и правок. Возвращает поля для дневника (start, end, words, ...)."""
    from . import clipedit, policy, render
    from . import credit as credit_mod
    work = os.path.join(_dir(), "build")
    os.makedirs(work, exist_ok=True)
    stamp = f"{int(time.time() * 1000)}"
    cur, shift = source(rec)
    frozen = [o for o in rec["ops"] if o["type"] == "frozen" and os.path.exists(o.get("file", ""))]
    if frozen and not any(o["type"] == "recut" for o in rec["ops"]):
        cur = frozen[-1]["file"]
    words = [[w[0] + shift, w[1] + shift, w[2]] for w in rec.get("words") or []]
    recut = next((o for o in reversed(rec["ops"]) if o["type"] == "recut"), None)
    if recut and recut.get("words") is not None:
        words = recut["words"]
    temps = []
    issues = [dict(i, t0=i["t0"] + shift, t1=i["t1"] + shift) for o in rec["ops"] if o["type"] == "fix"
              for i in o.get("issues", [])]
    if issues:
        log(T_("Исправляю нарушения..."))
        nxt = os.path.join(work, f"{stamp}_fix.mp4")
        policy.fix_clip(cur, nxt, issues, subs_burned=bool(words), words=words)
        temps.append(nxt)
        cur = nxt
    cr = next((o for o in rec["ops"] if o["type"] == "credit"), None)
    if cr:
        log(T_("Подписываю автора..."))
        ass = f"{stamp}_credit.ass"
        render.write_credit_ass(os.path.join(work, ass), credit_mod.platform_of(clip), credit_mod.author_of(clip),
                                cr.get("pos", "top-left"), text=cr.get("text") or None)
        nxt = os.path.join(work, f"{stamp}_credit.mp4")
        _ffmpeg(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(cur), "-vf", f"ass={ass}", "-c:v", "libx264",
                 "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", os.path.abspath(nxt)],
                cwd=work)
        os.remove(os.path.join(work, ass))
        temps.append(nxt)
        cur = nxt
    a, b = total_cut(rec)
    dur = clipedit.duration(cur)
    if a > 0 or b > 0:
        log(T_("Обрезаю..."))
        clipedit.trim_local(cur, out, a, b)
    elif cur in temps:
        shutil.move(cur, out)
        temps.remove(cur)
    else:
        shutil.copy2(cur, out)
    for t in temps:
        try:
            os.remove(t)
        except OSError:
            pass
    hook = next((o for o in reversed(rec["ops"]) if o["type"] == "hook" and (o.get("text") or "").strip()), None)
    if hook:  # хук-надпись вверху кадра в первые секунды — поверх уже готового клипа
        log(T_("Добавляю хук-надпись..."))
        ass = f"{stamp}_hook.ass"
        render.write_caption_ass(os.path.join(work, ass), hook["text"].strip(), 330,
                                 duration=float(hook.get("seconds") or 3))
        tmp = os.path.join(work, f"{stamp}_hook.mp4")
        _ffmpeg(["ffmpeg", "-y", "-v", "error", "-i", os.path.abspath(out), "-vf", f"ass={ass}", "-c:v", "libx264",
                 "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", os.path.abspath(tmp)],
                cwd=work)
        os.remove(os.path.join(work, ass))
        os.replace(tmp, out)
    new_len = max(0.0, dur - a - b)
    rng = (recut or {}).get("range") or rec.get("range") or [None, None]
    fields = {"words": clipedit.shift_words(words, a, new_len), "credit_burned": False}
    if rng[0] is not None:
        fields["start"] = float(rng[0]) + a
        fields["end"] = float(rng[0]) + a + new_len
        if rec.get("moment") is not None or (recut and clip.get("moment") is not None):
            fields["moment"] = fields["start"] if recut else float(rec["moment"]) + a
    return fields


def T_(s: str) -> str:
    from .i18n import T
    return T(s)


def commit(clip: dict, rec: dict, new_file: str, fields: dict) -> None:
    """Ставит собранную версию на место клипа и запоминает правки."""
    from . import library, policy
    path = os.path.normpath(clip["path"])
    if os.path.exists(path):
        os.remove(path)
    shutil.move(new_file, path)
    try:
        os.remove(library.thumb_path(path))
    except OSError:
        pass
    library.make_thumb(path)
    library.update_clip(path, fields)
    data = load()
    data[path] = rec
    _save(data)
    words = fields.get("words") or []
    # речь проверяем сразу; картинку окно «Исправить нарушение» проверит заново при открытии
    policy.save_result(path, {"issues": policy.check_words(words), "visual": False, "words": words, "note": "",
                              "checked": time.time(), "fixed": any(o["type"] in ("fix", "frozen") for o in rec["ops"])})


def add_op(rec: dict, op: dict) -> dict:
    op = dict(op, id=rec.get("next", 1))
    rec["next"] = op["id"] + 1
    if op["type"] == "credit":  # подпись одна
        rec["ops"] = [o for o in rec["ops"] if o["type"] != "credit"]
    if op["type"] == "recut":  # новые границы уже учитывают прежнюю обрезку
        rec["ops"] = [o for o in rec["ops"] if o["type"] not in ("trim", "recut")]
    rec["ops"].append(op)
    return rec


def remove_op(rec: dict, op_id: int) -> dict:
    gone = [o for o in rec["ops"] if o["id"] == op_id]
    rec["ops"] = [o for o in rec["ops"] if o["id"] != op_id]
    for o in gone:
        if o["type"] == "recut" and os.path.exists(o.get("file", "")):
            try:
                os.remove(o["file"])
            except OSError:
                pass
    return rec


def forget(path: str) -> None:
    """Клип удалён навсегда — его исходник больше не нужен."""
    data = load()
    rec = data.pop(os.path.normpath(path), None)
    if rec:
        for f in [rec.get("base")] + [o.get("file") for o in rec.get("ops", [])]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass
        _save(data)


def build_variant(clip: dict, extra_ops: list, out: str, log=print, platform: str | None = None) -> dict:
    """Копия клипа под конкретную площадку: правки клипа + монтаж, который заказали «Доктор» или автопилот.
    Сам клип в папке не меняется. Возвращает, что применено и что пропущено (пишется в каталог для проверки)."""
    from . import montage
    work = os.path.join(_dir(), "build")
    os.makedirs(work, exist_ok=True)
    tmp = os.path.join(work, f"{int(time.time() * 1000)}_var_src.mp4")
    rec = get(clip)
    if rec and rec.get("ops"):
        build(clip, rec, tmp, log)
    else:
        shutil.copy2(clip["path"], tmp)
    try:
        res = montage.render_plan(tmp, out, list(extra_ops or []), words=clip.get("words") or [], clip=clip, log=log)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    if platform:
        save_render(clip, platform, out, res)
    return res


def _renders_file() -> str:
    return os.path.join(paths.default_work_dir(), "renders.json")


def load_renders() -> dict:
    try:
        with open(_renders_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_render(clip: dict, platform: str, out: str, res: dict) -> None:
    """Версия клипа под площадку — для каталога («Доктор» и автопилот проверяют результат)."""
    from . import library
    data = load_renders()
    thumb = os.path.splitext(out)[0] + "_thumb.png"
    try:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", out, "-frames:v", "1", "-vf", "scale=-2:256",
                        thumb], capture_output=True, timeout=60,
                       creationflags=0x08000000 if os.name == "nt" else 0)
    except Exception:
        thumb = ""
    data.setdefault(os.path.normpath(clip["path"]), {})[platform] = {
        "path": out.replace("\\", "/"), "thumb": thumb.replace("\\", "/") if thumb and os.path.exists(thumb) else "",
        "applied": res.get("applied", []), "skipped": res.get("skipped", []), "cover": res.get("cover"),
        "duration": res.get("duration"), "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open(_renders_file(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
