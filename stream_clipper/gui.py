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

from . import detect, library, paths, updater
from . import i18n
from .exchange import exchange_dir
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
            "top": "5", "length": "35", "quality": "1080", "autoupdate": True, "doctor_settings": True,
            "wm_on": False, "wm_text": "", "wm_image": "", "wm_pos": T("плавает по экрану"), "wm_op": T("средне"), "game_view": T("целиком"), "yt_browser": T("не брать"),
            "credit_auto": False, "credit_pos": T("вверху слева"), "lang": i18n.LANG,
            "start_from": T("с начала"), "start_mode": T("от начала стрима"), "theme": T("Фиолетовая (как Twitch)")}
CREDIT_POS = {T("внизу слева"): "bottom-left", T("вверху слева"): "top-left", T("вверху справа"): "top-right"}
SHOW_ALL = T("все клипы")
SHOW_FILTERS = {SHOW_ALL: "", T("ещё не на YouTube"): "youtube", T("ещё не в Instagram"): "instagram",
                T("ещё не в TikTok"): "tiktok", T("нигде не выложенные"): "nowhere", T("с нарушениями"): "violations",
                T("советует аналитик"): "advice"}
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
    T("Минимал (как TikTok)"): dict(bg="#000000", panel="#121212", field="#161616", fg="#ffffff", muted="#8a8b91",
                                  accent="#fe2c55", accent_fg="#ffffff", border="#1e1e1e", select="#2b2b2b", flat=True),
    T("Классическая (серая)"): None,
}
SIMPLE_THEME = T("Минимал (как TikTok)")
GAME_VIEW = {T("целиком"): "full", T("крупнее"): "wide", T("только центр"): "center", T("авто (по кадрам)"): "auto"}
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
        if self.cfg.get("simple_ui", True) and not self.cfg.get("simple_theme_set"):
            self.cfg["theme"], self.cfg["simple_theme_set"] = SIMPLE_THEME, True
            try:
                data = _load_json(SETTINGS, DEFAULTS)
                data.update(theme=untranslate(SIMPLE_THEME), simple_theme_set=True)
                with open(SETTINGS, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=1)
            except Exception:
                pass
        self.v["simple_ui"] = tk.BooleanVar(value=bool(self.cfg.get("simple_ui", True)))
        self.v["simple_theme_set"] = tk.BooleanVar(value=bool(self.cfg.get("simple_theme_set")))
        self.pal = self._apply_theme(self.cfg.get("theme"))
        self.muted = self.pal["muted"] if self.pal else "#666"
        root.geometry("1120x880")
        root.minsize(900, 700)
        try:
            root.iconbitmap(os.path.join(PROG, "icon.ico"))
        except Exception:
            pass
        self._build()
        self._simple_ui()
        self._install_shortcuts()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(150, self._drain)

    def _scrollable(self, parent):
        """Рамка с прокруткой (колесо мыши и полоса справа): (внешняя рамка для вкладки, внутренняя — для содержимого)."""
        outer = ttk.Frame(parent)
        bg = (self.pal or {}).get("bg") if getattr(self, "pal", None) else None
        canvas = tk.Canvas(outer, highlightthickness=0, **({"bg": bg} if bg else {}))
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas, padding=8)
        win = canvas.create_window(0, 0, window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))

        def wheel(e):
            if canvas.winfo_height() < inner.winfo_reqheight():
                canvas.yview_scroll(-1 if (e.delta > 0 or getattr(e, "num", 0) == 4) else 1, "units")
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            outer.bind_all(seq, lambda e: wheel(e) if str(e.widget).startswith(str(outer)) else None, add="+")
        return outer, inner

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
        if pal.get("flat"):  # минимализм: без рамок, крупнее, вкладки — просто текст, главная кнопка — яркая
            style.configure(".", font=("Segoe UI", 11))
            style.configure("TLabelframe", bordercolor=bg, relief="flat")
            style.configure("TLabelframe.Label", foreground=muted, font=("Segoe UI", 10, "bold"))
            style.configure("TButton", background=panel, bordercolor=panel, padding=(14, 9), relief="flat")
            style.map("TButton", background=[("active", sel), ("disabled", bg)], foreground=[("disabled", muted)])
            style.configure("Big.TButton", font=("Segoe UI", 12, "bold"), padding=(22, 12), bordercolor=acc, relief="flat")
            style.configure("TMenubutton", background=panel, bordercolor=panel, padding=(14, 9), relief="flat")
            style.configure("Big.TMenubutton", padding=(18, 10), relief="flat")
            style.configure("TNotebook", background=bg, bordercolor=bg, tabmargins=(8, 8, 8, 0))
            style.configure("TNotebook.Tab", background=bg, foreground=muted, padding=(22, 10), bordercolor=bg,
                            font=("Segoe UI", 12, "bold"))
            style.map("TNotebook.Tab", background=[("selected", bg)], foreground=[("selected", fg)])
            style.configure("Treeview", rowheight=30, bordercolor=bg)
            style.configure("Treeview.Heading", background=bg, foreground=muted, bordercolor=bg, relief="flat")
            style.configure("TNotebook.Tab", lightcolor=bg, darkcolor=bg)
            style.configure("TNotebook", lightcolor=bg, darkcolor=bg)
            for opt, val in (("*Text.highlightThickness", 0), ("*Text.relief", "flat"), ("*Text.borderWidth", 8)):
                self.root.option_add(opt, val)
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
        sett_outer, sett = self._scrollable(self.nb)  # настроек стало много — вкладка прокручивается
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
        ttk.Checkbutton(themef, text=T("Простой вид (минимум кнопок)"), variable=self.v["simple_ui"],
                        command=lambda: self._set_simple(self.v["simple_ui"].get())).pack(side="left", padx=(16, 0))
        self.nb.add(main, text=T("  Управление  "))
        streams = ttk.Frame(self.nb, padding=8)
        self.nb.add(clips, text=T("  Клипы  "))
        self.nb.add(streams, text=T("  Стримы  "))
        arch = ttk.Frame(self.nb, padding=8)
        self.nb.add(arch, text=T("  Архив  "))
        plan_tab = ttk.Frame(self.nb, padding=8)
        self.nb.add(plan_tab, text=T("  План  "))
        self.nb.add(sett_outer, text=T("  Настройки  "))
        self.sett = sett
        self._build_clips(clips)
        self._build_streams(streams)
        self._build_archive(arch)
        self._build_plan(plan_tab)
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab)

        top = ttk.Frame(main)
        top.pack(fill="x")
        self.main_top = top
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
        self.main_opt = opt
        opt.pack(side="right", fill="y", before=box)  # блоку настроек — его полная ширина
        self._doc_widgets: dict = {}  # настройка → её поля (блокируются, пока выбирает «Доктор»)
        self._doc_reason: dict = {}
        self._doc_extra: dict = {}
        self._init_own()
        head = ttk.Frame(opt)
        head.pack(anchor="w", fill="x", pady=(0, 2))
        ttk.Button(head, text=T("🩺 Всё Доктору"), command=self._all_to_doctor).pack(side="left")
        ttk.Label(head, text=T("  🩺 — выбирает Доктор, ✋ — твоё значение (главнее)"),
                  foreground=self.muted).pack(side="left")
        self.doc_hint = ttk.Label(opt, text="", foreground=self.muted, wraplength=330, justify="left")
        self.doc_hint.pack(anchor="w", pady=(0, 4))
        for key, text in (("subs", T("Субтитры (речь стримера)")),
                          ("caption", T("Надпись-плашка с подписью к моменту")),
                          ("facecam", T("Вебка стримера сверху")),
                          ("audio", T("Искать по звуку и картинке (без чата)")),
                          ("cold_open", T("Холодный старт: пик момента в самом начале")),
                          ("punch_zoom", T("Резкий зум на лицо на пике"))):
            self.v[key] = tk.BooleanVar(value=bool(self.cfg.get(key)))
            row = ttk.Frame(opt)
            row.pack(anchor="w", pady=1)
            self._own_btn(row, key).pack(side="left", padx=(0, 4))
            w = ttk.Checkbutton(row, text=text, variable=self.v[key])
            w.pack(side="left")
            self._doc_reg(key, w)
            self.v[key].trace_add("write", lambda *a: self._on_live_setting(quick=True))
            if key in ("cold_open", "punch_zoom"):
                self.v[key].trace_add("write", lambda *a: self._on_post_setting())

        grid = ttk.Frame(opt)
        grid.pack(anchor="w", pady=(6, 0))
        digits = (self.root.register(lambda p: p == "" or (p.isdigit() and len(p) <= 3)), "%P")
        for r, (key, text, values, editable) in enumerate((
                ("top", T("Клипов за час стрима:"), ["1", "2", "3", "5", "10", "20", "50"], True),
                ("length", T("Длина клипа, сек:"), [T("авто"), "10", "15", "25", "35", "45", "60"], True),
                ("quality", T("Качество:"), ["720", "1080"], False))):
            ttk.Label(grid, text=text).grid(row=r, column=0, sticky="w", pady=2)
            val = str(self.cfg.get(key))
            ok = (val.isdigit() or val == T("авто")) if editable else val in values
            self.v[key] = tk.StringVar(value=val if ok else DEFAULTS[key])
            cb = ttk.Combobox(grid, textvariable=self.v[key], values=values, width=6,
                              state="normal" if editable else "readonly")
            if editable:
                cb.configure(validate="key", validatecommand=digits)
                self.v[key].trace_add("write", lambda *a: self._on_live_setting())
            cb.grid(row=r, column=1, sticky="w", padx=6)
            self._own_btn(grid, key).grid(row=r, column=2, sticky="w")
            self._doc_reg(key, cb)
        ttk.Label(grid, text=T("Игра в кадре:")).grid(row=3, column=0, sticky="w", pady=2)
        gv = self.cfg.get("game_view")
        self.v["game_view"] = tk.StringVar(value=gv if gv in GAME_VIEW else T("целиком"))
        w = ttk.Combobox(grid, textvariable=self.v["game_view"], values=list(GAME_VIEW), width=12, state="readonly")
        w.grid(row=3, column=1, sticky="w", padx=6)
        self._own_btn(grid, "game_view").grid(row=3, column=2, sticky="w")
        self._doc_reg("game_view", w)
        # картинка-пример: как будет выглядеть клип при выбранном варианте
        self.gv_images = {}
        for label, key in GAME_VIEW.items():
            try:
                self.gv_images[label] = tk.PhotoImage(file=os.path.join(PROG, "stream_clipper", "assets",
                                                                        f"gameview_{key}.png"))
            except Exception:
                pass
        self.gv_preview = ttk.Label(grid)
        self.gv_preview.grid(row=0, column=3, rowspan=4, padx=(10, 0), sticky="ne")
        self.v["game_view"].trace_add("write", lambda *a: self._update_gv_preview())
        self.v["game_view"].trace_add("write", lambda *a: self._on_live_setting(quick=True))
        self.v["quality"].trace_add("write", lambda *a: self._on_live_setting(quick=True))
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
        self._own_btn(r1, "watermark").pack(side="left", padx=(0, 4))
        w = ttk.Checkbutton(r1, text=T("Ставить"), variable=self.v["wm_on"])
        w.pack(side="left")
        self._doc_reg("wm_on", w)
        ttk.Label(r1, text=T("  Текст:")).pack(side="left")
        self.v["wm_text"] = tk.StringVar(value=self.cfg.get("wm_text", ""))
        w = ttk.Entry(r1, textvariable=self.v["wm_text"], width=20)
        w.pack(side="left", padx=4)
        self._doc_reg("wm_text", w)
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
        w = ttk.Combobox(r2, textvariable=self.v["wm_pos"], values=list(WM_POS), width=18, state="readonly")
        w.pack(side="left", padx=4)
        self._doc_reg("wm_pos", w)
        ttk.Label(r2, text=T("  Заметность:")).pack(side="left")
        self.v["wm_op"] = tk.StringVar(value=self.cfg.get("wm_op") if self.cfg.get("wm_op") in WM_OP else T("средне"))
        w = ttk.Combobox(r2, textvariable=self.v["wm_op"], values=list(WM_OP), width=9, state="readonly")
        w.pack(side="left", padx=4)
        self._doc_reg("wm_op", w)
        for k in ("wm_on", "wm_text", "wm_pos", "wm_op"):
            self.v[k].trace_add("write", lambda *a: self._on_live_setting())
        ttk.Label(r2, text=T("  «плавает» — лучшая защита: знак нельзя обрезать или замазать"),
                  foreground=self.muted).pack(side="left")

        # подпись автора
        cr = ttk.LabelFrame(sett, text=T(" Подпись автора — чей это клип (Twitch | KaiCenat) "), padding=6)
        cr.pack(fill="x", pady=(0, 6))
        self.v["credit_auto"] = tk.BooleanVar(value=bool(self.cfg.get("credit_auto", False)))
        self._own_btn(cr, "credit").pack(side="left", padx=(0, 4))
        w = ttk.Checkbutton(cr, text=T("Сразу подписывать все новые клипы"), variable=self.v["credit_auto"])
        w.pack(side="left")
        self._doc_reg("credit_auto", w)
        ttk.Label(cr, text=T("  Где:")).pack(side="left")
        cpos = self.cfg.get("credit_pos")
        if cpos == T("внизу слева") and not self.cfg.get("credit_pos_v2"):
            cpos = T("вверху слева")  # раньше по умолчанию было «внизу» — там подпись закрывает интерфейс площадок
        self.v["credit_pos"] = tk.StringVar(value=cpos if cpos in CREDIT_POS else T("вверху слева"))
        self.v["credit_pos_v2"] = tk.BooleanVar(value=True)
        w = ttk.Combobox(cr, textvariable=self.v["credit_pos"], values=list(CREDIT_POS), width=14, state="readonly")
        w.pack(side="left", padx=4)
        self._doc_reg("credit_pos", w)
        for k in ("credit_auto", "credit_pos"):
            self.v[k].trace_add("write", lambda *a: self._on_live_setting())
        ttk.Label(cr, text=T("  иначе — галочкой в колонке «Автор» на нужных клипах (вкладка «Клипы»)"),
                  foreground=self.muted).pack(side="left")

        self._build_tricks(sett)
        self._build_post_settings(sett)
        self._build_backup_settings(sett)
        self._build_team_settings(sett)
        self._build_telegram(sett)
        self._build_publish_settings(sett)

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
        self.main_vod = vod
        self.url = tk.StringVar()
        ttk.Entry(vod, textvariable=self.url).pack(side="left", fill="x", expand=True)
        self.b_vod = ttk.Button(vod, text=T("✂  Нарезать"), command=self.start_vod)
        self.b_vod.pack(side="left", padx=6)
        fromrow = ttk.Frame(main)
        fromrow.pack(fill="x", pady=(0, 4))
        self.main_from = fromrow
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
        self.v["autopilot"] = tk.BooleanVar(value=bool(self.cfg.get("autopilot", True)))
        self.v["pub_paused"] = tk.BooleanVar(value=bool(self.cfg.get("pub_paused", False)))
        ttk.Checkbutton(logbar, text=T("🤖 Автопилот"), variable=self.v["autopilot"],
                        command=self._autopilot_toggled).pack(side="left")
        ttk.Checkbutton(logbar, text=T("⏸ Пауза публикаций"), variable=self.v["pub_paused"],
                        command=self._save_settings).pack(side="left", padx=(10, 0))
        ttk.Button(logbar, text=T("⚡ Проход сейчас"), command=lambda: self._autopilot_tick(force=True)).pack(side="left", padx=8)
        self.b_hide_log = ttk.Button(logbar, text=T("Скрыть ▴"), command=self._toggle_log)
        self.b_hide_log.pack(side="right", padx=(6, 0))
        self.b_big_log = ttk.Button(logbar, text=T("⤢ Во всё окно"), command=self._toggle_big_log)
        self.b_big_log.pack(side="right", padx=(6, 0))
        self.b_details = ttk.Button(logbar, text=T("📄 Подробный журнал"), command=self._toggle_details)
        self.b_details.pack(side="right")
        from .activity import ActivityPanel
        self.activity = ActivityPanel(logf, self)  # карточки стримеров и лента событий
        self.activity.pack(fill="both", expand=True)
        self.log = ScrolledText(logf, height=8, font=("Consolas", 10), state="disabled", wrap="word")  # полный журнал
        self.logf = logf
        if self.cfg.get("log_hidden"):
            self.root.after(50, self._toggle_log)
        bottom = ttk.Frame(main)
        bottom.pack(side="bottom", fill="x", pady=(4, 0), before=logf)
        self.main_bottom = bottom
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
        self.root.after(20000, self._autopilot_tick)
        self.root.after(15000, self._assist_tick)
        self.root.after(3000, self._doctor_settings_tick)
        self.root.after(40000, lambda: self.sweep_sleepy(auto=True))
        self.root.after(25000, self._tg_on_start)
        self.root.after(90000, self._backup_tick)
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
        m.add_command(label=T("✍  Подписать автора / убрать подпись"), command=self.toggle_credit)
        m.add_command(label=T("✂  Обрезать / удлинить"), command=self.edit_clip)
        m.add_command(label=T("🕘  Правки этого клипа (отменить размытие, обрезку...)"), command=self.clip_history)
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
        ttk.Button(side, text=T("🎥 Вебка"), command=self.queue_facecam).pack(fill="x", pady=(10, 0))
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
            "Приходят только видео, которые надо выложить: с готовым текстом и временем публикации.")
        )).pack(anchor="w")
        row = ttk.Frame(tg)
        row.pack(fill="x", pady=(6, 0))
        self.tg_on = tk.BooleanVar(value=bool(cfg.get("all_clips")))
        ttk.Label(row, text=T("  Ключ бота:")).pack(side="left")
        self.tg_token = tk.StringVar(value=cfg.get("token", ""))
        ttk.Entry(row, textvariable=self.tg_token, show="•", width=24).pack(side="left", padx=4)
        ttk.Button(row, text=T("Подключить"), command=self._tg_connect).pack(side="left")
        ttk.Button(row, text=T("Проверить"), command=self._tg_test).pack(side="left", padx=4)
        self.tg_status = ttk.Label(row, text=(T("✔ подключено: ") + cfg.get("name", "")) if cfg.get("chat_id")
                                   else T("не подключено"), foreground=self.muted)
        self.tg_status.pack(side="left", padx=6)
        rowc = ttk.Frame(tg)
        rowc.pack(fill="x", pady=(4, 0))
        ttk.Checkbutton(rowc, text=T("Присылать ещё и каждый готовый клип (обычно не нужно — приходят только видео, "
                                     "которые надо выложить)"), variable=self.tg_on, command=self._tg_toggle).pack(side="left")
        rr = ttk.Frame(tg)
        rr.pack(fill="x", pady=(6, 0))
        ttk.Label(rr, foreground=self.muted, wraplength=1050, justify="left", text=T(
            "👥 Чтобы посты приходили и другу: он открывает твоего бота в Telegram и жмёт «Старт», а ты нажимаешь "
            "«Добавить друга». Вам обоим будут приходить одни и те же видео; кто выложил — жмёт «✅ Выложил», и у второго "
            "кнопка сразу меняется на «Выложил: имя». Программа другу не нужна.")).pack(anchor="w")
        rr2 = ttk.Frame(tg)
        rr2.pack(fill="x", pady=(4, 0))
        ttk.Button(rr2, text=T("➕ Добавить друга"), command=self._tg_approve).pack(side="left")
        ttk.Button(rr2, text=T("Убрать получателей"), command=self._tg_remove_recipient).pack(side="left", padx=6)
        self.tg_recips = ttk.Label(rr2, text=self._tg_recipients_text())
        self.tg_recips.pack(side="left", padx=6)

    def _tg_recipients_text(self) -> str:
        from . import telegram
        c = telegram.load()
        names = [T("ты (основной чат)")] + [e.get("name", "?") for e in c.get("extra_chats") or []]
        pend = c.get("pending_chats") or []
        txt = T("Получают посты: {0}").format(", ".join(names))
        if pend:
            txt += "   ·   " + T("ждут подтверждения: {0}").format(", ".join(p["name"] for p in pend))
        return txt

    def _tg_refresh_recipients(self):
        if hasattr(self, "tg_recips"):
            self.tg_recips.config(text=self._tg_recipients_text())

    def _tg_approve(self):
        """Подтвердить тех, кто нажал «Старт» у бота (например, друга): им будут приходить те же посты."""
        from . import telegram
        c = telegram.load()
        pend = c.get("pending_chats") or []
        if not pend:
            messagebox.showinfo("Telegram", T("Новых желающих нет. Пусть друг откроет твоего бота в Telegram и нажмёт "
                                             "«Старт», подожди полминуты и нажми эту кнопку снова."))
            return
        names = ", ".join(p["name"] for p in pend)
        if not messagebox.askyesno("Telegram", T("Добавить получателей: {0}? Им будут приходить те же видео и посты, "
                                                "и они смогут нажимать «✅ Выложил».").format(names)):
            return
        extra = c.setdefault("extra_chats", [])
        for p in pend:
            if p["id"] not in [e["id"] for e in extra]:
                extra.append(p)
                try:
                    telegram._call(c["token"], "sendMessage", data={"chat_id": p["id"], "text": "✅ Готово! Теперь сюда будут "
                                    "приходить видео для публикации. Выложил — нажми «✅ Выложил» под постом."})
                except Exception:
                    pass
        c["pending_chats"] = []
        telegram.save(c)
        self._tg_refresh_recipients()
        self.activity.event("👥", T("Получатели постов: {0}").format(", ".join(e["name"] for e in extra)))

    def _tg_remove_recipient(self):
        from . import telegram
        c = telegram.load()
        extra = c.get("extra_chats") or []
        if not extra:
            return
        if messagebox.askyesno("Telegram", T("Убрать получателей: {0}? Посты им приходить перестанут.").format(
                ", ".join(e["name"] for e in extra))):
            c["extra_chats"] = []
            telegram.save(c)
            self._tg_refresh_recipients()

    def _tg_toggle(self):
        from . import telegram
        cfg = telegram.load()
        cfg["all_clips"] = bool(self.tg_on.get())
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
                old = telegram.load()
                telegram.save(dict(old, token=token, chat_id=chat_id, name=name, on=True, forum=forum,
                                   all_clips=bool(old.get("all_clips"))))
                telegram.send_text(T("✅ Stream Clipper подключён! Сюда будут приходить только видео, которые надо "
                                     "выложить: с текстом и временем публикации."))
                label = T('✔ группа «{0}» (папки по датам)').format(name) if forum else T('✔ подключено: {0}').format(name)
                self.root.after(0, lambda: self.tg_status.config(text=label))
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
        from .caption import claude_allowed
        if not claude_allowed():
            self.key_status.config(text=T("бесплатный режим: Доктор выключил Claude — надписи и тексты по шаблонам"))
            return
        ok = bool(self.key.get().strip())
        self.key_status.config(text=T("✔ ключ есть") if ok else T("нет ключа — надписи по шаблону"))

    def _save_settings(self):
        hidden = self.cfg.get("log_hidden", False)
        manual = self.cfg.get("manual_settings")
        self.cfg = {k: (v.get()) for k, v in self.v.items()}
        self.cfg["log_hidden"] = hidden
        if manual:
            self.cfg["manual_settings"] = manual
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
        if self.v["length"].get() == T("авто"):  # длина под момент: от ~5 с до пика, дальше — пока длится реакция (до 60 с)
            return top, 5, 5
        length = self._num("length", 5, 180)
        pre = max(2, round(length * 0.57))
        return top, pre, max(2, length - pre)

    def _on_live_setting(self, quick: bool = False):
        """Поменяли настройку во время работы — передаём её рабочей части (числа — с задержкой на ввод)."""
        if getattr(self, "_live_job", None):
            self.root.after_cancel(self._live_job)
        self._live_job = self.root.after(300 if quick else 1200, self._push_live_settings)

    def _live_values(self) -> dict:
        top, pre, post = self._clip_numbers()
        subs = bool(self.v["subs"].get())
        if subs and importlib.util.find_spec("faster_whisper") is None:
            subs = False  # распознавание речи не установлено — включать нечего (предупреждение — в журнале)
        return {"top": top, "pre": pre, "post": post, "credit": bool(self.v["credit_auto"].get()),
                "credit_pos": CREDIT_POS.get(self.v["credit_pos"].get(), "top-left"),
                "subs": subs, "caption": bool(self.v["caption"].get()), "facecam": bool(self.v["facecam"].get()),
                "audio": bool(self.v["audio"].get()), "game_view": GAME_VIEW.get(self.v["game_view"].get(), "full"),
                "quality": int(self.v["quality"].get() or 1080),
                "auto_length": self.v["length"].get() == T("авто"),
                "watermark_text": self.v["wm_text"].get().strip() if self.v["wm_on"].get() else "",
                "watermark_pos": WM_POS.get(self.v["wm_pos"].get(), "moving"),
                "watermark_opacity": WM_OP.get(self.v["wm_op"].get(), 0.4),
                "per_streamer": dict(self._doc_extra.get("per_streamer") or {}),
                "no_facecam_fallback": self._doc_extra.get("no_facecam_fallback") or {}}

    _LIVE_NAMES = {"subs": "Субтитры", "caption": "Надпись-плашка", "facecam": "Вебка сверху",
                   "audio": "Поиск по звуку и картинке"}

    def _push_live_settings(self):
        self._live_job = None
        if not self.v["top"].get() or not self.v["length"].get():
            return  # ещё печатает
        self._save_settings()
        if not self.proc:
            return
        new = self._live_values()
        old = getattr(self, "_live_sent", None) or {}
        if new == old:
            return
        try:
            os.makedirs(os.path.dirname(paths.live_settings_path()), exist_ok=True)
            with open(paths.live_settings_path(), "w", encoding="utf-8") as f:
                json.dump(new, f)
        except OSError as e:
            self._append(T("Не удалось передать настройки: {0}").format(e) + "\n")
            return
        self._live_sent = new
        parts = []
        if (new["top"], new["pre"], new["post"]) != (old.get("top"), old.get("pre"), old.get("post")):
            parts.append(T("{0} клипов за час, по {1} с").format(new["top"], new["pre"] + new["post"]))
        for k, name in self._LIVE_NAMES.items():
            if k in old and new[k] != old[k]:
                parts.append(T(name) + ": " + (T("вкл") if new[k] else T("выкл")))
        if old and new["game_view"] != old.get("game_view"):
            parts.append(T("игра в кадре: {0}").format(self.v["game_view"].get()))
        if old and new["quality"] != old.get("quality"):
            parts.append(T("качество: {0}").format(new["quality"]))
        if old and (new["watermark_text"], new["watermark_pos"], new["watermark_opacity"]) != \
                (old.get("watermark_text"), old.get("watermark_pos"), old.get("watermark_opacity")):
            parts.append(T("водяной знак: {0}").format(new["watermark_text"] or T("выкл")))
        if old and new["per_streamer"] != old.get("per_streamer"):
            parts.append(T("свои настройки для: {0}").format(", ".join(new["per_streamer"]) or "—"))
        if self.v["subs"].get() and not new["subs"]:
            self._append(T("⚠ Субтитры не установлены — запусти install_subs.bat. Пока режу без них.\n"))
        self._append(T("Настройки изменены: {0} — применятся к следующим клипам, работа не прерывается.\n").format(
            "; ".join(parts) or T("без изменений")))

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
        if c.get("length") == T("авто"):
            f.append("--auto-length")
        if c.get("credit_auto"):
            f += ["--credit", "--credit-pos", CREDIT_POS.get(c.get("credit_pos"), "top-left")]
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
        try:
            self._live_sent = self._live_values()
            # рабочая часть сразу получает и то, чего нет в параметрах запуска (настройки «Доктора» по стримерам)
            os.makedirs(os.path.dirname(paths.live_settings_path()), exist_ok=True)
            with open(paths.live_settings_path(), "w", encoding="utf-8") as f:
                json.dump(self._live_sent, f)
        except Exception:
            self._live_sent = None
        threading.Thread(target=self._reader, args=(self.proc,), daemon=True).start()

    LIVE_CHOICE = "🔴 Текущий эфир и новые стримы"

    def _choose_streams(self, names: list, then):
        """Окно перед стартом: у каждого стримера — что разбирать: текущий эфир или прошлый стрим, который пропустили."""
        from . import progress
        win = tk.Toplevel(self.root)
        win.title(T("Какие стримы разбирать"))
        win.transient(self.root)
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, wraplength=820, justify="left", text=T(
            "У каждого стримера выбери, что разбирать. «Текущий эфир» — программа ждёт эфир и режет его по ходу. "
            "Прошлый стрим — тот, что вы пропустили: он разберётся по кругу вместе с остальными. "
            "Эфиры отслеживаются в любом случае.")).pack(anchor="w", pady=(0, 8))
        rows, choices = {}, {}
        for spec in names:
            kind, target, key = self._spec_kind(spec)
            r = ttk.Frame(frm)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=key, width=18).pack(side="left")
            var = tk.StringVar(value=T(self.LIVE_CHOICE))
            cb = ttk.Combobox(r, textvariable=var, values=[T(self.LIVE_CHOICE), T("загружаю список стримов...")],
                              width=90, state="readonly")
            cb.pack(side="left", fill="x", expand=True)
            rows[spec] = (var, cb, kind, target, key)
            choices[spec] = {}
        status = ttk.Label(frm, text=T("Загружаю списки прошлых стримов..."), foreground=self.muted)
        status.pack(anchor="w", pady=(6, 0))

        def load_all():
            from . import twitch
            data = progress.load()
            for spec, (var, cb, kind, target, key) in rows.items():
                try:
                    vods = twitch.list_streams(kind, target, 10)
                except Exception:
                    vods = []
                opts = {}
                for v in vods:
                    e = data.get(str(v.get("key")))
                    sm = progress.summary(e) if e else None
                    dur = float(v.get("duration") or 0)
                    if sm and sm["finished"]:
                        st_ = T("✔ разобран")
                    elif sm and dur:
                        st_ = T("разобран {0}%").format(int(100 * min(1.0, sm["seen"] / dur)))
                    else:
                        st_ = T("ещё не разбирали")
                    when = time.strftime("%d.%m %H:%M", time.localtime(v["ts"])) if v.get("ts") else ""
                    label = f"{when} · {(v.get('title') or '')[:55]} · {progress.fmt(dur) if dur else '?'} · {st_}"
                    v = dict(v, resume_from=(sm["upto"] if sm and not sm["finished"] else 0))
                    opts[label] = v
                self.root.after(0, lambda spec=spec, opts=opts: fill(spec, opts))
            self.root.after(0, lambda: status.config(text=T("Готово. Не разобранные отмечены «ещё не разбирали».")))

        def fill(spec, opts):
            try:
                var, cb, *_ = rows[spec]
                choices[spec] = opts
                cb.configure(values=[T(self.LIVE_CHOICE)] + list(opts) if opts
                             else [T(self.LIVE_CHOICE), T("прошлых записей не нашлось")])
            except tk.TclError:
                pass

        def start():
            vods = []
            for spec, (var, cb, kind, target, key) in rows.items():
                v = choices.get(spec, {}).get(var.get())
                if v:
                    vods.append({"url": v["url"], "key": str(v.get("key") or ""), "channel": key,
                                 "title": v.get("title") or "", "from": float(v.get("resume_from") or 0)})
            try:
                path = os.path.join(paths.default_work_dir(), "extra_vods.json")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"vods": vods}, f, ensure_ascii=False, indent=1)
            except OSError as e:
                messagebox.showwarning(T("Стримы"), str(e), parent=win)
            if vods:
                self._append(T("Прошлые стримы к разбору: {0}").format(
                    ", ".join(f"{v['channel']} — {v['title'][:40]}" for v in vods)) + "\n")
            win.destroy()
            then()
        bar = ttk.Frame(frm)
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text=T("▶ Начать"), command=start).pack(side="left")
        ttk.Button(bar, text=T("Отмена"), command=win.destroy).pack(side="right")
        self.streams_win = win  # для проверок
        win.grab_set()
        threading.Thread(target=load_all, daemon=True).start()

    def _lang_warning(self, names: list) -> None:
        """Канал английский, а в списке стример на другом языке (программа уже видела его чат) — предупреждаем."""
        from . import caption, strategy
        acc = strategy.get().get("account") or {}
        need = (acc.get("streamers_language") or acc.get("language") or "").lower()
        if not need:
            return
        langs = caption.streamer_langs()
        bad = [n for n in names if langs.get(n.lower().lstrip("@")) not in (None, need)]
        if bad:
            messagebox.showwarning(T("Язык стримера"), T(
                "Канал английский — для этих стримеров нужен отдельный канал: {0}.\n\n"
                "Программа их не будет нарезать и выкладывать.").format(", ".join(bad)))

    def apply_streamers(self):
        names = self._save_streamers()
        self._lang_warning(names)
        if self.proc:
            self._append(T("Список стримеров обновлён: ") + (", ".join(names) or T("пусто"))
                         + T(". Программа подхватит его через несколько секунд.\n"))
        else:
            self.status.config(text=T("Список сохранён: ") + (", ".join(names) or T("пусто")))

    def start_watch(self, quiet: bool = False):
        names = self._save_streamers()
        if quiet:  # продолжение после обновления программы — без окон, сразу работать
            if names:
                self._run(["watch", *self._flags()], T("Слежу за: ") + ", ".join(names), job=["watch"])
            return
        self._lang_warning(names)
        if not names:
            messagebox.showwarning(T("Нет стримеров"), T("Впиши хотя бы одного стримера во вкладку Twitch или YouTube."))
            return
        from . import facecam
        todo = []
        for spec in names:  # перед стартом — вебка у КАЖДОГО: от стрима к стриму она может переехать
            kind, target, key = self._spec_kind(spec)
            todo.append((key, kind, target))

        def go():
            self._choose_streams(names, lambda: self._run(["watch", *self._flags()], T("Слежу за: ") + ", ".join(names),
                                                          job=["watch"]))
        if not todo:
            go()
            return
        if not messagebox.askyesno(T("Вебка стримеров"), T(
                "Перед стартом проверим, где у стримеров вебка в этом стриме: {0}.\n\nПрограмма возьмёт свежий кадр — обведи "
                "на нём вебку мышкой. Не изменилась — «Оставить как в прошлый раз»; не видно — «Другой кадр»; "
                "вебки нет — «Нет веб-камеры».\n\n"
                "Проверить сейчас? («Нет» — начать сразу с прошлыми рамками, новые стримеры — автоматически)").format(
                    ", ".join(k for k, _, _ in todo))):
            go()
            return

        def step(i=0):
            if i >= len(todo):
                self._append(T("Вебки указаны — начинаю работу.") + "\n")
                go()
                return
            key, kind, target = todo[i]
            self._facecam_window(key, kind, target, fresh=True, on_done=lambda: step(i + 1),
                                 step=f"{i + 1}/{len(todo)}")
        step()

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
        if sm["finished"] or not sm["upto"]:
            return
        if messagebox.askyesno(T("Этот стрим уже разбирали"),
                               T("Стрим уже разобран до {0}.\nПродолжить с {0}?\n\n«Нет» — пройти стрим с самого начала.")
                               .format(progress.fmt(sm["upto"]))):
            t = sm["upto"]
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
                    self._append(T("=== Остановлено ===\n"), from_worker=True)
                    self.activity.stopped()
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
                    try:
                        self.activity.worker_line(item)
                    except Exception:
                        pass
                    self._append(tr_line(item), important=self._is_important(item), from_worker=True)
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

    def _append(self, text: str, important: bool = True, from_worker: bool = False):
        """Полный журнал получает всё; в ленту «Что происходит» попадают важные сообщения самого окна
        (строки рабочей части лента разбирает сама — в activity.worker_line)."""
        self.log_lines.append((text, important))
        if len(self.log_lines) > 6000:
            self.log_lines = self.log_lines[-4000:]
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")
        if text.strip() and important:
            self.status.config(text=text.strip().splitlines()[-1][:120])
            if not from_worker and hasattr(self, "activity"):
                icon = "⚠" if text.lstrip().startswith("⚠") else ("⏹" if "Останов" in text or "Dayan" in text else "ℹ")
                self.activity.info(text.lstrip("⚠ ").strip(), icon)

    def show_clip(self, path: str):
        """Клик по клипу в ленте — открыть его во вкладке «Клипы»."""
        self.nb.select(1)
        self.refresh_clips()
        for iid, c in self.clip_by_iid.items():
            if os.path.normpath(c["path"]) == os.path.normpath(path):
                self.tree.selection_set(iid)
                self.tree.see(iid)
                break

    def _log_body(self):
        return self.log if self.log_detailed.get() else self.activity

    def _toggle_big_log(self, big: bool | None = None):
        """«Что происходит» во всё окно: прячем список стримеров, настройки и нарезку по ссылке (кнопки остаются)."""
        big = (not getattr(self, "_log_big", False)) if big is None else big
        if big == getattr(self, "_log_big", False):
            return
        self._log_big = big
        if big:
            for w in (self.main_top, self.main_vod, self.main_from):
                w.pack_forget()
            self.b_big_log.config(text=T("⤡ Показать настройки"))
            self.activity.set_rows(6)
        else:
            self.main_top.pack(fill="x", before=self.b_watch.master)
            if not getattr(self, "_simple", False):
                self.main_vod.pack(fill="x", pady=4, before=self.logf)
                self.main_from.pack(fill="x", pady=(0, 4), before=self.logf)
            self.b_big_log.config(text=T("⤢ Во всё окно"))
            self.activity.set_rows(2)

    def _toggle_log(self):
        """Свернуть / развернуть окно «Что происходит» (последнее событие всё равно видно внизу)."""
        body = self._log_body()
        hidden = body.winfo_ismapped()
        if hidden:
            body.pack_forget()
            self.logf.pack_configure(fill="x", expand=False)
            self.b_hide_log.config(text=T("Показать ▾"))
        else:
            body.pack(fill="both", expand=True)
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
        """Переключатель: понятная лента ↔ полный текстовый журнал."""
        was_visible = self._log_body().winfo_ismapped()
        self._log_body().pack_forget()
        self.log_detailed.set(not self.log_detailed.get())
        self.b_details.config(text=T("🖼 Коротко и понятно") if self.log_detailed.get() else T("📄 Подробный журнал"))
        if was_visible:
            self._log_body().pack(fill="both", expand=True)
        self.log.see("end")

    def _set_running(self, running: bool, what: str = ""):
        self.b_watch.config(state="disabled" if running else "normal")
        self.b_vod.config(state="disabled" if running else "normal")
        self.b_stop.config(state="normal" if running else "disabled")
        if running:
            self.status.config(text=what)
        # во время работы «Что происходит» само разворачивается во всё окно, после «Стоп» — обратно
        try:
            self._toggle_big_log(running)
        except Exception:
            pass

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
            self.start_watch(quiet=True)

    def _restart(self):
        self._append(T("Перезапускаю программу...\n"))
        flags = 0x08000000 if os.name == "nt" else 0
        try:
            subprocess.Popen([sys.executable, "-m", "stream_clipper.gui"], cwd=PROG, creationflags=flags)
        except Exception as e:
            messagebox.showinfo(T("Обновление"), T('Обновление установлено. Открой программу заново.\n({0})').format(e))
        self.root.destroy()

    # ---------- простой вид (как в TikTok/Instagram): минимум кнопок на виду, остальное — в «Ещё» ----------
    def _simple_ui(self):
        if not self.cfg.get("simple_ui", True):
            return
        self._simple = True
        for w in (self.main_opt, self.main_vod, self.main_from, self.main_bottom, self.b_big_log.master):
            w.pack_forget()
        self.nb.tab(0, text=T("  Главная  "))
        for k in (2, 3, 5):
            self.nb.hide(k)
        tabs = self.nb.tabs()

        def open_tab(k):
            self.nb.add(tabs[k])
            self.nb.select(tabs[k])

        bar = self.b_watch.master
        for w in bar.winfo_children():  # «Папка с клипами» — в меню
            if isinstance(w, ttk.Button) and w not in (self.b_watch, self.b_stop):
                w.pack_forget()
        more = ttk.Menubutton(bar, text=T("⋯  Ещё"))
        m = tk.Menu(more, tearoff=0)
        m.add_command(label=T("📁  Папка с клипами"), command=self.open_folder)
        m.add_command(label=T("✂  Нарезать стрим по ссылке"), command=self._simple_show_vod)
        m.add_command(label=T("📺  Стримы"), command=lambda: open_tab(2))
        m.add_command(label=T("🗄  Архив"), command=lambda: open_tab(3))
        m.add_command(label=T("⚙  Настройки"), command=lambda: open_tab(5))
        m.add_separator()
        m.add_command(label=T("📄  Подробный журнал"), command=self._toggle_details)
        m.add_command(label=T("☰  Полный вид (все кнопки)"), command=lambda: self._set_simple(False))
        more["menu"] = m
        more.pack(side="right")
        self._move_to_menu(self.clips_btns, (T("🗑  Удалить"), T("🏆  Оставить лучшие"), T("Ещё ▾")), self.clips_more,
                           keep_first_menubutton=True)
        self._move_to_menu(self.plan_btns, (T("🔁 Отправить ещё раз"), T("📤 Видео на сегодня — в Telegram")), None)
        self.tree["displaycolumns"] = ("rating", "streamer", "why", "caption", "youtube", "instagram", "tiktok")

    def _move_to_menu(self, frame, keep, menu, keep_first_menubutton=False):
        """Кнопки, которых нет в keep, убираем с панели в меню «Ещё» (работают так же)."""
        moved, first_mb = [], True
        for w in frame.winfo_children():
            if isinstance(w, ttk.Menubutton):
                if (keep_first_menubutton and first_mb) or w.cget("text") in keep:
                    first_mb = False
                    continue
                moved.append(("cascade", w.cget("text"), w))
                w.pack_forget()
            elif isinstance(w, ttk.Button) and w.cget("text") not in keep:
                moved.append(("cmd", w.cget("text"), w))
                w.pack_forget()
        if not moved:
            return
        if menu is None:
            mb = ttk.Menubutton(frame, text=T("Ещё ▾"))
            menu = tk.Menu(mb, tearoff=0)
            mb["menu"] = menu
            mb.pack(side="left", padx=6)
        else:
            menu.insert_separator(0)
        for kind, text, w in reversed(moved):
            if kind == "cascade":
                menu.insert_cascade(0, label=text.strip(), menu=self.root.nametowidget(w.cget("menu")))
            else:
                menu.insert_command(0, label=text.strip(), command=w.invoke)

    def _simple_show_vod(self):
        self.main_vod.pack(fill="x", pady=4, before=self.logf)
        self.main_from.pack(fill="x", pady=(0, 4), before=self.logf)

    def _set_simple(self, on: bool):
        self.v["simple_ui"].set(on)
        self._save_settings()
        if messagebox.askyesno(T("Вид окна"), T("Чтобы сменить вид, окно перезапустится. Перезапустить сейчас?")):
            self._restart_window()

    def _on_tab(self, e=None):
        i = self.nb.index(self.nb.select())
        if getattr(self, "_simple", False) and i in (0, 1, 4):  # простой вид: лишние вкладки снова прячем
            for k in (2, 3, 5):
                try:
                    self.nb.hide(k)
                except tk.TclError:
                    pass
        if i == 1:
            self.refresh_clips()
        elif i == 2:
            self.refresh_streams()
        elif i == 3:
            self.refresh_archive()
        elif i == 4:
            self.refresh_plan()

    # ---------- 💾 Хранитель данных ----------
    def _build_backup_settings(self, parent):
        from . import backup
        box = ttk.LabelFrame(parent, text=T(" 💾 Хранитель данных — резервная копия раз в неделю "), padding=6)
        box.pack(fill="x", pady=(0, 6))
        r1 = ttk.Frame(box)
        r1.pack(fill="x")
        ttk.Label(r1, text=T("Папка:")).pack(side="left")
        self.bk_dir = tk.StringVar(value=backup.target_dir())
        ttk.Entry(r1, textvariable=self.bk_dir, width=60).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(r1, text=T("Выбрать…"), command=self._backup_choose).pack(side="left")
        r2 = ttk.Frame(box)
        r2.pack(fill="x", pady=(4, 0))
        self.bk_clips = tk.BooleanVar(value=bool(backup.load().get("with_clips")))
        ttk.Checkbutton(r2, text=T("Копировать и сами клипы (много места)"), variable=self.bk_clips,
                        command=self._backup_save_cfg).pack(side="left")
        ttk.Button(r2, text=T("💾 Сделать копию сейчас"), command=lambda: self._backup_run(force=True)).pack(side="left", padx=8)
        ttk.Button(r2, text=T("Восстановить из копии…"), command=self._backup_restore).pack(side="left")
        self.bk_status = ttk.Label(box, text="", foreground=self.muted)
        self.bk_status.pack(anchor="w", pady=(4, 0))
        self._backup_status()

    def _backup_status(self):
        from . import backup
        c = backup.load()
        if c.get("last"):
            self.bk_status.config(text=T("Последняя копия: {0} — {1} файлов, {2} МБ. Следующая — через неделю после неё.").format(
                time.strftime("%d.%m.%Y %H:%M", time.localtime(c["last"])), c.get("last_files", 0), c.get("last_mb", 0)))
        else:
            self.bk_status.config(text=T("Копий ещё не было — первая будет сделана сама через пару минут после запуска."))

    def _backup_save_cfg(self):
        from . import backup
        c = backup.load()
        c["dir"] = self.bk_dir.get().strip() or backup.default_dir()
        c["with_clips"] = bool(self.bk_clips.get())
        backup.save(c)

    def _backup_choose(self):
        d = filedialog.askdirectory(title=T("Куда складывать резервные копии"))
        if d:
            self.bk_dir.set(d)
            self._backup_save_cfg()

    def _backup_tick(self):
        """Раз в 6 часов: если неделя прошла — Хранитель делает копию."""
        self.root.after(6 * 3600 * 1000, self._backup_tick)
        self._backup_run(force=False)

    def _backup_run(self, force: bool):
        from . import backup
        if getattr(self, "_bk_busy", False) or (not force and not backup.due()):
            return
        self._backup_save_cfg()
        self._bk_busy = True
        self.bk_status.config(text=T("Делаю резервную копию..."))

        def work():
            try:
                res, err = backup.make_backup(log=lambda m: None), None
            except Exception as e:
                res, err = {}, e
            self.root.after(0, lambda: done(res, err))

        def done(res, err):
            self._bk_busy = False
            if err:
                self.activity.event("❌", T("💾 Хранитель данных: копия не получилась — {0}").format(err), kind="error")
                self.bk_status.config(text=T("Копия не получилась: {0}").format(err))
                return
            self.activity.event("💾", T("Хранитель данных: резервная копия готова — {0} файлов, {1} МБ").format(
                res["files"], res["mb"]))
            self._backup_status()
        threading.Thread(target=work, daemon=True).start()

    def _backup_restore(self):
        from . import backup
        d = filedialog.askdirectory(title=T("Папка копии (копия_ГГГГ-ММ-ДД_…)"), initialdir=self.bk_dir.get())
        if not d:
            return
        if not messagebox.askyesno(T("Восстановить"), T("Вернуть данные из этой копии? Текущие данные сначала сохранятся "
                                                       "отдельной копией. После этого программу нужно перезапустить.")):
            return
        try:
            n = backup.restore(d)
        except Exception as e:
            messagebox.showwarning(T("Восстановить"), str(e))
            return
        messagebox.showinfo(T("Восстановить"), T("Восстановлено файлов: {0}. Перезапусти программу.").format(n))

    CLEAR_CHAT_V = 1

    def _tg_on_start(self):
        """Включили программу: один раз — очистить чат бота (по просьбе), потом сразу прислать файлы на сегодня."""
        from . import telegram, tg_assist
        if not telegram.load().get("token") or tg_assist.mode() != "telegram_assist":
            return
        if paths.team_dir() and not self.v["team_main"].get():
            return
        if getattr(self, "_assist_busy", False):
            self.root.after(15000, self._tg_on_start)
            return
        self._assist_busy = True

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            try:
                c = telegram.load()
                if c.get("cleared_v") != self.CLEAR_CHAT_V:
                    tg_assist.clear_chat(event)
                    c = telegram.load()
                    c["cleared_v"] = self.CLEAR_CHAT_V
                    telegram.save(c)
                tg_assist.send_today(event)
            except Exception as e:
                event("❌", T("Telegram: не получилось прислать видео на сегодня — {0}").format(e), None, "error")
            self.root.after(0, done)

        def done():
            self._assist_busy = False
        threading.Thread(target=work, daemon=True).start()

    def wipe_all(self):
        """Полная очистка: клипы — в корзину, архив, план, очередь Telegram, отметки и память разбора — с нуля.
        Перед этим Хранитель данных делает резервную копию."""
        from . import backup
        if self.proc:
            messagebox.showinfo(T("Чистый лист"), T("Сначала нажми «Стоп» — программа сейчас работает."))
            return
        if not messagebox.askyesno(T("Чистый лист"), T(
                "Убрать ВСЕ клипы и начать с нуля?\n\n"
                "• все клипы и архив уйдут в корзину (вернуть можно, пока корзину не очистили);\n"
                "• план, очередь Telegram, отметки «выложено» и решения агентов очистятся;\n"
                "• стримы забудутся — их можно будет разобрать заново.\n\n"
                "Перед этим Хранитель данных сделает резервную копию.")):
            return
        self.status.config(text=T("Делаю копию и очищаю..."))
        if self.preview.path:
            self.preview.release()

        def work():
            try:
                res, err = backup.wipe_all(log=lambda m: None), None
            except Exception as e:
                res, err = {}, e
            self.root.after(0, lambda: done(res, err))

        def done(res, err):
            if err:
                messagebox.showwarning(T("Чистый лист"), T("Не получилось: {0}").format(err))
                return
            self.images.clear()
            self.activity.event("🧹", T("Чистый лист: клипов в корзину — {0}, из архива — {1}. План и отметки очищены.").format(
                res["clips"], res["archive"]))
            self.status.config(text=T("Готово — начинаем с чистого листа. Копия: {0}").format(res["backup"]))
            self.refresh_clips()
            try:
                self.refresh_plan()
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    def sweep_sleepy(self, auto: bool = False):
        """Проверить ВСЕ клипы фильтрами «стример спит» и убрать не прошедшие в архив (один раз — сам при запуске)."""
        from . import autopilot
        if getattr(self, "_sweep_busy", False):
            return
        if paths.team_dir() and not self.v["team_main"].get():
            return
        st = autopilot.load_state()
        if auto and st.get("sweep_all_v") == autopilot.SWEEP_V:
            return
        self._sweep_busy = True
        self.activity.event("💤", T("Проверяю все клипы: где стример спит — уберу в архив"))

        def say(msg):
            self.root.after(0, lambda: self.status.config(text=tr_line(msg)[:140]))

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            try:
                res, err = autopilot.sweep_all(event, say), None
                st2 = autopilot.load_state()
                st2["sweep_all_v"] = autopilot.SWEEP_V
                autopilot.save_state(st2)
            except Exception as e:
                res, err = {}, e
            self.root.after(0, lambda: done(res, err))

        def done(res, err):
            self._sweep_busy = False
            if err:
                self.activity.event("❌", T("Проверка клипов не удалась: {0}").format(err), kind="error")
                return
            self.activity.event("💤", T("Проверено клипов: {0}, убрано в архив (стример спит): {1}, снято с плана: {2}")
                                .format(res["checked"], res["archived"], res["plan_removed"]))
            self.status.config(text=T("Готово: убрано в архив {0} клипов, где стример спит").format(res["archived"]))
            self.refresh_clips()
        threading.Thread(target=work, daemon=True).start()

    def pick_best_clips(self):
        """«🏆 Оставить лучшие»: из готовых клипов оставить только сильные и без брака — не больше «Клипов за час»
        на час стрима; остальные — в архив (вернуть можно), выложенные не трогаются."""
        from . import autopilot
        if getattr(self, "_pick_busy", False):
            return
        try:
            per_hour = max(1, int(str(self.v["top"].get())))
        except ValueError:
            per_hour = 3
        self._pick_busy = True
        self.activity.event("🏆", T("Отбираю лучшие клипы: не больше {0} за час стрима, без лага, тихого начала и "
                                    "спящих стримеров").format(per_hour))

        def say(msg):
            self.root.after(0, lambda: self.status.config(text=tr_line(msg)[:140]))

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            try:
                res, err = autopilot.pick_best(per_hour, say), None
            except Exception as e:
                res, err = None, e
            self.root.after(0, lambda: ask(res, err))

        def ask(res, err):
            if err:
                self._pick_busy = False
                self.activity.event("❌", T("Отбор не получился: {0}").format(err), kind="error")
                return
            drop = res["drop"]
            if not drop:
                self._pick_busy = False
                self.status.config(text=T("Все {0} клипов прошли отбор — убирать нечего").format(res["total"]))
                self.activity.event("🏆", T("Все {0} клипов прошли отбор — убирать нечего").format(res["total"]))
                return
            kinds = {}
            for _c, why in drop:
                k = (T("лагает") if "стоп-кадр" in why or "подвис" in why or "лаг" in why
                     else T("тихое начало") if "первые 2 секунды" in why
                     else T("стример спит") if "спит" in why or "активност" in why
                     else T("слабее или лишние сверх квоты"))
                kinds[k] = kinds.get(k, 0) + 1
            detail = "\n".join(f"  • {k}: {n}" for k, n in kinds.items())
            msg = T("Из {0} клипов ({1} стримов) оставлю {2} — не больше {3} за час стрима.\n\n"
                    "В архив уйдут {4}:\n{5}\n\nПлохие снимутся с плана и из Telegram, план переделается под лучшие. "
                    "Выложенные клипы не трогаю. Вернуть любой можно из вкладки «Архив». Продолжить?").format(res["total"], res["streams"], len(res["keep"]), per_hour,
                                                    len(drop), detail)
            if not messagebox.askyesno(T("🏆 Оставить лучшие"), msg):
                self._pick_busy = False
                return

            def work2():
                try:
                    from .caption import _api_key
                    r, e2 = autopilot.apply_pick(drop, event, res["keep"], say, _api_key()), None
                except Exception as e:
                    r, e2 = None, e
                self.root.after(0, lambda: done(r, e2, len(res["keep"])))
            threading.Thread(target=work2, daemon=True).start()

        def done(r, err, kept):
            self._pick_busy = False
            if err:
                self.activity.event("❌", T("Отбор не получился: {0}").format(err), kind="error")
                return
            self.activity.event("🏆", T("Отбор готов: оставлено {0}, в архив {1}, снято с плана {2}. "
                                        "План переделан: в нём {3} публикаций, только лучшие клипы")
                                .format(kept, r["archived"], r["plan_removed"], r["planned"]))
            self.status.config(text=T("Отбор готов: оставлено {0} лучших клипов, в плане {1}").format(kept, r["planned"]))
            self.refresh_clips()
            try:
                self.refresh_plan()
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    # ---------- вкладка «План»: что и когда выйдет ----------
    def _build_plan(self, parent):
        top = ttk.Frame(parent)
        top.pack(fill="x")
        ttk.Label(top, text=T("Что и когда выйдет. Время — по Москве и по США (ET). Клип в корзине или архиве из плана "
                              "уходит сам, его время получает следующий."), foreground=self.muted,
                  wraplength=900, justify="left").pack(side="left")
        btns = ttk.Frame(parent)
        btns.pack(fill="x", pady=6)
        self.plan_btns = btns
        ttk.Button(btns, text=T("⬆ Поднять выше"), command=lambda: self._plan_action("raise")).pack(side="left")
        ttk.Button(btns, text=T("✕ Убрать из плана"), command=lambda: self._plan_action("remove")).pack(side="left", padx=6)
        ttk.Button(btns, text=T("▶ Открыть клип"), command=lambda: self._plan_action("open")).pack(side="left")
        ttk.Button(btns, text=T("🔁 Отправить ещё раз"), command=self._plan_resend).pack(side="left", padx=6)
        ttk.Button(btns, text=T("⟳ Пересобрать план"), command=lambda: self._plan_action("rebuild")).pack(side="right")
        ttk.Button(btns, text=T("⚡ Заполнить план сейчас"), command=self._fill_plan).pack(side="right", padx=6)
        ttk.Button(btns, text=T("📤 Видео на сегодня — в Telegram"), command=self._send_ahead).pack(side="right", padx=6)
        ttk.Button(btns, text=T("📋 План — в Telegram"), command=self._plan_to_tg).pack(side="right")
        self.plan_status = ttk.Label(btns, text="", foreground=self.muted)
        self.plan_status.pack(side="right", padx=8)
        cols = ("day", "msk", "et", "platform", "streamer", "clip", "state")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        for c, t_, w in (("day", T("Дата"), 70), ("msk", T("МСК"), 60), ("et", "ET", 60), ("platform", T("Где"), 90),
                         ("streamer", T("Стример"), 120), ("clip", T("Клип / название"), 420), ("state", T("Статус"), 150)):
            tree.heading(c, text=t_)
            tree.column(c, width=w, stretch=c == "clip", anchor="w")
        tree.pack(fill="both", expand=True)
        self.plan_tree = tree
        self.plan_why = ttk.Label(parent, text="", foreground=self.muted, wraplength=1100, justify="left")
        self.plan_why.pack(anchor="w", pady=(6, 0))
        self.plan_rows: dict = {}

    def refresh_plan(self):
        from datetime import datetime as _dt
        from . import autopilot, schedule
        try:  # удалённые, архивные и выложенные клипы — вон из плана, их время — следующим
            autopilot.rebuild_schedule()
        except Exception:
            pass
        tree = self.plan_tree
        tree.delete(*tree.get_children())
        self.plan_rows.clear()
        names = {"tiktok": "TikTok", "youtube": "YouTube", "instagram": "Instagram"}
        chans = {os.path.normpath(c["path"]): c.get("channel", "") for d in library.list_dates() for c in library.list_clips(d)}
        rows = autopilot.plan_rows()
        for r in rows:
            try:
                t = _dt.fromisoformat(r["when"])
                day, msk, et = schedule.day_label(t), f"{schedule.msk(t):%H:%M}", f"{schedule.et(t):%H:%M}"
            except (TypeError, ValueError):
                day = msk = et = "—"
            state = T("отправлено в Telegram") if r.get("sent") else (T("⬆ поднят") if r.get("pin") else T("ждёт"))
            iid = tree.insert("", "end", values=(day, msk, et, names.get(r["platform"], r["platform"]),
                                                 chans.get(os.path.normpath(r["path"]), ""),
                                                 f"{os.path.basename(r['path'])[:-4]} — {r.get('title') or ''}", state))
            self.plan_rows[iid] = r
        self.plan_status.config(text=T("в плане: {0}").format(len(rows)))
        self.plan_why.config(text="")
        if len(rows) < 3:  # план пустой или почти — объясняем почему
            threading.Thread(target=self._plan_explain, daemon=True).start()

    def _plan_explain(self):
        from . import autopilot
        try:
            d = autopilot.plan_diagnosis()
        except Exception as e:
            self.root.after(0, lambda: self.plan_why.config(text=T("Не удалось разобрать, почему план пуст: {0}").format(e)))
            return
        lines = [T("Почему в плане мало: клипов в папке — {0}; уже выложено — {1}; стримеры не на языке канала — {2}; "
                   "ждут отбора автопилотом — {3}; оценка ниже порога ({4:.0f}) — {5}; отклонены — {6}.").format(
            d["clips"], d["posted"], d["foreign"], d["waiting_review"], d["min_score"], d["low_score"], d["rejected"])]
        if d["archive_reasons"]:
            lines.append(T("В архиве: ") + "; ".join(f"{tr_line(r)} — {n}" for r, n in d["archive_reasons"]))
        if not self.v["autopilot"].get():
            lines.append(T("⚠ Автопилот выключен (вкладка «Управление») — без него план не заполняется."))
        elif paths.team_dir() and not self.v["team_main"].get():
            lines.append(T("⚠ План ведёт компьютер друга (общая папка) — здесь он не заполняется."))
        if d["waiting_review"]:
            lines.append(T("Нажми «⚡ Заполнить план сейчас» — автопилот сразу отберёт и смонтирует клипы."))
        elif d["low_score"] and not d["waiting_review"]:
            lines.append(T("Все свободные клипы ниже порога оценки — «⚡ Заполнить план сейчас» возьмёт лучшие из них."))
        self.root.after(0, lambda: self.plan_why.config(text="\n".join(lines)))

    def _fill_plan(self):
        from . import autopilot, strategy
        from .caption import _api_key
        if getattr(self, "_autopilot_busy", False):
            self.plan_status.config(text=T("автопилот уже работает — подожди"))
            return
        self._autopilot_busy = True
        self.plan_status.config(text=T("заполняю план: отбираю и монтирую клипы..."))

        def say(msg):
            self.root.after(0, lambda: self.plan_status.config(text=tr_line(msg)[:120]))

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            try:
                st = autopilot.fill_plan(say, event, _api_key())
                if not autopilot.plan_rows():  # всё ниже порога — берём лучшие из того, что есть
                    s = strategy.get()
                    ap = s.setdefault("autopilot", {})
                    old = ap.get("min_score_to_post", 55)
                    over = strategy.user_overrides()
                    over.setdefault("autopilot", {})["min_score_to_post"] = max(30, float(old) - 20)
                    strategy.save_user_overrides(over)
                    try:
                        st = autopilot.fill_plan(say, event, _api_key())
                    finally:
                        over = strategy.user_overrides()
                        (over.get("autopilot") or {}).pop("min_score_to_post", None)
                        strategy.save_user_overrides(over)
                err = None
            except Exception as e:
                st, err = {}, e
            self.root.after(0, lambda: done(st, err))

        def done(st, err):
            self._autopilot_busy = False
            if err:
                self.plan_status.config(text=T("не получилось: {0}").format(err))
            self.refresh_plan()
        threading.Thread(target=work, daemon=True).start()

    def _plan_to_tg(self):
        from . import tg_assist
        threading.Thread(target=lambda: (tg_assist.send_plan(None, 24),
                                         self.root.after(0, lambda: self.plan_status.config(text=T("план отправлен в Telegram")))),
                         daemon=True).start()

    def _send_ahead(self, then=None):
        """Все видео из плана на 2 дня — в Telegram сейчас (перед выключением компьютера)."""
        from . import tg_assist
        self.status.config(text=T("Отправляю в Telegram видео на сегодня... не закрывай программу"))

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            try:
                res, err = tg_assist.send_ahead(event), None
            except Exception as e:
                res, err = {}, e
            self.root.after(0, lambda: done(res, err))

        def done(res, err):
            self._ahead_done = True
            if err:
                messagebox.showwarning("Telegram", T("Не получилось отправить: {0}").format(err))
            else:
                messagebox.showinfo("Telegram", T("Отправлено видео: {0}. Запланируйте их в приложениях на время, "
                                                  "указанное у каждого.").format(res.get("sent", 0)))
            if then:
                then()
        threading.Thread(target=work, daemon=True).start()

    def _plan_resend(self):
        """Выбранные строки плана (или весь план на сутки) — снова в Telegram, даже если уже отправлялись."""
        from . import tg_assist
        sel = self.plan_tree.selection()
        rows = [self.plan_rows[i] for i in sel if i in self.plan_rows]
        if rows:
            items = [(r["path"], r["platform"]) for r in rows]
            msg = T("Отправить в Telegram ещё раз выбранные видео: {0}?").format(len(items))
        else:
            items = None
            msg = T("Ничего не выбрано. Отправить в Telegram ещё раз ВСЕ видео из плана на ближайшие сутки?")
        if not messagebox.askyesno(T("🔁 Отправить ещё раз"), msg):
            return
        self.plan_status.config(text=T("отправляю в Telegram..."))

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: (self.activity.event(icon, tr_line(text), path, kind),
                                        self.plan_status.config(text=tr_line(text)[:90])))

        def work():
            try:
                res, err = tg_assist.resend(items, event), None
            except Exception as e:
                res, err = {}, e
            self.root.after(0, lambda: done(res, err))

        def done(res, err):
            if err:
                messagebox.showwarning("Telegram", T("Не получилось отправить: {0}").format(err))
                return
            self.plan_status.config(text=T("отправлено ещё раз: {0} из {1}").format(res["sent"], res["total"]))
            self.activity.event("🔁", T("Telegram: отправлено ещё раз {0} из {1}").format(res["sent"], res["total"])
                                + (T(", не ушло {0}").format(res["failed"]) if res["failed"] else ""))
            self.refresh_plan()
        threading.Thread(target=work, daemon=True).start()

    def _plan_action(self, what: str):
        from . import autopilot
        if what == "rebuild":
            def work():
                try:
                    autopilot.rebuild_schedule()
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showwarning(T("План"), str(e)))
                self.root.after(0, self.refresh_plan)
            threading.Thread(target=work, daemon=True).start()
            return
        sel = self.plan_tree.selection()
        r = self.plan_rows.get(sel[0]) if sel else None
        if not r:
            messagebox.showinfo(T("План"), T("Выбери строку в плане."))
            return
        if what == "open":
            self._open(r["path"])
            return
        if what == "remove":
            autopilot.plan_remove(r["path"], r["platform"])
        else:
            autopilot.plan_raise(r["path"], r["platform"])
        self.refresh_plan()

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
        ttk.Button(btns, text=T("⏪  Другое время (отмотать)"), command=self.rewind_stream).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🗑  Забыть стрим (разобрать заново)"), command=self.forget_stream).pack(side="left")
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=6)
        cols = ("date", "title", "link", "upto", "live")
        self.st_tree = ttk.Treeview(frame, columns=cols, show="tree headings", selectmode="browse")
        self.st_tree.heading("#0", text=T("Стример"))
        self.st_tree.column("#0", width=115, stretch=False)
        for c, title, w in (("date", T("Дата стрима"), 110), ("title", T("Название"), 300),
                            ("link", T("Ссылка"), 220), ("upto", T("Разобрано до"), 150), ("live", T("Эфир"), 110)):
            self.st_tree.heading(c, text=title)
            self.st_tree.column(c, width=w, stretch=(c == "title"),
                                anchor="w" if c == "title" else "center")
        self.st_tree.tag_configure("live", foreground="#ff4d4d")
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
    def _clips_click(self, e):
        """Клик по колонке «Автор» — поставить или снять подпись автора на этом клипе."""
        if self.tree.identify_region(e.x, e.y) != "cell" or self.tree.identify_column(e.x) != "#3":
            return
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        if iid not in self.tree.selection():
            self.tree.selection_set(iid)
        self.root.after(10, self.toggle_credit)
        return "break"

    def toggle_credit(self):
        """Подпись «Twitch | KaiCenat» на выбранных клипах: у кого нет — поставить, у кого есть — снять."""
        from . import credit
        sel = self._selected()
        if not sel:
            return
        if getattr(self, "_credit_busy", False):
            self.clips_info.config(text=T("Подождите — предыдущая подпись ещё накладывается..."))
            return
        data = credit.load()
        states = [credit.state(c, data) for c in sel]
        if all(st == "burned" for st in states):
            messagebox.showinfo(T("Автор"), T("Подпись на этом клипе вшита при нарезке — снять её нельзя."))
            return
        turn_on = any(st in ("off", "unknown") for st in states)
        todo = [c for c, st in zip(sel, states) if (st in ("off", "unknown")) == turn_on and st != "burned"]
        if turn_on and any(st == "unknown" for c, st in zip(sel, states) if c in todo):
            if not messagebox.askyesno(T("Автор"), T("Этот клип нарезан до обновления — на нём уже может быть подпись "
                                                    "автора (раньше она ставилась всем клипам). Посмотри превью справа. "
                                                    "Всё равно подписать?")):
                return
        pos = CREDIT_POS.get(self.v["credit_pos"].get(), "top-left")
        if self.preview.path in {c["path"] for c in todo}:
            self.preview.release()
        self._credit_busy = True
        self.clips_info.config(text=(T("Подписываю автора на клипах: {0}...") if turn_on
                                     else T("Убираю подпись автора: {0}...")).format(len(todo)))

        def work():
            errors = []
            import copy
            from . import edits
            for c in todo:
                try:
                    rec = copy.deepcopy(edits.ensure(c))
                    if turn_on:
                        edits.add_op(rec, {"type": "credit", "pos": pos})
                    else:
                        ids = [o["id"] for o in rec["ops"] if o["type"] == "credit"]
                        if not ids:
                            raise ValueError(T("подпись вшита при нарезке — снять её нельзя"))
                        for i in ids:
                            edits.remove_op(rec, i)
                    out = os.path.join(paths.default_work_dir(), "edits", f"cr_{int(time.time() * 1000)}.mp4")
                    fields = edits.build(c, rec, out)
                    edits.commit(c, rec, out, fields)
                except Exception as ex:
                    errors.append(f"{c.get('channel', '')}: {ex}")
            self.root.after(0, lambda: done(errors))

        def done(errors):
            self._credit_busy = False
            for c in todo:
                self.images.pop(c["path"], None)
            self.refresh_clips()
            if errors:
                messagebox.showwarning(T("Автор"), "\n".join(tr_line(x) for x in errors))
            else:
                self.clips_info.config(text=(T("Готово: автор подписан ({0} шт.). Снять — ещё раз нажми на галочку.")
                                             if turn_on else T("Готово: подпись убрана ({0} шт.).")).format(len(todo)))
        threading.Thread(target=work, daemon=True).start()

    _SHORT = {"youtube": "YT", "tiktok": "TT", "instagram": "IG"}

    def _posted_cell(self, c: dict, platform: str, by_map: dict) -> str:
        """«✔» — выложено; в общей папке — «✔ Д», если выложил друг (первая буква имени)."""
        if not c["posted"].get(platform):
            return "—"
        who = (by_map.get(os.path.normpath(c["path"])) or {}).get(platform, "")
        if who and who != paths.user_name():
            return "✔ " + who[:1].upper()
        return "✔"

    def _advice_cell(self, c: dict, adv: dict | None) -> str:
        """Колонка «Совет»: куда «Доктор» советует выложить (ещё не выложенное) или «🗑», если советует удалить."""
        if not adv:
            return "—"
        if adv.get("delete"):
            return "🗑"
        parts = []
        for pl, p in adv.get("platforms", {}).items():
            if p.get("post") and not c["posted"].get(pl):
                when = p.get("when") or ""
                today = time.strftime("%Y-%m-%d")
                w = when[11:16] if when[:10] == today else (f"{when[8:10]}.{when[5:7]}" if len(when) >= 10 else "")
                parts.append(self._SHORT.get(pl, pl) + (f" {w}" if w else ""))
        return " · ".join(parts) or "✔"

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
        from . import edits, policy
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
                # сомнительное (Claude не указал место — пришлось бы размыть весь кадр) по умолчанию не отмечено
                i.setdefault("on", (i.get("severity") == "high" or i["kind"] in ("profanity",))
                             and not (i.get("source") == "video" and not i.get("box")))
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
            release_players()
            try:
                edits.commit(c, state["trial"], fixed_path, state["fields"])
            except OSError as e:
                messagebox.showerror(T("Нарушения"), T("Не получилось заменить файл: {0}").format(e), parent=win)
                return
            win.destroy()
            self.policy_window = None
            self.images.pop(c["path"], None)
            self.refresh_clips()
            self.clips_info.config(text=T("Готово: размытие/запикивание сохранено как правка — убрать его можно в «🕘 Правки»."))

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
            out = os.path.join(out_dir, f"fixed_{int(time.time())}_" + os.path.basename(c["path"]))

            def work():
                import copy
                try:
                    if not c.get("words") and (c.get("policy") or {}).get("words"):
                        c["words"] = c["policy"]["words"]
                    rec = copy.deepcopy(edits.ensure(c))
                    _, shift = edits.source(rec)
                    a0 = edits.total_cut(rec)[0] - shift  # время в клипе → время в исходнике
                    issues = [dict(i, t0=i["t0"] + a0, t1=i["t1"] + a0 if i["t1"] < 10 ** 5 else i["t1"])
                              for i in chosen]
                    edits.add_op(rec, {"type": "fix", "issues": issues})
                    state["fields"] = edits.build(c, rec, out)
                    state["trial"] = rec
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
        if res and res.get("nudity_v") == 2 and (res.get("issues") or res.get("visual") or res.get("words")):
            fill(res)
        elif res:  # клип проверяли старой версией (без поиска обнажёнки) — показываем, что есть, и проверяем заново
            fill(res)
            recheck()
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

    # ---------- перерезка клипа (удлинение) в отдельном процессе ----------
    def _run_recut(self, c: dict, start: float, end: float, say, on_done):
        """Качает кусок записи стрима [start, end] и собирает клип с той же надписью. on_done(result | None, error)."""
        work = os.path.join(paths.default_work_dir(), "recut")
        os.makedirs(work, exist_ok=True)
        stamp = str(int(time.time() * 1000))
        job = {"url": c["_src_url"], "start": start, "end": end, "out": os.path.join(work, f"new_{stamp}.mp4"),
               "result": os.path.join(work, f"result_{stamp}.json"),
               "meta": {"streamer": c.get("channel", ""), "title": c.get("vod_title", ""), "lang": c.get("lang", "en"),
                        "platform": c.get("platform") or ("YouTube" if "youtu" in c["_src_url"] else "Twitch"),
                        "credit_name": c.get("credit_name") or c.get("channel", ""),
                        "caption_text": c.get("caption") or "", "top_messages": []}}
        job_path = os.path.join(work, f"job_{stamp}.json")
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False)
        cmd = [_python_exe(), "-m", "stream_clipper", "recut", job_path, *self._flags()]
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        flags = 0x08000000 if os.name == "nt" else 0

        def work_():
            try:
                p = subprocess.Popen(cmd, cwd=PROG, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, creationflags=flags)
                for raw in iter(p.stdout.readline, b""):
                    line = raw.decode("utf-8", errors="replace").strip()
                    if line:
                        self.root.after(0, lambda l=line: say(tr_line(l)))
                p.wait()
                with open(job["result"], encoding="utf-8") as f:
                    res = json.load(f)
                err = res.get("error")
            except Exception as e:
                res, err = None, f"{type(e).__name__}: {e}"
            self.root.after(0, lambda: on_done(None if err else res, err))
        threading.Thread(target=work_, daemon=True).start()

    def _replace_clip(self, c: dict, new_file: str, fields: dict):
        """Ставит новую версию клипа на место старой; старая уходит в корзину (её можно вернуть)."""
        import shutil
        from . import credit, policy
        if self.preview.path == c["path"]:
            self.preview.release()
        library.move_to_trash(c, c.get("score10"))
        shutil.move(new_file, c["path"])
        library.make_thumb(c["path"])
        self.images.pop(c["path"], None)
        library.update_clip(c["path"], fields)
        data = credit.load()  # прежняя подпись автора к новому файлу не относится
        if data.pop(os.path.normpath(c["path"]), None) is not None:
            credit._save(data)
        words = fields.get("words") or []
        policy.save_result(c["path"], {"issues": policy.check_words(words), "visual": False, "words": words,
                                       "note": "", "checked": time.time()})

    def edit_clip(self):
        """Окно «Изменить длину»: обрезать начало/конец или удлинить (если есть запись стрима)."""
        from . import clipedit, edits
        sel = self._selected()
        if not sel:
            return
        c = dict(sel[0])
        src = clipedit.source_range(c)
        if src:
            c["_src_url"] = src[0]
        L = clipedit.duration(c["path"]) or float(c.get("end", 0)) - float(c.get("start", 0))
        win = tk.Toplevel(self.root)
        win.title(T("Изменить длину — {0}").format(c.get("channel", "")))
        win.transient(self.root)
        win.geometry("900x760")
        self.edit_window = win
        body = ttk.Frame(win, padding=10)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(body, padding=(12, 0))
        right.pack(side="left", fill="y")
        player = VideoPreview(left, self, big=True)
        player.pack(fill="both", expand=True)
        win.after(300, lambda: player.load(c["path"]))
        ttk.Label(right, text=f"«{(c.get('caption') or '')[:40]}»", font=("Segoe UI", 11, "bold"),
                  wraplength=330).pack(anchor="w")
        ttk.Label(right, text=T("Сейчас клип длится {0:.0f} с").format(L)).pack(anchor="w", pady=(4, 10))
        add_start, add_end = tk.DoubleVar(value=0), tk.DoubleVar(value=0)
        for title, var in ((T("В начале, сек:"), add_start), (T("В конце, сек:"), add_end)):
            row = ttk.Frame(right)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=title, width=16).pack(side="left")
            ttk.Spinbox(row, from_=-int(L) + 1, to=60, increment=1, textvariable=var, width=7).pack(side="left")
        ttk.Label(right, foreground=self.muted, wraplength=330, justify="left",
                  text=T("+5 — добавить 5 секунд, −3 — отрезать 3 секунды.")).pack(anchor="w", pady=(2, 8))

        def cut_here(which):
            t = player.pos / (player.fps or 30.0) if player.path else 0.0
            if which == "start":
                add_start.set(-round(t, 1))
            else:
                add_end.set(-round(max(0.0, L - t), 1))
        ttk.Button(right, text=T("✂ Отрезать всё ДО текущего кадра"), command=lambda: cut_here("start")).pack(fill="x")
        ttk.Button(right, text=T("✂ Отрезать всё ПОСЛЕ текущего кадра"), command=lambda: cut_here("end")).pack(fill="x",
                                                                                                         pady=4)
        result_lbl = ttk.Label(right, text="", font=("Segoe UI", 10, "bold"))
        result_lbl.pack(anchor="w", pady=(8, 0))
        ttk.Label(right, foreground=self.muted, wraplength=330, justify="left",
                  text=T("Удлинять можно: программа заново скачает кусок записи стрима.") if src else
                  T("Удлинить нельзя: у этого эфира нет сохранённой записи. Обрезать — можно.")).pack(anchor="w", pady=4)
        status = ttk.Label(right, text="", foreground=self.muted, wraplength=330, justify="left")
        status.pack(anchor="w", pady=(6, 0))

        def values():
            try:
                return float(add_start.get()), float(add_end.get())
            except (tk.TclError, ValueError):
                return 0.0, 0.0

        def upd(*_):
            a, b = values()
            result_lbl.config(text=T("Будет: {0:.0f} с (было {1:.0f} с)").format(max(0.0, L + a + b), L))
        add_start.trace_add("write", upd)
        add_end.trace_add("write", upd)
        upd()
        cmp_box = ttk.Frame(right)
        state = {"new": None}

        def show_new(new_file, fields):
            state["new"], state["fields"] = new_file, fields
            player.release()
            for w in cmp_box.winfo_children():
                w.destroy()
            cmp_box.pack(fill="x", pady=(10, 0))
            ttk.Label(cmp_box, text=T("Слева — НОВАЯ версия. Сравни и выбери:"), font=("Segoe UI", 10, "bold")).pack(anchor="w")
            row = ttk.Frame(cmp_box)
            row.pack(fill="x", pady=4)
            ttk.Button(row, text=T("👁 Новая"), command=lambda: (player.load(new_file), player.toggle())).pack(side="left")
            ttk.Button(row, text=T("👁 Как было"), command=lambda: (player.load(c["path"]), player.toggle())).pack(side="left",
                                                                                                           padx=4)
            ttk.Button(cmp_box, text=T("✔  Оставить новую"), style="Big.TButton", command=keep).pack(fill="x", pady=(4, 2))
            ttk.Button(cmp_box, text=T("↩  Оставить как было"), command=discard).pack(fill="x")
            win.after(200, lambda: (player.load(new_file), player.toggle()))

        def keep():
            player.release()
            if self.preview.path == c["path"]:
                self.preview.release()
            try:
                edits.commit(c, state["trial"], state["new"], state["fields"])
            except OSError as e:
                messagebox.showerror(T("Изменить длину"), str(e), parent=win)
                return
            win.destroy()
            self.images.pop(c["path"], None)
            self.refresh_clips()
            self.clips_info.config(text=T("Готово: клип изменён. Отменить — «🕘 Правки»."))

        def discard():
            player.release()
            try:
                os.remove(state["new"])
            except (OSError, TypeError):
                pass
            for w in cmp_box.winfo_children():
                w.destroy()
            cmp_box.pack_forget()
            player.load(c["path"])
            status.config(text=T("Оставлено как было."))

        def apply():
            a, b = values()
            if a == 0 and b == 0:
                status.config(text=T("Сначала укажи, сколько добавить или отрезать."))
                return
            if L + a + b < 2:
                status.config(text=T("Клип получится слишком коротким."))
                return
            b_apply.config(state="disabled")
            if a <= 0 and b <= 0:  # только обрезка — быстро, из готового файла
                status.config(text=T("Обрезаю..."))
                out = os.path.join(paths.default_work_dir(), "recut", f"trim_{int(time.time())}.mp4")
                os.makedirs(os.path.dirname(out), exist_ok=True)

                def work_():
                    import copy
                    try:
                        rec = copy.deepcopy(edits.ensure(c))
                        edits.add_op(rec, {"type": "trim", "cut_start": -a, "cut_end": -b})
                        fields = edits.build(c, rec, out)
                        state["trial"] = rec
                        err = None
                    except Exception as e:
                        err, fields = e, None
                    self.root.after(0, lambda: done_trim(err, fields))

                def done_trim(err, fields):
                    b_apply.config(state="normal")
                    if err:
                        status.config(text=T("Не получилось: {0}").format(err))
                        return
                    status.config(text="")
                    show_new(out, fields)
                threading.Thread(target=work_, daemon=True).start()
                return
            if not src:
                b_apply.config(state="normal")
                status.config(text=T("Удлинить нельзя: у этого эфира нет сохранённой записи. Обрезать — можно."))
                return
            url, s0, e0 = src
            ns, ne = max(0.0, s0 - a), e0 + b
            status.config(text=T("Качаю кусок стрима и собираю клип... (1–2 минуты)"))

            def done_recut(res, err):
                if err:
                    b_apply.config(state="normal")
                    status.config(text=T("Не получилось: {0}").format(tr_line(err)))
                    return
                status.config(text=T("Собираю клип с правками..."))

                def work_():
                    import copy
                    import shutil
                    try:
                        rec = copy.deepcopy(edits.ensure(c))
                        keep_file = os.path.join(paths.default_work_dir(), "edits", f"recut_{int(time.time() * 1000)}.mp4")
                        shutil.move(res["file"], keep_file)
                        orig0 = rec["moment"] if rec.get("moment") is not None else (rec.get("range") or [0])[0] or 0
                        edits.add_op(rec, {"type": "recut", "file": keep_file, "range": [ns, ne],
                                           "shift": float(orig0) - ns, "words": res.get("words") or []})
                        out = os.path.join(paths.default_work_dir(), "edits", f"ext_{int(time.time() * 1000)}.mp4")
                        fields = edits.build(c, rec, out)
                        fields["transcript"] = res.get("transcript", "")
                        state["trial"] = rec
                        self.root.after(0, lambda: (b_apply.config(state="normal"), status.config(text=""),
                                                    show_new(out, fields)))
                    except Exception as e:
                        self.root.after(0, lambda: (b_apply.config(state="normal"),
                                                    status.config(text=T("Не получилось: {0}").format(e))))
                threading.Thread(target=work_, daemon=True).start()
            self._run_recut(c, ns, ne, lambda m: status.config(text=m), done_recut)
        b_apply = ttk.Button(right, text=T("✔  Применить"), style="Big.TButton", command=apply)
        b_apply.pack(fill="x", pady=(10, 0))
        ttk.Button(right, text=T("Закрыть"), command=lambda: (player.release(), discard() if state["new"] else None,
                                                              win.destroy())).pack(fill="x", pady=(4, 0))
        win.protocol("WM_DELETE_WINDOW", lambda: (player.release(), win.destroy()))

    # ---------- корзина ----------
    def open_trash(self):
        """Корзина: удалённые клипы с их оценками — вернуть, нарезать заново (если файл удалён раньше) или стереть."""
        from . import clipedit
        win = tk.Toplevel(self.root)
        win.title(T("Корзина"))
        win.transient(self.root)
        win.geometry("1150x720")
        self.trash_window = win
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        info = ttk.Label(frm, text="", foreground=self.muted, wraplength=1100, justify="left")
        info.pack(anchor="w")
        panes = ttk.Panedwindow(frm, orient="horizontal")
        panes.pack(fill="both", expand=True, pady=6)
        lf = ttk.Frame(panes)
        player = VideoPreview(panes, self)
        panes.add(lf, weight=3)
        panes.add(player, weight=2)
        cols = ("rating", "streamer", "moment", "caption", "where", "when")
        tree = ttk.Treeview(lf, columns=cols, show="headings", selectmode="extended")
        for col, title, w in (("rating", T("Интерес"), 70), ("streamer", T("Стример"), 110), ("moment", T("Момент"), 70),
                              ("caption", T("Надпись"), 260), ("where", T("Где"), 230), ("when", T("Удалён"), 90)):
            tree.heading(col, text=title)
            tree.column(col, width=w, stretch=col == "caption", anchor="w" if col in ("caption", "where") else "center")
        sb = ttk.Scrollbar(lf, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        rows: dict = {}

        def fill():
            from datetime import datetime
            tree.delete(*tree.get_children())
            rows.clear()
            trash = library.load_trash()
            from . import archive as _arch
            in_trash = {t["orig"] for t in trash} | _arch.archived_paths()
            dates = library.list_dates()
            pool = [x for d in dates for x in library.list_clips(d, include_missing=True)]
            scores = library.frozen_ratings(pool)
            items = []
            for t in trash:
                size = os.path.getsize(t["file"]) / 1e6 if os.path.exists(t["file"]) else 0
                items.append(("trash", t, t.get("score10") or scores.get(t["orig"], 1),
                              T("в корзине · {0:.0f} МБ").format(size),
                              datetime.fromtimestamp(t.get("trashed", 0)).strftime("%d.%m %H:%M")))
            for x in pool:
                if x.get("missing") and not x.get("dismissed") and x["path"] not in in_trash:
                    can = clipedit.source_range(x) is not None
                    items.append(("gone", x, scores.get(x["path"], 1),
                                  T("файл удалён — можно нарезать заново") if can else T("файл удалён, записи стрима нет"),
                                  x.get("date", "")))
            items.sort(key=lambda it: -(it[2] or 0))
            total = 0.0
            for kind, x, score, where, when in items:
                sec = int(x.get("moment", x.get("start", 0)) or 0)
                iid = tree.insert("", "end", values=(f"{score}/10", x.get("channel", ""),
                                                     f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}",
                                                     x.get("caption") or "—", where, when))
                rows[iid] = (kind, x)
                if kind == "trash" and os.path.exists(x["file"]):
                    total += os.path.getsize(x["file"])
            n_trash = sum(1 for k, _ in rows.values() if k == "trash")
            info.config(text=T("В корзине: {0} клипов ({1:.0f} МБ). Место на диске освобождается только после «Удалить "
                               "навсегда». Клипы, удалённые до появления корзины, можно нарезать заново из записи стрима "
                               "— оценки у них сохранились.").format(n_trash, total / 1e6))
            b_clear.config(text=T("🧹 Очистить корзину ({0:.0f} МБ)").format(total / 1e6))
            self._update_trash_button()

        def selected():
            return [rows[i] for i in tree.selection() if i in rows]

        def on_select(e=None):
            sel = selected()
            if len(sel) == 1 and sel[0][0] == "trash":
                player.load(sel[0][1]["file"])
        tree.bind("<<TreeviewSelect>>", on_select)

        def restore():
            sel = [x for k, x in selected() if k == "trash"]
            gone = [x for k, x in selected() if k == "gone"]
            if not sel and not gone:
                messagebox.showinfo(T("Корзина"), T("Сначала выбери клип в списке."), parent=win)
                return
            if gone and messagebox.askyesno(T("Корзина"), T(
                    "Выбрано клипов, удалённых до появления корзины: {0}. Их файлов уже нет — вернуть их можно, только "
                    "нарезав заново из записи стрима (1–2 минуты на клип). Нарезать?").format(len(gone)), parent=win):
                recut_again()
            if not sel:
                return
            player.release()
            for x in sel:
                library.restore_from_trash(x)
            fill()
            self.refresh_clips()
            info.config(text=T("Возвращено клипов: {0} — они снова во вкладке «Клипы».").format(len(sel)))

        def recut_again():
            sel = [x for k, x in selected() if k == "gone"]
            if not sel:
                messagebox.showinfo(T("Корзина"), T("Выбери клипы с пометкой «файл удалён — можно нарезать заново»."),
                                    parent=win)
                return
            queue_ = [x for x in sel if clipedit.source_range(x)]
            if not queue_:
                info.config(text=T("У этих клипов нет записи стрима — нарезать заново нельзя."))
                return

            def next_one(done_n=0):
                if not queue_ or not win.winfo_exists():
                    if win.winfo_exists():
                        fill()
                    self.refresh_clips()
                    return
                x = dict(queue_.pop(0))
                url, s0, e0 = clipedit.source_range(x)
                x["_src_url"] = url
                info.config(text=T("Нарезаю заново: {0} «{1}»... осталось {2}").format(
                    x.get("channel", ""), (x.get("caption") or "")[:30], len(queue_)))

                def done(res, err):
                    if err:
                        info.config(text=T("Не получилось: {0}").format(tr_line(err)))
                    else:
                        import shutil
                        os.makedirs(os.path.dirname(x["path"]), exist_ok=True)
                        shutil.move(res["file"], x["path"])
                        library.make_thumb(x["path"])
                        library.update_clip(x["path"], {"words": res.get("words") or [],
                                                        "transcript": res.get("transcript", ""),
                                                        "credit_burned": bool(self.cfg.get("credit_auto"))})
                    next_one(done_n + 1)
                self._run_recut(x, s0, e0, lambda m: info.config(text=m), done)
            next_one()

        def purge():
            sel = selected()
            if not sel or not messagebox.askyesno(T("Корзина"), T("Удалить навсегда: {0}? Вернуть будет нельзя.").format(
                    len(sel)), parent=win):
                return
            player.release()
            freed = library.purge_trash([x for k, x in sel if k == "trash"])
            for k, x in sel:
                if k == "gone":  # «раньше удалённые» — просто скрываем из списка
                    library.update_clip(x["path"], {"dismissed": True})
            fill()
            info.config(text=T("Освобождено {0:.0f} МБ.").format(freed / 1e6))

        def clear_all():
            trash = library.load_trash()
            if not trash or not messagebox.askyesno(T("Корзина"), T("Очистить корзину целиком ({0} клипов)? Вернуть будет "
                                                                   "нельзя.").format(len(trash)), parent=win):
                return
            player.release()
            freed = library.purge_trash(trash)
            fill()
            info.config(text=T("Корзина очищена, освобождено {0:.0f} МБ.").format(freed / 1e6))
        bar = ttk.Frame(frm)
        bar.pack(fill="x")
        ttk.Button(bar, text=T("↩  Вернуть"), style="Big.TButton", command=restore).pack(side="left")
        ttk.Button(bar, text=T("✂  Нарезать заново"), command=recut_again).pack(side="left", padx=6)
        ttk.Button(bar, text=T("🗑  Удалить навсегда"), command=purge).pack(side="left")
        b_clear = ttk.Button(bar, text="", command=clear_all)
        b_clear.pack(side="left", padx=6)
        ttk.Button(bar, text=T("Закрыть"), command=lambda: (player.release(), win.destroy())).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", lambda: (player.release(), win.destroy()))
        fill()

    def _update_trash_button(self):
        n = len(library.load_trash())
        if hasattr(self, "b_trash"):
            self.b_trash.config(text=T("♻  Корзина ({0})").format(n) if n else T("♻  Корзина"))

    def clip_history(self):
        """Окно «Правки»: что сделано с клипом (размытие, обрезка, подпись...) — любую правку можно убрать."""
        from . import edits
        sel = self._selected()
        if not sel:
            return
        c = sel[0]
        win = tk.Toplevel(self.root)
        win.title(T("Правки — {0}").format(c.get("channel", "")))
        win.transient(self.root)
        win.geometry("640x420")
        self.history_window = win
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=f"«{(c.get('caption') or '')[:60]}»", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(frm, foreground=self.muted, wraplength=600, justify="left", text=T(
            "Программа хранит исходный клип и собирает готовый заново из правок. Убери ненужную правку — "
            "остальные останутся.")).pack(anchor="w", pady=(2, 8))
        pal = self.pal or {}
        lb = tk.Listbox(frm, height=10, font=("Segoe UI", 11), activestyle="none", bg=pal.get("field", "#ffffff"),
                        fg=pal.get("fg", "#000000"), selectbackground=pal.get("accent", "#3b82f6"),
                        highlightthickness=0, relief="flat")
        lb.pack(fill="both", expand=True)
        status = ttk.Label(frm, text="", foreground=self.muted, wraplength=600, justify="left")
        status.pack(anchor="w", pady=(6, 0))
        ids: list = []

        def fill():
            lb.delete(0, "end")
            ids.clear()
            rec = edits.get(c)
            ops = (rec or {}).get("ops") or []
            if not ops:
                lb.insert("end", T("Правок нет — клип такой, каким его нарезала программа."))
            for o in ops:
                lb.insert("end", f"  {len(ids) + 1}.  " + edits.label(o))
                ids.append(o["id"])

        def rebuild(change, done_text):
            import copy
            rec = edits.get(c)
            if not rec:
                return
            trial = copy.deepcopy(rec)
            change(trial)
            for b in buttons:
                b.config(state="disabled")
            status.config(text=T("Собираю клип заново... (до минуты)"))
            if self.preview.path == c["path"]:
                self.preview.release()

            def work():
                try:
                    out = os.path.join(paths.default_work_dir(), "edits", f"undo_{int(time.time() * 1000)}.mp4")
                    fields = edits.build(c, trial, out)
                    edits.commit(c, trial, out, fields)
                    err = None
                except Exception as e:
                    err = e
                self.root.after(0, lambda: done(err))

            def done(err):
                if not win.winfo_exists():
                    return
                for b in buttons:
                    b.config(state="normal")
                status.config(text=T("Не получилось: {0}").format(err) if err else done_text)
                self.images.pop(c["path"], None)
                fill()
                self.refresh_clips()
            threading.Thread(target=work, daemon=True).start()

        def remove_selected():
            s_ = lb.curselection()
            if not s_ or s_[0] >= len(ids):
                status.config(text=T("Выбери правку в списке."))
                return
            op_id = ids[s_[0]]
            rebuild(lambda r: edits.remove_op(r, op_id), T("Правка убрана."))

        def remove_all():
            if not ids:
                return
            if messagebox.askyesno(T("Правки"), T("Убрать все правки и вернуть клип, каким его нарезала программа?"),
                                   parent=win):
                rebuild(lambda r: [edits.remove_op(r, i) for i in list(ids)], T("Клип возвращён к исходному."))
        bar = ttk.Frame(frm)
        bar.pack(fill="x", pady=(8, 0))
        buttons = [ttk.Button(bar, text=T("✖  Убрать выбранную правку"), style="Big.TButton", command=remove_selected),
                   ttk.Button(bar, text=T("↩  Вернуть исходный клип"), command=remove_all)]
        buttons[0].pack(side="left")
        buttons[1].pack(side="left", padx=6)
        ttk.Button(bar, text=T("Закрыть"), command=win.destroy).pack(side="right")
        fill()

    # ---------- вкладка «Архив» ----------
    def _build_archive(self, parent):
        self.arch_rows: dict = {}
        bar = ttk.Frame(parent)
        bar.pack(fill="x")
        ttk.Label(bar, text=T("Поиск:")).pack(side="left")
        self.arch_q = tk.StringVar()
        e = ttk.Entry(bar, textvariable=self.arch_q, width=30)
        e.pack(side="left", padx=4)
        self.arch_q.trace_add("write", lambda *a: self.refresh_archive())
        ttk.Label(bar, text=T("(ник стримера или слова из надписи и речи)"), foreground=self.muted).pack(side="left")
        ttk.Button(bar, text=T("⟳ Обновить"), command=self.refresh_archive).pack(side="right")
        self.arch_trend = ttk.Label(parent, text="", foreground="#f0a020", wraplength=1100, justify="left")
        self.arch_trend.pack(anchor="w", pady=(4, 0))
        self.arch_info = ttk.Label(parent, text="", foreground=self.muted, wraplength=1100, justify="left")
        self.arch_info.pack(side="bottom", fill="x", pady=(6, 0))
        btns = ttk.Frame(parent)
        btns.pack(side="bottom", fill="x")
        ttk.Button(btns, text=T("↩  Достать из архива"), style="Big.TButton",
                   command=self.restore_archived).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🗑  Удалить из архива навсегда"), command=self.forget_archived).pack(side="left")
        panes = ttk.Panedwindow(parent, orient="horizontal")
        panes.pack(fill="both", expand=True, pady=6)
        lf = ttk.Frame(panes)
        self.arch_player = VideoPreview(panes, self)
        panes.add(lf, weight=3)
        panes.add(self.arch_player, weight=2)
        cols = ("trend", "date", "streamer", "caption", "score", "reason")
        self.arch_tree = ttk.Treeview(lf, columns=cols, show="headings", selectmode="extended")
        for c, title, w in (("trend", "★", 30), ("date", T("В архиве с"), 100), ("streamer", T("Стример"), 110),
                            ("caption", T("Надпись"), 260), ("score", T("Оценка"), 60), ("reason", T("Почему в архиве"), 260)):
            self.arch_tree.heading(c, text=title)
            self.arch_tree.column(c, width=w, stretch=c in ("caption", "reason"), anchor="w" if c in ("caption", "reason") else "center")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.arch_tree.yview)
        self.arch_tree.configure(yscrollcommand=sb.set)
        self.arch_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.arch_tree.bind("<<TreeviewSelect>>", self._arch_select)

    def _arch_select(self, e=None):
        sel = self.arch_tree.selection()
        if len(sel) == 1 and sel[0] in self.arch_rows:
            rec = self.arch_rows[sel[0]]
            if rec.get("small") and os.path.exists(rec["small"]):
                self.arch_player.load(rec["small"])

    def refresh_archive(self):
        from datetime import datetime
        from . import archive, strategy
        self.arch_tree.delete(*self.arch_tree.get_children())
        self.arch_rows = {}
        trends = dict((r["id"], hit) for r, hit in archive.trend_matches(strategy.get().get("trends") or []))
        items = archive.search(self.arch_q.get())
        for r in sorted(items, key=lambda r: (r["id"] not in trends, -(r.get("archived") or 0))):
            sc = r.get("score")
            iid = self.arch_tree.insert("", "end", values=(
                "★" if r["id"] in trends else "", datetime.fromtimestamp(r.get("archived", 0)).strftime("%d.%m %H:%M"),
                r.get("channel", ""), r.get("caption") or "—", "" if sc is None else f"{sc:.0f}" if isinstance(sc, (int, float)) else sc,
                tr_line(r.get("reason") or "")))
            self.arch_rows[iid] = r
        allr = archive.search("")
        size = sum(os.path.getsize(r["small"]) for r in allr if r.get("small") and os.path.exists(r["small"]))
        freed = sum((r.get("size") or 0) for r in allr) - size
        self.arch_info.config(text=T("В архиве: {0} клипов, занимают {1:.0f} МБ (освобождено {2:.0f} МБ). «Достать» заново "
                                     "нарежет клип из записи стрима в полном качестве; если запись уже удалена — вернёт "
                                     "сжатую копию.").format(len(allr), size / 1e6, max(0, freed) / 1e6))
        self.arch_trend.config(text=T("★ В трендах сейчас: {0} — совпало клипов в архиве: {1}. Их стоит достать.").format(
            ", ".join(sorted(set(trends.values()))), len(trends)) if trends else "")

    def _arch_selected(self) -> list:
        recs = [self.arch_rows[i] for i in self.arch_tree.selection() if i in self.arch_rows]
        if not recs:
            messagebox.showinfo(T("Архив"), T("Сначала выбери клип в списке."))
        return recs

    def restore_archived(self, recs: list | None = None, quiet: bool = False):
        """Достать клипы из архива: перенарезать из записи стрима, а если её нет — вернуть сжатую копию."""
        from . import archive, clipedit
        recs = recs or self._arch_selected()
        if not recs:
            return
        self.arch_player.release()
        queue_ = list(recs)

        def next_one():
            if not queue_:
                self.refresh_archive()
                self.refresh_clips()
                return
            r = queue_.pop(0)
            src = clipedit.source_range(r)
            if not src:
                archive.restore_from_small(r)
                self.activity.event("↩", T("{0}: достал из архива сжатую копию (записи стрима нет)").format(r.get("channel", "")))
                return next_one()
            x = dict(r, path=r["orig"], _src_url=src[0])
            self.arch_info.config(text=T("Достаю из архива: {0} «{1}» — качаю кусок стрима...").format(
                r.get("channel", ""), (r.get("caption") or "")[:30]))

            def done(res, err):
                import shutil
                if err:
                    archive.restore_from_small(r)
                    self.activity.event("↩", T("{0}: запись стрима недоступна — достал сжатую копию").format(r.get("channel", "")))
                else:
                    os.makedirs(os.path.dirname(r["orig"]), exist_ok=True)
                    shutil.move(res["file"], r["orig"])
                    library.make_thumb(r["orig"])
                    library.update_clip(r["orig"], {"words": res.get("words") or [], "transcript": res.get("transcript", "")})
                    archive.mark_restored(r)
                    self.activity.event("↩", T("{0}: достал из архива в полном качестве — «{1}»").format(
                        r.get("channel", ""), r.get("caption") or ""), r["orig"])
                next_one()
            self._run_recut(x, src[1], src[2], lambda m: self.arch_info.config(text=m), done)
        next_one()

    def forget_archived(self):
        from . import archive
        recs = self._arch_selected()
        if not recs or not messagebox.askyesno(T("Архив"), T("Удалить из архива навсегда: {0}? Достать их будет нельзя "
                                                            "(разве что заново из записи стрима вручную).").format(len(recs))):
            return
        self.arch_player.release()
        for r in recs:
            archive.forget(r)
        self.refresh_archive()

    # ---------- настройки: автопубликация через официальные API ----------
    def _build_publish_settings(self, parent):
        from . import publisher
        box = ttk.LabelFrame(parent, text=T(" 📤 Автопубликация (официальные API площадок) "), padding=6)
        box.pack(fill="x", pady=(0, 6))
        ttk.Label(box, foreground=self.muted, wraplength=1050, justify="left", text=T(
            "Настраивается один раз. Пошаговая инструкция — файл «АВТОПУБЛИКАЦИЯ — настройка.txt» в папке программы. "
            "TikTok до проверки их приложения принимает видео только в черновики — останется нажать «Опубликовать» в телефоне.")
                  ).pack(anchor="w")
        self.pub_status: dict = {}
        rows = ttk.Frame(box)
        rows.pack(fill="x", pady=(4, 0))
        # YouTube
        ttk.Label(rows, text="YouTube:", width=11).grid(row=0, column=0, sticky="w")
        ttk.Button(rows, text=T("Подключить (файл client_secret.json)…"), command=self._yt_connect).grid(row=0, column=1, sticky="w")
        self.pub_status["youtube"] = ttk.Label(rows, text="")
        self.pub_status["youtube"].grid(row=0, column=2, sticky="w", padx=8)
        # Instagram
        ttk.Label(rows, text="Instagram:", width=11).grid(row=1, column=0, sticky="w", pady=4)
        igf = ttk.Frame(rows)
        igf.grid(row=1, column=1, sticky="w", pady=4)
        ig = publisher.load().get("instagram") or {}
        self.ig_id = tk.StringVar(value=ig.get("user_id", ""))
        self.ig_token = tk.StringVar(value=ig.get("token", ""))
        ttk.Label(igf, text=T("ID аккаунта:")).pack(side="left")
        ttk.Entry(igf, textvariable=self.ig_id, width=18).pack(side="left", padx=4)
        ttk.Label(igf, text=T("Токен:")).pack(side="left")
        ttk.Entry(igf, textvariable=self.ig_token, width=26, show="•").pack(side="left", padx=4)
        ttk.Button(igf, text=T("Подключить"), command=self._ig_connect).pack(side="left")
        self.pub_status["instagram"] = ttk.Label(rows, text="")
        self.pub_status["instagram"].grid(row=1, column=2, sticky="w", padx=8)
        # TikTok
        ttk.Label(rows, text="TikTok:", width=11).grid(row=2, column=0, sticky="w")
        ttf = ttk.Frame(rows)
        ttf.grid(row=2, column=1, sticky="w")
        tt = publisher.load().get("tiktok") or {}
        self.tt_key = tk.StringVar(value=tt.get("client_key", ""))
        self.tt_secret = tk.StringVar(value=tt.get("client_secret", ""))
        ttk.Label(ttf, text="Client key:").pack(side="left")
        ttk.Entry(ttf, textvariable=self.tt_key, width=18).pack(side="left", padx=4)
        ttk.Label(ttf, text="Client secret:").pack(side="left")
        ttk.Entry(ttf, textvariable=self.tt_secret, width=18, show="•").pack(side="left", padx=4)
        ttk.Button(ttf, text=T("Подключить"), command=self._tt_connect).pack(side="left")
        self.pub_status["tiktok"] = ttk.Label(rows, text="")
        self.pub_status["tiktok"].grid(row=2, column=2, sticky="w", padx=8)
        self._update_pub_status()

    def _update_pub_status(self):
        from . import publisher
        cfg, ok = publisher.load(), publisher.connected()
        for pl, lbl in self.pub_status.items():
            if ok[pl]:
                extra = (cfg.get(pl) or {}).get("username") or ""
                lbl.config(text=T("✔ подключено") + (f" (@{extra})" if extra else ""), foreground="#3ddc84")
            else:
                lbl.config(text=T("не подключено"), foreground=self.muted)

    def _pub_bg(self, platform: str, fn):
        lbl = self.pub_status[platform]
        lbl.config(text=T("подключаю... (войди в аккаунт в открывшемся браузере)"))

        def work():
            try:
                fn()
                err = None
            except Exception as e:
                err = e
            self.root.after(0, lambda: (self._update_pub_status(),
                                        messagebox.showwarning(library.PLATFORM_NAMES[platform], tr_line(str(err)))
                                        if err else self.activity.event("📤", T("{0} подключён для автопубликации").format(
                                            library.PLATFORM_NAMES[platform]))))
        threading.Thread(target=work, daemon=True).start()

    def _yt_connect(self):
        from . import publisher
        path = filedialog.askopenfilename(title=T("Файл client_secret.json из Google Cloud"),
                                          filetypes=[("JSON", "*.json"), (T("Все файлы"), "*.*")])
        if path:
            self._pub_bg("youtube", lambda: publisher.youtube_connect(path))

    def _ig_connect(self):
        from . import publisher
        uid, tok = self.ig_id.get().strip(), self.ig_token.get().strip()
        if not uid or not tok:
            messagebox.showinfo("Instagram", T("Впиши ID аккаунта Instagram и токен доступа."))
            return
        self._pub_bg("instagram", lambda: publisher.instagram_connect(uid, tok))

    def _tt_connect(self):
        from . import publisher
        key, sec = self.tt_key.get().strip(), self.tt_secret.get().strip()
        if not key or not sec:
            messagebox.showinfo("TikTok", T("Впиши Client key и Client secret своего приложения TikTok."))
            return
        self._pub_bg("tiktok", lambda: publisher.tiktok_connect(key, sec))

    def unpublish_window(self):
        """Выложенные клипы с неисправленным серьёзным нарушением: снять с YouTube (через API) или удалить вручную."""
        from . import policy, publisher
        win = tk.Toplevel(self.root)
        win.title(T("Снять с публикации"))
        win.transient(self.root)
        win.geometry("980x460")
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, wraplength=940, justify="left", text=T(
            "Эти клипы уже выложены, но в них нашлось серьёзное нарушение. YouTube программа снимает сама (делает "
            "приватным или удаляет), если видео выкладывал автопилот и YouTube подключён. Instagram и TikTok через API "
            "удалять не дают — открой видео и удали или заархивируй вручную, потом нажми «Снято».")).pack(anchor="w")
        cols = ("streamer", "clip", "platform", "reason")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=10)
        for c, t_, w in (("streamer", T("Стример"), 110), ("clip", T("Клип"), 150), ("platform", T("Где"), 90),
                         ("reason", T("Нарушение"), 520)):
            tree.heading(c, text=t_)
            tree.column(c, width=w, stretch=c == "reason", anchor="w")
        tree.pack(fill="both", expand=True, pady=6)
        rows: dict = {}
        status = ttk.Label(frm, text="", foreground=self.muted)
        status.pack(anchor="w")

        def fill():
            tree.delete(*tree.get_children())
            rows.clear()
            for f in policy.flagged_posted():
                iid = tree.insert("", "end", values=(f["clip"].get("channel", ""), os.path.basename(f["clip"]["path"])[:-4],
                                                     library.PLATFORM_NAMES.get(f["platform"], f["platform"]), tr_line(f["reason"])))
                rows[iid] = f
            if not rows:
                status.config(text=T("✔ Выложенных клипов с нарушениями нет."))

        def sel():
            s_ = tree.selection()
            return rows.get(s_[0]) if s_ else None

        def yt(action):
            f = sel()
            if not f or f["platform"] != "youtube":
                status.config(text=T("Выбери строку с YouTube."))
                return
            if not f["id"] or not publisher.connected().get("youtube"):
                status.config(text=T("ID видео неизвестен или YouTube не подключён — сделай это в YouTube Studio вручную."))
                webbrowser.open("https://studio.youtube.com")
                return
            try:
                publisher.youtube_set_privacy(f["id"], "private") if action == "private" else publisher.youtube_delete(f["id"])
                library.set_posted(f["clip"]["path"], False, "youtube")
                status.config(text=T("Готово: видео снято с YouTube."))
            except Exception as e:
                status.config(text=tr_line(str(e)))
            fill()

        def open_post():
            f = sel()
            if f:
                webbrowser.open(f["url"] or {"tiktok": "https://www.tiktok.com/tiktokstudio/content",
                                             "instagram": "https://www.instagram.com/",
                                             "youtube": "https://studio.youtube.com"}[f["platform"]])

        def mark_removed():
            f = sel()
            if f:
                library.set_posted(f["clip"]["path"], False, f["platform"])
                fill()
                self.refresh_clips()
        bar = ttk.Frame(frm)
        bar.pack(fill="x", pady=(6, 0))
        ttk.Button(bar, text=T("🔒 YouTube: сделать приватным"), command=lambda: yt("private")).pack(side="left")
        ttk.Button(bar, text=T("🗑 YouTube: удалить"), command=lambda: yt("delete")).pack(side="left", padx=6)
        ttk.Button(bar, text=T("🔗 Открыть видео"), command=open_post).pack(side="left")
        ttk.Button(bar, text=T("✔ Снято (убрать галочку «выложено»)"), command=mark_removed).pack(side="left", padx=6)
        ttk.Button(bar, text=T("Закрыть"), command=win.destroy).pack(side="right")
        fill()

    # ---------- настройки: общая папка с другом ----------
    def _build_team_settings(self, parent):
        box = ttk.LabelFrame(parent, text=T(" 👥 Общая папка с другом — общие клипы и галочки «выложено» "), padding=6)
        box.pack(fill="x", pady=(0, 6))
        ttk.Label(box, foreground=self.muted, wraplength=1050, justify="left", text=T(
            "Сделайте папку в облаке с приложением на компьютере (Google Диск, Яндекс Диск, Dropbox), расшарьте её только "
            "друг другу и укажите здесь у обоих. Клипы будут нарезаться в неё, вы оба увидите все клипы и кто что выложил. "
            "Инструкция — файл «ОБЩАЯ ПАПКА — настройка.txt».")).pack(anchor="w")
        r1 = ttk.Frame(box)
        r1.pack(fill="x", pady=(4, 0))
        ttk.Label(r1, text=T("Папка:")).pack(side="left")
        self.v["team_dir"] = tk.StringVar(value=self.cfg.get("team_dir", ""))
        ttk.Entry(r1, textvariable=self.v["team_dir"], width=55).pack(side="left", padx=4)
        ttk.Button(r1, text=T("Выбрать…"), command=self._team_choose).pack(side="left")
        ttk.Label(r1, text=T("  Моё имя:")).pack(side="left")
        self.v["user_name"] = tk.StringVar(value=self.cfg.get("user_name", ""))
        ttk.Entry(r1, textvariable=self.v["user_name"], width=12).pack(side="left", padx=4)
        r2 = ttk.Frame(box)
        r2.pack(fill="x", pady=(4, 0))
        self.v["team_main"] = tk.BooleanVar(value=bool(self.cfg.get("team_main", True)))
        ttk.Checkbutton(r2, text=T("Этот компьютер ведёт автопилот и публикации через Telegram (включите только у одного из вас)"),
                        variable=self.v["team_main"], command=self._save_settings).pack(side="left")
        r3 = ttk.Frame(box)
        r3.pack(fill="x", pady=(4, 0))
        ttk.Button(r3, text=T("✔ Включить общую папку"), command=self._team_apply).pack(side="left")
        ttk.Button(r3, text=T("📦 Перенести мои клипы в общую папку"), command=self._team_migrate).pack(side="left", padx=6)
        ttk.Button(r3, text=T("Выключить"), command=self._team_off).pack(side="left")
        self.team_status = ttk.Label(r3, text="", foreground=self.muted)
        self.team_status.pack(side="left", padx=8)
        self._team_show()

    def _team_show(self):
        td = paths.team_dir()
        if td:
            from . import team
            users = sorted({u for u, _ in team.files("posted")} | {os.path.basename(p)[11:-5]
                                                                 for _, p in library._day_files()} | {team.me()})
            self.team_status.config(text=T("✔ включена: {0} · участники: {1}").format(td, ", ".join(u for u in users if u)),
                                    foreground="#3ddc84")
        else:
            self.team_status.config(text=T("выключена — клипы только на этом компьютере"), foreground=self.muted)

    def _team_choose(self):
        d = filedialog.askdirectory(title=T("Общая папка в облаке"))
        if d:
            self.v["team_dir"].set(d)

    def _team_apply(self):
        d, name = self.v["team_dir"].get().strip(), self.v["user_name"].get().strip()
        if not d or not os.path.isdir(d):
            messagebox.showinfo(T("Общая папка"), T("Выбери существующую папку (она должна синхронизироваться облаком)."))
            return
        if not name:
            messagebox.showinfo(T("Общая папка"), T("Впиши своё имя — так будет видно, кто нарезал и кто выложил клип."))
            return
        self._save_settings()
        self.refresh_clips()
        self._team_show()
        self.activity.event("👥", T("Общая папка включена: {0}. Новые клипы будут нарезаться туда.").format(d))
        if self.proc:
            self._append(T("Нажми «Стоп» и снова «Следить» — работа начнёт складывать клипы в общую папку.") + "\n")
        if messagebox.askyesno(T("Общая папка"), T("Перенести в общую папку клипы, которые уже есть на этом компьютере? "
                                                  "Тогда их увидит и друг.")):
            self._team_migrate()

    def _team_migrate(self):
        from . import team
        if not paths.team_dir():
            messagebox.showinfo(T("Общая папка"), T("Сначала включи общую папку."))
            return
        old = os.path.join(paths.desktop_dir(), "YouTube")
        self.preview.release()
        self.team_status.config(text=T("переношу..."))

        def work():
            try:
                n, err = team.migrate(old, log=lambda m: None), None
            except Exception as e:
                n, err = 0, e
            self.root.after(0, lambda: (self.team_status.config(text=T("Перенесено клипов: {0}").format(n) if not err
                                                                else tr_line(str(err))), self.refresh_clips()))
        threading.Thread(target=work, daemon=True).start()

    def _team_off(self):
        self.v["team_dir"].set("")
        self._save_settings()
        self.refresh_clips()
        self._team_show()

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
                                         values=("", T('стримов: {0}').format(len(items)), "", "", ""))
            for r in items:
                sm = progress.summary(r)
                live = bool(r.get("live") and r.get("ranges"))
                if sm["finished"]:
                    upto = T("✔ весь стрим")
                elif not r.get("ranges"):
                    upto = T("— не смотрели")
                else:
                    upto = T("до {0}").format(progress.fmt(sm["upto"]))
                if not sm["finished"]:
                    unfinished += 1
                ts = r.get("stream_ts")
                date = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M") if ts else "—"
                tags = ("live",) if live else (("done",) if sm["finished"] else ())
                iid = self.st_tree.insert(parent, "end", text="", tags=tags,
                                          values=(date, r.get("title") or "—", _short_url(r.get("url") or ""),
                                                  upto, T("🔴 идёт") if live else ""))
                self.stream_rows[iid] = dict(r, summary=sm)
                if r.get("key") == sel_key:
                    self.st_tree.selection_set(iid)
        if not self.stream_rows:
            self.st_info.config(text=T("Тут появятся стримы, которые программа разбирала: какой кусок уже просмотрен и "
                                     "откуда продолжать. Выбери стримера и нажми «Показать все стримы канала», чтобы "
                                     "увидеть и те, что ещё не смотрели."))
        else:
            self.st_info.config(text=T("«Разобрано до» — до какого времени стрима программа уже всё проверила. Выбери стрим и нажми "
                                       "«Продолжить» — анализ начнётся с этого времени."))

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
            start = sm["upto"] or 0
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
        t = int(r["summary"]["upto"] or 0)
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
        if r and messagebox.askyesno(T("Стримы"), T(
                "Забыть всё, что разобрано в этом стриме?\n\nСледующий разбор начнётся с самого начала, как будто стрим "
                "новый. Клипы в папке не удалятся, и те же моменты второй раз нарезаны не будут — найдутся новые.")):
            progress.reset_memory(r["key"], r.get("url", ""))
            self._append(T("Память о стриме «{0}» очищена — разбор начнётся заново.").format(r.get("title") or r["key"]) + "\n")
            self.refresh_streams()

    def rewind_stream(self):
        """«Другое время»: считать разобранным только до указанного места — дальше разобрать заново."""
        from tkinter import simpledialog
        from . import progress
        r = self._stream_selected()
        if not r:
            return
        upto = int(r["summary"].get("upto") or 0)
        cur = f"{upto // 3600}:{upto % 3600 // 60:02d}"
        ans = simpledialog.askstring(T("Другое время"), T(
            "Сейчас разобрано до {0}.\nДо какого места считать стрим разобранным? (часы:минуты, например 12:30; "
            "0 — с самого начала)\nВсё, что дальше, программа разберёт заново.").format(cur), initialvalue=cur,
            parent=self.root)
        if ans is None:
            return
        try:
            parts = [int(x) for x in ans.strip().replace(".", ":").split(":")] if ans.strip() not in ("", "0") else [0, 0]
            sec = parts[0] * 3600 + (parts[1] if len(parts) > 1 else 0) * 60
        except ValueError:
            messagebox.showwarning(T("Другое время"), T("Не понял время. Напиши, например, 12:30."))
            return
        progress.reset_memory(r["key"], r.get("url", ""), upto=float(sec))
        self._append(T("Стрим «{0}»: теперь разобран до {1} — дальше разберётся заново.").format(
            r.get("title") or r["key"], f"{sec // 3600}:{sec % 3600 // 60:02d}") + "\n")
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
        pub.add_command(label=T("📋 По плану аналитика (что пора выкладывать)"), command=self.publish_plan)
        pub.add_separator()
        for key, label in library.PLATFORM_NAMES.items():
            pub.add_command(label=T('в {0}').format(label),
                            command=lambda k=key: (setattr(self, "_plan_mode", False), self.publish(k)))
        pub_mb["menu"] = pub
        pub_mb.pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("✂  Длина"), command=self.edit_clip).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🛠  Нарушения"), command=self.fix_violations).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🕘  Правки"), command=self.clip_history).pack(side="left", padx=(0, 6))
        posted_mb = ttk.Menubutton(btns, text=T("✔  Выложено в…"))
        pm = tk.Menu(posted_mb, tearoff=0)
        for key, label in library.PLATFORM_NAMES.items():
            pm.add_command(label=T('{0} — выложено / снять отметку').format(label), command=lambda k=key: self.toggle_posted(k))
        posted_mb["menu"] = pm
        posted_mb.pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🗑  Удалить"), command=self.delete_clip).pack(side="left", padx=(0, 6))
        self.b_trash = ttk.Button(btns, text=T("♻  Корзина"), command=self.open_trash)
        self.b_trash.pack(side="left", padx=(0, 6))
        ttk.Button(btns, text=T("🏆  Оставить лучшие"), command=self.pick_best_clips).pack(side="left", padx=(0, 6))
        more = ttk.Menubutton(btns, text=T("Ещё ▾"))
        mm = tk.Menu(more, tearoff=0)
        self.clips_btns, self.clips_more = btns, mm
        mm.add_command(label=T("🩺  Обмен с «Доктором шортсов»: открыть папку"),
                       command=lambda: (self._export_catalog(), self._open(exchange_dir())))
        mm.add_command(label=T("📥  Загрузить решения аналитика из файла…"), command=self.import_decisions_file)
        mm.add_command(label=T("🗑  Удалить, что советует аналитик…"), command=self.delete_advised)
        mm.add_command(label=T("⛔  Снять с публикации (выложенные с нарушениями)…"), command=self.unpublish_window)
        mm.add_command(label=T("💤  Убрать в архив клипы, где стример спит (проверить все)"), command=self.sweep_sleepy)
        mm.add_separator()
        mm.add_command(label=T("🧹  Начать с чистого листа (убрать все клипы, план и отметки)…"), command=self.wipe_all)
        mm.add_separator()
        mm.add_command(label=T("☑  Выбрать все"), command=self.select_all_clips)
        mm.add_command(label=T("✍  Описание и хэштеги"), command=self.post_texts)
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
        cols = ("rating", "rules", "author", "advice", "streamer", "moment", "why", "caption", "youtube", "instagram", "tiktok")
        self.tree = ttk.Treeview(frame, columns=cols, show="tree headings", style="Clips.Treeview",
                                 selectmode="extended", height=3)
        self.tree.heading("#0", text=T("Превью"))
        self.tree.column("#0", width=66, stretch=False)
        for c, title, w in (("rating", T("Интерес"), 70), ("rules", T("Правила"), 64), ("author", T("Автор"), 56), ("advice", T("Совет"), 92), ("streamer", T("Стример"), 96), ("moment", T("Момент"), 64),
                            ("why", T("Почему"), 200), ("caption", T("Надпись"), 200), ("youtube", "YT", 40), ("instagram", "Inst", 44),
                            ("tiktok", "TikTok", 50)):
            self.tree.heading(c, text=title)
            self.tree.column(c, width=w, stretch=(c in ("caption", "why")), anchor="w" if c in ("caption", "why") else "center")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.preview.play_selected())
        self.tree.bind("<Return>", lambda e: self.preview.play_selected())
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.preview.show_selected())
        self.tree.bind("<Delete>", lambda e: self.delete_clip())
        self.tree.bind("<Button-3>", self._clips_menu)
        self.tree.bind("<Button-1>", self._clips_click, add="+")
        self.clip_by_iid: dict = {}
        self.root.after(1000, self._auto_refresh)
        self.root.after(4000, self._exchange_tick)

    # ---------- настройки клипов от «Доктора» (strategy.json → clip_settings) ----------
    # приёмы монтажа: поле окна, ключ «Доктора», подпись, значение «включено» по умолчанию
    TRICKS_UI = (("tr_pattern", "pattern_interrupt_sec", "Смена картинки каждые 2–3 с (лёгкий зум)", 2.5),
                 ("tr_speed", "speed_talk", "Речь до реакции чуть быстрее (1,1×)", 1.1),
                 ("tr_kw", "subtitle_keyword_highlight", "Субтитры: текущее слово и ключевые слова цветом", True),
                 ("tr_voice", "voice_over_game_db", "Голос стримера громче игры", 4),
                 ("tr_question", "question_overlay", "Хук-вопрос для эпика и фейлов", True),
                 ("tr_freeze", "freeze_wait", "Стоп-кадр «WAIT…» перед развязкой", True),
                 ("tr_sfx", "sfx_accents", "Звуки: «вжух» на склейках, бас на зуме", True),
                 ("tr_replay", "instant_replay", "Повтор момента в замедлении после реакции", True),
                 ("tr_face", "face_fullscreen_on_peak", "Лицо на весь кадр на пике", True),
                 ("tr_context", "context_line", "Строка контекста из названия стрима (2 с)", True))
    DOC_KEYS = ("subs", "caption", "facecam", "audio", "cold_open", "punch_zoom", "top", "length", "quality", "game_view",
                "wm_on", "wm_text", "wm_pos", "wm_op", "credit_auto", "credit_pos")
    DOC_NAMES = {"subs": "субтитры", "caption": "надпись-плашка", "facecam": "вебка сверху",
                 "audio": "поиск по звуку и картинке", "top": "клипов за час", "length": "длина клипа",
                 "quality": "качество", "game_view": "игра в кадре", "wm_on": "водяной знак",
                 "wm_text": "текст знака", "wm_pos": "где знак", "wm_op": "заметность знака",
                 "credit_auto": "подпись автора", "credit_pos": "где подпись автора"}
    # ключ «Доктора» → поля окна, на которые он влияет
    DOC_MAP = {"subs": ("subs",), "caption": ("caption",), "facecam": ("facecam",), "layout": ("facecam",),
               "audio": ("audio",), "top": ("top",), "length": ("length",), "auto_length": ("length",),
               "quality": ("quality",), "game_view": ("game_view",), "credit": ("credit_auto",),
               "credit_pos": ("credit_pos",), "watermark_text": ("wm_on", "wm_text"),
               "watermark_pos": ("wm_pos",), "watermark_opacity": ("wm_op",), "cold_open": ("cold_open",),
               "punch_in_zoom": ("punch_zoom",)}
    DOC_MAP.update({dk: (key,) for key, dk, _t, _on in TRICKS_UI})
    DOC_NAMES.update({key: text for key, _dk, text, _on in TRICKS_UI})

    def _doc_reg(self, key: str, widget):
        """Поле, которое может выбирать «Доктор»: запоминаем его и вешаем подсказку «выбирает Доктор: причина»."""
        self._doc_widgets.setdefault(key, []).append(widget)
        tip = {"w": None}

        def show(e):
            text = self._doc_reason.get(key)
            if not text or tip["w"] is not None:
                return
            t = tk.Toplevel(widget)
            t.wm_overrideredirect(True)
            t.wm_geometry(f"+{e.x_root + 14}+{e.y_root + 14}")
            tk.Label(t, text=text, bg="#fff8d6", fg="#222", justify="left", wraplength=340,
                     padx=8, pady=4, font=("Segoe UI", 9)).pack()
            tip["w"] = t

        def hide(e):
            if tip["w"] is not None:
                tip["w"].destroy()
                tip["w"] = None
        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", hide, add="+")

    def _doctor_to_gui(self, d: dict) -> dict:
        """clip_settings.defaults (ключи рабочей части) → значения полей окна."""
        out = {}
        for k in ("subs", "caption", "facecam", "audio"):
            if isinstance(d.get(k), bool):
                out[k] = d[k]
        if d.get("layout") in ("auto", "facecam", "blur", "crop"):
            out["facecam"] = d["layout"] in ("auto", "facecam")
        for k in ("top", "quality"):
            if isinstance(d.get(k), int) and not isinstance(d.get(k), bool) and d[k] > 0:
                out[k] = str(d[k])
        if "quality" in out and out["quality"] not in ("720", "1080"):
            out.pop("quality")
        if d.get("auto_length") is True or d.get("length") == "auto":
            out["length"] = T("авто")
        elif isinstance(d.get("length"), (int, float)) and not isinstance(d.get("length"), bool) and d["length"] > 0:
            out["length"] = str(int(d["length"]))
        rev = {v: k for k, v in GAME_VIEW.items()}
        if d.get("game_view") in rev:
            out["game_view"] = rev[d["game_view"]]
        if isinstance(d.get("credit"), bool):
            out["credit_auto"] = d["credit"]
        rev = {v: k for k, v in CREDIT_POS.items()}
        if d.get("credit_pos") in rev:
            out["credit_pos"] = rev[d["credit_pos"]]
        if isinstance(d.get("watermark_text"), str):
            out["wm_text"] = d["watermark_text"].strip()
            out["wm_on"] = bool(out["wm_text"])
        rev = {v: k for k, v in WM_POS.items()}
        if d.get("watermark_pos") in rev:
            out["wm_pos"] = rev[d["watermark_pos"]]
        op = d.get("watermark_opacity")
        if isinstance(op, (int, float)) and not isinstance(op, bool):
            out["wm_op"] = min(WM_OP, key=lambda lab: abs(WM_OP[lab] - op))
        if isinstance(d.get("cold_open"), bool):
            out["cold_open"] = d["cold_open"]
        z = d.get("punch_in_zoom")
        if z is not None:
            out["punch_zoom"] = isinstance(z, (int, float)) and not isinstance(z, bool) and z > 1
        for key, dk, _t, _on in self.TRICKS_UI:
            if dk in d:
                v = d[dk]
                out[key] = bool(v) and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v <= 0)
        return out

    def _doctor_reasons(self, cs: dict, keys) -> dict:
        """Причина для каждого поля окна: reasons — словарь по ключам «Доктора» или общий текст."""
        r = cs.get("reasons")
        out = {}
        general = r if isinstance(r, str) else " ".join(map(str, r)) if isinstance(r, list) else str(cs.get("why") or "")
        if isinstance(r, dict):
            general = str(r.get("general") or r.get("all") or r.get("defaults") or cs.get("why") or "")
            for dk, gks in self.DOC_MAP.items():
                if r.get(dk):
                    for g in gks:
                        out[g] = str(r[dk])
        for g in keys:
            out.setdefault(g, general)
        return out

    def _doc_lock(self, locked: set):
        for key, ws in self._doc_widgets.items():
            for w in ws:
                try:
                    w.state(["disabled"] if key in locked else ["!disabled"])
                except Exception:
                    pass

    def _doctor_settings_tick(self):
        """Раз в минуту: свежая стратегия (качается не чаще раза в час) → применить clip_settings."""
        self.root.after(60000, self._doctor_settings_tick)
        if getattr(self, "_doc_busy", False):
            return
        self._doc_busy = True

        def work():
            from . import autopilot, strategy
            try:
                strategy.refresh(log=lambda m: None)
            except Exception:
                pass
            try:  # раз в минуту чистим план от удалённых клипов — даже если Telegram и автопилот выключены
                if not paths.team_dir() or self.v["team_main"].get():
                    autopilot.rebuild_schedule()
            except Exception:
                pass
            self.root.after(0, done)

        def done():
            self._doc_busy = False
            try:
                self._apply_doctor_settings()
            except Exception as e:
                self.activity.event("❌", T("Настройки от Доктора не применились: {0}").format(e), kind="error")
        threading.Thread(target=work, daemon=True).start()

    def _fmt_doc_value(self, val) -> str:
        if isinstance(val, bool):
            return T("вкл") if val else T("выкл")
        return str(val) if val != "" else "—"

    # группы настроек с переключателем «🩺 Доктор / ✋ Вручную»
    OWN_GROUPS = {"subs": ("subs",), "caption": ("caption",), "facecam": ("facecam",), "audio": ("audio",),
                  "top": ("top",), "length": ("length",), "quality": ("quality",), "game_view": ("game_view",),
                  "watermark": ("wm_on", "wm_text", "wm_pos", "wm_op"), "credit": ("credit_auto", "credit_pos"),
                  "cold_open": ("cold_open",), "punch_zoom": ("punch_zoom",),
                  "ppd": ("ppd_tiktok", "ppd_youtube", "ppd_instagram"),
                  "slots": ("slots_tiktok", "slots_youtube", "slots_instagram")}
    OWN_GROUPS.update({key: (key,) for key, _dk, _t, _on in TRICKS_UI})

    def _group_of(self, key: str) -> str:
        return next((g for g, ks in self.OWN_GROUPS.items() if key in ks), key)

    def _init_own(self):
        """Чьи настройки: ✋ (True) — твои, 🩺 (False) — Доктора. «Клипов за час» по умолчанию твой (5)."""
        if getattr(self, "_own_ready", False):
            return
        self._own_ready = True
        from . import strategy
        uo = strategy.get(raw=True).get("user_overrides") or {}
        default_own = set(uo.get("default_user_controlled") or ["top"])
        legacy_manual = self.cfg.get("doctor_settings") is False  # раньше сняли общую галочку — всё было твоим
        first = "own_top" not in self.cfg
        for g in self.OWN_GROUPS:
            val = self.cfg.get(f"own_{g}")
            if val is None:
                val = legacy_manual or g in default_own
            self.v[f"own_{g}"] = tk.BooleanVar(value=bool(val))
        if first and "top" in default_own:
            try:
                if int(str(self.cfg.get("top") or 0)) < 5:
                    self.cfg["top"] = "5"
            except ValueError:
                self.cfg["top"] = "5"

    def _own_btn(self, parent, group: str):
        self._init_own()
        var = self.v[f"own_{group}"]
        b = ttk.Button(parent, width=3, command=lambda g=group: self._toggle_own(g))
        upd = lambda *a: b.config(text="✋" if var.get() else "🩺")
        var.trace_add("write", upd)
        upd()
        self._own_tips = getattr(self, "_own_tips", {})
        b.bind("<Enter>", lambda e, g=group: self.status.config(
            text=T("✋ — твоё значение, Доктор его не трогает") if self.v[f"own_{g}"].get()
            else T("🩺 — выбирает Доктор; нажми, чтобы задать самому")), add="+")
        return b

    def _toggle_own(self, group: str):
        var = self.v[f"own_{group}"]
        var.set(not var.get())
        self.activity.event("✋" if var.get() else "🩺", (T("{0}: теперь твоё значение — Доктор его не меняет") if var.get()
                            else T("{0}: снова выбирает Доктор")).format(T(self.GROUP_NAMES.get(group, group))))
        self._apply_doctor_settings()
        self._save_settings()
        self._write_user_overrides()

    GROUP_NAMES = {"subs": "субтитры", "caption": "надпись-плашка", "facecam": "вебка сверху",
                   "audio": "поиск по звуку и картинке", "top": "клипов за час", "length": "длина клипа",
                   "quality": "качество", "game_view": "игра в кадре", "watermark": "водяной знак",
                   "credit": "подпись автора", "ppd": "публикаций в день", "slots": "время публикаций",
                   "cold_open": "холодный старт", "punch_zoom": "зум на пике"}
    GROUP_NAMES.update({key: text for key, _dk, text, _on in TRICKS_UI})

    def _all_to_doctor(self):
        for g in self.OWN_GROUPS:
            self.v[f"own_{g}"].set(False)
        self.activity.event("🩺", T("Все настройки снова выбирает Доктор"))
        self._apply_doctor_settings()
        self._save_settings()
        self._write_user_overrides()

    def _apply_doctor_settings(self):
        from . import strategy
        raw = strategy.get(raw=True)
        cs = raw.get("clip_settings") or {}
        vals_all = self._doctor_to_gui(cs.get("defaults") or {}) if isinstance(cs, dict) else {}
        ap = raw.get("autopilot") or {}
        for pl in ("tiktok", "youtube", "instagram"):  # публикации — тоже из стратегии
            n = (ap.get("posts_per_day") or {}).get(pl)
            if isinstance(n, int):
                vals_all[f"ppd_{pl}"] = str(n)
            sl = (ap.get("target_slots_et") or {}).get(pl)
            if isinstance(sl, list):
                vals_all[f"slots_{pl}"] = ", ".join(sl)
        own = {g for g in self.OWN_GROUPS if self.v[f"own_{g}"].get()}
        vals = {k: v for k, v in vals_all.items() if self._group_of(k) not in own and k in self.v}
        changes = []
        for k, v in vals.items():
            if self.v[k].get() != v:
                changes.append(k)
                self.v[k].set(v)
        ps = cs.get("per_streamer") if isinstance(cs, dict) and isinstance(cs.get("per_streamer"), dict) else {}
        fb = cs.get("no_facecam_fallback") if isinstance(cs, dict) else None
        fb = fb if isinstance(fb, dict) else ({"game_view": fb} if fb in GAME_VIEW.values() else {})
        # своё значение главнее: из «своих настроек для стримера» убираем то, что ты задал сам
        own_doc_keys = {dk for dk, gks in self.DOC_MAP.items() if any(self._group_of(g) in own for g in gks)}
        ps = {str(n): {k: v for k, v in o.items() if k not in own_doc_keys} for n, o in ps.items() if isinstance(o, dict)}
        ps = {n: o for n, o in ps.items() if o}
        fb = {k: v for k, v in fb.items() if k not in own_doc_keys}
        extra = {"per_streamer": ps, "no_facecam_fallback": fb}
        extra_changed = extra != self._doc_extra
        self._doc_extra = extra
        reasons = self._doctor_reasons(cs if isinstance(cs, dict) else {}, vals)
        self._doc_reason = {k: T("выбирает Доктор: {0}").format(r) if r else T("выбирает Доктор")
                            for k, r in reasons.items() if k in vals}
        self._doc_lock(set(vals))
        if not vals_all:
            hint = T("🩺 Доктор ещё не прислал настройки — пока работают твои.")
        else:
            hint = T("Заблокированные поля выбирает Доктор (наведи мышь — почему). Нажми 🩺 рядом с полем, чтобы задать самому.")
            if ps:
                hint += "\n" + T("Свои настройки для: {0}").format(", ".join(ps))
        self.doc_hint.config(text=hint)
        if changes or (extra_changed and getattr(self, "_doc_announced", False)):
            names = dict(self.DOC_NAMES, ppd_tiktok="TikTok в день", ppd_youtube="YouTube в день",
                         ppd_instagram="Instagram в день", slots_tiktok="время TikTok", slots_youtube="время YouTube",
                         slots_instagram="время Instagram")
            parts = [f"{T(names.get(k, k))}: {self._fmt_doc_value(self.v[k].get())}" for k in changes
                     if k != "wm_on" or "wm_text" not in changes]
            if extra_changed and ps:
                parts.append(T("для {0} — свои").format(", ".join(ps)))
            why = "; ".join(dict.fromkeys(reasons.get(k, "") for k in changes if reasons.get(k)))
            if getattr(self, "_doc_announced", False) or changes:
                self.activity.event("🩺", T("Доктор поменял настройки: {0}").format(", ".join(parts) or "—")
                                    + (f" — {why}" if why else ""))
        self._doc_announced = True
        if changes or extra_changed:
            self._save_settings()
            self._on_live_setting(quick=True)

    def _write_user_overrides(self):
        """Твои «Публикаций в день» и «Время публикаций» — в user_overrides.json (главнее стратегии «Доктора»)."""
        from . import strategy
        over: dict = {"autopilot": {}}
        if self.v["own_ppd"].get():
            ppd = {}
            for pl in ("tiktok", "youtube", "instagram"):
                try:
                    ppd[pl] = max(0, min(24, int(self.v[f"ppd_{pl}"].get())))
                except ValueError:
                    pass
            over["autopilot"]["posts_per_day"] = ppd
        if self.v["own_slots"].get():
            slots = {}
            for pl in ("tiktok", "youtube", "instagram"):
                items = [x.strip() for x in self.v[f"slots_{pl}"].get().replace(";", ",").split(",") if x.strip()]
                ok = []
                for x in items:
                    try:
                        h, m = x.split(":")
                        ok.append(f"{int(h) % 24:02d}:{int(m) % 60:02d}")
                    except ValueError:
                        pass
                if ok:
                    slots[pl] = sorted(set(ok))
            over["autopilot"]["target_slots_et"] = slots
        cdef = {}
        if self.v["own_cold_open"].get():  # монтаж делает автопилот по стратегии — твоё значение идёт поверх
            cdef["cold_open"] = bool(self.v["cold_open"].get())
        if self.v["own_punch_zoom"].get():
            cdef["punch_in_zoom"] = 1.2 if self.v["punch_zoom"].get() else 0
        doc_def = (strategy.get(raw=True).get("clip_settings") or {}).get("defaults") or {}
        for key, dk, _t, on in self.TRICKS_UI:
            if key in self.v and self.v[f"own_{key}"].get():
                dv = doc_def.get(dk)
                val = dv if dv and not isinstance(on, bool) and isinstance(dv, (int, float)) else on
                cdef[dk] = val if self.v[key].get() else (False if isinstance(on, bool) else 0)
        if cdef:
            over["clip_settings"] = {"defaults": cdef}
        if not over["autopilot"]:
            over.pop("autopilot")
        strategy.save_user_overrides(over)

    def _build_tricks(self, parent):
        """Приёмы монтажа против «скучно»: каждый — 🩺 (решает Доктор) или ✋ (твоё)."""
        tricks = ttk.LabelFrame(parent, text=T(" ✂ Приёмы монтажа (против «скучно») "), padding=6)
        tricks.pack(fill="x", pady=(0, 6))
        cols = [ttk.Frame(tricks), ttk.Frame(tricks)]
        for c in cols:
            c.pack(side="left", anchor="n", padx=(0, 24))
        for i, (key, dk, text, on) in enumerate(self.TRICKS_UI):
            self.v[key] = tk.BooleanVar(value=bool(self.cfg.get(key, True)))
            row = ttk.Frame(cols[i % 2])
            row.pack(anchor="w", pady=1)
            self._own_btn(row, key).pack(side="left", padx=(0, 4))
            w = ttk.Checkbutton(row, text=T(text), variable=self.v[key])
            w.pack(side="left")
            self._doc_reg(key, w)
            self.v[key].trace_add("write", lambda *a: self._on_post_setting())

    def _build_post_settings(self, parent):
        box = ttk.LabelFrame(parent, text=T(" 🗓 Публикации: сколько в день и во сколько (время США, ET) "), padding=6)
        box.pack(fill="x", pady=(0, 6))
        top_row = ttk.Frame(box)
        top_row.pack(fill="x")
        ttk.Label(top_row, text=T("Публикаций в день:")).pack(side="left")
        self._own_btn(top_row, "ppd").pack(side="left", padx=4)
        ttk.Label(top_row, text=T("   Время публикаций (ET, через запятую):")).pack(side="left")
        self._own_btn(top_row, "slots").pack(side="left", padx=4)
        for pl, name in (("tiktok", "TikTok"), ("youtube", "YouTube"), ("instagram", "Instagram")):
            row = ttk.Frame(box)
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=name, width=10).pack(side="left")
            self.v[f"ppd_{pl}"] = tk.StringVar(value=str(self.cfg.get(f"ppd_{pl}", "")))
            w = ttk.Spinbox(row, from_=0, to=24, width=4, textvariable=self.v[f"ppd_{pl}"])
            w.pack(side="left")
            self._doc_reg(f"ppd_{pl}", w)
            self.v[f"slots_{pl}"] = tk.StringVar(value=str(self.cfg.get(f"slots_{pl}", "")))
            w = ttk.Entry(row, textvariable=self.v[f"slots_{pl}"], width=52)
            w.pack(side="left", padx=(12, 0))
            self._doc_reg(f"slots_{pl}", w)
            for k in (f"ppd_{pl}", f"slots_{pl}"):
                self.v[k].trace_add("write", lambda *a: self._on_post_setting())
        ttk.Label(box, text=T("По Москве это время само сдвигается, когда в США переводят часы. Пачки видео в Telegram "
                              "приходят днём, у каждого — на какое время его запланировать."),
                  foreground=self.muted, wraplength=900, justify="left").pack(anchor="w", pady=(4, 0))

    def _on_post_setting(self):
        if getattr(self, "_post_job", None):
            self.root.after_cancel(self._post_job)
        self._post_job = self.root.after(1500, self._post_setting_apply)

    def _post_setting_apply(self):
        self._post_job = None
        if any(self.v[f"own_{g}"].get() for g in ("ppd", "slots", "cold_open", "punch_zoom")
               + tuple(k for k, *_ in self.TRICKS_UI) if f"own_{g}" in self.v):
            self._write_user_overrides()
            self._save_settings()

    # ---------- автопилот ----------
    AUTOPILOT_EVERY = 5 * 60 * 1000

    def _autopilot_toggled(self):
        self._save_settings()
        on = self.v["autopilot"].get()
        self.activity.event("🤖", T("Автопилот включён — отбирает, монтирует и публикует по стратегии «Доктора»") if on
                            else T("Автопилот выключен"))
        if on:
            self.root.after(500, lambda: self._autopilot_tick(force=True))

    def _autopilot_tick(self, force: bool = False):
        """Раз в 5 минут — проход автопилота в фоне (один за раз)."""
        if not force:
            self.root.after(self.AUTOPILOT_EVERY, self._autopilot_tick)
        if not self.v["autopilot"].get() or getattr(self, "_autopilot_busy", False):
            return
        if paths.team_dir() and not self.v["team_main"].get():
            return  # общая папка: автопилот ведёт компьютер друга, чтобы не делать работу дважды
        from .caption import _api_key
        self._autopilot_busy = True
        paused = bool(self.v["pub_paused"].get())

        def say(msg):
            self.root.after(0, lambda: self.status.config(text="🤖 " + tr_line(msg)[:140]))

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            from . import autopilot
            try:
                # план пустой — сразу набираем побольше (до 30 клипов), иначе обычным темпом
                budget = 30 if not autopilot.plan_rows() else autopilot.MAX_REVIEWS_PER_RUN
                stats = autopilot.run_step(_api_key(), paused, say, event, budget=budget)
                err = None
            except Exception as e:
                stats, err = {}, e
            self.root.after(0, lambda: done(stats, err))

        def done(stats, err):
            self._autopilot_busy = False
            if err:
                self.activity.event("❌", T("Автопилот: {0}").format(err), kind="error")
            elif any(stats.values()):
                self.status.config(text=T("🤖 Проход автопилота: опубликовано {0}, в очередь {1}, проверено {2}, в архив {3}")
                                   .format(stats["published"], stats["queued"], stats["reviewed"], stats["archived"]))
                self.refresh_clips()
            else:
                self.status.config(text=T("🤖 Автопилот: новых клипов для отбора нет, жду"))
            self._check_trends()
        threading.Thread(target=work, daemon=True).start()

    def _assist_tick(self):
        """Раз в 20 секунд: публикация через Telegram — отправить то, чему пора, и прочитать «✅ Выложил» / «⏭ Пропустить»."""
        self.root.after(20000, self._assist_tick)
        from . import telegram, tg_assist
        if getattr(self, "_assist_busy", False) or not telegram.load().get("token") or tg_assist.mode() != "telegram_assist":
            return
        if paths.team_dir() and not self.v["team_main"].get():
            return
        self._assist_busy = True
        paused = bool(self.v["pub_paused"].get())

        def event(icon, text, path=None, kind="info"):
            self.root.after(0, lambda: self.activity.event(icon, tr_line(text), path, kind))

        def work():
            try:
                stats = tg_assist.tick(paused, event)
            except Exception as e:
                stats = {"error": str(e)}
            self.root.after(0, lambda: done(stats))

        def done(stats):
            self._assist_busy = False
            self._tg_refresh_recipients()
            if stats.get("posted"):
                self.refresh_clips()
            if stats.get("need_more") and not getattr(self, "_autopilot_busy", False) \
                    and time.time() - getattr(self, "_need_more_t", 0) > 120:
                self._need_more_t = time.time()  # «Не выкладывать», а замены в плане нет — автопилот подберёт клип сейчас
                self._autopilot_tick(force=True)
        threading.Thread(target=work, daemon=True).start()

    def _check_trends(self):
        """Тема или стример из трендов совпали с клипом в архиве — подсказываем (или достаём сами)."""
        from . import archive, strategy
        hits = archive.trend_matches(strategy.get().get("trends") or [])
        new = [(r, h) for r, h in hits if r["id"] not in getattr(self, "_trend_seen", set())]
        if not new:
            return
        self._trend_seen = getattr(self, "_trend_seen", set()) | {r["id"] for r, _ in new}
        if (strategy.get().get("autopilot") or {}).get("auto_restore"):
            self.activity.event("★", T("Тренд «{0}» — достаю из архива клипов: {1}").format(new[0][1], len(new)))
            self.restore_archived([r for r, _ in new], quiet=True)
        else:
            self.activity.event("★", T("Тренд «{0}»: в архиве есть подходящие клипы ({1}) — вкладка «Архив»").format(
                new[0][1], len(new)))

    # ---------- обмен с «Доктором шортсов» ----------
    def _export_catalog(self):
        from . import exchange
        try:
            exchange.export_catalog()
        except Exception as e:
            self._append(T("Не удалось обновить каталог для аналитика: {0}").format(e) + "\n", important=False)

    def _exchange_tick(self):
        """Раз в 30 секунд: свежий каталог клипов для «Доктора» и проверка, не прислал ли он решения."""
        from . import exchange
        try:
            path = os.path.join(exchange.exchange_dir(), "decisions.json")
            mt = os.path.getmtime(path) if os.path.exists(path) else None
            if mt and mt != getattr(self, "_decisions_mtime", None):
                first = getattr(self, "_decisions_mtime", None) is None and \
                    os.path.exists(exchange._store()) and os.path.getmtime(exchange._store()) >= mt
                self._decisions_mtime = mt
                if not first:
                    self._apply_decisions(path)
            n = len(library.list_dates())
            if n and time.time() - getattr(self, "_catalog_time", 0) > 60:
                self._catalog_time = time.time()
                threading.Thread(target=self._export_catalog, daemon=True).start()
        except Exception as e:
            self._append(T("Обмен с аналитиком: {0}").format(e) + "\n", important=False)
        self.root.after(30000, self._exchange_tick)

    def _apply_decisions(self, path: str):
        from . import exchange
        try:
            sm = exchange.import_decisions(path)
        except Exception as e:
            self.activity.event("❌", T("Не получилось прочитать решения аналитика: {0}").format(e), kind="error")
            return
        self.activity.event("🩺", T("«Доктор шортсов» прислал решения: выложить — {0}, удалить — {1}, отмечено "
                                   "выложенным — {2}. Смотри колонку «Совет» во вкладке «Клипы».").format(
            sm["post"], sm["delete"], sm["posted"]))
        self.refresh_clips()

    def import_decisions_file(self):
        path = filedialog.askopenfilename(title=T("Файл решений аналитика"),
                                          filetypes=[("JSON", "*.json"), (T("Все файлы"), "*.*")])
        if path:
            self._apply_decisions(path)

    def delete_advised(self):
        """Удалить (в корзину) клипы, которые «Доктор» советует удалить — после подтверждения."""
        from . import exchange
        dec = exchange.load_decisions()
        clips = [c for d in library.list_dates() for c in library.list_clips(d)]
        todo = [c for c in clips if (dec.get(exchange.clip_id(c["path"])) or {}).get("delete")]
        if not todo:
            messagebox.showinfo(T("Удалить"), T("Аналитик ничего не советует удалять."))
            return
        lines = "\n".join(f"• {c.get('channel', '')}: «{(c.get('caption') or '')[:40]}» — "
                          f"{(dec[exchange.clip_id(c['path'])].get('reason') or '')[:60]}" for c in todo[:15])
        if not messagebox.askyesno(T("Удалить"), T("Аналитик советует удалить клипов: {0}.\n\n{1}\n\nПереложить их в "
                                                  "корзину? Вернуть можно в любой момент.").format(len(todo), lines)):
            return
        if self.preview.path in {c["path"] for c in todo}:
            self.preview.release()
        for c in todo:
            try:
                library.move_to_trash(c, None)
                self.activity.event("🗑", T("{0}: в корзину по совету аналитика — {1}").format(
                    c.get("channel", ""), dec[exchange.clip_id(c["path"])].get("reason") or "—"))
            except OSError:
                pass
        self.refresh_clips()

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
        # оценка ставится один раз (в сравнении со всеми клипами, и удалёнными тоже) и больше не меняется
        pool = [c for d in dates for c in library.list_clips(d, include_missing=True)]
        scores = library.frozen_ratings(pool + [c for c in clips if c["path"] not in {p["path"] for p in pool}])
        from . import policy
        pol_results = policy.load_results()
        from . import credit, exchange
        by_map = library.posted_by()
        from . import team as _team
        me_safe = _team._safe(paths.user_name()) if paths.team_dir() else ""
        credit_data = credit.load()
        decisions = exchange.load_decisions()
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
            if need == "advice" and self._advice_cell(c, decisions.get(exchange.clip_id(c["path"]))) in ("", "—"):
                continue
            img = self._thumb(c["path"])
            if img is None:
                missing.append(c["path"])
            sec = int(c.get("moment", c.get("start", 0)))
            cst = credit.state(c, credit_data)
            adv = decisions.get(exchange.clip_id(c["path"]))
            values = (f"{c['score10']}/10", self._policy_cell(c), {"on": "☑", "burned": "☑", "off": "☐", "unknown": "?"}[cst],
                      self._advice_cell(c, adv),
                      c.get("channel", "") + (f" · {c['by']}" if c.get("by") and c["by"] != me_safe else ""),
                      f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}", tr_line(detect.why(c)), c.get("caption", "") or "—",
                      *(self._posted_cell(c, p, by_map) for p in library.PLATFORMS))
            iid = self.tree.insert("", "end", text="", image=img or "", values=values)
            self.clip_by_iid[iid] = c
            if c["path"] in sel_paths:
                self.tree.selection_add(iid)
            shown += 1
        self._update_trash_button()
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

    def publish_plan(self, skip: set | None = None):
        """«Выложить → по плану аналитика»: следующий клип и площадка, которым уже пора (по советам «Доктора»)."""
        from datetime import datetime
        from . import exchange
        dates = library.list_dates()
        clips = [c for d in dates for c in library.list_clips(d)]
        skip = skip or set()
        from . import policy
        items = [t for t in exchange.plan(clips) if (t[0]["path"], t[1]) not in skip and t[0]["path"] not in skip
                 and not policy.publish_block(t[0]["path"], t[2].get("edits"))]
        now = datetime.now().isoformat(timespec="seconds")
        ready = [t for t in items if (t[2].get("when") or "") <= now]
        if not ready:
            self._plan_mode = False
            if items:
                w = items[0][2].get("when", "")
                messagebox.showinfo(T("Выложить"), T("Сейчас выкладывать нечего. Следующая публикация по плану: {0} — "
                                                    "{1} в {2}.").format(w.replace("T", " ")[:16], items[0][0].get("channel", ""),
                                                                         library.PLATFORM_NAMES[items[0][1]]))
            else:
                messagebox.showinfo(T("Выложить"), T("Плана от аналитика пока нет (или всё уже выложено)."))
            return
        clip, platform, _ = ready[0]
        self._plan_mode = True
        self.publish(platform, clip)

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
        from . import exchange, policy
        advice = ((exchange.decision_for(clip) or {}).get("platforms") or {}).get(platform) or {}
        block = policy.publish_block(clip["path"], advice.get("edits"))
        if block:  # жёсткое правило: с неисправленной наготой / языком вражды не публикуем
            self._plan_mode = False
            messagebox.showwarning(T("Выложить"), "⛔ " + tr_line(block))
            self.activity.event("⛔", f"{clip.get('channel', '')}: {tr_line(block)}", clip["path"], "error")
            return
        if advice.get("edits") and not getattr(self, "_variant_ready", None) == (clip["path"], platform):
            # «Доктор» посоветовал монтаж под эту площадку — собираем отдельную копию (сам клип не меняется)
            self.clips_info.config(text=T("Готовлю версию клипа для {0} по совету аналитика...").format(name))

            def work():
                try:
                    from . import edits
                    d = library.upload_dir()
                    os.makedirs(d, exist_ok=True)
                    for f in os.listdir(d):
                        try:
                            os.remove(os.path.join(d, f))
                        except OSError:
                            pass
                    title = advice.get("title") or clip.get("caption") or os.path.basename(clip["path"])[:-4]
                    out = os.path.join(d, library._safe_name(title) + ".mp4")
                    res = edits.build_variant(clip, advice["edits"], out, log=lambda m: None, platform=platform)
                    if res.get("skipped"):
                        self.root.after(0, lambda r=res: self.activity.event("✂", T("Монтаж для {0}: пропущено — {1}").format(
                            name, "; ".join(f"{x['type']}: {tr_line(x['why'])}" for x in r["skipped"])), kind="warn"))
                    err = None
                except Exception as e:
                    out, err = None, e
                self.root.after(0, lambda: done(out, err))

            def done(out, err):
                if err:
                    messagebox.showerror(T("Выложить"), T('Не получилось подготовить файл: {0}').format(err))
                    return
                self._variant_ready = (clip["path"], platform)
                self._variant_file = out
                self.publish(platform, clip)
            threading.Thread(target=work, daemon=True).start()
            return
        try:
            if getattr(self, "_variant_ready", None) == (clip["path"], platform):
                staged = self._variant_file
                self._variant_ready = None
            else:
                staged = library.stage_for_upload(clip)
        except OSError as e:
            messagebox.showerror(T("Выложить"), T('Не получилось подготовить файл: {0}').format(e))
            return
        opened = getattr(self, "_publish_opened", set())
        self._publish_opened = opened
        auto = platform in ("youtube", "tiktok", "instagram") and self.cfg.get("yt_auto", True)
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
                T("Программа сама откроет {0} в отдельном окне браузера и вставит туда файл, название, описание "
                  "и хэштеги. Тебе останется проверить и нажать «Опубликовать».\n"
                  "В первый раз войди в этом окне в свой аккаунт {0} — дальше он запомнится.").format(pname)) if auto else (
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
                ttk.Button(tools, text=T("▶  Вставить в {0} ещё раз").format(pname),
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
            from . import exchange as _ex
            post = dict(post, description=_ex.with_author(post.get("description", ""), c, platform))
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
                    try:  # запоминаем текст, который ушёл в публикацию — по нему «Доктор» найдёт видео в аналитике
                        library.record_published(
                            c["path"], platform, fields["title"].get("1.0", "end-1c").strip(),
                            (fields["description"].get("1.0", "end-1c").strip() + "\n\n"
                             + fields["hashtags"].get("1.0", "end-1c").strip()).strip())
                    except Exception:
                        pass
                else:
                    skip.add(c["path"])
                win.destroy()
                self.post_window = None
                self.refresh_clips()
                if getattr(self, "_plan_mode", False):
                    self.publish_plan(skip=skip | {(c["path"], platform)})
                    return
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
                    if platform == "youtube":
                        ok = browser_upload.youtube_upload(staged, title, desc, log=say)
                    else:  # TikTok / Instagram: одно поле — название, описание и хэштеги вместе
                        text = "\n\n".join(x for x in (title, desc) if x)
                        ok = (browser_upload.tiktok_upload if platform == "tiktok"
                              else browser_upload.instagram_upload)(staged, text, log=say)
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
        from . import exchange
        advice = ((exchange.decision_for(c) or {}).get("platforms") or {}).get(platform or "") or {}
        if advice.get("description") or advice.get("hashtags"):
            # тексты и хэштеги под эту площадку прислал «Доктор» — берём их
            if advice.get("title"):
                fields["title"].delete("1.0", "end")
                fields["title"].insert("1.0", advice["title"])
            fill({"description": advice.get("description", ""), "hashtags": " ".join(advice.get("hashtags") or [])})
            status.config(text=T("Тексты и хэштеги для {0} — от аналитика («Доктор шортсов»).").format(pname or ""))
        elif c["path"] in self.post_cache:
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
        """Удалить = переложить в корзину (вернуть можно, место освобождается после очистки корзины)."""
        sel = self._selected()
        if not sel:
            return
        if not messagebox.askyesno(T("Удалить"), T("Переложить в корзину клипов: {0}? Вернуть можно в любой момент "
                                                  "(кнопка «Корзина»).").format(len(sel))):
            return
        if self.preview.path in {c["path"] for c in sel}:
            self.preview.release()
        for c in sel:
            try:
                library.move_to_trash(c, c.get("score10"))
            except OSError as e:
                messagebox.showwarning(T("Удалить"), str(e))
            self.images.pop(c["path"], None)
        self.refresh_clips()
        self.clips_info.config(text=T("В корзине: {0}. Вернуть — кнопка «♻ Корзина».").format(len(sel)))

        def replan():  # удалённые клипы сразу уходят из плана и из очереди Telegram
            from . import autopilot
            try:
                autopilot.rebuild_schedule()
            except Exception:
                pass
        threading.Thread(target=replan, daemon=True).start()

    def _spec_for(self, channel: str) -> str | None:
        """Стример из списка (twitch-логин или @ник YouTube), которому соответствует имя канала из клипа."""
        ch = channel.lower().lstrip("@")
        for n in self._read_streamers():
            k = n.strip()
            k = k[3:] if k.startswith("yt:") else k
            if k.lower().lstrip("@") == ch or k.lower().rstrip("/").split("/")[-1].lstrip("@") == ch:
                return k
        return None

    @staticmethod
    def _spec_kind(spec: str) -> tuple[str, str, str]:
        """(платформа, что передать сайту, имя для памяти вебки)."""
        s = spec.strip()
        s = s[3:] if s.startswith("yt:") else s
        if s.startswith("@") or "youtu" in s:
            return "youtube", s, s.rstrip("/").split("/")[-1].lstrip("@").lower()
        return "twitch", s.lower(), s.lower()

    def queue_facecam(self):
        """Кнопка «Вебка» во вкладке «Очередь»: указать вебку выбранного стримера по кадру со стрима."""
        sel = self.queue_list.curselection()
        if not sel or sel[0] >= len(self.queue_keys):
            messagebox.showinfo(T("Вебка"), T("Выбери стримера в списке."))
            return
        kind, target, name = self._spec_kind(self.queue_keys[sel[0]])
        self._facecam_window(name, kind, target)

    def _fetch_stream_frame(self, name: str, kind: str, target: str, then, another: bool = False, on_fail=None):
        """Берёт кадр со стрима в фоне (из эфира или последней записи), потом вызывает then()."""
        from . import facecam
        self.clips_info.config(text=T("Беру кадр со стрима {0}... (до минуты)").format(name))
        self._append(T("Беру кадр со стрима {0}... (до минуты)").format(name) + "\n")

        def work():
            msgs = []
            try:
                res = facecam.grab_stream_frame(kind, target, name, log=msgs.append, another=another)
            except Exception as e:
                res, msgs = None, msgs + [f"{type(e).__name__}: {e}"]
            self.root.after(0, lambda: done(res, msgs))

        def done(res, msgs):
            if not res:
                messagebox.showwarning(T("Вебка"), T("Не получилось взять кадр со стрима {0}.").format(name) + "\n"
                                       + "\n".join(tr_line(m) for m in msgs[-3:]))
                if on_fail:
                    on_fail()
                return
            self.clips_info.config(text="")
            then()
        threading.Thread(target=work, daemon=True).start()

    def pick_facecam(self):
        """Окно, где мышкой обводят вебку стримера — дальше она всегда будет браться отсюда."""
        sel = self._selected()
        if not sel:
            return
        channel = sel[0].get("channel", "")
        spec = self._spec_for(channel)
        if spec:
            kind, target, _ = self._spec_kind(spec)
        else:
            url = sel[0].get("vod_url") or ""
            kind, target = ("youtube", "@" + channel) if "youtu" in url else ("twitch", channel.lower())
        self._facecam_window(channel, kind, target)

    def _facecam_window(self, channel: str, kind: str, target: str, fresh: bool = False, on_done=None,
                        another: bool = False, step: str = ""):
        """Окно «обведи вебку». on_done — что делать после (например, следующий стример перед стартом слежки)."""
        from . import facecam
        frame = facecam.frame_path(channel)
        if fresh or not os.path.exists(frame):
            self._fetch_stream_frame(channel, kind, target,
                                     lambda: self._facecam_window(channel, kind, target, on_done=on_done, step=step),
                                     another=another, on_fail=on_done)
            return
        finished = {"v": False}

        def finish():
            if not finished["v"]:
                finished["v"] = True
                if on_done:
                    self.root.after(100, on_done)
        old = getattr(self, "facecam_win", None)
        if old is not None:
            try:
                old.destroy()
            except tk.TclError:
                pass
        win = tk.Toplevel(self.root)
        self.facecam_win = win
        win.title(T('Вебка стримера {0}').format(channel) + (f"  ({step})" if step else ""))
        win.transient(self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), finish()))
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
            finish()

        def no_cam():
            facecam.set_manual(channel, None, no_cam=True)
            self._append(T('Для {0}: вебки нет — игра будет на размытом фоне.\n').format(channel))
            win.destroy()
            finish()

        def auto():
            facecam.set_manual(channel, None)
            self._append(T('Для {0}: вебка снова ищется автоматически.\n').format(channel))
            win.destroy()
            finish()

        def another_frame():
            win.destroy()
            self._facecam_window(channel, kind, target, fresh=True, on_done=on_done, another=True, step=step)
        bar = ttk.Frame(win, padding=6)
        bar.pack(fill="x")
        ttk.Button(bar, text=T("✔  Сохранить рамку"), command=save).pack(side="left")
        ttk.Button(bar, text=T("🚫 Нет веб-камеры"), command=no_cam).pack(side="left", padx=6)
        ttk.Button(bar, text=T("🔄 На этом кадре нет веб-камеры — другой кадр"), command=another_frame).pack(side="left")
        ttk.Button(bar, text=T("Пропустить (искать самой)"), command=auto).pack(side="right")
        if entry.get("manual") and (entry.get("region") or entry.get("none")):
            def keep():
                self._append(T('Для {0}: вебка как в прошлый раз.\n').format(channel))
                win.destroy()
                finish()
            ttk.Button(bar, text=T("↩ Оставить как в прошлый раз"), command=keep).pack(side="right", padx=6)
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
        from . import autopilot, telegram, tg_assist
        if telegram.load().get("token") and tg_assist.mode() == "telegram_assist" and not getattr(self, "_ahead_done", False):
            ahead = [r for r in autopilot.plan_rows() if not r.get("sent")]
            if messagebox.askyesno(T("Выход"), T(
                    "Ещё не отправлено видео из плана: {0}. Пока компьютер выключен, бот их не пришлёт.\n\n"
                    "Отправить в Telegram (тебе и другу) план и видео на сегодня (ближайшие сутки)? Запланируете их в "
                    "приложениях на указанное время — и всё выйдет без компьютера.").format(len(ahead))):
                self._send_ahead(then=self.on_close)
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
