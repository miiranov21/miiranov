"""Публикация через Telegram (бесплатный режим «telegram_assist»).

В момент слота из плана (автопилот или decisions.json «Доктора») бот присылает на каждую площадку отдельное сообщение:
  * готовое видео именно для этой площадки (с хуком, подписью автора и остальным монтажом) — как видео, чтобы его
    можно было сразу «Поделиться» в приложение TikTok / Instagram / YouTube;
  * текст: заголовок, описание и хэштеги в блоке <code> — одно нажатие копирует всё;
  * кнопки: «📲 Открыть <площадку>», «✅ Выложил», «⏭ Пропустить».
«✅ Выложил» ставит галочку «выложено» (и запоминает текст и время для «Доктора»), «⏭ Пропустить» переносит
клип на следующий слот. Через 30 минут без ответа — одно напоминание. Непросмотренных постов на площадку
не больше двух: остальные ждут.
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import time
from datetime import datetime, timedelta

from . import exchange, library, paths, telegram

OPEN_URL = {"tiktok": "https://www.tiktok.com/upload", "youtube": "https://studio.youtube.com",
            "instagram": "https://www.instagram.com"}
NAMES = {"tiktok": "TikTok", "youtube": "YouTube", "instagram": "Instagram"}
MAX_PENDING = 2
REMIND_AFTER = 30 * 60
FLAGS = 0x08000000 if os.name == "nt" else 0
HINT = ("📌 Как выкладывать: нажми на видео → «Поделиться» → TikTok / Instagram / YouTube → вставь текст "
        "(нажми на блок с текстом — он скопируется) → «Опубликовать». Потом нажми здесь «✅ Выложил».")


def _file() -> str:
    return os.path.join(paths.default_work_dir(), "tg_assist.json")


def load() -> dict:
    try:
        with open(_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"jobs": {}, "offset": 0}


def save(st: dict) -> None:
    tmp = _file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _file())


def mode() -> str:
    from . import strategy
    s = strategy.get()
    return s.get("publish_mode") or (s.get("autopilot") or {}).get("publish_mode") or "telegram_assist"


def _job_id(path: str, platform: str) -> str:
    import hashlib
    return hashlib.sha1(f"{os.path.normpath(path)}|{platform}".encode()).hexdigest()[:10]


# ---------- откуда берутся задания: очередь автопилота и план «Доктора» ----------
def sync_jobs(st: dict) -> None:
    from . import autopilot
    jobs = st["jobs"]
    ap = autopilot.load_state()
    for path, rec in ap.get("clips", {}).items():
        for pl, q in (rec.get("queue") or {}).items():
            if q.get("status") != "waiting":
                continue
            jid = _job_id(path, pl)
            if jid not in jobs:
                jobs[jid] = {"path": path, "platform": pl, "when": q.get("when"), "title": q.get("title", ""),
                             "description": q.get("description", ""), "hashtags": q.get("hashtags") or [],
                             "file": q.get("file"), "applied": (rec.get("renders") or {}).get(pl, {}).get("applied"),
                             "status": "pending", "source": "autopilot"}
    clips = [c for d in library.list_dates() for c in library.list_clips(d)]
    for c, pl, p in exchange.plan(clips):
        jid = _job_id(c["path"], pl)
        if jid in jobs or not p.get("when"):
            continue
        title, desc = exchange.platform_text(p)
        jobs[jid] = {"path": c["path"], "platform": pl, "when": p["when"], "title": p.get("title") or c.get("caption") or "",
                     "description": exchange.with_author(p.get("description") or "", c, pl),
                     "hashtags": p.get("hashtags") or [], "edits": p.get("edits") or [], "file": None,
                     "status": "pending", "source": "doctor"}


def _fit_size(path: str) -> str:
    """Больше 49 МБ — сжимаем (CRF), а не отправляем ссылкой."""
    if os.path.getsize(path) <= telegram.LIMIT:
        return path
    out = os.path.join(paths.default_work_dir(), "tg_assist_small.mp4")
    for scale, crf in (("-2:1920", 24), ("-2:1920", 28), ("-2:1280", 28), ("-2:1280", 32)):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", f"scale={scale}", "-c:v", "libx264",
                        "-preset", "medium", "-crf", str(crf), "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                        out], capture_output=True, creationflags=FLAGS)
        if os.path.exists(out) and os.path.getsize(out) <= telegram.LIMIT:
            return out
    raise RuntimeError("видео не ужимается до 49 МБ")


def _render_for(job: dict) -> str:
    if job.get("file") and os.path.exists(job["file"]):
        return job["file"]
    clip = next((c for d in library.list_dates() for c in library.list_clips(d)
                 if os.path.normpath(c["path"]) == os.path.normpath(job["path"])), None)
    if clip is None:
        raise RuntimeError("клип больше не в папке")
    if not job.get("edits"):
        return clip["path"]
    from . import edits
    out = os.path.join(paths.default_work_dir(), "tg_assist", f"{job['platform']}_{os.path.basename(clip['path'])}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    res = edits.build_variant(clip, job["edits"], out, log=lambda m: None, platform=job["platform"])
    job["applied"] = [a["type"] for a in res.get("applied", [])]
    job["file"] = out
    return out


def _target(c: dict) -> dict:
    """Группа с темами — отдельная тема «📤 К публикации»; личный чат — просто сообщения."""
    if not c.get("forum"):
        return {}
    if not c.get("assist_topic"):
        t = telegram._call(c["token"], "createForumTopic", data={"chat_id": c["chat_id"], "name": "📤 К публикации"})
        c["assist_topic"] = t["message_thread_id"]
        telegram.save(c)
    return {"message_thread_id": c["assist_topic"]}


def _text(job: dict, channel: str) -> str:
    when = (job.get("when") or "")[11:16]
    e = lambda s: html.escape(s or "", quote=False)
    tags = " ".join(job.get("hashtags") or [])
    head = f"🎬 <b>{NAMES[job['platform']]} · {when} · {e(channel)}</b>"
    if job["platform"] == "youtube":
        body = (f"Название:\n<code>{e(job.get('title'))}</code>\n\nОписание:\n<code>{e(job.get('description'))}"
                f"{chr(10) * 2 + e(tags) if tags else ''}</code>")
    else:
        text = "\n\n".join(x for x in (job.get("title"), job.get("description"), tags) if x)
        body = f"<code>{e(text)}</code>"
    return (head + "\n\n" + body)[:4000]


def _buttons(job: dict, jid: str) -> str:
    return json.dumps({"inline_keyboard": [
        [{"text": f"📲 Открыть {NAMES[job['platform']]}", "url": OPEN_URL[job["platform"]]}],
        [{"text": "✅ Выложил", "callback_data": f"ok:{jid}"}, {"text": "⏭ Пропустить", "callback_data": f"skip:{jid}"}]]},
        ensure_ascii=False)


def _send(c: dict, jid: str, job: dict, channel: str) -> None:
    target = _target(c)
    if not c.get("assist_hint"):
        try:
            m = telegram._call(c["token"], "sendMessage", data={"chat_id": c["chat_id"], "text": HINT, **target})
            try:
                telegram._call(c["token"], "pinChatMessage", data={"chat_id": c["chat_id"], "message_id": m["message_id"],
                                                                   "disable_notification": "true"})
            except Exception:
                pass
            c["assist_hint"] = True
            telegram.save(c)
        except Exception:
            pass
    video = _fit_size(_render_for(job))
    try:
        with open(video, "rb") as f:
            v = telegram._call(c["token"], "sendVideo", timeout=900,
                               data={"chat_id": c["chat_id"], "supports_streaming": "true",
                                     "caption": f"{NAMES[job['platform']]} · {channel}", **target},
                               files={"video": (f"{job['platform']}_{jid}.mp4", f, "video/mp4")})
    finally:
        if video.endswith("tg_assist_small.mp4"):
            try:
                os.remove(video)
            except OSError:
                pass
    m = telegram._call(c["token"], "sendMessage", data={"chat_id": c["chat_id"], "text": _text(job, channel),
                                                        "parse_mode": "HTML", "reply_markup": _buttons(job, jid),
                                                        "reply_to_message_id": v["message_id"], **target})
    job.update({"status": "sent", "msg_id": m["message_id"], "video_msg": v["message_id"], "sent_at": time.time()})


def _next_when(st: dict, platform: str) -> str:
    """«Пропустить» — на следующий свободный слот площадки (окна, паузы и лимиты — из стратегии «Доктора»)."""
    from . import autopilot, strategy
    taken = {"clips": {}}
    for i, j in enumerate(st["jobs"].values()):
        if j.get("when") and j["status"] in ("pending", "sent"):
            taken["clips"][f"j{i}"] = {"queue": {j["platform"]: {"when": j["when"]}}}
    return autopilot.next_slot(platform, taken, strategy.get()).isoformat(timespec="minutes")


def _sync_autopilot(job: dict, status: str, when: str | None = None) -> None:
    if job.get("source") != "autopilot":
        return
    from . import autopilot
    ap = autopilot.load_state()
    q = ((ap.get("clips", {}).get(job["path"]) or {}).get("queue") or {}).get(job["platform"])
    if q:
        q["status"] = status
        if when:
            q["when"] = when
        autopilot.save_state(ap)


def handle_updates(st: dict, c: dict, event) -> int:
    """Нажатия «✅ Выложил» / «⏭ Пропустить»."""
    ups = telegram._call(c["token"], "getUpdates", timeout=20,
                         data={"offset": st.get("offset", 0), "timeout": 0,
                               "allowed_updates": json.dumps(["callback_query"])})
    n = 0
    for u in ups:
        st["offset"] = max(st.get("offset", 0), u["update_id"] + 1)
        cq = u.get("callback_query")
        if not cq or ":" not in (cq.get("data") or ""):
            continue
        act, jid = cq["data"].split(":", 1)
        job = st["jobs"].get(jid)
        note = "?"
        if job and act == "ok" and job["status"] != "posted":
            library.set_posted(job["path"], True, job["platform"])
            library.record_published(job["path"], job["platform"], job.get("title", ""),
                                     (job.get("description", "") + "\n\n" + " ".join(job.get("hashtags") or [])).strip())
            job["status"] = "posted"
            _sync_autopilot(job, "published")
            note = "✅ Отмечено: выложено"
            event("✅", f"{os.path.basename(job['path'])[:-4]}: выложено в {NAMES[job['platform']]} (отмечено в Telegram)",
                  job["path"], "clip")
            n += 1
        elif job and act == "skip" and job["status"] != "posted":
            job["when"] = _next_when(st, job["platform"])
            job["status"] = "pending"
            job.pop("reminded", None)
            _sync_autopilot(job, "waiting", job["when"])
            note = f"⏭ Перенёс на {job['when'][8:10]}.{job['when'][5:7]} {job['when'][11:16]}"
            event("⏭", f"{os.path.basename(job['path'])[:-4]}: {NAMES[job['platform']]} — {note}", None, "info")
        try:
            telegram._call(c["token"], "answerCallbackQuery", data={"callback_query_id": cq["id"], "text": note})
            if job and job.get("msg_id"):
                telegram._call(c["token"], "editMessageReplyMarkup",
                               data={"chat_id": c["chat_id"], "message_id": job["msg_id"],
                                     "reply_markup": json.dumps({"inline_keyboard": [[{"text": note, "callback_data": "noop:0"}]]},
                                                                ensure_ascii=False)})
        except Exception:
            pass
    return n


def tick(paused: bool, event) -> dict:
    """Один проход: обработать нажатия, отправить то, чему пора, напомнить о непросмотренном."""
    c = telegram.load()
    if not (c.get("token") and c.get("chat_id")):
        return {"error": "Telegram не подключён"}
    st = load()
    stats = {"sent": 0, "posted": 0, "reminded": 0}
    try:
        stats["posted"] = handle_updates(st, c, event)
    except Exception as e:
        event("❌", f"Telegram: не смог прочитать нажатия кнопок — {e}", None, "error")
    sync_jobs(st)
    now = datetime.now()
    if not paused:
        from . import policy
        for jid, job in sorted(st["jobs"].items(), key=lambda kv: kv[1].get("when") or ""):
            if job["status"] != "pending" or not job.get("when") or job["when"] > now.isoformat(timespec="minutes"):
                continue
            clip_posted = (library.load_posted().get(os.path.normpath(job["path"])) or {}).get(job["platform"])
            if clip_posted:
                job["status"] = "posted"
                continue
            block = policy.publish_block(job["path"], job.get("applied") or job.get("edits"))
            if block:
                job["status"] = "blocked"
                event("⛔", f"{os.path.basename(job['path'])[:-4]}: {NAMES[job['platform']]} — не отправляю: {block}",
                      job["path"], "error")
                continue
            pending = sum(1 for j in st["jobs"].values() if j["platform"] == job["platform"] and j["status"] == "sent")
            if pending >= MAX_PENDING:  # не заваливаем: пока два поста не просмотрены, остальные ждут
                job["when"] = (now + timedelta(minutes=30)).isoformat(timespec="minutes")
                continue
            channel = next((cc.get("channel", "") for d in library.list_dates() for cc in library.list_clips(d)
                            if os.path.normpath(cc["path"]) == os.path.normpath(job["path"])), "")
            try:
                _send(c, jid, job, channel)
                stats["sent"] += 1
                event("📤", f"{channel}: {NAMES[job['platform']]} — отправил в Telegram, выкладывай с телефона", job["path"], "info")
            except Exception as e:
                job["errors"] = job.get("errors", 0) + 1
                job["when"] = (now + timedelta(minutes=15)).isoformat(timespec="minutes")
                if job["errors"] >= 3:
                    job["status"] = "error"
                event("❌", f"Telegram: не отправилось ({NAMES[job['platform']]}) — {e}"[:220], None, "error")
    for jid, job in st["jobs"].items():  # одно напоминание через 30 минут
        if job["status"] == "sent" and not job.get("reminded") and time.time() - job.get("sent_at", 0) > REMIND_AFTER:
            try:
                telegram._call(c["token"], "sendMessage", data={
                    "chat_id": c["chat_id"], "text": f"⏰ Напоминание: {NAMES[job['platform']]} ждёт публикации — "
                                                     "выложи и нажми «✅ Выложил» (или «⏭ Пропустить»).",
                    "reply_to_message_id": job.get("msg_id"), **_target(c)})
                job["reminded"] = True
                stats["reminded"] += 1
            except Exception:
                pass
    save(st)
    return stats


def overview() -> list[dict]:
    st = load()
    return sorted(({"id": k, **{x: v.get(x) for x in ("path", "platform", "when", "status", "title")}}
                   for k, v in st["jobs"].items()), key=lambda x: x.get("when") or "")
