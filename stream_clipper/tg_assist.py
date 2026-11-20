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
HINT_SCHEDULE = (
    "📌 Как планировать публикации (аудитория — США, поэтому время ночное по Москве — вставать не нужно).\n"
    "Бот присылает видео на сегодня днём, файлами. У каждого написано, на какое время его запланировать.\n\n"
    "1) Сохрани файл видео в галерею: нажми на файл → «⋯» → «Сохранить в галерею» (файл — без потери качества).\n"
    "2) Скопируй текст (нажми на блок с текстом — он скопируется).\n"
    "3) Запланируй в приложении:\n"
    "• TikTok: «+» → загрузи видео → «Далее» → вставь текст → «Ещё параметры» → «Запланировать публикацию» → "
    "выбери дату и время → «Запланировать».\n"
    "• YouTube: «+» → «Создать Short» → загрузи видео → «Далее» → вставь название и описание → «Видимость» → "
    "«Запланировать» → дата и время → «Загрузить Short».\n"
    "• Instagram: «+» → «Reels» → выбери видео → «Далее» → вставь подпись → «Дополнительные настройки» → "
    "«Запланировать» → дата и время → «Запланировать». Если написано «🧪 пробный Reels» — включи «Пробный Reels».\n\n"
    "Время в приложении — московское (как на телефоне). Потом нажми здесь «✅ Запланировал».")
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


def schedule_mode() -> bool:
    """Публикацию планируют в приложениях заранее: бот шлёт пачку днём (telegram_delivery_msk), без ночных подъёмов."""
    from . import strategy
    ap = strategy.get().get("autopilot") or {}
    return bool(ap.get("schedule_in_app") and ap.get("telegram_delivery_msk"))


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
    """Больше 49 МБ (лимит бота) — та же 1080p, только битрейт ниже; иначе отправляем как есть, без пересжатия."""
    if os.path.getsize(path) <= telegram.LIMIT:
        return path
    out = telegram.fit_1080(path, os.path.join(paths.default_work_dir(), "tg_assist_small.mp4"))
    if not out:
        raise RuntimeError("видео не ужимается до 49 МБ")
    return out


def _block_after_render(job: dict) -> str | None:
    """Сначала собрать готовую версию (запикать мат, размыть наготу), потом проверить жёсткое правило публикации."""
    from . import policy
    try:
        _render_for(job)
    except Exception:
        pass
    return policy.publish_block(job["path"], job.get("applied") or job.get("edits"))


def _types(ops) -> set:
    return {(o.get("type") if isinstance(o, dict) else o) for o in (ops or [])}


def _render_for(job: dict) -> str:
    """Готовое видео для площадки: весь монтаж уже сделан — мат запикан, нагота размыта, подпись автора, громкость.
    Если версия от автопилота собрана раньше без этого — пересобираем."""
    have = job.get("applied") or []
    if job.get("file") and os.path.exists(job["file"]) and _types(have) & {"bleep_profanity", "bleep", "mute"}:
        return job["file"]
    clip = next((c for d in library.list_dates() for c in library.list_clips(d)
                 if os.path.normpath(c["path"]) == os.path.normpath(job["path"])), None)
    if clip is None:
        raise RuntimeError("клип больше не в папке")
    from . import autopilot, edits, policy, strategy
    clip["policy"] = policy.load_results().get(os.path.normpath(clip["path"])) or {}
    base = [o for o in (have if have and isinstance(have[0], dict) else (job.get("edits") or [])) if isinstance(o, dict)]
    ops = autopilot.ensure_mandatory(base, clip, strategy.get(), job["platform"], autopilot._dur(clip))
    out = os.path.join(paths.default_work_dir(), "tg_assist", f"{job['platform']}_{os.path.basename(clip['path'])}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    res = edits.build_variant(clip, ops, out, log=lambda m: None, platform=job["platform"])
    job["applied"] = res.get("applied", [])
    job["file"] = out
    return out


def _cover_for(job: dict) -> str | None:
    if job["platform"] != "instagram":
        return None
    from . import edits
    rec = (edits.load_renders().get(os.path.normpath(job["path"])) or {}).get("instagram") or {}
    p = rec.get("cover")
    return p if p and os.path.exists(p) else None


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
    if job.get("schedule"):
        from . import schedule
        t = datetime.fromisoformat(job["when"])
        head = (f"🗓 <b>{NAMES[job['platform']]} · {e(channel)}</b>\n"
                f"Запланировать на <b>{schedule.day_label(t)} {schedule.label(t)}</b>")
        if job.get("trial"):
            head += "\n🧪 Можно как «Пробный Reels» (покажут не подписчикам)"
    if job["platform"] == "youtube":
        body = (f"Название:\n<code>{e(job.get('title'))}</code>\n\nОписание:\n<code>{e(job.get('description'))}"
                f"{chr(10) * 2 + e(tags) if tags else ''}</code>")
    else:
        text = "\n\n".join(x for x in (job.get("title"), job.get("description"), tags) if x)
        body = f"<code>{e(text)}</code>"
    return (head + "\n\n" + body)[:4000]


def _buttons(job: dict, jid: str) -> str:
    done = "✅ Запланировал" if job.get("schedule") else "✅ Выложил"
    return json.dumps({"inline_keyboard": [
        [{"text": f"📲 Открыть {NAMES[job['platform']]}", "url": OPEN_URL[job["platform"]]}],
        [{"text": done, "callback_data": f"ok:{jid}"}, {"text": "⏭ Пропустить", "callback_data": f"skip:{jid}"}],
        [{"text": "🚫 Не выкладывать: мат", "callback_data": f"nobad:{jid}"},
         {"text": "🚫 Не залетит", "callback_data": f"noweak:{jid}"}]]},
        ensure_ascii=False)


REJECT_WHY = {"nobad": "мат / плохое слово", "noweak": "не залетит"}


def _edit_all(c: dict, job: dict, note: str) -> None:
    for m in job.get("msgs") or ([{"chat": c["chat_id"], "msg": job["msg_id"]}] if job.get("msg_id") else []):
        try:
            telegram._call(c["token"], "editMessageReplyMarkup", data={
                "chat_id": m["chat"], "message_id": m["msg"],
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": note, "callback_data": "noop:0"}]]},
                                           ensure_ascii=False)})
        except Exception:
            pass


def reject_clip(st: dict, c: dict, job: dict, why: str, who: str, event) -> None:
    """«Не выкладывать»: клип убирается из плана на ВСЕХ площадках (и из Telegram), автопилот его больше не берёт,
    «Доктор» видит причину. Освободившиеся слоты получат другие клипы — замену пришлём сразу."""
    from . import autopilot
    path = os.path.normpath(job["path"])
    ap = autopilot.load_state()
    rec = ap.get("clips", {}).get(job["path"]) or {}
    plats = set((rec.get("queue") or {}).keys()) | {job["platform"]}
    ap.setdefault("clips", {})[job["path"]] = dict(rec, stage="rejected_by_user", reason=why, by=who, queue={})
    autopilot.save_state(ap)
    for pl in plats:
        exchange.drop_platform(job["path"], pl)
    for jid2, j in list(st["jobs"].items()):
        if os.path.normpath(j.get("path", "")) == path and j.get("status") in ("pending", "sent", "error"):
            if j.get("status") == "sent" and j is not job:
                _edit_all(c, j, f"🚫 Не выкладываем ({why})")
            j["status"] = "rejected"
            j["why"] = why
    rep = st.setdefault("replace", {})
    for pl in plats:
        rep[pl] = int(rep.get(pl, 0)) + 1
    autopilot.journal({"clip": exchange.clip_id(job["path"]), "action": "rejected_by_user", "platform": job["platform"],
                       "why": why, "by": who})
    event("🚫", f"{os.path.basename(path)[:-4]}: не выкладываем — {why}{' (' + who + ')' if who else ''}; "
               f"ищу замену", job["path"], "warn")


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
    hint_v = "schedule2" if job.get("schedule") else True
    if c.get("assist_hint") != hint_v:
        for r in recipients(c):
            try:
                m = telegram._call(c["token"], "sendMessage", data={"chat_id": r["id"],
                                                                    "text": HINT_SCHEDULE if job.get("schedule") else HINT,
                                                                    **(target if r.get("main") else {})})
                try:
                    telegram._call(c["token"], "pinChatMessage", data={"chat_id": r["id"], "message_id": m["message_id"],
                                                                       "disable_notification": "true"})
                except Exception:
                    pass
            except Exception:
                pass
        c["assist_hint"] = hint_v
        telegram.save(c)
    video = _fit_size(_render_for(job))
    msgs, file_id = [], None
    try:
        for r in recipients(c):
            extra = target if r.get("main") else {}
            # ФАЙЛОМ, а не «видео»: Telegram не пережимает файл — на телефон скачивается исходное качество
            data = {"chat_id": r["id"], "disable_content_type_detection": "true",
                    "caption": f"{NAMES[job['platform']]} · {channel}", **extra}
            safe = "".join(ch if ch.isascii() and (ch.isalnum() or ch in "-_") else "_" for ch in channel) or "clip"
            try:
                if file_id:
                    v = telegram._call(c["token"], "sendDocument", timeout=120, data=dict(data, document=file_id))
                else:
                    with open(video, "rb") as f:
                        v = telegram._call(c["token"], "sendDocument", timeout=900, data=data,
                                           files={"document": (f"{job['platform']}_{safe}_{jid}.mp4", f, "video/mp4")})
                    file_id = ((v.get("document") or v.get("video") or {}).get("file_id")) or None
                m = telegram._call(c["token"], "sendMessage", data={"chat_id": r["id"], "text": _text(job, channel),
                                                                    "parse_mode": "HTML", "reply_markup": _buttons(job, jid),
                                                                    "reply_to_message_id": v["message_id"], **extra})
                msgs.append({"chat": r["id"], "msg": m["message_id"], "video": v["message_id"]})
                cover = _cover_for(job)
                if cover:  # обложка с крупным текстом (Instagram показывает её в сетке профиля)
                    try:
                        with open(cover, "rb") as f:
                            telegram._call(c["token"], "sendPhoto", timeout=120,
                                           data={"chat_id": r["id"], "caption": "🖼 Обложка для Reels: «Изменить обложку» → "
                                                 "«Добавить из галереи»", "reply_to_message_id": v["message_id"], **extra},
                                           files={"photo": ("cover.jpg", f, "image/jpeg")})
                    except Exception:
                        pass
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
                                     (job.get("description", "") + "\n\n" + " ".join(job.get("hashtags") or [])).strip(),
                                     when=job.get("when", "") if job.get("schedule") else "")
            job["status"] = "posted"
            job["posted_by"] = who
            _sync_autopilot(job, "published")
            if job.get("schedule"):
                from . import schedule
                t = datetime.fromisoformat(job["when"])
                note = f"✅ Запланировал{': ' + who if who else ''} на {schedule.day_label(t)} {schedule.label(t)}"
                event("🗓", f"{os.path.basename(job['path'])[:-4]}: {NAMES[job['platform']]} запланирован на "
                           f"{schedule.day_label(t)} {schedule.label(t)}{' (' + who + ')' if who else ''}",
                      job["path"], "clip")
            else:
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
            if schedule_mode():
                from . import schedule
                t = datetime.fromisoformat(job["when"])
                note = (f"⏭ {who + ' перенёс' if who else 'Перенёс'} на {schedule.day_label(t)} {schedule.label(t)} — "
                        f"придёт в следующей пачке")
            else:
                note = f"⏭ {who + ' перенёс' if who else 'Перенёс'} на {job['when'][8:10]}.{job['when'][5:7]} {job['when'][11:16]}"
            event("⏭", f"{os.path.basename(job['path'])[:-4]}: {NAMES[job['platform']]} — {note}", None, "info")
        try:
            telegram._call(c["token"], "answerCallbackQuery", data={"callback_query_id": cq["id"], "text": note})
        except Exception:
            pass
        if job and act in REJECT_WHY and job["status"] not in ("posted", "rejected"):
            why = REJECT_WHY[act]
            reject_clip(st, c, job, why, who, event)
            note = f"🚫 Не выкладываем ({why}){': ' + who if who else ''} — пришлю замену"
            _edit_all(c, job, note)
            try:
                telegram._call(c["token"], "answerCallbackQuery", data={"callback_query_id": cq["id"], "text": note})
            except Exception:
                pass
            continue
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
    if schedule_mode():
        try:  # расписание пересобирается при каждом изменении: удалённые/архивные клипы снимаются, слоты сдвигаются
            from . import autopilot
            autopilot.rebuild_schedule(event=event)
        except Exception as e:
            event("❌", f"План публикаций не пересобрался: {e}"[:200], None, "error")
    st = load()
    stats = {"sent": 0, "posted": 0, "reminded": 0}
    try:
        stats["posted"] = handle_updates(st, c, event)
    except Exception as e:
        event("❌", f"Telegram: не смог прочитать нажатия кнопок — {e}", None, "error")
    sync_jobs(st)
    now = datetime.now()
    if st.get("cleanup_v") != CLEANUP_V:
        try:
            cleanup_future(c, st, event)
        except Exception:
            pass
        st["cleanup_v"] = CLEANUP_V
    if schedule_mode():
        if not paused:
            _deliver_batch(st, c, event, stats, now)
        save(st)
        return stats
    if not paused:
        from . import policy
        for jid, job in sorted(st["jobs"].items(), key=lambda kv: kv[1].get("when") or ""):
            if job["status"] != "pending" or not job.get("when") or job["when"] > now.isoformat(timespec="minutes"):
                continue
            clip_posted = (library.load_posted().get(os.path.normpath(job["path"])) or {}).get(job["platform"])
            if clip_posted:
                job["status"] = "posted"
                continue
            block = _block_after_render(job)
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


def _channel_of(path: str) -> str:
    return next((cc.get("channel", "") for d in library.list_dates() for cc in library.list_clips(d)
                 if os.path.normpath(cc["path"]) == os.path.normpath(path)), "")


def _deliver_batch(st: dict, c: dict, event, stats: dict, now: datetime) -> None:
    """Дневная пачка: в 12:00 и 18:00 МСК (из стратегии) — все видео с будущими слотами, у каждого — на какое время
    запланировать. Слот, который уже прошёл, а видео так и не ушло, — переносим на следующий свободный."""
    from . import policy, schedule, strategy
    ap = strategy.get().get("autopilot") or {}
    last, nxt = schedule.deliveries(ap.get("telegram_delivery_msk") or [], now)
    if not last:
        return
    stamp = last.isoformat(timespec="minutes")
    now_s = now.isoformat(timespec="minutes")
    for job in st["jobs"].values():  # прошедшие слоты, которые так и не отправили, — на новое время
        if job["status"] == "pending" and job.get("when") and job["when"] <= now_s:
            job["when"] = _next_when(st, job["platform"])
            _sync_autopilot(job, "waiting", job["when"])
    horizon = (now + timedelta(hours=24)).isoformat(timespec="minutes")  # только на сутки вперёд, не на неделю
    todo = sorted(((jid, j) for jid, j in st["jobs"].items()
                   if j["status"] == "pending" and j.get("when") and j["when"] <= horizon),
                  key=lambda kv: kv[1]["when"])
    extra = st.get("last_delivery") == stamp
    rep = {pl: n for pl, n in (st.get("replace") or {}).items() if n > 0}
    if rep:  # «Не выкладывать» — замену шлём сразу, не дожидаясь пачки
        swap = []
        for pl, n in rep.items():
            cands = [(jid, j) for jid, j in todo if j["platform"] == pl and (jid, j) not in swap][:n]
            swap += cands
            st["replace"][pl] = n - len(cands)
        if swap:
            _send_list(st, c, event, stats, swap, "🔁 Замена вместо клипа, который не выкладываем:")
            todo = [(j_, x) for j_, x in todo if x["status"] == "pending"]
        if any(n > 0 for n in st["replace"].values()):
            stats["need_more"] = True  # в плане замены нет — окно попросит автопилот подобрать клип
    if extra and not 9 <= schedule.msk(now).hour < 23:
        return  # ночью не будим: всё, что не успели, уйдёт в утренней пачке (слоты пересоберутся сами)
    if extra:
        # пачка уже была — новые видео, слот которых раньше следующей пачки, шлём сразу отдельным сообщением
        limit = (nxt + timedelta(hours=1)).isoformat(timespec="minutes") if nxt else "9999"
        todo = [(jid, j) for jid, j in todo if j["when"] < limit]
        if not todo:
            return
        unconfirmed = []
    else:
        unconfirmed = [j for j in st["jobs"].values() if j["status"] == "sent" and (j.get("when") or "") > now_s]
    if not todo and not unconfirmed:
        st["last_delivery"] = stamp
        return
    # «Пробный Reels» — первые 2 Reels за день (по времени США)
    per_day: dict = {}
    for jid, j in sorted(st["jobs"].items(), key=lambda kv: kv[1].get("when") or ""):
        if j["platform"] == "instagram" and j.get("when") and j["status"] in ("pending", "sent", "posted"):
            d = schedule.et(datetime.fromisoformat(j["when"])).date().isoformat()
            per_day[d] = per_day.get(d, 0) + 1
            j["trial"] = per_day[d] <= 2
    try:
        telegram._call(c["token"], "sendMessage", data={
            "chat_id": c["chat_id"], **_target(c),
            "text": (f"➕ Новые видео вне пачки: {len(todo)} — их слоты раньше следующей пачки, запланируй сейчас."
                     if extra else
                     f"📦 Пачка на публикацию: {len(todo)} видео. У каждого написано, на какое время его запланировать "
                     "в приложении." + (f" Ещё не запланированы из прошлой пачки: {len(unconfirmed)}." if unconfirmed else ""))})
        for r in recipients(c)[1:]:
            telegram._call(c["token"], "sendMessage", data={
                "chat_id": r["id"], "text": (f"➕ Новые видео вне пачки: {len(todo)}" if extra
                                             else f"📦 Пачка на публикацию: {len(todo)} видео.")})
    except Exception:
        pass
    for jid, job in todo:
        clip_posted = (library.load_posted().get(os.path.normpath(job["path"])) or {}).get(job["platform"])
        if clip_posted:
            job["status"] = "posted"
            continue
        block = _block_after_render(job)
        if block:
            job["status"] = "blocked"
            event("⛔", f"{os.path.basename(job['path'])[:-4]}: {NAMES[job['platform']]} — не отправляю: {block}",
                  job["path"], "error")
            continue
        job["schedule"] = True
        channel = _channel_of(job["path"])
        try:
            _send(c, jid, job, channel)
            stats["sent"] += 1
        except Exception as e:
            job["errors"] = job.get("errors", 0) + 1
            if job["errors"] >= 3:
                job["status"] = "error"
            event("❌", f"Telegram: не отправилось ({NAMES[job['platform']]}) — {e}"[:220], None, "error")
    for job in unconfirmed:  # напоминание: слот ещё впереди, а «Запланировал» не нажали
        for m in job.get("msgs") or []:
            try:
                telegram._call(c["token"], "sendMessage", data={
                    "chat_id": m["chat"], "reply_to_message_id": m["msg"],
                    "text": "⏰ Это видео ещё не запланировано — успей до времени слота и нажми «✅ Запланировал».",
                    **(_target(c) if m["chat"] == c["chat_id"] else {})})
            except Exception:
                pass
        stats["reminded"] += 1
    st["last_delivery"] = stamp
    if not extra:
        send_plan(event, 24)
    if stats["sent"]:
        event("📦", (f"Telegram: новые видео вне пачки — {stats['sent']}, запланируй сейчас" if extra else
                     f"Telegram: пачка на публикацию — {stats['sent']} видео, у каждого время для «Запланировать»"),
              None, "info")


def plan_text(hours: float = 24) -> str:
    """План публикаций текстом для Telegram: время МСК / ET, площадка, стример, название."""
    from . import autopilot, schedule
    now = datetime.now()
    limit = (now + timedelta(hours=hours)).isoformat(timespec="minutes")
    chans = {os.path.normpath(c["path"]): (c.get("channel", ""), c.get("by", ""))
             for d in library.list_dates() for c in library.list_clips(d)}
    rows = [r for r in autopilot.plan_rows() if (r.get("when") or "") <= limit]
    if not rows:
        return "📋 План на ближайшие сутки пуст — новые клипы появятся, когда программа нарежет и отберёт их."
    lines, day = [f"📋 План публикаций на {int(hours)} ч ({len(rows)}):"], None
    for r in rows:
        t = datetime.fromisoformat(r["when"])
        d = schedule.day_label(t)
        if d != day:
            day = d
            lines.append(f"\n{d}:")
        ch, by = chans.get(os.path.normpath(r["path"]), ("", ""))
        mark = "📨" if r.get("sent") else "•"
        lines.append(f"{mark} {schedule.msk(t):%H:%M} МСК ({schedule.et(t):%H:%M} ET) — {NAMES.get(r['platform'], r['platform'])} — "
                     f"{ch}{' · ' + by if by else ''}: {(r.get('title') or os.path.basename(r['path'])[:-4])[:60]}")
    lines.append("\n📨 — видео уже в чате")
    return "\n".join(lines)[:4000]


def send_plan(event=None, hours: float = 24) -> None:
    c = telegram.load()
    if not (c.get("token") and c.get("chat_id")):
        return
    text = plan_text(hours)
    for r in recipients(c):
        try:
            telegram._call(c["token"], "sendMessage", data={"chat_id": r["id"], "text": text,
                                                            **(_target(c) if r.get("main") else {})})
        except Exception:
            pass


def send_ahead(event, hours: float = 24) -> dict:
    """Компьютер выключают: прислать в Telegram (тебе и другу) ВСЕ видео из плана на ближайшие hours часов —
    каждое со временем «Запланировать на …». Их ставят на отложенную публикацию в приложениях, и дальше
    компьютер не нужен."""
    c = telegram.load()
    if not (c.get("token") and c.get("chat_id")):
        raise RuntimeError("Telegram не подключён")
    from . import autopilot, policy
    try:
        autopilot.rebuild_schedule(event=event)
    except Exception:
        pass
    st = load()
    try:
        handle_updates(st, c, event)
    except Exception:
        pass
    sync_jobs(st)
    now = datetime.now()
    limit = (now + timedelta(hours=hours)).isoformat(timespec="minutes")
    now_s = now.isoformat(timespec="minutes")
    todo = sorted(((jid, j) for jid, j in st["jobs"].items()
                   if j["status"] == "pending" and j.get("when") and now_s < j["when"] <= limit),
                  key=lambda kv: kv[1]["when"])
    sent = 0
    try:
        telegram._call(c["token"], "sendMessage", data={
            "chat_id": c["chat_id"], **_target(c),
            "text": f"🖥 Компьютер выключается. Вот все видео на ближайшие {int(hours)} ч: {len(todo)}. "
                    "Запланируй каждое в приложении на указанное время — дальше всё выйдет само."})
        for r in recipients(c)[1:]:
            telegram._call(c["token"], "sendMessage", data={
                "chat_id": r["id"], "text": f"🖥 Компьютер выключается. Видео на ближайшие {int(hours)} ч: {len(todo)}."})
    except Exception:
        pass
    for jid, job in todo:
        if (library.load_posted().get(os.path.normpath(job["path"])) or {}).get(job["platform"]):
            job["status"] = "posted"
            continue
        if _block_after_render(job):
            job["status"] = "blocked"
            continue
        job["schedule"] = True
        try:
            _send(c, jid, job, _channel_of(job["path"]))
            sent += 1
        except Exception as e:
            event("❌", f"Telegram: не отправилось ({NAMES[job['platform']]}) — {e}"[:220], None, "error")
        save(st)
    save(st)
    send_plan(event, hours)  # и общий план — что и когда выходит
    event("📦", f"Telegram: отправил видео на {int(hours)} ч вперёд — {sent}. Запланируйте их в приложениях.", None, "info")
    return {"sent": sent, "total": len(todo)}


def _send_list(st: dict, c: dict, event, stats: dict, items: list, header: str) -> None:
    from . import policy
    try:
        for r in recipients(c):
            telegram._call(c["token"], "sendMessage", data={"chat_id": r["id"], "text": f"{header} {len(items)}",
                                                            **(_target(c) if r.get("main") else {})})
    except Exception:
        pass
    for jid, job in items:
        if _block_after_render(job):
            job["status"] = "blocked"
            continue
        job["schedule"] = schedule_mode()
        try:
            _send(c, jid, job, _channel_of(job["path"]))
            stats["sent"] += 1
            event("🔁", f"{_channel_of(job['path'])}: замена для {NAMES[job['platform']]} отправлена в Telegram",
                  job["path"], "info")
        except Exception as e:
            event("❌", f"Telegram: не отправилось ({NAMES[job['platform']]}) — {e}"[:220], None, "error")


CLEANUP_V = 1


def cleanup_future(c: dict, st: dict, event=None, hours: float = 24) -> int:
    """Раньше бот слал видео на много дней вперёд. Убираем из чата те, что не на ближайшие сутки (Telegram даёт
    боту удалять свои сообщения за последние 48 ч), — они придут файлами в свой день."""
    limit = (datetime.now() + timedelta(hours=hours)).isoformat(timespec="minutes")
    n = 0
    for job in st["jobs"].values():
        if job.get("status") != "sent" or (job.get("when") or "") <= limit:
            continue
        for m in job.get("msgs") or []:
            for mid in (m.get("video"), m.get("msg")):
                if mid:
                    try:
                        telegram._call(c["token"], "deleteMessage", data={"chat_id": m["chat"], "message_id": mid})
                    except Exception:
                        pass
        job.update({"status": "pending", "msgs": [], "msg_id": None})
        job.pop("file_sent", None)
        n += 1
    if n and event:
        event("🧹", f"Telegram: убрал из чата {n} видео на будущие дни — придут файлами в свой день", None, "info")
    return n


def overview() -> list[dict]:
    st = load()
    return sorted(({"id": k, **{x: v.get(x) for x in ("path", "platform", "when", "status", "title")}}
                   for k, v in st["jobs"].items()), key=lambda x: x.get("when") or "")
