"""Окно программы: стримеры, галочки, кнопки «Следить», «Нарезать по ссылке», «Стоп»."""
from __future__ import annotations

import importlib.util
import json
import os
import queue
import subprocess
import sys
import threading
import webbrowser
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from . import library, paths, updater
from . import i18n
from .i18n import T, tr_line, untranslate

PROG = paths.program_dir()
SETTINGS = os.path.join(PROG, "settings.json")
STREAMERS = os.path.join(PROG, "streamers.txt")
STREAMERS_BACKUP = os.path.join(paths.default_work_dir(), "streamers.txt")  # запасная копия
RESUME = os.path.join(paths.default_work_dir(), "resume.json")  # что продолжить после обновления
KEYFILE = os.path.join(PROG, "claude_key.txt")
STREAMERS_HEADER = T("""# Стримеры, за которыми следит программа. По одному в строке.
# Twitch — логин из ссылки (twitch.tv/evelone2004 -> evelone2004)
# YouTube — @ник канала (youtube.com/@MrBeast -> @MrBeast)
""")
DEFAULTS = {"subs": True, "caption": True, "facecam": True, "audio": True,
            "top": "3", "length": "35", "quality": "1080", "autoupdate": True,
            "wm_on": False, "wm_text": "", "wm_image": "", "wm_pos": T("плавает по экрану"), "wm_op": T("средне"), "game_view": T("целиком"), "yt_browser": T("не брать"),
            "credit_on": True, "credit_pos": T("внизу слева"), "lang": i18n.LANG,
            "start_from": T("с начала"), "start_mode": T("от начала стрима"), "theme": T("Фиолетовая (как Twitch)")}
CREDIT_POS = {T("внизу слева"): "bottom-left", T("вверху слева"): "top-left", T("вверху справа"): "top-right"}
SHOW_ALL = T("все клипы")
SHOW_FILTERS = {SHOW_ALL: "", T("ещё не на YouTube"): "youtube", T("ещё не в Instagram"): "instagram",
                T("ещё не в TikTok"): "tiktok", T("нигде не выложенные"): "nowhere", T("с нарушениями"): "violations"}
SHOW_FOR = {"youtube": T("ещё не на YouTube"), "instagram": T("ещё не в Instagram"), "tiktok": T("ещё не в TikTok")}
WM_POS = {T("плавает по экрану"): "moving", T("по центру"): "center", T("в углу"): "corner"}

# цветовые темы окна: bg — фон, panel — блоки, field — поля ввода, accent — главные кнопки и акценты
THEMES = {
    T("Фиолетовая (как Twitch)"): dict(bg="#18181b", panel="#232328", field="#2d2d34", fg="#efeff1", muted="#a1a1aa",
                                    accent="#9147ff", accent_fg="#ffffff", border="#3a3a44", select="#5b2bb5"),
    T("Красная (как YouTube)"): dict(bg="#0f0f0f", panel="#1c1c1c", field="#272727", fg="#f1f1f1", muted="#aaaaaa",
                                  accent="#e62117", accent_fg="#ffffff", border="#333333", select="#8a1610"),
    T("Синяя ночь"): dict(bg="#0f172a", panel="#16213a", field="#1e2a47", fg="#e2e8f0", muted="#94a3b8",
                       accent="#06b6d4", accent_fg="#04212a", border="#2a3a5c", select="#0e7490"),
    T("Светлая мятная"): dict(bg="#f3f7f6", panel="#ffffff", field="#ffffff", fg="#1f2a2e", muted="#6b7c80",
                           accent="#10a37f", accent_fg="#ffffff", border="#d5e2df", select="#bfe9dc"),
    T("Классическая (серая)"): None,
}
GAME_VIEW = {T("целиком"): "full", T("крупнее"): "wide", T("только центр"): "center"}
YT_BROWSERS = {T("не брать"): "", "Firefox": "firefox", "Chrome": "chrome", "Edge": "edge", "Opera": "opera",
               "Brave": "brave", "Vivaldi": "vivaldi"}
WM_OP = {T("слабо"): 0.25, T("средне"): 0.4, T("сильно"): 0.6}


def norm_twitch(s: str) -> str:
    """kaicenat / Kai Cenat / https://www.twitch.tv/kaicenat -> kaicenat"""
    s = s.strip()
    if "twitch.tv/" in s:
        s = s.split("twitch.tv/", 1)[1].split("/")[0].split("?")[0]
    return s.replace(" ", "").lstrip("@").lower()


def norm_youtube(s: str) -> str:
    """MrBeast / @MrBeast / Mr Beast -> @MrBeast; ссылки на канал оставляем как есть."""
    s = s.strip()
    if "youtube.com/" in s or "youtu.be/" in s:
        if "/@" in s:
            return "@" + s.split("/@", 1)[1].split("/")[0].split("?")[0]
        return s
    return "@" + s.replace(" ", "").lstrip("@")


def split_platforms(names: list[str]) -> tuple[list[str], list[str]]:
    tw, yt = [], []
    for n in names:
        if n.startswith(("@", "yt:")) or "youtube.com/" in n or "youtu.be/" in n:
            yt.append(n[3:] if n.startswith("yt:") else n)
        else:
            tw.append(n)
    return tw, [n.lstrip("@") if not n.startswith("http") else n for n in yt]


def _unique(items: list[str]) -> list[str]:
    seen, out = set(), []
    for x in items:
        if x and x.lower() not in seen:
            seen.add(x.lower())
            out.append(x)
    return out


def _python_exe() -> str:
    """python.exe рядом с pythonw.exe (окно запускается через pythonw, без чёрной консоли)."""
    exe = sys.executable
    d, name = os.path.split(exe)
    if name.lower() == "pythonw.exe" and os.path.exists(os.path.join(d, "python.exe")):
        return os.path.join(d, "python.exe")
    return exe


def _short_url(url: str) -> str:
    """https://www.twitch.tv/videos/123 → 🔗 twitch.tv/videos/123 (для колонки «Ссылка»)."""
    if not url:
        return "—"
    return "🔗 " + url.split("://", 1)[-1].removeprefix("www.")


def _ru(d: dict) -> dict:
    """Настройки храним по-русски (как в коде), чтобы смена языка окна их не ломала."""
    return {k: untranslate(v) if isinstance(v, str) else v for k, v in d.items()}


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return {**default, **json.load(f)}
    except Exception:
        return dict(default)


class VideoPreview(ttk.Frame):
    """Просмотр клипа прямо в окне: картинка через OpenCV, звук (Windows) — через встроенный winsound."""
    def __init__(self, parent, app, big: bool = False):
        super().__init__(parent)
        self.app = app
        self.W, self.H = (288, 512)
        self.big = big
        self.cap = None
        self.path = None
        self.playing = False
        self.sound = tk.BooleanVar(value=True)
        self.fps = 30.0
        self.frames_total = 0
        self.pos = 0
        self.job = None
        self.wav = os.path.join(paths.default_work_dir(), f"preview_{id(self) % 100000}.wav")
        self.screen = tk.Label(self, bg="#000000", fg="#888888",
                               text=T("Нажми на клип\nв списке слева —\nон покажется здесь"), justify="center")
        self.screen.pack(fill="both", expand=True)
        self.screen.bind("<Configure>", self._on_resize)
        self.screen.bind("<Button-1>", lambda e: self.toggle())
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(4, 0))
        self.b_play = ttk.Button(bar, text="▶", width=3, command=self.toggle)
        self.b_play.pack(side="left")
        ttk.Checkbutton(bar, text=T("звук"), variable=self.sound, command=self._sound_changed).pack(side="left", padx=4)
        self.time_lbl = ttk.Label(bar, text="0:00", foreground=app.muted)
        self.time_lbl.pack(side="right")
        if not big:
            ttk.Button(bar, text=T("⛶ Крупно"), command=self.open_big).pack(side="left", padx=4)
        self.img = None
        self._last_frame = None

    def _on_resize(self, e):
        # видео вертикальное 9:16 — вписываем в доступное место
        w, h = max(90, e.width - 4), max(160, e.height - 4)
        if w * 16 / 9 > h:
            w = int(h * 9 / 16)
        else:
            h = int(w * 16 / 9)
        if abs(w - self.W) > 4 or abs(h - self.H) > 4:
            self.W, self.H = w, h
            if self._last_frame is not None and not self.playing:
                self._draw(self._last_frame)

    def open_big(self):
        """Клип в большом окне — почти на всю высоту экрана."""
        if not self.path:
            messagebox.showinfo(T("Просмотр"), T("Сначала нажми на клип в списке."))
            return
        self.stop()
        win = tk.Toplevel(self.app.root)
        win.title(T("Просмотр клипа"))
        sh = self.app.root.winfo_screenheight()
        h = max(480, sh - 140)
        win.geometry(f"{int(h * 9 / 16) + 20}x{h + 50}")
        big = VideoPreview(win, self.app, big=True)
        big.pack(fill="both", expand=True, padx=6, pady=6)
        win.protocol("WM_DELETE_WINDOW", lambda: (big.release(), win.destroy()))
        win.after(200, lambda: (big.load(self.path), big.toggle()))
        self.app.big_window = win  # для проверок

    # --- выбор клипа ---
    def show_selected(self):
        sel = [self.app.clip_by_iid[i] for i in self.app.tree.selection() if i in self.app.clip_by_iid]
        if len(sel) == 1 and sel[0]["path"] != self.path:
            self.load(sel[0]["path"])

    def play_selected(self):
        self.show_selected()
        if self.path and not self.playing:
            self.toggle()

    def load(self, path: str):
        self.stop()
        try:
            import cv2
        except ImportError:
            self.screen.config(image="", text=T("Просмотр недоступен:\nнет OpenCV"))
            return
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            self.screen.config(image="", text=T("Не удалось\nоткрыть клип"))
            self.cap = None
            return
        self.path = path
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.frames_total = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        self.pos = 0
        self._show_frame(read=True)

    def release(self):
        """Закрыть файл (Windows не даёт удалить открытый в плеере клип)."""
        self.stop()
        if self.cap is not None:
            self.cap.release()
        self.cap = None
        self.path = None
        self.img = None
        self._last_frame = None
        self.screen.config(image="", text=T("Нажми на клип\nв списке слева —\nон покажется здесь"))

    # --- воспроизведение ---
    def toggle(self):
        if not self.cap:
            return
        if self.playing:
            self.stop()
        else:
            if self.frames_total and self.pos >= self.frames_total - 1:
                self.pos = 0
                import cv2
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.playing = True
            self.b_play.config(text="⏸")
            self.t0 = time.time() - self.pos / self.fps
            self._start_sound()
            self._tick()

    def stop(self):
        self.playing = False
        self.b_play.config(text="▶")
        if self.job:
            self.after_cancel(self.job)
            self.job = None
        self._stop_sound()

    def _tick(self):
        if not self.playing or not self.cap:
            return
        import cv2
        want = int((time.time() - self.t0) * self.fps)
        while self.pos < want - 1:  # отстаём — пропускаем кадры, чтобы не расходиться со звуком
            if not self.cap.grab():
                break
            self.pos += 1
        if not self._show_frame(read=True):
            self.stop()
            return
        delay = max(1, int(1000 * ((self.pos + 1) / self.fps - (time.time() - self.t0))))
        self.job = self.after(delay, self._tick)

    def _show_frame(self, read: bool = True) -> bool:
        import cv2
        ok, frame = self.cap.read()
        if not ok:
            return False
        self.pos += 1
        self._last_frame = frame
        self._draw(frame)
        sec = int(self.pos / self.fps)
        total = int(self.frames_total / self.fps) if self.frames_total else 0
        self.time_lbl.config(text=f"{sec // 60}:{sec % 60:02d} / {total // 60}:{total % 60:02d}")
        return True

    def _draw(self, frame):
        import cv2
        h, w = frame.shape[:2]
        scale = min(self.W / w, self.H / h)
        small = cv2.resize(frame, (max(2, int(w * scale)), max(2, int(h * scale))),
                           interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
        ok, buf = cv2.imencode(".ppm", small)
        if ok:
            self.img = tk.PhotoImage(data=buf.tobytes(), format="PPM")
            self.screen.config(image=self.img, text="")

    # --- звук (Windows) ---
    def _sound_changed(self):
        if self.playing:
            self._stop_sound()
            self._start_sound()

    def _start_sound(self):
        if not self.sound.get() or os.name != "nt" or not self.path:
            return
        try:
            import winsound
            flags = 0x08000000
            start = self.pos / self.fps
            r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-i", self.path, "-vn",
                                "-ac", "2", "-ar", "44100", self.wav], capture_output=True, creationflags=flags)
            if r.returncode == 0:
                winsound.PlaySound(self.wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

    def _stop_sound(self):
        if os.name == "nt":
            try:
                import winsound
                winsound.PlaySound(None, 0)
            except Exception:
                pass


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.proc: subprocess.Popen | None = None
        self.lines: queue.Queue = queue.Queue()
        self.cfg = {k: T(v) if isinstance(v, str) else v for k, v in _load_json(SETTINGS, DEFAULTS).items()}
        root.title(T("Stream Clipper — нарезки для Shorts"))
        self.v: dict = {}
        self.pal = self._apply_theme(self.cfg.get("theme"))
        self.muted = self.pal["muted"] if self.pal else "#666"
        root.geometry("1120x880")
        root.minsize(900, 700)
        try:
            root.iconbitmap(os.path.join(PROG, "icon.ico"))
        except Exception:
            pass
        self._build()
        self._install_shortcuts()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(150, self._drain)

    # ---------- оформление ----------
    def _apply_theme(self, name):
        pal = THEMES.get(name) if name in THEMES else THEMES[T("Фиолетовая (как Twitch)")]
        style = ttk.Style()
        if not pal:
            return None
        style.theme_use("clam")
        bg, panel, field, fg, muted, acc, acc_fg, border, sel = (pal[k] for k in (
            "bg", "panel", "field", "fg", "muted", "accent", "accent_fg", "border", "select"))
        self.root.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg, fieldbackground=field, bordercolor=border,
                        lightcolor=panel, darkcolor=panel, troughcolor=panel, focuscolor=acc,
                        selectbackground=sel, selectforeground=fg, insertcolor=fg, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelframe", background=bg, bordercolor=border)
        style.configure("TLabelframe.Label", background=bg, foreground=acc, font=("Segoe UI", 10, "bold"))
        style.configure("TButton", background=panel, foreground=fg, bordercolor=border, padding=6)
        style.map("TButton", background=[("active", border), ("disabled", bg)], foreground=[("disabled", muted)])
        style.configure("Big.TButton", background=acc, foreground=acc_fg, bordercolor=acc)
        style.map("Big.TButton", background=[("active", sel), ("disabled", panel)],
                  foreground=[("disabled", muted)])
        style.configure("TMenubutton", background=panel, foreground=fg, bordercolor=border, padding=6)
        style.configure("Big.TMenubutton", background=acc, foreground=acc_fg, bordercolor=acc,
                        font=("Segoe UI", 11, "bold"), padding=8, arrowcolor=acc_fg)
        style.map("Big.TMenubutton", background=[("active", sel)])
        style.configure("TCheckbutton", background=bg, foreground=fg, indicatorbackground=field,
                        indicatorforeground=acc)
        style.map("TCheckbutton", background=[("active", bg)], indicatorbackground=[("selected", acc)])
        style.configure("TEntry", fieldbackground=field, foreground=fg, bordercolor=border)
        style.configure("TCombobox", fieldbackground=field, foreground=fg, background=panel, arrowcolor=fg,
                        bordercolor=border)
        style.map("TCombobox", fieldbackground=[("readonly", field)], foreground=[("readonly", fg)])
        style.configure("TNotebook", background=bg, bordercolor=border, tabmargins=(4, 4, 4, 0))
        style.configure("TNotebook.Tab", background=panel, foreground=muted, padding=(14, 6), bordercolor=border)
        style.map("TNotebook.Tab", background=[("selected", acc)], foreground=[("selected", acc_fg)])
        style.configure("Treeview", background=field, fieldbackground=field, foreground=fg, bordercolor=border)
        style.map("Treeview", background=[("selected", sel)], foreground=[("selected", fg)])
        style.configure("Treeview.Heading", background=panel, foreground=fg, bordercolor=border)
        style.configure("Vertical.TScrollbar", background=panel, arrowcolor=fg, bordercolor=border)
        # обычные (не ttk) поля и списки
        for opt, val in (("*Text.background", field), ("*Text.foreground", fg), ("*Text.insertBackground", fg),
                         ("*Text.selectBackground", sel), ("*Listbox.background", field),
                         ("*Listbox.foreground", fg), ("*Listbox.selectBackground", sel),
                         ("*Menu.background", panel), ("*Menu.foreground", fg), ("*Menu.activeBackground", acc),
                         ("*Menu.activeForeground", acc_fg), ("*TCombobox*Listbox.background", field),
                         ("*TCombobox*Listbox.foreground", fg), ("*Canvas.background", bg),
                         ("*Toplevel.background", bg)):
            self.root.option_add(opt, val)
        return pal

    def _change_theme(self, *_):
        name = self.v["theme"].get()
        if name == self.cfg.get("theme"):
            return
        self._save_settings()
        if messagebox.askyesno(T("Оформление"), T("Чтобы применить тему, окно перезапустится. Перезапустить сейчас?")
                               + (T("\n(Работа остановится аккуратно и продолжится сама.)") if self.proc else "")):
            self._restart_window()

    def _restart_window(self):
        if self.proc:
            with open(RESUME, "w", encoding="utf-8") as f:
                json.dump(self.job or ["watch"], f)
            self.updating = True
            open(paths.stop_request_path(), "w").close()
        else:
            self._restart()

    def _change_lang(self, *_):
        """Язык окна (подписи на двух языках, чтобы друг нашёл переключатель, даже если не читает по-русски)."""
        code = next((k for k, v in i18n.LANGS.items() if v == self.lang_name.get()), "ru")
        if code == self.v["lang"].get():
            return
        self.v["lang"].set(code)
        self._save_settings()
        if messagebox.askyesno("Язык / Dil", "Чтобы сменить язык, окно перезапустится. Перезапустить сейчас?\n\n"
                                             "Dili dəyişmək üçün pəncərə yenidən açılacaq. İndi yenidən açılsın?"):
            self._restart_window()

    # ---------- интерфейс ----------
    def _build(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)
        main = ttk.Frame(self.nb, padding=8)
        clips = ttk.Frame(self.nb, padding=8)
        sett = ttk.Frame(self.nb, padding=8)
        themef = ttk.LabelFrame(sett, text=T(" 🎨 Оформление "), padding=6)
        themef.pack(fill="x", pady=(0, 6))
        ttk.Label(themef, text=T("Тема окна:")).pack(side="left")
        th = self.cfg.get("theme")
        self.v["theme"] = tk.StringVar(value=th if th in THEMES else T("Фиолетовая (как Twitch)"))
        cb_theme = ttk.Combobox(themef, textvariable=self.v["theme"], values=list(THEMES), width=26, state="readonly")
        cb_theme.pack(side="left", padx=6)
        cb_theme.bind("<<ComboboxSelected>>", self._change_theme)
        ttk.Label(themef, text="     🌐 Язык / Dil:").pack(side="left")
        self.v["lang"] = tk.StringVar(value=self.cfg.get("lang") if self.cfg.get("lang") in i18n.LANGS else "ru")
        self.lang_name = tk.StringVar(value=i18n.LANGS[self.v["lang"].get()])
        cb_lang = ttk.Combobox(themef, textvariable=self.lang_name, values=list(i18n.LANGS.values()), width=14,
                               state="readonly")
        cb_lang.pack(side="left", padx=6)
        cb_lang.bind("<<ComboboxSelected>>", self._change_lang)
        self.nb.add(main, text=T("  Управление  "))
        streams = ttk.Frame(self.nb, padding=8)
        self.nb.add(clips, text=T("  Клипы  "))
        self.nb.add(streams, text=T("  Стримы  "))
        self.nb.add(sett, text=T("  Настройки  "))
        self.sett = sett
        self._build_clips(clips)
        self._build_streams(streams)
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab)

        top = ttk.Frame(main)
        top.pack(fill="x")
        # стримеры
        box = ttk.LabelFrame(top, text=T(" За кем следим (Twitch и YouTube — одновременно) "), padding=6)
        box.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.platforms = ttk.Notebook(box)
        self.platforms.pack(fill="both", expand=True)
        tw_names, yt_names = split_platforms(self._read_streamers())
        self.tw_text = self._platform_tab("  Twitch  ", T("Ник из ссылки: twitch.tv/kaicenat → kaicenat"), tw_names)
        self.yt_text = self._platform_tab("  YouTube  ", T("Ник канала: youtube.com/@MrBeast → MrBeast"), yt_names)
        self._build_queue_tab()
        self._update_platform_titles()
        ttk.Button(box, text=T("✔  Применить список (можно и во время слежки)"),
                   command=self.apply_streamers).pack(fill="x", pady=(6, 0))

        # настройки
        opt = ttk.LabelFrame(top, text=T(" Что делать с клипом "), padding=6)
        opt.pack(side="right", fill="y", before=box)  # блоку настроек — его полная ширина
        for key, text in (("subs", T("Субтитры (речь стримера)")),
                          ("caption", T("Надпись-плашка с подписью к моменту")),
                          ("facecam", T("Вебка стримера сверху")),
                          ("audio", T("Искать по звуку и картинке (без чата)"))):
            self.v[key] = tk.BooleanVar(value=bool(self.cfg.get(key)))
            ttk.Checkbutton(opt, text=text, variable=self.v[key]).pack(anchor="w", pady=2)
        grid = ttk.Frame(opt)
        grid.pack(anchor="w", pady=(6, 0))
        digits = (self.root.register(lambda p: p == "" or (p.isdigit() and len(p) <= 3)), "%P")
        for r, (key, text, values, editable) in enumerate((
                ("top", T("Клипов за час стрима:"), ["1", "2", "3", "5", "10", "20", "50"], True),
                ("length", T("Длина клипа, сек:"), ["10", "15", "25", "35", "45", "60"], True),
                ("quality", T("Качество:"), ["720", "1080"], False))):
            ttk.Label(grid, text=text).grid(row=r, column=0, sticky="w", pady=2)
            val = str(self.cfg.get(key))
            ok = val.isdigit() if editable else val in values
            self.v[key] = tk.StringVar(value=val if ok else DEFAULTS[key])
            cb = ttk.Combobox(grid, textvariable=self.v[key], values=values, width=6,
                              state="normal" if editable else "readonly")
            if editable:
                cb.configure(validate="key", validatecommand=digits)
                self.v[key].trace_add("write", lambda *a: self._on_live_setting())
            cb.grid(row=r, column=1, sticky="w", padx=6)
        ttk.Label(grid, text=T("Игра в кадре:")).grid(row=3, column=0, sticky="w", pady=2)
        gv = self.cfg.get("game_view")
        self.v["game_view"] = tk.StringVar(value=gv if gv in GAME_VIEW else T("целиком"))
        ttk.Combobox(grid, textvariable=self.v["game_view"], values=list(GAME_VIEW), width=12,
                     state="readonly").grid(row=3, column=1, sticky="w", padx=6)
        # картинка-пример: как будет выглядеть клип при выбранном варианте
        self.gv_images = {}
        for label, key in GAME_VIEW.items():
            try:
                self.gv_images[label] = tk.PhotoImage(file=os.path.join(PROG, "stream_clipper", "assets",
                                                                        f"gameview_{key}.png"))
            except Exception:
                pass
        self.gv_preview = ttk.Label(grid)
        self.gv_preview.grid(row=0, column=2, rowspan=4, padx=(10, 0), sticky="ne")
        self.v["game_view"].trace_add("write", lambda *a: self._update_gv_preview())
        self._update_gv_preview()
        ttk.Label(grid, text=T("числа можно вписать свои;\nменяются и во время работы"),
                  foreground=self.muted).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))

        # ключ Claude
        keyf = ttk.LabelFrame(sett, text=T(" Ключ Claude API для умных надписей (необязательно) "), padding=6)
        keyf.pack(fill="x", pady=6)
        self.key = tk.StringVar(value=self._read_key())
        ttk.Entry(keyf, textvariable=self.key, show="•").pack(side="left", fill="x", expand=True)
        ttk.Button(keyf, text=T("Сохранить ключ"), command=self.save_key).pack(side="left", padx=6)
        self.key_status = ttk.Label(keyf, text="")
        self.key_status.pack(side="left")
        self._update_key_status()
        # вход в YouTube из браузера — чтобы YouTube не считал программу ботом (часто бывает через VPN)
        ytf = ttk.Frame(sett)
        ytf.pack(fill="x", pady=(0, 6))
        ttk.Label(ytf, text=T("Вход в YouTube через браузер:")).pack(side="left")
        yb = self.cfg.get("yt_browser")
        self.v["yt_browser"] = tk.StringVar(value=yb if yb in YT_BROWSERS else T("не брать"))
        ttk.Combobox(ytf, textvariable=self.v["yt_browser"], values=list(YT_BROWSERS), width=12,
                     state="readonly").pack(side="left", padx=6)
        ttk.Label(ytf, text=T("нужно, если YouTube считает программу ботом (лучше Firefox, войди в нём в YouTube)"),
                  foreground=self.muted).pack(side="left")

        # водяной знак
        wm = ttk.LabelFrame(sett, text=T(" Водяной знак — чтобы клипы не крали "), padding=6)
        wm.pack(fill="x", pady=(0, 6))
        r1 = ttk.Frame(wm)
        r1.pack(fill="x")
        self.v["wm_on"] = tk.BooleanVar(value=bool(self.cfg.get("wm_on")))
        ttk.Checkbutton(r1, text=T("Ставить"), variable=self.v["wm_on"]).pack(side="left")
        ttk.Label(r1, text=T("  Текст:")).pack(side="left")
        self.v["wm_text"] = tk.StringVar(value=self.cfg.get("wm_text", ""))
        ttk.Entry(r1, textvariable=self.v["wm_text"], width=20).pack(side="left", padx=4)
        ttk.Label(r1, text=T("(например @твой_канал)"), foreground=self.muted).pack(side="left")
        self.v["wm_image"] = tk.StringVar(value=self.cfg.get("wm_image", ""))
        ttk.Button(r1, text="✕", width=3, command=lambda: self.v["wm_image"].set("")).pack(side="right")
        ttk.Button(r1, text=T("Логотип…"), command=self.choose_logo).pack(side="right", padx=4)
        self.logo_label = ttk.Label(r1, text="", foreground=self.muted)
        self.logo_label.pack(side="right")
        self.v["wm_image"].trace_add("write", lambda *a: self._update_logo_label())
        self._update_logo_label()
        r2 = ttk.Frame(wm)
        r2.pack(fill="x", pady=(4, 0))
        ttk.Label(r2, text=T("Где:")).pack(side="left")
        self.v["wm_pos"] = tk.StringVar(value=self.cfg.get("wm_pos") if self.cfg.get("wm_pos") in WM_POS
                                        else T("плавает по экрану"))
        ttk.Combobox(r2, textvariable=self.v["wm_pos"], values=list(WM_POS), width=18,
                     state="readonly").pack(side="left", padx=4)
        ttk.Label(r2, text=T("  Заметность:")).pack(side="left")
        self.v["wm_op"] = tk.StringVar(value=self.cfg.get("wm_op") if self.cfg.get("wm_op") in WM_OP else T("средне"))
        ttk.Combobox(r2, textvariable=self.v["wm_op"], values=list(WM_OP), width=9,
                     state="readonly").pack(side="left", padx=4)
        ttk.Label(r2, text=T("  «плавает» — лучшая защита: знак нельзя обрезать или замазать"),
                  foreground=self.muted).pack(side="left")

        # подпись автора
        cr = ttk.LabelFrame(sett, text=T(" Подпись автора — чей это клип (Twitch | KaiCenat) "), padding=6)
        cr.pack(fill="x", pady=(0, 6))
        self.v["credit_on"] = tk.BooleanVar(value=bool(self.cfg.get("credit_on", True)))
        ttk.Checkbutton(cr, text=T("Подписывать платформу и стримера"), variable=self.v["credit_on"]).pack(side="left")
        ttk.Label(cr, text=T("  Где:")).pack(side="left")
        self.v["credit_pos"] = tk.StringVar(value=self.cfg.get("credit_pos") if self.cfg.get("credit_pos") in CREDIT_POS
                                            else T("внизу слева"))
        ttk.Combobox(cr, textvariable=self.v["credit_pos"], values=list(CREDIT_POS), width=14,
                     state="readonly").pack(side="left", padx=4)
        for k in ("credit_on", "credit_pos"):
            self.v[k].trace_add("write", lambda *a: self._on_live_setting())
        ttk.Label(cr, text=T("  указывает источник — так требуют правила площадок"),
                  foreground=self.muted).pack(side="left")

        self._build_telegram(sett)

        # кнопки
        btns = ttk.Frame(main)
        btns.pack(fill="x", pady=6)
        style = ttk.Style()
        style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        self.b_watch = ttk.Button(btns, text=T("▶  Следить за стримерами"), style="Big.TButton", command=self.start_watch)
        self.b_watch.pack(side="left")
        self.b_stop = ttk.Button(btns, text=T("■  Стоп"), style="Big.TButton", command=self.stop, state="disabled")
        self.b_stop.pack(side="left", padx=8)
        ttk.Button(btns, text=T("📁  Папка с клипами"), style="Big.TButton", command=self.open_folder).pack(side="right")

        # нарезка по ссылке
        vod = ttk.LabelFrame(main, text=T(" Нарезать один стрим по ссылке (запись Twitch или YouTube) "), padding=6)
        vod.pack(fill="x", pady=4)
        self.url = tk.StringVar()
        ttk.Entry(vod, textvariable=self.url).pack(side="left", fill="x", expand=True)
        self.b_vod = ttk.Button(vod, text=T("✂  Нарезать"), command=self.start_vod)
        self.b_vod.pack(side="left", padx=6)
        fromrow = ttk.Frame(main)
        fromrow.pack(fill="x", pady=(0, 4))
        ttk.Label(fromrow, text=T("Для ссылки — начать с:")).pack(side="left")
        self.v["start_from"] = tk.StringVar(value=self.cfg.get("start_from") or T("с начала"))
        ttk.Combobox(fromrow, textvariable=self.v["start_from"], width=11,
                     values=[T("с начала"), T("сейчас"), "0:30", "1:00", "1:30", "2:00", "3:00", "4:00"]
                     ).pack(side="left", padx=6)
        lm = self.cfg.get("start_mode")
        self.v["start_mode"] = tk.StringVar(value=lm if lm in (T("от начала стрима"), T("по часам")) else T("от начала стрима"))
        ttk.Combobox(fromrow, textvariable=self.v["start_mode"], width=16, state="readonly",
                     values=[T("от начала стрима"), T("по часам")]).pack(side="left", padx=(0, 6))
        ttk.Label(fromrow, foreground=self.muted,
                  text=T("Для стримеров время задаётся отдельно: «За кем следим» → «Очередь»")).pack(side="left")

        # журнал
        logf = ttk.LabelFrame(main, text=T(" Что происходит "), padding=6)
        logf.pack(fill="both", expand=True, pady=(6, 0))
        logbar = ttk.Frame(logf)
        logbar.pack(fill="x")
        self.log_detailed = tk.BooleanVar(value=False)
        self.log_lines: list = []  # (текст, важная ли строка)
        ttk.Label(logbar, text=T("Коротко: что началось и какие клипы готовы"), foreground=self.muted).pack(side="left")
        self.b_hide_log = ttk.Button(logbar, text=T("Скрыть ▴"), command=self._toggle_log)
        self.b_hide_log.pack(side="right", padx=(6, 0))
        self.b_details = ttk.Button(logbar, text=T("Подробнее ▾"), command=self._toggle_details)
        self.b_details.pack(side="right")
        self.log = ScrolledText(logf, height=8, font=("Consolas", 10), state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)
        self.logf = logf
        if self.cfg.get("log_hidden"):
            self.root.after(50, self._toggle_log)
        bottom = ttk.Frame(main)
        bottom.pack(side="bottom", fill="x", pady=(4, 0), before=logf)
        self.v["autoupdate"] = tk.BooleanVar(value=bool(self.cfg.get("autoupdate", True)))
        ttk.Checkbutton(bottom, text=T("Обновляться автоматически"), variable=self.v["autoupdate"]).pack(side="right")
        ttk.Button(bottom, text=T("⟳ Проверить обновления"),
                   command=lambda: self.check_updates(manual=True)).pack(side="right", padx=6)
        self.status = ttk.Label(bottom, text=T("Готово. Не забудь включить VPN."), anchor="w", width=10)
        self.status.pack(side="left", fill="x", expand=True)
        # плашка «есть новая версия» (показывается, когда нужно)
        self.update_bar = tk.Frame(self.root, bg="#fff3c4")  # жёлтая плашка видна в любой теме
        self.update_label = tk.Label(self.update_bar, bg="#fff3c4", font=("Segoe UI", 10, "bold"))
        self.update_label.pack(side="left", padx=10, pady=6)
        ttk.Button(self.update_bar, text=T("Обновить сейчас"), command=self.install_update).pack(side="right", padx=8)
        self.pending_update = None
        self.updating = False
        self.job = None  # что сейчас делается: ("watch",) или ("vod", ссылка)
        self.root.after(1500, self._resume_after_update)
        self.root.after(2500, self.check_updates)

    # ---------- горячие клавиши и меню правой кнопки ----------
    # Ctrl+C/V/X/A/Z работают и при русской раскладке (там вместо C приходит «С» и т.д.)
    _CTRL_KEYS = {
        "c": "copy", "cyrillic_es": "copy", "insert": "copy",
        "v": "paste", "cyrillic_em": "paste",
        "x": "cut", "cyrillic_che": "cut",
        "a": "all", "cyrillic_ef": "all",
        "z": "undo", "cyrillic_ya": "undo",
        "y": "redo", "cyrillic_en": "redo",
    }
    _WIN_KEYCODES = {67: "copy", 86: "paste", 88: "cut", 65: "all", 90: "undo", 89: "redo"}  # клавиши C V X A Z Y

    def _install_shortcuts(self):
        self.root.bind_all("<Control-KeyPress>", self._on_ctrl_key, add="+")
        for cls in ("TEntry", "Entry", "Text"):
            self.root.bind_class(cls, "<Button-3>", self._edit_menu, add="+")

    def _on_ctrl_key(self, e):
        keysym = (e.keysym or "").lower()
        action = self._CTRL_KEYS.get(keysym)
        if action is None and os.name == "nt":
            action = self._WIN_KEYCODES.get(e.keycode)
        if not action:
            return None
        w = e.widget
        if isinstance(w, ttk.Treeview):
            if action == "copy":
                self.copy_caption()
            elif action == "all":
                w.selection_set(w.get_children())
            return "break"
        if action == "all":
            self._select_all(w)
            return "break"
        if keysym in ("c", "v", "x", "z", "y") and isinstance(w, (tk.Entry, ttk.Entry, tk.Text)):
            return None  # с английской раскладкой Tk справится сам (иначе вставит дважды)
        event = {"copy": "<<Copy>>", "paste": "<<Paste>>", "cut": "<<Cut>>",
                 "undo": "<<Undo>>", "redo": "<<Redo>>"}[action]
        try:
            w.event_generate(event)
        except tk.TclError:
            pass
        return "break"

    def _select_all(self, w):
        try:
            if isinstance(w, tk.Text):
                w.tag_add("sel", "1.0", "end-1c")
                w.mark_set("insert", "end-1c")
            else:
                w.select_range(0, "end")
                w.icursor("end")
        except (tk.TclError, AttributeError):
            pass

    def _edit_menu(self, e):
        w = e.widget
        try:
            w.focus_set()
        except tk.TclError:
            pass
        try:
            readonly = str(w.cget("state")) in ("disabled", "readonly")
        except tk.TclError:
            readonly = False
        m = tk.Menu(self.root, tearoff=0)
        if not readonly:
            m.add_command(label=T("Вырезать        Ctrl+X"), command=lambda: w.event_generate("<<Cut>>"))
        m.add_command(label=T("Копировать     Ctrl+C"), command=lambda: w.event_generate("<<Copy>>"))
        if not readonly:
            m.add_command(label=T("Вставить          Ctrl+V"), command=lambda: w.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label=T("Выделить всё   Ctrl+A"), command=lambda: self._select_all(w))
        m.tk_popup(e.x_root, e.y_root)
        return "break"

    def _clips_menu(self, e):
        iid = self.tree.identify_row(e.y)
        if iid and iid not in self.tree.selection():
            self.tree.selection_set(iid)
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label=T("▶  Смотреть"), command=self.play_clip)
        for key, label in library.PLATFORM_NAMES.items():
            m.add_command(label=T('🚀  Выложить в {0}').format(label), command=lambda k=key: self.publish(k))
        m.add_command(label=T("📋  Копировать надпись   Ctrl+C"), command=self.copy_caption)
        m.add_command(label=T("✍  Описание и хэштеги"), command=self.post_texts)
        m.add_command(label=T("🛡  Проверить правила / исправить нарушение"), command=self.fix_violations)
        for key, label in library.PLATFORM_NAMES.items():
            m.add_command(label=T('✔  Выложено в {0} / снять').format(label), command=lambda k=key: self.toggle_posted(k))
        m.add_command(label=T("📂  Показать в папке"), command=self.reveal_clip)
        m.add_command(label=T("🎥  Указать вебку этого стримера"), command=self.pick_facecam)
        m.add_separator()
        m.add_command(label=T("🗑  Удалить   Delete"), command=self.delete_clip)
        m.tk_popup(e.x_root, e.y_root)

    # ---------- файлы ----------
    def _platform_tab(self, title: str, hint: str, names: list[str]) -> tk.Text:
        f = ttk.Frame(self.platforms, padding=4)
        self.platforms.add(f, text=title)
        ttk.Label(f, text=hint + T("  (по одному в строке)"), foreground=self.muted).pack(anchor="w")
        t = tk.Text(f, height=6, width=28, font=("Segoe UI", 11), undo=True)
        t.pack(fill="both", expand=True)
        t.insert("1.0", "\n".join(names))
        t.bind("<KeyRelease>", lambda e: self._on_streamers_edit())
        return t

    def _on_streamers_edit(self):
        self._update_platform_titles()
        if getattr(self, "_autosave_job", None):
            self.root.after_cancel(self._autosave_job)
        self._autosave_job = self.root.after(1500, self._autosave_streamers)

    def _autosave_streamers(self):
        """Сохраняем список сразу при вводе, не трогая поле (чтобы не мешать печатать)."""
        self._autosave_job = None
        tw = _unique([norm_twitch(n) for n in self._platform_names(self.tw_text)])
        yt = _unique([norm_youtube(n) for n in self._platform_names(self.yt_text)])
        self._write_streamers(tw, yt)

    # ---------- очередь: кого обрабатывать первым (Twitch и YouTube вместе) ----------
    def _build_queue_tab(self):
        f = ttk.Frame(self.platforms, padding=4)
        self.platforms.add(f, text=T("  Очередь  "))
        ttk.Label(f, text=T("Кто выше — того программа обрабатывает первым"), foreground=self.muted).pack(anchor="w")
        row = ttk.Frame(f)
        row.pack(fill="both", expand=True)
        self.queue_list = tk.Listbox(row, height=6, font=("Segoe UI", 11), activestyle="none", exportselection=False)
        self.queue_list.pack(side="left", fill="both", expand=True)
        side = ttk.Frame(row)
        side.pack(side="left", fill="y", padx=(6, 0))
        ttk.Button(side, text=T("⏫ Первым"), command=lambda: self._queue_move("top")).pack(fill="x")
        ttk.Button(side, text=T("▲ Выше"), command=lambda: self._queue_move(-1)).pack(fill="x", pady=4)
        ttk.Button(side, text=T("▼ Ниже"), command=lambda: self._queue_move(1)).pack(fill="x")
        st = ttk.Frame(f)
        st.pack(fill="x", pady=(6, 0))
        ttk.Label(st, text=T("Начать с:")).pack(side="left")
        self.q_start = tk.StringVar(value="")
        ttk.Combobox(st, textvariable=self.q_start, width=8,
                     values=[T("с начала"), T("сейчас"), "1:00", "2:00", "13:00", "18:00"]).pack(side="left", padx=4)
        self.q_mode = tk.StringVar(value=T("от начала стрима"))
        ttk.Combobox(st, textvariable=self.q_mode, width=16, state="readonly",
                     values=[T("от начала стрима"), T("по часам")]).pack(side="left")
        ttk.Button(st, text=T("Задать выбранному"), command=self._queue_set_start).pack(side="left", padx=4)
        self.queue_list.bind("<<ListboxSelect>>", lambda e: self._queue_show_start())
        self.queue_keys: list[str] = []
        self.platforms.bind("<<NotebookTabChanged>>", lambda e: self._refresh_queue(), add="+")
        self._refresh_queue()

    def _current_keys(self) -> list[str]:
        tw = _unique([norm_twitch(n) for n in self._platform_names(self.tw_text)])
        yt = _unique([norm_youtube(n) for n in self._platform_names(self.yt_text)])
        return [paths.priority_key(x) for x in tw + yt]

    def _refresh_queue(self):
        current = self._current_keys()
        try:
            with open(paths.priority_path(), encoding="utf-8") as fh:
                saved = [paths.priority_key(x) for x in json.load(fh)]
        except Exception:
            saved = []
        self.queue_keys = [k for k in saved if k in current] + [k for k in current if k not in saved]
        sel = self.queue_list.curselection()
        self.queue_list.delete(0, "end")
        tw = _unique([norm_twitch(n) for n in self._platform_names(self.tw_text)])
        yt_ = _unique([norm_youtube(n) for n in self._platform_names(self.yt_text)])
        shown = {paths.priority_key(x): x for x in tw + yt_}  # как записано (с большими буквами)
        starts = paths.load_start_times()
        for i, k in enumerate(self.queue_keys, 1):
            yt = k.startswith("@") or "youtube.com" in k or "youtu.be" in k
            orig = shown.get(k, k)
            name = orig.lstrip("@") if not orig.startswith("http") else orig.rstrip("/").split("/")[-1]
            st = starts.get(k) or {}
            if st.get("value"):
                name += T('   ⏱ с {0}').format(st['value']) + (T(" по часам") if st.get("mode") == "clock" else T(" от начала"))
            self.queue_list.insert("end", f"{i}. {'YouTube' if yt else 'Twitch'} — {name}")
        if sel and sel[0] < len(self.queue_keys):
            self.queue_list.selection_set(sel[0])

    def _queue_move(self, delta):
        sel = self.queue_list.curselection()
        if not sel:
            messagebox.showinfo(T("Очередь"), T("Выбери стримера в списке."))
            return
        i = sel[0]
        keys = list(self.queue_keys)
        j = 0 if delta == "top" else max(0, min(len(keys) - 1, i + delta))
        keys.insert(j, keys.pop(i))
        try:
            os.makedirs(os.path.dirname(paths.priority_path()), exist_ok=True)
            with open(paths.priority_path(), "w", encoding="utf-8") as fh:
                json.dump(keys, fh, ensure_ascii=False)
        except OSError:
            return
        self._refresh_queue()
        self.queue_list.selection_clear(0, "end")
        self.queue_list.selection_set(j)
        if self.proc:
            self._append(T("Очередь изменена — применится на следующем круге проверки: ")
                         + " → ".join(k.lstrip("@") for k in keys) + "\n")

    def _queue_show_start(self):
        sel = self.queue_list.curselection()
        if not sel or sel[0] >= len(self.queue_keys):
            return
        st = paths.load_start_times().get(self.queue_keys[sel[0]]) or {}
        self.q_start.set(st.get("value") or T("с начала"))
        self.q_mode.set(T("по часам") if st.get("mode") == "clock" else T("от начала стрима"))

    def _queue_set_start(self):
        sel = self.queue_list.curselection()
        if not sel or sel[0] >= len(self.queue_keys):
            messagebox.showinfo(T("Очередь"), T("Выбери стримера в списке."))
            return
        key = self.queue_keys[sel[0]]
        value = self.q_start.get().strip()
        try:
            parsed = paths.parse_start(value)
        except ValueError as e:
            messagebox.showwarning(T("Время"), str(e))
            return
        data = paths.load_start_times()
        if parsed is None:
            data.pop(key, None)
            text = T("с начала стрима")
        else:
            data[key] = {"value": value, "mode": "clock" if self.q_mode.get() == T("по часам") else "stream"}
            text = T('с {0} ').format(value) + (T("по часам") if self.q_mode.get() == T("по часам") else T("от начала стрима"))
        paths.save_start_times(data)
        self._refresh_queue()
        self.queue_list.selection_set(sel[0])
        yt = key.startswith("@") or "youtube" in key
        self._append(T('Для {0}: начинать {1}').format(key.lstrip('@'), text)
                     + (T(" (для YouTube-эфира прошлое недоступно — запись идёт с момента запуска)") if yt else "")
                     + (T("; применится на следующем круге проверки") if self.proc else "") + "\n")

    def _platform_names(self, t: tk.Text) -> list[str]:
        return [ln.strip() for ln in t.get("1.0", "end").splitlines() if ln.strip()]

    def _update_platform_titles(self):
        self.platforms.tab(0, text=f"  Twitch ({len(self._platform_names(self.tw_text))})  ")
        self.platforms.tab(1, text=f"  YouTube ({len(self._platform_names(self.yt_text))})  ")
        if hasattr(self, "queue_list"):
            self._refresh_queue()

    def _read_streamers(self) -> list[str]:
        for path in (STREAMERS, STREAMERS_BACKUP):
            try:
                with open(path, encoding="utf-8-sig") as f:
                    names = [ln.split("#")[0].strip() for ln in f if ln.split("#")[0].strip()]
            except OSError:
                continue
            if names or path == STREAMERS_BACKUP:
                return names
        return []

    def _write_streamers(self, tw: list[str], yt: list[str]):
        text = (STREAMERS_HEADER + "\n# Twitch\n" + "".join(n + "\n" for n in tw)
                + "\n# YouTube\n" + "".join(n + "\n" for n in yt))
        for path in (STREAMERS, STREAMERS_BACKUP):
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
            except OSError:
                pass

    def _save_streamers(self) -> list[str]:
        tw = _unique([norm_twitch(n) for n in self._platform_names(self.tw_text)])
        yt = _unique([norm_youtube(n) for n in self._platform_names(self.yt_text)])
        # показываем, как программа поняла ники
        for t, names, show in ((self.tw_text, tw, lambda n: n), (self.yt_text, yt, lambda n: n.lstrip("@"))):
            t.delete("1.0", "end")
            t.insert("1.0", "\n".join(show(n) for n in names))
        self._update_platform_titles()
        self._write_streamers(tw, yt)
        return tw + yt

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

    # ---------- телефон: Telegram ----------
    def _build_telegram(self, parent):
        from . import telegram
        cfg = telegram.load()
        tg = ttk.LabelFrame(parent, text=T(" 📱 Клипы на телефон (Telegram) "), padding=6)
        tg.pack(fill="x", pady=(0, 6))
        ttk.Label(tg, justify="left", foreground=self.muted, text=(
            T("1) В Telegram найди @BotFather → /newbot → придумай имя → он пришлёт ключ (токен). Вставь его сюда.\n"
            "2) Папки по датам (лучше): создай группу → в её настройках включи «Темы» → добавь туда бота\n"
            "    администратором с правом «Управление темами» → напиши в группе любое сообщение.\n"
            "    Без группы: просто открой бота и нажми «Старт».   3) Нажми «Подключить».\n"
            "Клипы приходят ФАЙЛАМИ (без потери качества); в группе бот сам заводит тему-папку на каждый день.")
        )).pack(anchor="w")
        row = ttk.Frame(tg)
        row.pack(fill="x", pady=(6, 0))
        self.tg_on = tk.BooleanVar(value=bool(cfg.get("on")))
        ttk.Checkbutton(row, text=T("Отправлять клипы"), variable=self.tg_on, command=self._tg_toggle).pack(side="left")
        ttk.Label(row, text=T("  Ключ бота:")).pack(side="left")
        self.tg_token = tk.StringVar(value=cfg.get("token", ""))
        ttk.Entry(row, textvariable=self.tg_token, show="•", width=24).pack(side="left", padx=4)
        ttk.Button(row, text=T("Подключить"), command=self._tg_connect).pack(side="left")
        ttk.Button(row, text=T("Проверить"), command=self._tg_test).pack(side="left", padx=4)
        self.tg_status = ttk.Label(row, text=(T("✔ подключено: ") + cfg.get("name", "")) if cfg.get("chat_id")
                                   else T("не подключено"), foreground=self.muted)
        self.tg_status.pack(side="left", padx=6)

    def _tg_toggle(self):
        from . import telegram
        cfg = telegram.load()
        cfg["on"] = bool(self.tg_on.get())
        telegram.save(cfg)

    def _tg_connect(self):
        from . import telegram
        token = self.tg_token.get().strip()
        if not token:
            messagebox.showinfo("Telegram", T("Сначала вставь ключ бота от @BotFather."))
            return
        self.tg_status.config(text=T("подключаю..."))

        def work():
            try:
                chat_id, name, forum = telegram.find_chat(token)
                telegram.save({"token": token, "chat_id": chat_id, "name": name, "on": True, "forum": forum})
                telegram.send_text(T("✅ Stream Clipper подключён! ") + (
                    T("Клипы будут складываться в темы-папки по датам.") if forum else
                    T("Сюда будут приходить готовые клипы файлами (для папок по датам подключи группу с темами).")))
                label = T('✔ группа «{0}» (папки по датам)').format(name) if forum else T('✔ подключено: {0}').format(name)
                self.root.after(0, lambda: (self.tg_on.set(True), self.tg_status.config(text=label)))
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda: (self.tg_status.config(text=T("не подключено")),
                                            messagebox.showwarning("Telegram", T('Не получилось подключить:\n{0}').format(err))))
        threading.Thread(target=work, daemon=True).start()

    def _tg_test(self):
        from . import telegram

        def work():
            try:
                telegram.send_text(T("👋 Проверка связи от Stream Clipper"))
                self.root.after(0, lambda: self.tg_status.config(text=T("✔ сообщение отправлено — проверь Telegram")))
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda: messagebox.showwarning("Telegram", T('Не отправилось:\n{0}').format(err)))
        threading.Thread(target=work, daemon=True).start()

    def choose_logo(self):
        path = filedialog.askopenfilename(title=T("Логотип для водяного знака"),
                                          filetypes=[(T("Картинки"), "*.png *.jpg *.jpeg *.webp"), (T("Все файлы"), "*.*")])
        if not path:
            return
        # копируем к себе, чтобы знак не пропал, если исходный файл переместят
        import shutil
        dest = os.path.join(paths.default_work_dir(), "watermark" + os.path.splitext(path)[1].lower())
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(path, dest)
        self.v["wm_image"].set(dest)
        self.v["wm_on"].set(True)

    def _update_logo_label(self):
        p = self.v["wm_image"].get()
        self.logo_label.config(text=T("логотип выбран ✔") if p and os.path.exists(p) else T("без логотипа"))

    def _update_key_status(self):
        ok = bool(self.key.get().strip())
        self.key_status.config(text=T("✔ ключ есть") if ok else T("нет ключа — надписи по шаблону"))

    def _save_settings(self):
        hidden = self.cfg.get("log_hidden", False)
        self.cfg = {k: (v.get()) for k, v in self.v.items()}
        self.cfg["log_hidden"] = hidden
        with open(SETTINGS, "w", encoding="utf-8") as f:
            json.dump(_ru(self.cfg), f, ensure_ascii=False, indent=1)

    # ---------- запуск ----------
    def _update_gv_preview(self):
        img = self.gv_images.get(self.v["game_view"].get())
        if img is not None:
            self.gv_preview.config(image=img, text="")

    def _num(self, key: str, lo: int, hi: int) -> int:
        """Число из поля с границами; пустое/неверное — значение по умолчанию."""
        try:
            n = int(self.v[key].get())
        except ValueError:
            n = int(DEFAULTS[key])
        return max(lo, min(hi, n))

    def _clip_numbers(self) -> tuple[int, int, int]:
        top = self._num("top", 1, 500)
        length = self._num("length", 5, 180)
        pre = max(2, round(length * 0.57))
        return top, pre, max(2, length - pre)

    def _on_live_setting(self):
        """Поменяли «клипов в час» или длину во время работы — передаём сразу (с задержкой на ввод)."""
        if getattr(self, "_live_job", None):
            self.root.after_cancel(self._live_job)
        self._live_job = self.root.after(1200, self._push_live_settings)

    def _push_live_settings(self):
        self._live_job = None
        if not self.v["top"].get() or not self.v["length"].get():
            return  # ещё печатает
        top, pre, post = self._clip_numbers()
        self._save_settings()
        if not self.proc:
            return
        try:
            with open(paths.live_settings_path(), "w", encoding="utf-8") as f:
                json.dump({"top": top, "pre": pre, "post": post, "credit": bool(self.v["credit_on"].get()),
                           "credit_pos": CREDIT_POS.get(self.v["credit_pos"].get(), "bottom-left")}, f)
        except OSError:
            return
        self._append(T('Настройки изменены: {0} клипов за час, по {1} с — применятся к следующим клипам.\n').format(top, pre + post))

    def _flags(self, for_link: bool = False) -> list[str]:
        self._save_settings()
        c = self.cfg
        top, pre, post = self._clip_numbers()
        f = ["-n", str(top), "--pre", str(pre), "--post", str(post),
             "--max-height", c["quality"], "--game-view", GAME_VIEW.get(c.get("game_view"), "full"),
             "--layout", "auto" if c["facecam"] else "blur"]
        if c["subs"]:
            if importlib.util.find_spec("faster_whisper") is None:
                self._append(T("⚠ Субтитры не установлены — запусти install_subs.bat. Пока режу без них.\n"))
                f.append("--no-subs")
            else:
                f.append("--subs")
        else:
            f.append("--no-subs")
        if not c["caption"]:
            f.append("--no-caption")
        if not c["audio"]:
            f.append("--no-audio")
        if for_link:  # у слежки время своё для каждого стримера (вкладка «Очередь»)
            try:
                start = paths.parse_start(c.get("start_from"))
            except ValueError as e:
                messagebox.showwarning(T("Время"), str(e))
                start = None
            if start == "now":
                f += ["--from", T("сейчас")]
            elif start:
                f += ["--from", f"{int(start // 3600)}:{int(start % 3600 // 60):02d}"]
            if start and c.get("start_mode") == T("по часам"):
                f += ["--from-mode", "clock"]
        browser = YT_BROWSERS.get(c.get("yt_browser"), "")
        if browser:
            f += ["--cookies-browser", browser]
        if not c.get("credit_on", True):
            f += ["--no-credit"]
        else:
            f += ["--credit-pos", CREDIT_POS.get(c.get("credit_pos"), "bottom-left")]
        text, image = c.get("wm_text", "").strip(), c.get("wm_image", "")
        if c.get("wm_on") and (text or (image and os.path.exists(image))):
            if text:
                f += ["--watermark-text", text]
            if image and os.path.exists(image):
                f += ["--watermark-image", image]
            f += ["--watermark-pos", WM_POS.get(c.get("wm_pos"), "moving"),
                  "--watermark-opacity", str(WM_OP.get(c.get("wm_op"), 0.4))]
        return f

    def _run(self, args: list[str], what: str, job=None):
        if self.proc:
            return
        self.job = job
        self._last_job = job
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
        cmd = [_python_exe(), "-m", "stream_clipper", *args]
        self._append(f"\n=== {what} ===\n")
        try:
            self.proc = subprocess.Popen(cmd, cwd=PROG, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, creationflags=flags)
        except Exception as e:
            self._append(T('Не удалось запустить: {0}\n').format(e))
            self.proc = None
            return
        self._set_running(True, what)
        threading.Thread(target=self._reader, args=(self.proc,), daemon=True).start()

    def apply_streamers(self):
        names = self._save_streamers()
        if self.proc:
            self._append(T("Список стримеров обновлён: ") + (", ".join(names) or T("пусто"))
                         + T(". Программа подхватит его через несколько секунд.\n"))
        else:
            self.status.config(text=T("Список сохранён: ") + (", ".join(names) or T("пусто")))

    def start_watch(self):
        names = self._save_streamers()
        if not names:
            messagebox.showwarning(T("Нет стримеров"), T("Впиши хотя бы одного стримера во вкладку Twitch или YouTube."))
            return
        self._run(["watch", *self._flags()], T("Слежу за: ") + ", ".join(names), job=["watch"])

    def start_vod(self):
        url = self.url.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning(T("Нет ссылки"), T("Вставь ссылку на запись стрима (twitch.tv/videos/... или youtube.com/watch?v=...)."))
            return
        self._offer_resume(url)
        self._run(["vod", url, *self._flags(for_link=True)], T("Нарезаю ") + url, job=["vod", url])

    def _offer_resume(self, url: str):
        """Ссылку уже разбирали, а время стоит «с начала» — предлагаем продолжить с места остановки."""
        from . import progress
        from urllib.parse import parse_qs, urlparse
        if self.v["start_from"].get() not in ("", T("с начала")):
            return
        if "watch?v=" in url:
            key = (parse_qs(urlparse(url).query).get("v") or [""])[0]
        elif "youtu.be/" in url or "/live/" in url:
            key = urlparse(url).path.rstrip("/").split("/")[-1]
        else:
            key = url.rstrip("/").split("/")[-1].split("?")[0].lstrip("v")
        e = progress.load().get(key)
        if not e or not e.get("ranges"):
            return
        sm = progress.summary(e)
        if sm["finished"] or not sm["resume"]:
            return
        if messagebox.askyesno(T("Этот стрим уже разбирали"),
                               T('Разобрано: {0}.\nПродолжить с {1} (место остановки)?\n\n«Нет» — пройти стрим с самого начала.').format(sm['done'], progress.fmt(sm['resume']))):
            t = sm["resume"]
            self.v["start_from"].set(f"{int(t // 3600)}:{int(t % 3600 // 60):02d}")
            self.v["start_mode"].set(T("от начала стрима"))

    def stop(self):
        """Первое нажатие — аккуратно: программа дорежет начатое и сохранит прогресс.
        Второе нажатие — остановить сразу."""
        p = self.proc
        if not p:
            return
        if not getattr(self, "stopping", False):
            self.stopping = True
            try:
                open(paths.stop_request_path(), "w").close()
            except OSError:
                pass
            self._append(T("\nОстанавливаю аккуратно: дорежу начатое и сохраню прогресс, чтобы потом продолжить "
                         "с этого места. Нажми «Стоп» ещё раз, чтобы остановить сразу.\n"))
            self.b_stop.config(text=T("■  Стоп сразу"))
            self._force_job = self.root.after(5 * 60 * 1000, self.force_stop)
            return
        self.force_stop()

    def force_stop(self):
        p = self.proc
        if not p:
            return
        self._append(T("\nОстанавливаю сразу...\n"))
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
                    self._append(T("=== Остановлено ===\n"))
                    self.proc = None
                    self.job = None
                    self.stopping = False
                    if getattr(self, "_force_job", None):
                        self.root.after_cancel(self._force_job)
                        self._force_job = None
                    self.b_stop.config(text=T("■  Стоп"))
                    self._set_running(False)
                    if self.updating:  # остановились ради обновления — перезапускаемся и продолжим
                        self._restart()
                        return
                    if getattr(self, "restart_worker", False):  # обновилась только рабочая часть
                        self.restart_worker = False
                        job = self._last_job
                        self._append(T("=== Продолжаю работу на новой версии ===\n"))
                        if job and job[0] == "vod" and len(job) > 1:
                            self.url.set(job[1])
                            self.root.after(500, self.start_vod)
                        else:
                            self.root.after(500, self.start_watch)
                        continue
                    if self.pending_update and self.v["autoupdate"].get():
                        self.root.after(1000, self.install_update)
                else:
                    self._append(tr_line(item), important=self._is_important(item))
                    if "готово ->" in item:
                        self.root.after(500, self.refresh_clips)
        except queue.Empty:
            pass
        self.root.after(150, self._drain)

    _IMPORTANT_START = ("▶", "✅", "🔴", "⏹", "👀", "⚠", "❌", "===", T("Есть обновление"), T("Обновлени"), T("Настройки"),
                        T("Список стримеров"), T("Очередь"), T("Вебка"), T("Для "), T("Останавлива"), "Telegram", T("Клипы будут"))
    _IMPORTANT_HAS = (T("ОШИБКА"), T("не смог"), T("не получил"), T("ошибка"), T("нет связи"), T("не бот"), T("не найден"),
                      T("не сработает"), T("не получились"), T("продолжаю с того места"))

    def _is_important(self, line: str) -> bool:
        t = line.strip()
        if not t:
            return False
        return t.startswith(self._IMPORTANT_START) or any(k in t for k in self._IMPORTANT_HAS)

    def _append(self, text: str, important: bool = True):
        self.log_lines.append((text, important))
        if len(self.log_lines) > 6000:
            self.log_lines = self.log_lines[-4000:]
        if important or self.log_detailed.get():
            self.log.config(state="normal")
            self.log.insert("end", text if text.endswith("\n") or not important else text)
            self.log.see("end")
            self.log.config(state="disabled")
        if text.strip() and important:
            self.status.config(text=text.strip().splitlines()[-1][:120])

    def _toggle_log(self):
        """Свернуть / развернуть окно «Что происходит» (последнее событие всё равно видно внизу)."""
        hidden = self.log.winfo_ismapped()
        if hidden:
            self.log.pack_forget()
            self.logf.pack_configure(fill="x", expand=False)
            self.b_hide_log.config(text=T("Показать ▾"))
        else:
            self.log.pack(fill="both", expand=True)
            self.logf.pack_configure(fill="both", expand=True)
            self.b_hide_log.config(text=T("Скрыть ▴"))
        self.cfg["log_hidden"] = hidden
        try:
            data = _load_json(SETTINGS, DEFAULTS)
            data["log_hidden"] = hidden
            with open(SETTINGS, "w", encoding="utf-8") as f:
                json.dump(_ru(data), f, ensure_ascii=False, indent=1)
        except OSError:
            pass

    def _toggle_details(self):
        self.log_detailed.set(not self.log_detailed.get())
        self.b_details.config(text=T("Коротко ▴") if self.log_detailed.get() else T("Подробнее ▾"))
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        for text, important in self.log_lines:
            if important or self.log_detailed.get():
                self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")

    def _set_running(self, running: bool, what: str = ""):
        self.b_watch.config(state="disabled" if running else "normal")
        self.b_vod.config(state="disabled" if running else "normal")
        self.b_stop.config(state="normal" if running else "disabled")
        if running:
            self.status.config(text=what)

    # ---------- обновления ----------
    def check_updates(self, manual: bool = False):
        if os.environ.get("STREAM_CLIPPER_NO_UPDATE"):  # для проверок разработчика
            return
        def work():
            try:
                info = updater.check()
            except Exception as e:
                info, err = None, e
            else:
                err = None
            self.root.after(0, lambda: self._on_update_info(info, err, manual))
        threading.Thread(target=work, daemon=True).start()
        if not manual:
            self.root.after(3 * 3600 * 1000, self.check_updates)  # и потом каждые 3 часа

    def _on_update_info(self, info, err, manual):
        if err:
            if manual:
                messagebox.showwarning(T("Обновление"), T('Не удалось проверить обновления (интернет/VPN?):\n{0}').format(err))
            return
        if not info:
            if manual:
                messagebox.showinfo(T("Обновление"), T("У тебя последняя версия."))
            return
        self.pending_update = info
        if self.v["autoupdate"].get():
            self.install_update(auto=True)  # и во время работы: она продолжится после перезапуска
            return
        self.update_label.config(text=T('Доступна новая версия программы (от {0})').format(info['date']))
        self.update_bar.pack(side="top", fill="x", before=self.nb)

    def install_update(self, auto: bool = False):
        info = self.pending_update
        if not info or self.updating:
            return
        recs = paths.recordings_active() if self.proc else []
        if auto and recs:
            # идёт запись YouTube-эфира: перезапуск дал бы дыру в записи — ждём конца эфира
            self.update_label.config(text=T('Новая версия ждёт конца записи эфира ({0})').format(', '.join(recs)[:40]))
            self.update_bar.pack(side="top", fill="x", before=self.nb)
            if not getattr(self, "_deferred_logged", False):
                self._append(T("Есть обновление, но сейчас идёт запись эфира — поставлю его, когда эфир закончится.\n"))
                self._deferred_logged = True
            self.root.after(3 * 60 * 1000, lambda: self.install_update(auto=True))
            return
        self._deferred_logged = False
        self.updating = True
        self._save_settings()
        self._append(T('\n=== Обновляю программу (версия от {0}) ===\n').format(info['date']))
        self.update_bar.pack_forget()

        def work():
            try:
                changed = updater.apply(info["sha"], log=lambda m: self.lines.put(m + "\n"))
            except Exception as e:
                self.lines.put(T('Обновление не удалось: {0}\n').format(e))
                self.updating = False
                return
            self.root.after(0, lambda: self._after_files_updated(changed))
        threading.Thread(target=work, daemon=True).start()

    def _after_files_updated(self, changed=None):
        changed = changed if changed is not None else ["stream_clipper/gui.py"]
        self.pending_update = None
        if not updater.needs_window_restart(changed):
            # поменялась только «рабочая» часть — окно не трогаем
            self.updating = False
            if not changed:
                self._append(T("Обновление установлено (менять ничего не пришлось).\n"))
            elif self.proc:
                self.restart_worker = True
                self._append(T("Обновление установлено. Перезапускаю только рабочую часть "
                             "(окно не закрывается, работа продолжится сама)...\n"))
                try:
                    open(paths.stop_request_path(), "w").close()
                except OSError:
                    pass
            else:
                self._append(T("Обновление установлено — окно перезапускать не нужно.\n"))
            return
        if not self.proc:
            self._restart()
            return
        # идёт работа: запоминаем её, аккуратно останавливаем (начатое дорежется), потом перезапуск
        try:
            with open(RESUME, "w", encoding="utf-8") as f:
                json.dump(self.job or ["watch"], f)
        except OSError:
            pass
        self._append(T("Аккуратно останавливаю работу (дорезаю начатое) — после перезапуска она продолжится сама...\n"))
        try:
            open(paths.stop_request_path(), "w").close()
        except OSError:
            pass
        self.root.after(10 * 60 * 1000, self._force_stop_if_stuck)

    def _force_stop_if_stuck(self):
        if self.updating and self.proc:
            self._append(T("Работа не остановилась за 10 минут — останавливаю принудительно.\n"))
            self.force_stop()

    def _resume_after_update(self):
        """Продолжить работу — только если окно только что перезапустилось ради обновления/темы.
        Старый файл (например, программа закрылась не до конца) не должен запускать слежку при обычном открытии."""
        try:
            fresh = time.time() - os.path.getmtime(RESUME) < 10 * 60
            with open(RESUME, encoding="utf-8") as f:
                job = json.load(f)
            os.remove(RESUME)
        except Exception:
            return
        if not fresh:
            return
        self._append(T("\n=== Программа обновлена — продолжаю работу с того же места ===\n"))
        if job and job[0] == "vod" and len(job) > 1:
            self.url.set(job[1])
            self.start_vod()
        else:
            self.start_watch()

    def _restart(self):
        self._append(T("Перезапускаю программу...\n"))
        flags = 0x08000000 if os.name == "nt" else 0
        try:
            subprocess.Popen([sys.executable, "-m", "stream_clipper.gui"], cwd=PROG, creationflags=flags)
        except Exception as e:
            messagebox.showinfo(T("Обновление"), T('Обновление установлено. Открой программу заново.\n({0})').format(e))
        self.root.destroy()

    def _on_tab(self, e=None):
        i = self.nb.index(self.nb.select())
        if i == 1:
            self.refresh_clips()
        elif i == 2:
            self.refresh_streams()

    # ---------- вкладка «Стримы»: что уже разобрано и откуда продолжать ----------
    def _build_streams(self, parent):
        self.online_streams: dict = {}   # канал -> список его стримов с сайта (загружается кнопкой)
        self.stream_rows: dict = {}
        bar = ttk.Frame(parent)
        bar.pack(fill="x")
        ttk.Label(bar, text=T("Стример:")).pack(side="left")
        self.st_channel = tk.StringVar(value=T("Все"))
        self.st_box = ttk.Combobox(bar, textvariable=self.st_channel, width=20, state="readonly")
        self.st_box.pack(side="left", padx=4)
        self.st_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_streams())
        ttk.Button(bar, text=T("🔎  Показать все стримы канала"), command=self.load_channel_streams).pack(side="left",
                                                                                                    padx=6)
        ttk.Button(bar, text=T("⟳ Обновить"), command=self.refresh_streams).pack(side="right")
        self.st_info = ttk.Label(parent, text="", anchor="w", foreground=self.muted, wraplength=1100, justify="left")
        self.st_info.pack(side="bottom", fill="x", pady=(6, 0))
        btns = ttk.Frame(parent)
        btns.pack(side="bottom", fill="x")
        ttk.Button(btns, text=T("▶  Продолжить с места остановки"), style="Big.TButton",
                   command=self.continue_stream).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🔗  Открыть стрим на этом месте"), command=self.open_stream).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("✔  Отметить досмотренным"), command=self.mark_stream_done).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🗑  Убрать из списка"), command=self.forget_stream).pack(side="left")
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=6)
        cols = ("date", "title", "link", "length", "done", "left", "clips", "status")
        self.st_tree = ttk.Treeview(frame, columns=cols, show="tree headings", selectmode="browse")
        self.st_tree.heading("#0", text=T("Стример"))
        self.st_tree.column("#0", width=115, stretch=False)
        for c, title, w in (("date", T("Дата стрима"), 100), ("title", T("Название"), 140),
                            ("link", T("Ссылка"), 170), ("length", T("Длина"), 62),
                            ("done", T("Разобрано"), 105), ("left", T("Не разобрано"), 125), ("clips", T("Клипов"), 66),
                            ("status", T("Где остановились"), 215)):
            self.st_tree.heading(c, text=title)
            self.st_tree.column(c, width=w, stretch=(c == "title"),
                                anchor="w" if c in ("title", "status") else "center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.st_tree.yview)
        self.st_tree.configure(yscrollcommand=sb.set)
        self.st_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.st_tree.tag_configure("done", foreground=self.muted)
        self.st_tree.bind("<Double-1>", self._stream_dblclick)
        self.st_tree.bind("<Button-1>", self._stream_click, add="+")
        self.st_tree.bind("<Motion>", self._stream_hover)
        self.st_tree.bind("<Button-3>", self._stream_menu)

    def _stream_at_link(self, e) -> dict | None:
        if self.st_tree.identify_region(e.x, e.y) != "cell" or self.st_tree.identify_column(e.x) != "#3":
            return None
        return self.stream_rows.get(self.st_tree.identify_row(e.y))

    def _stream_click(self, e):
        r = self._stream_at_link(e)
        if r and r.get("url"):
            webbrowser.open(r["url"])
            return "break"

    def _stream_dblclick(self, e):
        if self._stream_at_link(e) is None:
            self.continue_stream()

    def _stream_hover(self, e):
        r = self._stream_at_link(e)
        self.st_tree.configure(cursor="hand2" if r and r.get("url") else "")

    def _stream_menu(self, e):
        iid = self.st_tree.identify_row(e.y)
        r = self.stream_rows.get(iid)
        if not r:
            return
        self.st_tree.selection_set(iid)
        m = tk.Menu(self.root, tearoff=0)
        if r.get("url"):
            m.add_command(label=T("🔗  Открыть стрим"), command=lambda: webbrowser.open(r["url"]))
            m.add_command(label=T("⏩  Открыть на месте остановки"), command=self.open_stream)
            m.add_command(label=T("📋  Копировать ссылку"), command=lambda: self._copy_link(r["url"]))
        m.add_command(label=T("▶  Продолжить с места остановки"), command=self.continue_stream)
        m.tk_popup(e.x_root, e.y_root)

    def _copy_link(self, url: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.st_info.config(text=T("Ссылка скопирована: ") + url)

    # ---------- правила площадок: проверка и исправление нарушений ----------
    def _policy_cell(self, c: dict) -> str:
        res = c.get("policy")
        if not res:
            return "—"
        if res.get("fixed") and not res.get("issues"):
            return T("✔ испр.")
        n = len(res.get("issues") or [])
        return f"⚠ {n}" if n else "✔"

    def fix_violations(self):
        """Окно: что нарушает правила YouTube / TikTok / Instagram, исправление и сравнение «до / после»."""
        from . import policy
        sel = self._selected()
        if not sel:
            return
        c = sel[0]
        old = getattr(self, "policy_window", None)
        if old is not None:
            try:
                old.destroy()
            except tk.TclError:
                pass
        win = tk.Toplevel(self.root)
        win.title(T("Нарушения правил — {0}").format(c.get("channel", "")))
        win.transient(self.root)
        win.geometry("980x720")
        self.policy_window = win
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        sec = int(c.get("moment", c.get("start", 0)))
        ttk.Label(frm, text=f"{c.get('channel', '')}  ·  {sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}  ·  "
                            f"«{(c.get('caption') or '')[:60]}»", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        status = ttk.Label(frm, text="", foreground=self.muted, wraplength=940, justify="left")
        status.pack(anchor="w", pady=(4, 6))
        cols = ("on", "time", "title", "what", "risk", "fix")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=8, selectmode="browse")
        for col, title, w in (("on", "✔", 34), ("time", T("Время"), 90), ("title", T("Нарушение"), 170),
                              ("what", T("Что именно"), 170), ("risk", T("Чем грозит"), 330),
                              ("fix", T("Как исправить (клик — сменить)"), 170)):
            tree.heading(col, text=title)
            tree.column(col, width=w, stretch=col in ("risk", "what"), anchor="center" if col in ("on", "time") else "w")
        tree.pack(fill="x")
        detail = ttk.Label(frm, text="", wraplength=940, justify="left")
        detail.pack(anchor="w", pady=(4, 0))

        def show_detail(e=None):
            sel_ = tree.selection()
            i = state["rows"].get(sel_[0]) if sel_ else None
            if i:
                detail.config(text=T(i["title"]) + " — " + i["what"] + "\n" + "\n".join(
                    f"   • {p}: {T(r)}" for p, r in i.get("platforms", {}).items()))
        tree.bind("<<TreeviewSelect>>", show_detail)
        fix_names = {"bleep": T("🔇 запикать"), "mute": T("🔈 заглушить звук"), "blur": T("🌫 размыть"),
                     "skip": T("— не трогать")}
        fix_cycle = {"speech": ["bleep", "mute", "skip"], "music": ["mute", "skip"], "video": ["blur", "skip"]}
        state = {"issues": [], "rows": {}}

        def fill(res):
            if not win.winfo_exists():
                return
            tree.delete(*tree.get_children())
            state["res"] = res
            state["issues"] = [dict(i) for i in res.get("issues") or []]
            state["rows"] = {}
            for i in state["issues"]:
                i.setdefault("on", i.get("severity") == "high" or i["kind"] in ("profanity",))
                a, b = i["t0"], i["t1"]
                when = T("весь клип") if b > 10 ** 5 else T("{0:.1f}–{1:.1f} с").format(a, b)
                risk = "; ".join(f"{p}: {T(r)}" for p, r in i.get("platforms", {}).items())
                iid = tree.insert("", "end", values=("☑" if i["on"] else "☐", when, T(i["title"]), i["what"],
                                                     risk, fix_names.get(i["fix"], i["fix"])))
                state["rows"][iid] = i
            if state["rows"]:
                tree.selection_set(next(iter(state["rows"])))
                show_detail()
            else:
                detail.config(text="")
            parts = []
            if state["issues"]:
                high = sum(1 for i in state["issues"] if i.get("severity") == "high")
                parts.append(T("Найдено нарушений: {0} (серьёзных: {1}). Отметь, что исправить, и нажми «Исправить».")
                             .format(len(state["issues"]), high))
            else:
                parts.append(T("✔ Нарушений не найдено — клип можно выкладывать."))
            if res.get("fixed"):
                parts.append(T("Этот клип уже исправлен."))
            if res.get("note"):
                parts.append(T("Не проверено: {0}").format("; ".join(tr_line(x) for x in res["note"].split("; "))))
            if not res.get("visual"):
                parts.append(T("Картинку проверяет Claude — нажми «Проверить заново», если есть ключ Claude."))
            status.config(text="  ".join(parts))
            b_fix.config(state="normal" if state["issues"] else "disabled")

        def on_click(e):
            iid = tree.identify_row(e.y)
            i = state["rows"].get(iid)
            if not i:
                return
            col = tree.identify_column(e.x)
            if col == "#1":
                i["on"] = not i["on"]
                tree.set(iid, "on", "☑" if i["on"] else "☐")
            elif col == "#6":
                cyc = fix_cycle["music" if i["kind"] == "music" else i.get("source", "speech")]
                i["fix"] = cyc[(cyc.index(i["fix"]) + 1) % len(cyc)] if i["fix"] in cyc else cyc[0]
                i["on"] = i["fix"] != "skip"
                tree.set(iid, "fix", fix_names[i["fix"]])
                tree.set(iid, "on", "☑" if i["on"] else "☐")
        tree.bind("<Button-1>", on_click)

        def recheck():
            status.config(text=T("Проверяю клип..."))
            from .caption import _api_key

            def work():
                try:
                    res = policy.check_clip(c, _api_key(), log=lambda m: self.root.after(0, lambda: status.config(text=tr_line(m))))
                except Exception as e:
                    res = {"issues": [], "note": f"{type(e).__name__}: {e}"}
                c["policy"] = res
                self.root.after(0, lambda: (fill(res), self.refresh_clips()))
            threading.Thread(target=work, daemon=True).start()

        # --- сравнение до / после ---
        cmp_frame = ttk.Frame(frm)
        players: list = []

        def show_compare(fixed_path):
            for w in cmp_frame.winfo_children():
                w.destroy()
            cmp_frame.pack(fill="both", expand=True, pady=(8, 0))
            row = ttk.Frame(cmp_frame)
            row.pack(fill="both", expand=True)
            for title, path, sound in ((T("ДО (оригинал)"), c["path"], False), (T("ПОСЛЕ (исправлено)"), fixed_path, True)):
                box = ttk.LabelFrame(row, text=f" {title} ", padding=4)
                box.pack(side="left", fill="both", expand=True, padx=4)
                p = VideoPreview(box, self, big=True)
                p.sound.set(sound)
                p.pack(fill="both", expand=True)
                players.append(p)
                win.after(300, lambda p=p, path=path: p.load(path))
            choose = ttk.Frame(cmp_frame)
            choose.pack(fill="x", pady=(6, 0))
            ttk.Button(choose, text=T("✔  Выкладывать исправленную"), style="Big.TButton",
                       command=lambda: keep(fixed_path)).pack(side="left")
            ttk.Button(choose, text=T("↩  Оставить оригинал"), command=lambda: discard(fixed_path)).pack(side="left", padx=6)
            ttk.Label(choose, foreground=self.muted, text=T("Звук включён у правой версии — послушай, где запикано.")
                      ).pack(side="left", padx=6)

        def release_players():
            for p in players:
                p.release()
            players.clear()
            if self.preview.path == c["path"]:
                self.preview.release()

        def keep(fixed_path):
            import shutil
            release_players()
            os.makedirs(policy.originals_dir(), exist_ok=True)
            backup = os.path.join(policy.originals_dir(), f"{int(time.time())}_{os.path.basename(c['path'])}")
            try:
                shutil.move(c["path"], backup)
                shutil.move(fixed_path, c["path"])
            except OSError as e:
                messagebox.showerror(T("Нарушения"), T("Не получилось заменить файл: {0}").format(e), parent=win)
                return
            try:
                os.remove(library.thumb_path(c["path"]))
            except OSError:
                pass
            self.images.pop(c["path"], None)
            left = [i for i in state["issues"] if not i.get("on")]
            res = dict(c.get("policy") or {}, issues=left, fixed=True, original=backup)
            policy.save_result(c["path"], res)
            win.destroy()
            self.policy_window = None
            self.refresh_clips()
            self.clips_info.config(text=T("Готово: в папке теперь исправленная версия. Оригинал сохранён: {0}").format(backup))

        def discard(fixed_path):
            release_players()
            try:
                os.remove(fixed_path)
            except OSError:
                pass
            for w in cmp_frame.winfo_children():
                w.destroy()
            cmp_frame.pack_forget()
            status.config(text=T("Оставлен оригинал."))

        def do_fix():
            chosen = [dict(i) for i in state["issues"] if i.get("on") and i.get("fix") != "skip"]
            if not chosen:
                messagebox.showinfo(T("Нарушения"), T("Отметь хотя бы одно нарушение (колонка ✔)."), parent=win)
                return
            status.config(text=T("Исправляю клип... (полминуты)"))
            b_fix.config(state="disabled")
            out_dir = os.path.join(paths.default_work_dir(), "fixed")
            os.makedirs(out_dir, exist_ok=True)
            out = os.path.join(out_dir, "fixed_" + os.path.basename(c["path"]))

            def work():
                try:
                    words = c.get("words") or (c.get("policy") or {}).get("words") or []
                    policy.fix_clip(c["path"], out, chosen, subs_burned=bool(c.get("transcript") or words),
                                    words=words)
                    err = None
                except Exception as e:
                    err = e
                self.root.after(0, lambda: done(err))

            def done(err):
                if not win.winfo_exists():
                    return
                b_fix.config(state="normal")
                if err:
                    status.config(text=T("Исправить не получилось: {0}").format(err))
                    return
                status.config(text=T("Готово. Сравни: слева как было, справа исправленная. Выбери, что выкладывать."))
                show_compare(out)
            threading.Thread(target=work, daemon=True).start()

        bar = ttk.Frame(frm)
        bar.pack(fill="x", pady=(8, 0))
        b_fix = ttk.Button(bar, text=T("🛠  Исправить отмеченное"), style="Big.TButton", command=do_fix)
        b_fix.pack(side="left")
        ttk.Button(bar, text=T("🔎  Проверить заново"), command=recheck).pack(side="left", padx=6)

        def add_manual(issue):
            res = dict(state.get("res") or {}, issues=state["issues"] + [issue])
            fill(res)
            status.config(text=T("Добавлено ручное размытие. Нажми «Исправить отмеченное»."))
        ttk.Button(bar, text=T("✏  Размыть вручную"),
                   command=lambda: self._manual_blur(win, c["path"], add_manual)).pack(side="left")
        ttk.Button(bar, text=T("Закрыть"), command=lambda: (release_players(), win.destroy())).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", lambda: (release_players(), win.destroy()))
        res = c.get("policy") or policy.load_results().get(os.path.normpath(c["path"]))
        if res and (res.get("issues") or res.get("visual") or res.get("words")):
            fill(res)
        else:
            fill({"issues": [], "note": ""})
            recheck()

    def _manual_blur(self, parent, clip_path: str, on_add):
        """Ручное размытие: двигаешь ползунок до нужного кадра, обводишь мышкой область, ставишь «с» и «по»."""
        import cv2
        cap = cv2.VideoCapture(clip_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        dur = (cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0) / fps or 30.0
        win = tk.Toplevel(parent)
        win.title(T("Размыть вручную"))
        win.transient(parent)
        W, H = 360, 640
        top = ttk.Frame(win, padding=8)
        top.pack(fill="both", expand=True)
        ttk.Label(top, wraplength=360, justify="left", text=T(
            "1) Ползунком найди кадр с нарушением.  2) Обведи мышкой, что размыть (без рамки — весь кадр).  "
            "3) Поставь начало и конец.  4) «Добавить».")).pack(anchor="w")
        cv = tk.Canvas(top, width=W, height=H, cursor="crosshair", highlightthickness=0, bg="#000000")
        cv.pack(pady=6)
        st = {"img": None, "rect": None, "box": None, "t0": None, "t1": None, "x": 0, "y": 0}
        pos = tk.DoubleVar(value=0.0)
        info = ttk.Label(top, text="")
        info.pack(anchor="w")

        def show(*_):
            cap.set(cv2.CAP_PROP_POS_MSEC, pos.get() * 1000)
            ok, frame = cap.read()
            if not ok:
                return
            small = cv2.resize(frame, (W, H), interpolation=cv2.INTER_AREA)
            ok, buf = cv2.imencode(".ppm", small)
            st["img"] = tk.PhotoImage(data=buf.tobytes(), format="PPM")
            cv.delete("frame")
            cv.create_image(0, 0, image=st["img"], anchor="nw", tags="frame")
            cv.tag_lower("frame")
            upd()

        def upd():
            t0, t1 = st["t0"], st["t1"]
            info.config(text=T("Кадр: {0:.1f} с   ·   с: {1}   по: {2}   ·   {3}").format(
                pos.get(), "—" if t0 is None else f"{t0:.1f}", "—" if t1 is None else f"{t1:.1f}",
                T("область выбрана") if st["box"] else T("весь кадр")))

        def press(e):
            st["x"], st["y"] = e.x, e.y
            if st["rect"]:
                cv.delete(st["rect"])
            st["rect"] = cv.create_rectangle(e.x, e.y, e.x, e.y, outline="#ff3b30", width=3)

        def drag(e):
            cv.coords(st["rect"], st["x"], st["y"], e.x, e.y)

        def release(e):
            x0, x1 = sorted((max(0, min(W, st["x"])), max(0, min(W, e.x))))
            y0, y1 = sorted((max(0, min(H, st["y"])), max(0, min(H, e.y))))
            st["box"] = [x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H] if x1 - x0 > 6 and y1 - y0 > 6 else None
            if not st["box"] and st["rect"]:
                cv.delete(st["rect"])
                st["rect"] = None
            upd()
        cv.bind("<ButtonPress-1>", press)
        cv.bind("<B1-Motion>", drag)
        cv.bind("<ButtonRelease-1>", release)
        ttk.Scale(top, from_=0, to=max(0.1, dur - 0.05), variable=pos, orient="horizontal", length=W,
                  command=lambda v: show()).pack(fill="x")
        row = ttk.Frame(top)
        row.pack(fill="x", pady=4)

        def mark(which):
            st[which] = round(pos.get(), 2)
            upd()
        ttk.Button(row, text=T("⏮ Начало здесь"), command=lambda: mark("t0")).pack(side="left")
        ttk.Button(row, text=T("Конец здесь ⏭"), command=lambda: mark("t1")).pack(side="left", padx=6)

        def add():
            t0 = st["t0"] if st["t0"] is not None else max(0.0, pos.get() - 1)
            t1 = st["t1"] if st["t1"] is not None else min(dur, pos.get() + 1)
            if t1 <= t0:
                t0, t1 = t1, t0
            from . import policy
            issue = policy._issue("manual", t0, t1 if t1 > t0 else t0 + 0.5, T("отмечено вручную"), st["box"],
                                  source="video")
            issue["on"] = True
            cap.release()
            win.destroy()
            on_add(issue)
        bar = ttk.Frame(top)
        bar.pack(fill="x", pady=(6, 0))
        ttk.Button(bar, text=T("➕  Добавить"), style="Big.TButton", command=add).pack(side="left")
        ttk.Button(bar, text=T("Отмена"), command=lambda: (cap.release(), win.destroy())).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", lambda: (cap.release(), win.destroy()))
        self.manual_window = win  # для проверок
        win.after(100, show)

    def _stream_rows(self) -> dict:
        """Все известные стримы по каналам: из памяти программы + загруженные с сайта."""
        from . import progress
        data = progress.load()
        rows: dict = {}  # канал(lower) -> {key: row}
        # эфир, который программа писала сама (у Twitch), — это тот же стрим, что и его запись (VOD)
        merged_into: dict = {}
        for k in [k for k in data if k.startswith("tw-live:")]:
            e = data[k]
            ch = e.get("channel", "").lower()
            others = [(o, data[o]) for o in data if not o.startswith("tw-live:")]
            others += [(v["key"], {"channel": e.get("channel"), "stream_ts": v.get("ts")})
                       for v in self.online_streams.get(ch, [])]
            for o, oe in others:
                if oe.get("channel", "").lower() == ch and oe.get("stream_ts") and e.get("stream_ts") \
                        and abs(float(oe["stream_ts"]) - float(e["stream_ts"])) < 1800:
                    merged_into[k] = o
                    break
        for k, e in data.items():
            if k not in merged_into:
                rows.setdefault(e.get("channel", "?").lower(), {})[k] = dict(e, key=k)
        for ch, vods in self.online_streams.items():
            for v in vods:
                r = rows.setdefault(ch, {}).get(v["key"])
                if r is None:
                    rows[ch][v["key"]] = {"key": v["key"], "channel": v.get("channel", ch), "title": v["title"],
                                          "url": v["url"], "duration": v["duration"], "stream_ts": v.get("ts"),
                                          "platform": v.get("platform", ""), "ranges": [], "clips": 0}
                else:
                    r["duration"] = max(float(r.get("duration") or 0), v["duration"])
                    r["url"] = v["url"]
                    r["stream_ts"] = r.get("stream_ts") or v.get("ts")
        for k, target in merged_into.items():
            e = data[k]
            ch = e.get("channel", "?").lower()
            r = rows.setdefault(ch, {}).setdefault(target, {"key": target, "channel": e.get("channel"),
                                                              "url": "", "ranges": [], "clips": 0})
            r["ranges"] = list(r.get("ranges") or []) + list(e.get("ranges") or [])
            r["clips"] = int(r.get("clips") or 0) + int(e.get("clips") or 0)
            r["title"] = r.get("title") or e.get("title", "")
            r["stream_ts"] = r.get("stream_ts") or e.get("stream_ts")
            r["live"] = r.get("live") or e.get("live")
            r["duration"] = max(float(r.get("duration") or 0), float(e.get("duration") or 0))
        return rows

    def refresh_streams(self):
        from . import progress
        from datetime import datetime
        rows = self._stream_rows()
        names = {ch: next((r.get("channel") for r in items.values() if r.get("channel")), ch)
                 for ch, items in rows.items()}
        known = [n.lstrip("@") for n in self._read_streamers()]
        self.st_box.config(values=[T("Все"), *sorted({*names.values(), *known}, key=str.lower)])
        want = self.st_channel.get()
        sel = self.st_tree.selection()
        sel_key = self.stream_rows.get(sel[0], {}).get("key") if sel else None
        self.st_tree.delete(*self.st_tree.get_children())
        self.stream_rows = {}
        unfinished = 0
        for ch in sorted(rows, key=lambda c: names[c].lower()):
            if want != T("Все") and names[ch].lower().lstrip("@") != want.lower().lstrip("@"):
                continue
            items = sorted(rows[ch].values(), key=lambda r: -(r.get("stream_ts") or r.get("updated") or 0))
            parent = self.st_tree.insert("", "end", text=names[ch], open=True,
                                         values=("", T('стримов: {0}').format(len(items)), "", "", "", "", "", ""))
            for r in items:
                sm = progress.summary(r)
                if r.get("live") and r.get("ranges"):
                    status = T("🔴 эфир идёт, разбираю")
                elif sm["finished"]:
                    status = T("✔ досмотрен")
                elif not r.get("ranges"):
                    status = T("— ещё не смотрели")
                elif not sm["resume"] and sm["gaps"]:
                    status = T('⏸ не разобрано начало (до {0})').format(progress.fmt(sm['gaps'][0][1]))
                else:
                    status = T('⏸ остановились на {0}').format(progress.fmt(sm['resume'] or 0))
                if not sm["finished"]:
                    unfinished += 1
                ts = r.get("stream_ts")
                date = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M") if ts else "—"
                dur = float(r.get("duration") or 0)
                iid = self.st_tree.insert(parent, "end", text="", tags=("done",) if sm["finished"] else (),
                                          values=(date, r.get("title") or "—", _short_url(r.get("url") or ""),
                                                  progress.fmt(dur) if dur else "?",
                                                  sm["done"], "—" if sm["finished"] else sm["gaps_txt"],
                                                  r.get("clips") or 0, status))
                self.stream_rows[iid] = dict(r, summary=sm)
                if r.get("key") == sel_key:
                    self.st_tree.selection_set(iid)
        if not self.stream_rows:
            self.st_info.config(text=T("Тут появятся стримы, которые программа разбирала: какой кусок уже просмотрен и "
                                     "откуда продолжать. Выбери стримера и нажми «Показать все стримы канала», чтобы "
                                     "увидеть и те, что ещё не смотрели."))
        else:
            self.st_info.config(text=T('Не досмотрено стримов: {0}.  «Разобрано» — какие часы стрима программа уже проверила, «Не разобрано» — что осталось. Выбери стрим и нажми «Продолжить» — анализ начнётся ровно с места остановки.').format(unfinished))

    def load_channel_streams(self):
        """Тянем с сайта последние стримы выбранного канала — чтобы видеть и те, что ещё не разбирали."""
        from . import progress
        name = self.st_channel.get()
        if name in ("", T("Все")):
            messagebox.showinfo(T("Стримы"), T("Сначала выбери стримера в списке «Стример»."))
            return
        tw, yt = split_platforms(self._read_streamers())
        plat = next((e.get("platform") for e in progress.load().values()
                     if e.get("channel", "").lower() == name.lower()), "")
        bare = name.lower().lstrip("@")
        if bare in {n.lower() for n in tw}:
            kind, target = "twitch", name
        elif bare in {n.lower().lstrip("@") for n in yt}:
            kind, target = "youtube", next(n for n in yt if n.lower().lstrip("@") == bare)
        else:
            kind, target = ("youtube", "@" + name.lstrip("@")) if plat == "YouTube" else ("twitch", name)
        self.st_info.config(text=T('Загружаю список стримов {0}...').format(name))

        def work():
            from . import twitch
            try:
                vods, err = twitch.list_streams(kind, target), None
            except Exception as e:
                vods, err = [], e
            for v in vods:
                v["channel"], v["platform"] = name, "YouTube" if kind == "youtube" else "Twitch"
            self.root.after(0, lambda: done(vods, err))

        def done(vods, err):
            if err is not None:
                self.st_info.config(text=T('Не получилось загрузить стримы {0}: {1}').format(name, err))
                return
            self.online_streams[name.lower()] = vods
            self.refresh_streams()
            self.st_info.config(text=T('{0}: найдено записей стримов — {1}. Те, что ещё не смотрели, отмечены «— ещё не смотрели».').format(name, len(vods)))
        threading.Thread(target=work, daemon=True).start()

    def _stream_selected(self) -> dict | None:
        sel = self.st_tree.selection()
        r = self.stream_rows.get(sel[0]) if sel else None
        if r is None:
            messagebox.showinfo(T("Стримы"), T("Выбери стрим в списке (строку под именем стримера)."))
        return r

    def continue_stream(self):
        r = self._stream_selected()
        if not r:
            return
        sm = r["summary"]
        url = r.get("url") or ""
        if not any(p in url for p in ("/videos/", "watch?v=", "youtu.be/")):
            messagebox.showinfo(T("Стримы"), T("У этого эфира нет сохранённой записи (стример её не оставил), продолжить "
                                          "нельзя. Нажми «Показать все стримы канала» — если запись появилась, "
                                          "она подтянется сюда."))
            return
        if sm["finished"]:
            if not messagebox.askyesno(T("Стримы"), T("Этот стрим уже разобран целиком. Пройти его ещё раз с начала?")):
                return
            start = 0
        else:
            start = sm["resume"] or 0
        if self.proc:
            messagebox.showinfo(T("Стримы"), T("Сейчас программа уже работает. Нажми «Стоп», потом «Продолжить»."))
            return
        self.url.set(url)
        self.v["start_from"].set(T("с начала") if start < 60 else f"{int(start // 3600)}:{int(start % 3600 // 60):02d}")
        self.v["start_mode"].set(T("от начала стрима"))
        self.nb.select(0)
        self.start_vod()

    def open_stream(self):
        r = self._stream_selected()
        if not r or not r.get("url"):
            return
        t = int(r["summary"]["resume"] or 0)
        url = r["url"]
        if t:
            if "twitch.tv/videos/" in url:
                url += f"?t={t // 3600}h{t % 3600 // 60}m{t % 60}s"
            elif "watch?v=" in url:
                url += f"&t={t}s"
        webbrowser.open(url)

    def mark_stream_done(self):
        from . import progress
        r = self._stream_selected()
        if not r:
            return
        if not r.get("duration"):
            messagebox.showinfo(T("Стримы"), T("Длина этого стрима неизвестна — нажми «Показать все стримы канала»."))
            return
        progress.record(r["key"], 0, float(r["duration"]), channel=r.get("channel", ""),
                        platform=r.get("platform", ""), title=r.get("title", ""), url=r.get("url", ""),
                        stream_ts=r.get("stream_ts"), duration=float(r["duration"]))
        self.refresh_streams()

    def forget_stream(self):
        from . import progress
        r = self._stream_selected()
        if r and messagebox.askyesno(T("Стримы"), T("Убрать этот стрим из списка? Клипы не удалятся — программа просто "
                                               "забудет, какой кусок разобран.")):
            progress.forget(r["key"])
            for vods in self.online_streams.values():
                vods[:] = [v for v in vods if v["key"] != r["key"]]
            self.refresh_streams()

    # ---------- вкладка «Клипы» ----------
    def _build_clips(self, parent):
        self.images: dict = {}
        bar = ttk.Frame(parent)
        bar.pack(fill="x")
        ttk.Label(bar, text=T("Дата:")).pack(side="left")
        self.date_var = tk.StringVar()
        self.date_box = ttk.Combobox(bar, textvariable=self.date_var, width=12, state="readonly")
        self.date_box.pack(side="left", padx=(4, 12))
        self.date_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_clips())
        ttk.Label(bar, text=T("Стример:")).pack(side="left")
        self.streamer_var = tk.StringVar(value=T("Все"))
        self.streamer_box = ttk.Combobox(bar, textvariable=self.streamer_var, width=16, state="readonly")
        self.streamer_box.pack(side="left", padx=(4, 12))
        self.streamer_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_clips())
        ttk.Label(bar, text=T("Показать:")).pack(side="left")
        self.show_var = tk.StringVar(value=SHOW_ALL)
        show_box = ttk.Combobox(bar, textvariable=self.show_var, values=list(SHOW_FILTERS), width=20,
                                state="readonly")
        show_box.pack(side="left", padx=4)
        show_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_clips())
        ttk.Button(bar, text=T("⟳ Обновить"), command=self.refresh_clips).pack(side="right")
        self.sort_var = tk.StringVar(value=T("лучшие сверху"))
        sort_box = ttk.Combobox(bar, textvariable=self.sort_var, values=[T("лучшие сверху"), T("новые сверху")],
                                width=14, state="readonly")
        sort_box.pack(side="right", padx=6)
        sort_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_clips())
        ttk.Label(bar, text=T("Порядок:")).pack(side="right")

        style = ttk.Style()
        style.configure("Clips.Treeview", rowheight=70, font=("Segoe UI", 10))
        style.configure("Clips.Treeview.Heading", font=("Segoe UI", 10, "bold"))
        # кнопки и подпись закрепляем внизу, список занимает остальное место
        self.clips_info = ttk.Label(parent, text="", anchor="w", foreground=self.muted)
        self.clips_info.pack(side="bottom", fill="x", pady=(6, 0))
        btns = ttk.Frame(parent)
        btns.pack(side="bottom", fill="x")
        pub_mb = ttk.Menubutton(btns, text=T("🚀  Выложить"), style="Big.TMenubutton")
        pub = tk.Menu(pub_mb, tearoff=0)
        for key, label in library.PLATFORM_NAMES.items():
            pub.add_command(label=T('в {0}').format(label), command=lambda k=key: self.publish(k))
        pub_mb["menu"] = pub
        pub_mb.pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🛠  Исправить нарушение"), command=self.fix_violations).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("☑  Выбрать все"), command=self.select_all_clips).pack(side="left", padx=(0, 6))

        ttk.Button(btns, text=T("✍  Описание и хэштеги"),
                   command=self.post_texts).pack(side="left", padx=(0, 6))
        posted_mb = ttk.Menubutton(btns, text=T("✔  Отметить: выложено в…"))
        pm = tk.Menu(posted_mb, tearoff=0)
        for key, label in library.PLATFORM_NAMES.items():
            pm.add_command(label=T('{0} — выложено / снять отметку').format(label), command=lambda k=key: self.toggle_posted(k))
        posted_mb["menu"] = pm
        posted_mb.pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🗑  Удалить"), command=self.delete_clip).pack(side="left", padx=(0, 6))
        more = ttk.Menubutton(btns, text=T("Ещё ▾"))
        mm = tk.Menu(more, tearoff=0)
        mm.add_command(label=T("▶  Открыть в отдельном плеере"), command=self.play_clip)
        mm.add_command(label=T("📋  Копировать надпись"), command=self.copy_caption)
        mm.add_command(label=T("📂  Показать в папке"), command=self.reveal_clip)
        mm.add_command(label=T("🎥  Указать вебку этого стримера"), command=self.pick_facecam)
        more["menu"] = mm
        more.pack(side="left")
        panes = ttk.Panedwindow(parent, orient="horizontal")  # разделитель можно тянуть мышкой
        panes.pack(fill="both", expand=True, pady=6)
        frame = ttk.Frame(panes)
        self.preview = VideoPreview(panes, self)  # просмотр клипа прямо в программе
        panes.add(frame, weight=3)
        panes.add(self.preview, weight=2)
        cols = ("rating", "rules", "streamer", "moment", "caption", "youtube", "instagram", "tiktok")
        self.tree = ttk.Treeview(frame, columns=cols, show="tree headings", style="Clips.Treeview",
                                 selectmode="extended", height=3)
        self.tree.heading("#0", text=T("Превью"))
        self.tree.column("#0", width=66, stretch=False)
        for c, title, w in (("rating", T("Интерес"), 70), ("rules", T("Правила"), 64), ("streamer", T("Стример"), 96), ("moment", T("Момент"), 64),
                            ("caption", T("Надпись"), 220), ("youtube", "YT", 40), ("instagram", "Inst", 44),
                            ("tiktok", "TikTok", 50)):
            self.tree.heading(c, text=title)
            self.tree.column(c, width=w, stretch=(c == "caption"), anchor="w" if c == "caption" else "center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.preview.play_selected())
        self.tree.bind("<Return>", lambda e: self.preview.play_selected())
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.preview.show_selected())
        self.tree.bind("<Delete>", lambda e: self.delete_clip())
        self.tree.bind("<Button-3>", self._clips_menu)
        self.clip_by_iid: dict = {}
        self.root.after(1000, self._auto_refresh)

    def _auto_refresh(self):
        if self.nb.index(self.nb.select()) == 1:
            self.refresh_clips()
        self.root.after(20000, self._auto_refresh)

    def refresh_clips(self):
        dates = library.list_dates()
        self.date_box.config(values=[T("Все дни"), *dates])
        if self.date_var.get() not in [T("Все дни"), *dates]:
            self.date_var.set(T("Все дни"))
        date = self.date_var.get()
        if date == T("Все дни"):
            clips = [c for d in dates for c in library.list_clips(d)]
        else:
            clips = library.list_clips(date) if date else []
        names = sorted({c.get("channel", "") for c in clips})
        self.streamer_box.config(values=[T("Все"), *names])
        if self.streamer_var.get() not in [T("Все"), *names]:
            self.streamer_var.set(T("Все"))
        sel_paths = {self.clip_by_iid[i]["path"] for i in self.tree.selection() if i in self.clip_by_iid}
        self.tree.delete(*self.tree.get_children())
        self.clip_by_iid = {}
        missing = []
        shown = 0
        from .caption import display_ratings
        # оценка — в сравнении со ВСЕМИ твоими клипами (а не только показанными), чтобы она не скакала
        pool = clips if date == T("Все дни") else [c for d in dates for c in library.list_clips(d)]
        scores = display_ratings(pool or clips)
        from . import policy
        pol_results = policy.load_results()
        for c in clips:
            c["score10"] = scores.get(c["path"], 1)
            c["policy"] = pol_results.get(os.path.normpath(c["path"]))
        ranked = sorted(clips, key=lambda c: -c["score10"])
        if self.sort_var.get() == T("лучшие сверху"):
            clips = ranked
        for c in clips:
            if self.streamer_var.get() != T("Все") and c.get("channel") != self.streamer_var.get():
                continue
            need = SHOW_FILTERS.get(self.show_var.get())
            if need == "nowhere" and any(c["posted"].get(p) for p in library.PLATFORMS):
                continue
            if need in library.PLATFORMS and c["posted"].get(need):
                continue
            if need == "violations" and not (c.get("policy") or {}).get("issues"):
                continue
            img = self._thumb(c["path"])
            if img is None:
                missing.append(c["path"])
            sec = int(c.get("moment", c.get("start", 0)))
            values = (f"{c['score10']}/10", self._policy_cell(c), c.get("channel", ""),
                      f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}", c.get("caption", "") or "—",
                      *("✔" if c["posted"].get(p) else "—" for p in library.PLATFORMS))
            iid = self.tree.insert("", "end", text="", image=img or "", values=values)
            self.clip_by_iid[iid] = c
            if c["path"] in sel_paths:
                self.tree.selection_add(iid)
            shown += 1
        fresh = sum(1 for c in clips if not any(c["posted"].values()))
        where = T("всего") if date == T("Все дни") else T('за {0}').format(date)
        self.clips_info.config(text=T('Клипов {0}: {1}, нигде не выложено: {2}.  Интерес 1–10 — в сравнении со всеми твоими клипами.  Клик — посмотреть справа.').format(where, len(clips), fresh))
        self.nb.tab(1, text=T('  Клипы ({0} новых)  ').format(fresh) if clips else T("  Клипы  "))
        if missing:
            threading.Thread(target=self._make_thumbs, args=(missing,), daemon=True).start()

    def _thumb(self, path: str):
        if path in self.images:
            return self.images[path]
        tp = library.thumb_path(path)
        if not os.path.exists(tp):
            return None
        try:
            img = tk.PhotoImage(file=tp)
            if img.height() > 80:
                img = img.subsample(2)  # компактный список: превью вдвое меньше
        except Exception:
            return None
        self.images[path] = img
        return img

    def _make_thumbs(self, paths_: list[str]):
        made = False
        for p in paths_:
            if library.make_thumb(p):
                made = True
        if made:
            self.root.after(0, self.refresh_clips)

    def _selected(self) -> list[dict]:
        sel = [self.clip_by_iid[i] for i in self.tree.selection() if i in self.clip_by_iid]
        if not sel:
            messagebox.showinfo(T("Клипы"), T("Сначала выбери клип в списке."))
        return sel

    def play_clip(self):
        for c in self._selected()[:1]:
            self._open(c["path"])

    def copy_caption(self):
        sel = self._selected()
        if sel:
            text = "\n".join(c.get("caption", "") for c in sel if c.get("caption"))
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.clips_info.config(text=T("Надпись скопирована — вставь её в название ролика (Ctrl+V)."))

    def toggle_posted(self, platform: str = "youtube"):
        sel = self._selected()
        if sel:
            value = not all(c["posted"].get(platform) for c in sel)
            for c in sel:
                library.set_posted(c["path"], value, platform)
            name = library.PLATFORM_NAMES.get(platform, platform)
            self.refresh_clips()
            self.clips_info.config(text=T('{0}: {1} ({2} шт.)').format(name, 'отмечено как выложенное' if value else 'отметка снята', len(sel)))

    def select_all_clips(self):
        kids = self.tree.get_children()
        if kids:
            self.tree.selection_set(kids)

    def _next_unposted(self, platform: str, skip: set) -> tuple[str, dict] | tuple[None, None]:
        """Первый клип в списке (в его текущем порядке — лучшие сверху), ещё не выложенный на площадку."""
        for iid in self.tree.get_children():
            c = self.clip_by_iid.get(iid)
            if c and not c["posted"].get(platform) and c["path"] not in skip:
                return iid, c
        return None, None

    def publish(self, platform: str, clip: dict | None = None):
        """Выкладка в пару кликов: файл сам кладётся в папку «К загрузке» (там больше ничего нет),
        открывается страница загрузки, рядом — готовые название, описание и хэштеги."""
        name = library.PLATFORM_NAMES[platform]
        if clip is None:
            sel = [self.clip_by_iid[i] for i in self.tree.selection() if i in self.clip_by_iid]
            if sel:
                clip = sel[0]
            else:
                self.show_var.set(SHOW_FOR[platform])
                self.refresh_clips()
                iid, clip = self._next_unposted(platform, set())
                if clip is None:
                    messagebox.showinfo(T("Выложить"), T('Все клипы уже выложены в {0} 🎉').format(name))
                    return
                self.tree.selection_set(iid)
                self.tree.see(iid)
        try:
            staged = library.stage_for_upload(clip)
        except OSError as e:
            messagebox.showerror(T("Выложить"), T('Не получилось подготовить файл: {0}').format(e))
            return
        opened = getattr(self, "_publish_opened", set())
        self._publish_opened = opened
        auto = platform == "youtube" and self.cfg.get("yt_auto", True)
        if not auto:
            self._open_manual_upload(platform)
        self.post_texts(clip, platform, staged, auto=auto)

    def _open_manual_upload(self, platform: str, force: bool = False):
        """Ручной способ: страница загрузки в обычном браузере + окно папки «К загрузке» (по разу за сеанс)."""
        opened = self._publish_opened
        if force or "folder" not in opened:  # окно папки открываем один раз — дальше файл в нём просто меняется
            opened.add("folder")
            self._open(library.upload_dir())
        if force or platform not in opened:
            opened.add(platform)
            webbrowser.open(library.UPLOAD_PAGES[platform])

    def post_texts(self, clip: dict | None = None, platform: str | None = None, staged: str = "",
                   auto: bool = False):
        """Окно с описанием и хэштегами для выбранного клипа (YouTube / Instagram / TikTok)."""
        from . import caption as cap
        if clip is None:
            sel = self._selected()
            if not sel:
                return
            clip = sel[0]
        c = clip
        old = getattr(self, "post_window", None)
        if old is not None:
            try:
                old.destroy()
            except tk.TclError:
                pass
        lang = c.get("lang") or ("ru" if any("а" <= ch.lower() <= "я" for ch in (c.get("caption") or "")) else "en")
        win = tk.Toplevel(self.root)
        pname = library.PLATFORM_NAMES.get(platform or "", "")
        win.title(T('Выложить в {0} — {1}').format(pname, c.get('channel', '')) if platform
                  else T('Описание и хэштеги — {0}').format(c.get('channel', '')))
        win.transient(self.root)
        win.geometry("660x650" if platform else "620x470")
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        if platform:
            sec = int(c.get("moment", c.get("start", 0)))
            ttk.Label(frm, text=T('{0}  ·  интерес {1}/10  ·  момент {2}:{3:02d}:{4:02d}').format(c.get('channel', ''), c.get('score10', '?'), sec // 3600, sec % 3600 // 60, sec % 60),
                      font=("Segoe UI", 12, "bold")).pack(anchor="w")
            ttk.Label(frm, wraplength=620, justify="left", text=(
                T("Программа сама откроет YouTube в отдельном окне браузера и вставит туда файл, название, описание "
                "и хэштеги. Тебе останется проверить и нажать «Опубликовать».\n"
                "В первый раз войди в этом окне в свой Google-аккаунт — дальше он запомнится.")) if auto else (
                T('Файл уже лежит в папке «К загрузке» (Рабочий стол → YouTube → К загрузке), кроме него там ничего нет.\nНа сайте {0} нажми «Выбрать файл» и открой эту папку — или перетащи файл из открытого окна папки.\n').format(pname)
                + (T("Имя файла = название ролика, YouTube подставит его сам.") if platform == "youtube" else "")
            )).pack(anchor="w", pady=(4, 4))
            tools = ttk.Frame(frm)
            tools.pack(fill="x")
            ttk.Button(tools, text=T('🌐  Страница загрузки {0}').format(pname),
                       command=lambda: webbrowser.open(library.UPLOAD_PAGES[platform])).pack(side="left")
            ttk.Button(tools, text=T("📂  Папка «К загрузке»"),
                       command=lambda: self._open(library.upload_dir())).pack(side="left", padx=6)
            ttk.Button(tools, text=T("📋  Путь к файлу"),
                       command=lambda: self._copy_text(staged, win)).pack(side="left")
            if auto:
                ttk.Button(tools, text=T("▶  Вставить в YouTube ещё раз"),
                           command=lambda: start_upload()).pack(side="left", padx=6)
        fields = {}
        for key, label, h in (("title", T("Название (надпись на клипе)"), 2), ("description", T("Описание"), 5),
                              ("hashtags", T("Хэштеги"), 3)):
            row = ttk.Frame(frm)
            row.pack(fill="x", pady=(6, 0))
            ttk.Label(row, text=label, font=("Segoe UI", 10, "bold")).pack(side="left")
            ttk.Button(row, text=T("📋 Копировать"),
                       command=lambda k=key: self._copy_text(fields[k].get("1.0", "end-1c"), win)).pack(side="right")
            t = tk.Text(frm, height=h, wrap="word", font=("Segoe UI", 10), undo=True)
            t.pack(fill="x")
            fields[key] = t
        fields["title"].insert("1.0", c.get("caption") or "")
        status = ttk.Label(frm, text="", foreground=self.muted)
        status.pack(anchor="w", pady=(8, 0))
        bar = ttk.Frame(frm)
        bar.pack(fill="x", pady=(6, 0))

        def fill(post):
            if not win.winfo_exists():
                return
            for k in ("description", "hashtags"):
                fields[k].delete("1.0", "end")
                fields[k].insert("1.0", post[k])
            status.config(text=T("Готово. Скопируй и вставь при публикации (Ctrl+V)."))
            data = {"description": post["description"], "hashtags": post["hashtags"]}
            self.post_cache[c["path"]] = data

        def generate():
            status.config(text=T("Придумываю...") + (" (Claude)" if cap._api_key() else T(" (шаблон — без ключа Claude)")))

            def work():
                post = cap.make_post(c.get("channel", ""), fields["title"].get("1.0", "end-1c").strip(),
                                     c.get("vod_title", ""), c.get("transcript", ""), lang, c.get("link", ""),
                                     log=lambda m: None)
                self.root.after(0, lambda: fill(post))
            threading.Thread(target=work, daemon=True).start()

        def copy_all():
            text = "\n\n".join(fields[k].get("1.0", "end-1c").strip() for k in ("title", "description", "hashtags"))
            self._copy_text(text, win)
        ttk.Button(bar, text=T("✨  Придумать заново"), command=generate).pack(side="left")
        ttk.Button(bar, text=T("📋  Копировать всё"), command=copy_all).pack(side="left", padx=6)
        ttk.Button(bar, text=T("Закрыть"), command=win.destroy).pack(side="right")
        if platform:
            skip = getattr(self, "_publish_skip", set())
            self._publish_skip = skip

            def go_next(mark: bool):
                if mark:
                    library.set_posted(c["path"], True, platform)
                else:
                    skip.add(c["path"])
                win.destroy()
                self.post_window = None
                self.refresh_clips()
                iid, nxt = self._next_unposted(platform, skip | {c["path"]})
                if nxt is None:
                    self.clips_info.config(text=T('Готово — невыложенных в {0} клипов больше нет 🎉').format(pname))
                    return
                self.tree.selection_set(iid)
                self.tree.see(iid)
                self.publish(platform, nxt)
            nb = ttk.Frame(frm)
            nb.pack(fill="x", pady=(12, 0))
            ttk.Button(nb, text=T('✔  Выложил — следующий'), style="Big.TButton",
                       command=lambda: go_next(True)).pack(side="left")
            ttk.Button(nb, text=T("Пропустить этот"), command=lambda: go_next(False)).pack(side="left", padx=6)
        if not hasattr(self, "post_cache"):
            self.post_cache = {}
        started = []

        def start_upload():
            """Заполняем YouTube в браузере (в фоне, чтобы окно программы не замирало)."""
            from . import browser_upload
            started.append(1)
            title = fields["title"].get("1.0", "end-1c").strip()
            desc = (fields["description"].get("1.0", "end-1c").strip() + "\n\n"
                    + fields["hashtags"].get("1.0", "end-1c").strip()).strip()

            def say(msg):
                def show():
                    if win.winfo_exists():
                        status.config(text=msg)
                    self.clips_info.config(text=msg)
                self.root.after(0, show)

            def work():
                try:
                    ok = browser_upload.youtube_upload(staged, title, desc, log=say)
                except Exception as e:
                    say(T('Не получилось заполнить YouTube автоматически: {0}: {1}').format(type(e).__name__, e))
                    ok = False
                if not ok:
                    say(T("Автоматически не вышло — открыл страницу загрузки и папку «К загрузке», перетащи файл сам."))
                    self.root.after(0, lambda: self._open_manual_upload(platform, force=True))
            threading.Thread(target=work, daemon=True).start()

        if auto:
            orig_fill = fill

            def fill(post):  # noqa: F811 — как только текст готов, сразу несём его в YouTube
                orig_fill(post)
                if not started and win.winfo_exists():
                    start_upload()
        if c["path"] in self.post_cache:
            fill(self.post_cache[c["path"]])
        else:
            generate()
        self.post_window = win  # для проверок

    def _copy_text(self, text: str, parent=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.clips_info.config(text=T("Скопировано — вставь при публикации (Ctrl+V)."))

    def reveal_clip(self):
        for c in self._selected()[:1]:
            if os.name == "nt":
                subprocess.Popen(["explorer", "/select,", c["path"]])
            else:
                self._open(os.path.dirname(c["path"]))

    def delete_clip(self):
        sel = self._selected()
        if sel and messagebox.askyesno(T("Удалить"), T('Удалить клипов: {0}? Файлы удалятся с диска.').format(len(sel))):
            if self.preview.path in {c["path"] for c in sel}:
                self.preview.release()
            for c in sel:
                for p in (c["path"], library.thumb_path(c["path"])):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
                library.forget(c["path"])
                self.images.pop(c["path"], None)
            self.refresh_clips()

    def pick_facecam(self):
        """Окно, где мышкой обводят вебку стримера — дальше она всегда будет браться отсюда."""
        from . import facecam
        sel = self._selected()
        if not sel:
            return
        channel = sel[0].get("channel", "")
        frame = facecam.frame_path(channel)
        if not os.path.exists(frame):
            messagebox.showinfo(T("Вебка"), T('Пока нет кадра со стрима {0}. Он появится, когда программа нарежет следующий клип этого стримера.').format(channel))
            return
        win = tk.Toplevel(self.root)
        win.title(T('Вебка стримера {0}').format(channel))
        win.transient(self.root)
        img = tk.PhotoImage(file=frame)
        W, H = img.width(), img.height()
        ttk.Label(win, text=T("Обведи мышкой вебку стримера (зажми левую кнопку и тяни). "
                            "Рамка будет использоваться для всех следующих клипов."),
                  padding=6).pack(anchor="w")
        cv = tk.Canvas(win, width=W, height=H, cursor="crosshair", highlightthickness=0)
        cv.pack(padx=6)
        cv.create_image(0, 0, image=img, anchor="nw")
        cv.image = img
        entry = facecam.get_entry(channel)
        if entry.get("region"):
            x, y, w, h = entry["region"]
            cv.create_rectangle(x * W, y * H, (x + w) * W, (y + h) * H, outline="#3ddc84", width=3, dash=(6, 4))
        state = {"start": None, "rect": None, "box": None}

        def press(e):
            state["start"] = (e.x, e.y)
            if state["rect"]:
                cv.delete(state["rect"])
            state["rect"] = cv.create_rectangle(e.x, e.y, e.x, e.y, outline="#ff3b30", width=3)

        def drag(e):
            if state["start"]:
                x0, y0 = state["start"]
                cv.coords(state["rect"], x0, y0, max(0, min(W, e.x)), max(0, min(H, e.y)))

        def release(e):
            if not state["start"]:
                return
            x0, y0 = state["start"]
            x1, y1 = max(0, min(W, e.x)), max(0, min(H, e.y))
            x0, x1 = sorted((x0, x1))
            y0, y1 = sorted((y0, y1))
            if x1 - x0 > 15 and y1 - y0 > 15:
                state["box"] = (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H)
        cv.bind("<ButtonPress-1>", press)
        cv.bind("<B1-Motion>", drag)
        cv.bind("<ButtonRelease-1>", release)

        def save():
            if not state["box"]:
                messagebox.showinfo(T("Вебка"), T("Сначала обведи вебку мышкой."), parent=win)
                return
            facecam.set_manual(channel, tuple(round(v, 4) for v in state["box"]))
            self._append(T('Вебка стримера {0} задана вручную — применится к следующим клипам.\n').format(channel))
            win.destroy()

        def no_cam():
            facecam.set_manual(channel, None, no_cam=True)
            self._append(T('Для {0}: вебки нет — игра будет на размытом фоне.\n').format(channel))
            win.destroy()

        def auto():
            facecam.set_manual(channel, None)
            self._append(T('Для {0}: вебка снова ищется автоматически.\n').format(channel))
            win.destroy()
        bar = ttk.Frame(win, padding=6)
        bar.pack(fill="x")
        ttk.Button(bar, text=T("✔  Сохранить рамку"), command=save).pack(side="left")
        ttk.Button(bar, text=T("У этого стримера нет вебки"), command=no_cam).pack(side="left", padx=6)
        ttk.Button(bar, text=T("Искать автоматически"), command=auto).pack(side="left")
        ttk.Button(bar, text=T("Отмена"), command=win.destroy).pack(side="right")
        win.grab_set()
        self.facecam_window = win  # для проверок

    def _open(self, path: str):
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", path])

    def open_folder(self):
        d = paths.default_out_dir()
        os.makedirs(d, exist_ok=True)
        if os.name == "nt":
            os.startfile(d)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", d])

    def on_close(self):
        if self.proc and not messagebox.askyesno(T("Выход"), T("Программа сейчас работает. Остановить и закрыть?\n"
                                                          "(Лучше сначала нажать «Стоп» — тогда прогресс сохранится.)")):
            return
        self.force_stop()
        self._save_settings()
        self._autosave_streamers()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
