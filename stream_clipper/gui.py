"""Окно программы: стримеры, галочки, кнопки «Следить», «Нарезать по ссылке», «Стоп»."""
from __future__ import annotations

import importlib.util
import json
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from . import paths

PROG = paths.program_dir()
SETTINGS = os.path.join(PROG, "settings.json")
STREAMERS = os.path.join(PROG, "streamers.txt")
KEYFILE = os.path.join(PROG, "claude_key.txt")
STREAMERS_HEADER = """# Стримеры, за которыми следит программа. По одному в строке.
# Twitch — логин из ссылки (twitch.tv/evelone2004 -> evelone2004)
# YouTube — @ник канала (youtube.com/@MrBeast -> @MrBeast)
"""
DEFAULTS = {"subs": True, "caption": True, "facecam": True, "audio": True,
            "top": "8", "length": "35", "quality": "1080"}


def _python_exe() -> str:
    """python.exe рядом с pythonw.exe (окно запускается через pythonw, без чёрной консоли)."""
    exe = sys.executable
    d, name = os.path.split(exe)
    if name.lower() == "pythonw.exe" and os.path.exists(os.path.join(d, "python.exe")):
        return os.path.join(d, "python.exe")
    return exe


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return {**default, **json.load(f)}
    except Exception:
        return dict(default)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.proc: subprocess.Popen | None = None
        self.lines: queue.Queue = queue.Queue()
        self.cfg = _load_json(SETTINGS, DEFAULTS)
        root.title("Stream Clipper — нарезки для Shorts")
        root.geometry("820x780")
        root.minsize(700, 640)
        try:
            root.iconbitmap(os.path.join(PROG, "icon.ico"))
        except Exception:
            pass
        self._build()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(150, self._drain)

    # ---------- интерфейс ----------
    def _build(self):
        pad = {"padx": 10, "pady": 4}
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill="both", expand=True)

        top = ttk.Frame(main)
        top.pack(fill="x")
        # стримеры
        box = ttk.LabelFrame(top, text=" Стримеры (по одному в строке; YouTube — через @) ", padding=6)
        box.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.streamers = tk.Text(box, height=7, width=28, font=("Segoe UI", 11))
        self.streamers.pack(fill="both", expand=True)
        self.streamers.insert("1.0", "\n".join(self._read_streamers()))

        # настройки
        opt = ttk.LabelFrame(top, text=" Что делать с клипом ", padding=6)
        opt.pack(side="left", fill="both", expand=True)
        self.v = {}
        for key, text in (("subs", "Субтитры (речь стримера)"),
                          ("caption", "Надпись-плашка («Спид первый попробовал GTA 6»)"),
                          ("facecam", "Вебка стримера сверху"),
                          ("audio", "Учитывать громкость (крики, взрывы)")):
            self.v[key] = tk.BooleanVar(value=bool(self.cfg.get(key)))
            ttk.Checkbutton(opt, text=text, variable=self.v[key]).pack(anchor="w", pady=2)
        grid = ttk.Frame(opt)
        grid.pack(anchor="w", pady=(6, 0))
        for r, (key, text, values) in enumerate((("top", "Клипов за стрим:", ["3", "5", "8", "10", "15"]),
                                                 ("length", "Длина клипа, сек:", ["25", "35", "45", "60"]),
                                                 ("quality", "Качество:", ["720", "1080"]))):
            ttk.Label(grid, text=text).grid(row=r, column=0, sticky="w", pady=2)
            self.v[key] = tk.StringVar(value=str(self.cfg.get(key)))
            ttk.Combobox(grid, textvariable=self.v[key], values=values, width=6,
                         state="readonly").grid(row=r, column=1, sticky="w", padx=6)

        # ключ Claude
        keyf = ttk.LabelFrame(main, text=" Ключ Claude API для умных надписей (необязательно) ", padding=6)
        keyf.pack(fill="x", pady=6)
        self.key = tk.StringVar(value=self._read_key())
        ttk.Entry(keyf, textvariable=self.key, show="•").pack(side="left", fill="x", expand=True)
        ttk.Button(keyf, text="Сохранить ключ", command=self.save_key).pack(side="left", padx=6)
        self.key_status = ttk.Label(keyf, text="")
        self.key_status.pack(side="left")
        self._update_key_status()

        # кнопки
        btns = ttk.Frame(main)
        btns.pack(fill="x", pady=6)
        style = ttk.Style()
        style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        self.b_watch = ttk.Button(btns, text="▶  Следить за стримерами", style="Big.TButton", command=self.start_watch)
        self.b_watch.pack(side="left")
        self.b_stop = ttk.Button(btns, text="■  Стоп", style="Big.TButton", command=self.stop, state="disabled")
        self.b_stop.pack(side="left", padx=8)
        ttk.Button(btns, text="📁  Папка с клипами", style="Big.TButton", command=self.open_folder).pack(side="right")

        # нарезка по ссылке
        vod = ttk.LabelFrame(main, text=" Нарезать один стрим по ссылке (запись Twitch или YouTube) ", padding=6)
        vod.pack(fill="x", pady=4)
        self.url = tk.StringVar()
        ttk.Entry(vod, textvariable=self.url).pack(side="left", fill="x", expand=True)
        self.b_vod = ttk.Button(vod, text="✂  Нарезать", command=self.start_vod)
        self.b_vod.pack(side="left", padx=6)

        # журнал
        logf = ttk.LabelFrame(main, text=" Что происходит ", padding=6)
        logf.pack(fill="both", expand=True, pady=(6, 0))
        self.log = ScrolledText(logf, height=14, font=("Consolas", 10), state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)
        self.status = ttk.Label(main, text="Готово. Не забудь включить VPN.", anchor="w")
        self.status.pack(fill="x", pady=(4, 0))

    # ---------- файлы ----------
    def _read_streamers(self) -> list[str]:
        try:
            with open(STREAMERS, encoding="utf-8-sig") as f:
                return [ln.split("#")[0].strip() for ln in f if ln.split("#")[0].strip()]
        except OSError:
            return []

    def _save_streamers(self) -> list[str]:
        names = [ln.strip() for ln in self.streamers.get("1.0", "end").splitlines() if ln.strip()]
        with open(STREAMERS, "w", encoding="utf-8") as f:
            f.write(STREAMERS_HEADER + "\n".join(names) + "\n")
        return names

    def _read_key(self) -> str:
        try:
            return open(KEYFILE, encoding="utf-8-sig").read().strip()
        except OSError:
            return ""

    def save_key(self):
        k = self.key.get().strip()
        if k:
            with open(KEYFILE, "w", encoding="utf-8") as f:
                f.write(k)
        elif os.path.exists(KEYFILE):
            os.remove(KEYFILE)
        self._update_key_status()

    def _update_key_status(self):
        ok = bool(self.key.get().strip())
        self.key_status.config(text="✔ ключ есть" if ok else "нет ключа — надписи по шаблону")

    def _save_settings(self):
        self.cfg = {k: (v.get()) for k, v in self.v.items()}
        with open(SETTINGS, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=1)

    # ---------- запуск ----------
    def _flags(self) -> list[str]:
        self._save_settings()
        c = self.cfg
        length = int(c["length"])
        pre = round(length * 0.57)
        f = ["-n", c["top"], "--pre", str(pre), "--post", str(length - pre),
             "--max-height", c["quality"], "--zoom", "1.3",
             "--layout", "auto" if c["facecam"] else "blur"]
        if c["subs"]:
            if importlib.util.find_spec("faster_whisper") is None:
                self._append("⚠ Субтитры не установлены — запусти install_subs.bat. Пока режу без них.\n")
                f.append("--no-subs")
            else:
                f.append("--subs")
        else:
            f.append("--no-subs")
        if not c["caption"]:
            f.append("--no-caption")
        if not c["audio"]:
            f.append("--no-audio")
        return f

    def _run(self, args: list[str], what: str):
        if self.proc:
            return
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
        cmd = [_python_exe(), "-m", "stream_clipper", *args]
        self._append(f"\n=== {what} ===\n")
        try:
            self.proc = subprocess.Popen(cmd, cwd=PROG, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, creationflags=flags)
        except Exception as e:
            self._append(f"Не удалось запустить: {e}\n")
            self.proc = None
            return
        self._set_running(True, what)
        threading.Thread(target=self._reader, args=(self.proc,), daemon=True).start()

    def start_watch(self):
        names = self._save_streamers()
        if not names:
            messagebox.showwarning("Нет стримеров", "Впиши хотя бы одного стримера слева.")
            return
        self._run(["watch", *self._flags()], "Слежу за: " + ", ".join(names))

    def start_vod(self):
        url = self.url.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning("Нет ссылки", "Вставь ссылку на запись стрима (twitch.tv/videos/... или youtube.com/watch?v=...).")
            return
        self._run(["vod", url, *self._flags()], "Нарезаю " + url)

    def stop(self):
        p = self.proc
        if not p:
            return
        self._append("\nОстанавливаю...\n")
        try:
            if os.name == "nt":  # вместе с дочерними ffmpeg
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True,
                               creationflags=0x08000000)
            else:
                p.terminate()
        except Exception:
            p.kill()

    def _reader(self, p: subprocess.Popen):
        assert p.stdout is not None
        for raw in iter(p.stdout.readline, b""):
            self.lines.put(raw.decode("utf-8", errors="replace"))
        p.wait()
        self.lines.put(None)

    def _drain(self):
        try:
            while True:
                item = self.lines.get_nowait()
                if item is None:
                    self._append("=== Остановлено ===\n")
                    self.proc = None
                    self._set_running(False)
                else:
                    self._append(item)
        except queue.Empty:
            pass
        self.root.after(150, self._drain)

    def _append(self, text: str):
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")
        if text.strip():
            self.status.config(text=text.strip().splitlines()[-1][:120])

    def _set_running(self, running: bool, what: str = ""):
        self.b_watch.config(state="disabled" if running else "normal")
        self.b_vod.config(state="disabled" if running else "normal")
        self.b_stop.config(state="normal" if running else "disabled")
        if running:
            self.status.config(text=what)

    def open_folder(self):
        d = paths.default_out_dir()
        os.makedirs(d, exist_ok=True)
        if os.name == "nt":
            os.startfile(d)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", d])

    def on_close(self):
        if self.proc and not messagebox.askyesno("Выход", "Программа сейчас работает. Остановить и закрыть?"):
            return
        self.stop()
        self._save_settings()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
