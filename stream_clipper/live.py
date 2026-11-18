"""Запись живого эфира (YouTube, или Twitch без сохранения VOD) и нарезка прямо по ходу.

Как это работает:
  * ffmpeg пишет эфир кусками по 5 минут (chunk_ГГГГММДД-ЧЧММСС.ts — в имени время начала куска);
  * параллельно собирается живой чат с точным временем каждого сообщения;
  * каждые N минут ищем всплески чата/громкости и вырезаем моменты из записанных кусков;
  * старые куски, которые уже не понадобятся, удаляются — диск не забивается.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import threading
import time
from datetime import datetime

import numpy as np

from . import daily, render, twitch
from .audio import loudness_per_second
from .chat import ChatMessage

CHUNK_FMT = "chunk_%Y%m%d-%H%M%S.ts"


class LiveSession:
    def __init__(self, url: str, cfg, log=print, segment_time: int = 300, max_height: int = 720):
        self.url = url
        self.cfg = cfg
        self.log = log
        self.segment_time = segment_time
        self.max_height = max_height
        self.input_opts: list[str] = []      # для тестов (-re и т.п.)
        self.stop_evt = threading.Event()
        self.lock = threading.Lock()
        self.msgs: list[ChatMessage] = []
        self.done: list[dict] = []
        self.cutoff = 0.0                    # секунды записи, раньше которых больше не ищем
        self.proc: subprocess.Popen | None = None
        self.threads: list[threading.Thread] = []

    # ---------- запуск/остановка ----------
    def start(self) -> None:
        info = twitch.get_info(self.url)
        self.info = info
        self.vid = str(info.get("id") or "live").lstrip("v")
        self.title = info.get("title") or self.vid
        self.channel = (info.get("uploader_id") or info.get("channel") or info.get("uploader") or "live").lstrip("@")
        self.chat_url = info.get("webpage_url") or self.url
        self.is_youtube = "youtube" in (info.get("extractor") or "").lower()
        self.stream_start = info.get("release_timestamp") or info.get("timestamp")
        self.rec_start = time.time()
        self.work = os.path.join(self.cfg.work_dir,
                                 f"live_{self.vid}_{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        self.chunks_dir = os.path.join(self.work, "chunks")
        os.makedirs(self.chunks_dir, exist_ok=True)
        self.log(f"[{self.channel}] начинаю запись эфира «{self.title}»")
        for target in (self._record_loop, self._chat_loop):
            th = threading.Thread(target=target, daemon=True)
            th.start()
            self.threads.append(th)

    def stop(self) -> None:
        self.stop_evt.set()
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self._save_chat()

    # ---------- запись видео ----------
    def _resolve(self) -> tuple[str, dict]:
        h = self.max_height
        info = twitch.get_info(self.url, {"format": f"best[height<={h}]/best"})
        return info["url"], info.get("http_headers") or {}

    def _record_loop(self) -> None:
        while not self.stop_evt.is_set():
            try:
                src, headers = self._resolve()
            except Exception as e:
                self.log(f"[{self.channel}] не получил поток: {e}")
                self.stop_evt.wait(30)
                continue
            cmd = ["ffmpeg", "-v", "error", *self.input_opts]
            if headers:
                cmd += ["-headers", "".join(f"{k}: {v}\r\n" for k, v in headers.items())]
            cmd += ["-i", src, "-map", "0:v:0", "-map", "0:a:0?", "-c", "copy",
                    "-f", "segment", "-segment_time", str(self.segment_time), "-reset_timestamps", "1",
                    "-strftime", "1", os.path.join(self.chunks_dir, CHUNK_FMT)]
            self.proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL)
            while self.proc.poll() is None and not self.stop_evt.is_set():
                self.stop_evt.wait(2)
            if not self.stop_evt.is_set():
                self.log(f"[{self.channel}] запись прервалась, переподключаюсь...")
                self.stop_evt.wait(5)

    def _chunks(self) -> list[tuple[str, float, float]]:
        """[(файл, начало, конец)] в секундах от начала записи."""
        files = sorted(glob.glob(os.path.join(self.chunks_dir, "chunk_*.ts")))
        out = []
        for f in files:
            try:
                st = datetime.strptime(os.path.basename(f), CHUNK_FMT).timestamp() - self.rec_start
            except ValueError:
                continue
            out.append([f, st, st + self.segment_time])
        for i in range(len(out) - 1):
            out[i][2] = min(out[i][2], out[i + 1][1])
        if out:
            out[-1][2] = time.time() - self.rec_start  # пишется прямо сейчас
        return [tuple(c) for c in out]

    # ---------- чат ----------
    def _chat_loop(self) -> None:
        from chat_downloader import ChatDownloader
        seen: set = set()
        while not self.stop_evt.is_set():
            try:
                for item in ChatDownloader().get_chat(self.chat_url):
                    if self.stop_evt.is_set():
                        return
                    ts = item.get("timestamp")
                    if ts is None:
                        continue
                    author = (item.get("author") or {}).get("name", "") or ""
                    text = item.get("message", "") or ""
                    key = (ts, author, text)
                    if key in seen:
                        continue
                    seen.add(key)
                    with self.lock:
                        self.msgs.append(ChatMessage(t=ts / 1e6 - self.rec_start, author=author, text=text))
            except Exception as e:
                if not self.stop_evt.is_set():
                    self.log(f"[{self.channel}] чат отвалился ({e}), переподключаюсь...")
            self.stop_evt.wait(10)

    def _save_chat(self) -> None:
        with self.lock:
            data = [m.__dict__ for m in self.msgs]
        if hasattr(self, "work"):
            with open(os.path.join(self.work, "chat.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    # ---------- анализ и нарезка ----------
    def _audio(self, chunks, duration: int, final: bool):
        if not self.cfg.audio or not chunks:
            return None
        arr = None
        usable = chunks if final else chunks[:-1]  # последний кусок ещё пишется
        parts = []
        for f, st, _ in usable:
            npy = f + ".npy"
            if os.path.exists(npy):
                a = np.load(npy)
            else:
                try:
                    a = loudness_per_second(f)
                except Exception:
                    continue
                np.save(npy, a)
            parts.append((int(max(0, st)), a))
        if not parts:
            return None
        base = float(np.median(np.concatenate([a for _, a in parts])))
        arr = np.full(duration + 1, base, dtype=np.float32)
        for st, a in parts:
            n = max(0, min(a.size, arr.size - st))
            arr[st:st + n] = a[:n]
        return arr

    def _cut(self, chunks, start: float, end: float, out: str) -> str:
        need = [c for c in chunks if c[1] < end and c[2] > start]
        if not need:
            raise RuntimeError("нет записи для этого момента")
        lst = out + ".txt"
        with open(lst, "w", encoding="utf-8") as f:
            for c in need:
                f.write("file '" + os.path.abspath(c[0]).replace("\\", "/").replace("'", r"'\''") + "'\n")
        offset = max(0.0, start - need[0][1])
        render._run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                     "-ss", f"{offset:.2f}", "-t", f"{end - start:.2f}",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", out])
        os.remove(lst)
        return out

    def _link(self, sec: float) -> str | None:
        if self.is_youtube and self.stream_start:
            t = int(self.rec_start + sec - self.stream_start)
            return f"https://youtu.be/{self.vid}?t={max(0, t)}"
        return None

    def process(self, final: bool = False) -> list[dict]:
        from .pipeline import _analyze, _fmt, _make_short, _finish, refresh_live
        refresh_live(self.cfg, self.log)

        cfg, log = self.cfg, self.log
        self._save_chat()
        now_t = time.time() - self.rec_start
        chunks = self._chunks()
        if not chunks:
            log(f"[{self.channel}] запись ещё пустая — пропускаю проход")
            return []
        with self.lock:
            msgs = sorted(self.msgs, key=lambda m: m.t)
        duration = int(now_t)
        audio_db = self._audio(chunks, duration, final)

        skip = list(self.done)
        skip.append({"start": 0.0, "end": max(self.cutoff, chunks[0][1] + cfg.clip_pre)})
        tail = 0.0 if final else cfg.clip_post + cfg.chat_lag + 60
        if tail:
            skip.append({"start": max(0.0, now_t - tail), "end": now_t + tail})
        log(f"[{self.channel}] {'финальный' if final else 'промежуточный'} проход по записи эфира")
        from .pipeline import clip_budget
        allowed = clip_budget(cfg.top, duration) - len(self.done)
        if allowed <= 0:
            log(f"[{self.channel}] лимит клипов на это время эфира набран — жду дальше")
            self._save_chat()
            return []
        hl = _analyze(msgs, duration, audio_db, cfg, skip, log, top=allowed)
        from .caption import detect_language
        lang = cfg.language or detect_language([m.text for m in msgs], self.title)

        new = []
        for i, h in enumerate(hl, 1):
            d = dict(h.to_dict(), vod_url=self.chat_url, vod_title=self.title)
            if self._link(h.start):
                d["link"] = self._link(h.start)
            if self.stream_start:  # время от начала эфира, а не от запуска программы
                d["moment"] = max(0.0, self.rec_start + h.start - self.stream_start)
            if cfg.dry_run:
                new.append(d)
                continue
            stamp = datetime.fromtimestamp(self.rec_start + h.start).strftime("%H-%M-%S")
            name = f"{self.channel}_{stamp}"
            try:
                seg = self._cut(chunks, h.start, h.end, os.path.join(self.work, name + "_raw.mp4"))
                tmp = os.path.join(self.work, name + ".mp4")
                d["caption"] = _make_short(seg, tmp, cfg, log, {"streamer": self.channel, "title": self.title,
                                                                "top_messages": h.top_messages, "lang": lang})
                os.remove(seg)
                d["file"] = daily.deliver_clip(cfg.out_dir, tmp, d, self.channel)
                log(f"  [{i}/{len(hl)}] готово -> {d['file']}")
                new.append(d)
            except Exception as e:
                log(f"  ошибка: {e}")
                daily.log_event(cfg.out_dir, f"{self.channel}: не удалось сделать клип {_fmt(h.start)} — {e}")
        self.done += new

        # дальше ищем только в последних ~10 минутах до хвоста; старые куски удаляем
        if not final:
            self.cutoff = max(self.cutoff, now_t - tail - 600)
            for f, st, en in chunks[:-1]:
                if en < self.cutoff - cfg.clip_pre - 30:
                    for p in (f, f + ".npy"):
                        if os.path.exists(p):
                            os.remove(p)
        _finish(cfg, new, self.work, self.done, self.title, None, log)
        return new

    def cleanup(self) -> None:
        if not self.cfg.keep_raw:
            for f in glob.glob(os.path.join(self.chunks_dir, "*")):
                try:
                    os.remove(f)
                except OSError:
                    pass
