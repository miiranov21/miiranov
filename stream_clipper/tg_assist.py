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


def recipients(c: dict) -> list[dict]:
    """Кому слать посты: основной чат (личный или группа) + подтверждённые получатели (например, друг)."""
    out = [{"id": c["chat_id"], "main": True}]
    for e in c.get("extra_chats") or []:
        if e.get("id") and e["id"] != c["chat_id"]:
            out.append({"id": e["id"], "name": e.get("name", "")})
    return out


def _send(c: dict, jid: str, job: dict, channel: str) -> None:
    """Видео и текст с кнопками — каждому получателю (видео загружается один раз, остальным уходит по file_id)."""
    target = _target(c)
    if not c.get("assist_hint"):
        for r in recipients(c):
            try:
                m = telegram._call(c["token"], "sendMessage", data={"chat_id": r["id"], "text": HINT,
                                                                    **(target if r.get("main") else {})})
                try:
                    telegram._call(c["token"], "pinChatMessage", data={"chat_id": r["id"], "message_id": m["message_id"],
                                                                       "disable_notification": "true"})
                except Exception:
                    pass
            except Exception:
                pass
        c["assist_hint"] = True
        telegram.save(c)
    video = _fit_size(_render_for(job))
    msgs, file_id = [], None
    try:
        for r in recipients(c):
            extra = target if r.get("main") else {}
            data = {"chat_id": r["id"], "supports_streaming": "true",
                    "caption": f"{NAMES[job['platform']]} · {channel}", **extra}
            try:
                if file_id:
                    v = telegram._call(c["token"], "sendVideo", timeout=120, data=dict(data, video=file_id))
                else:
                    with open(video, "rb") as f:
                        v = telegram._call(c["token"], "sendVideo", timeout=900, data=data,
                                           files={"video": (f"{job['platform']}_{jid}.mp4", f, "video/mp4")})
                    file_id = ((v.get("video") or {}).get("file_id")) or None
                m = telegram._call(c["token"], "sendMessage", data={"chat_id": r["id"], "text": _text(job, channel),
                                                                    "parse_mode": "HTML", "reply_markup": _buttons(job, jid),
                                                                    "reply_to_message_id": v["message_id"], **extra})
                msgs.append({"chat": r["id"], "msg": m["message_id"], "video": v["message_id"]})
            except Exception:
                if r.get("main"):
                    raise  # основной чат обязателен; у друга может быть, например, бот на паузе — не мешаем остальным
    finally:
        if video.endswith("tg_assist_small.mp4"):
            try:
                os.remove(video)
            except OSError:
                pass
    job.update({"status": "sent", "msgs": msgs, "msg_id": msgs[0]["msg"] if msgs else None, "sent_at": time.time()})


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


def _who(cq: dict) -> str:
    u = cq.get("from") or {}
    return (u.get("first_name") or u.get("username") or "").strip()


def handle_updates(st: dict, c: dict, event) -> int:
    """Нажатия «✅ Выложил» / «⏭ Пропустить» (от любого получателя) и новые желающие получать посты (/start)."""
    ups = telegram._call(c["token"], "getUpdates", timeout=20,
                         data={"offset": st.get("offset", 0), "timeout": 0,
                               "allowed_updates": json.dumps(["message", "callback_query"])})
    known = {r["id"] for r in recipients(c)}
    n = 0
    for u in ups:
        st["offset"] = max(st.get("offset", 0), u["update_id"] + 1)
        msg = u.get("message") or {}
        chat = msg.get("chat") or {}
        if msg and chat.get("type") == "private" and chat.get("id") not in known:
            # кто-то нажал «Старт» у бота — посты он получит только после подтверждения в программе
            pend = c.setdefault("pending_chats", [])
            if chat["id"] not in [p["id"] for p in pend]:
                name = chat.get("first_name") or chat.get("username") or str(chat["id"])
                pend.append({"id": chat["id"], "name": name})
                telegram.save(c)
                event("👤", f"{name} нажал «Старт» у бота и хочет получать посты — подтверди в «Настройки» → Telegram",
                      None, "warn")
                try:
                    telegram._call(c["token"], "sendMessage", data={
                        "chat_id": chat["id"], "text": "👋 Запрос принят. Посты начнут приходить, когда владелец "
                                                       "подтвердит тебя в программе Stream Clipper."})
                except Exception:
                    pass
            continue
        cq = u.get("callback_query")
        if not cq or ":" not in (cq.get("data") or ""):
            continue
        act, jid = cq["data"].split(":", 1)
        job = st["jobs"].get(jid)
        who = _who(cq)
        note = "?"
        if job and act == "ok" and job["status"] != "posted":
            library.set_posted(job["path"], True, job["platform"])
            library.record_published(job["path"], job["platform"], job.get("title", ""),
                                     (job.get("description", "") + "\n\n" + " ".join(job.get("hashtags") or [])).strip())
            job["status"] = "posted"
            job["posted_by"] = who
            _sync_autopilot(job, "published")
            note = f"✅ Выложил{': ' + who if who else ''}"
            event("✅", f"{os.path.basename(job['path'])[:-4]}: выложено в {NAMES[job['platform']]}"
                       f"{' (' + who + ')' if who else ''}", job["path"], "clip")
            n += 1
        elif job and act == "ok":
            note = f"Уже выложено{': ' + job.get('posted_by') if job.get('posted_by') else ''}"
        elif job and act == "skip" and job["status"] != "posted":
            job["when"] = _next_when(st, job["platform"])
            job["status"] = "pending"
            job.pop("reminded", None)
            _sync_autopilot(job, "waiting", job["when"])
            note = f"⏭ {who + ' перенёс' if who else 'Перенёс'} на {job['when'][8:10]}.{job['when'][5:7]} {job['when'][11:16]}"
            event("⏭", f"{os.path.basename(job['path'])[:-4]}: {NAMES[job['platform']]} — {note}", None, "info")
        try:
            telegram._call(c["token"], "answerCallbackQuery", data={"callback_query_id": cq["id"], "text": note})
        except Exception:
            pass
        if job and act in ("ok", "skip"):  # кнопки меняются у ВСЕХ получателей — второй увидит, что уже выложено
            for m in job.get("msgs") or ([{"chat": c["chat_id"], "msg": job["msg_id"]}] if job.get("msg_id") else []):
                try:
                    telegram._call(c["token"], "editMessageReplyMarkup", data={
                        "chat_id": m["chat"], "message_id": m["msg"],
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
            for m in job.get("msgs") or [{"chat": c["chat_id"], "msg": job.get("msg_id")}]:
                try:
                    telegram._call(c["token"], "sendMessage", data={
                        "chat_id": m["chat"], "text": f"⏰ Напоминание: {NAMES[job['platform']]} ждёт публикации — "
                                                      "выложи и нажми «✅ Выложил» (или «⏭ Пропустить»).",
                        "reply_to_message_id": m["msg"], **(_target(c) if m["chat"] == c["chat_id"] else {})})
                except Exception:
                    pass
            job["reminded"] = True
            stats["reminded"] += 1
    save(st)
    return stats


def overview() -> list[dict]:
    st = load()
    return sorted(({"id": k, **{x: v.get(x) for x in ("path", "platform", "when", "status", "title")}}
                   for k, v in st["jobs"].items()), key=lambda x: x.get("when") or "")
