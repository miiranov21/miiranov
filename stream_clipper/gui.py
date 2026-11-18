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
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from . import library, paths, updater

PROG = paths.program_dir()
SETTINGS = os.path.join(PROG, "settings.json")
STREAMERS = os.path.join(PROG, "streamers.txt")
STREAMERS_BACKUP = os.path.join(paths.default_work_dir(), "streamers.txt")  # запасная копия
RESUME = os.path.join(paths.default_work_dir(), "resume.json")  # что продолжить после обновления
KEYFILE = os.path.join(PROG, "claude_key.txt")
STREAMERS_HEADER = """# Стримеры, за которыми следит программа. По одному в строке.
# Twitch — логин из ссылки (twitch.tv/evelone2004 -> evelone2004)
# YouTube — @ник канала (youtube.com/@MrBeast -> @MrBeast)
"""
DEFAULTS = {"subs": True, "caption": True, "facecam": True, "audio": True,
            "top": "3", "length": "35", "quality": "1080", "autoupdate": True,
            "wm_on": False, "wm_text": "", "wm_image": "", "wm_pos": "плавает по экрану", "wm_op": "средне", "game_view": "целиком", "yt_browser": "не брать",
            "start_from": "с начала"}
WM_POS = {"плавает по экрану": "moving", "по центру": "center", "в углу": "corner"}
GAME_VIEW = {"целиком": "full", "крупнее": "wide", "только центр": "center"}
YT_BROWSERS = {"не брать": "", "Firefox": "firefox", "Chrome": "chrome", "Edge": "edge", "Opera": "opera",
               "Brave": "brave", "Vivaldi": "vivaldi"}
WM_OP = {"слабо": 0.25, "средне": 0.4, "сильно": 0.6}


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
        root.geometry("920x820")
        root.minsize(700, 640)
        try:
            root.iconbitmap(os.path.join(PROG, "icon.ico"))
        except Exception:
            pass
        self._build()
        self._install_shortcuts()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(150, self._drain)

    # ---------- интерфейс ----------
    def _build(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)
        main = ttk.Frame(self.nb, padding=8)
        clips = ttk.Frame(self.nb, padding=8)
        sett = ttk.Frame(self.nb, padding=8)
        self.nb.add(main, text="  Управление  ")
        self.nb.add(clips, text="  Клипы  ")
        self.nb.add(sett, text="  Настройки  ")
        self.sett = sett
        self._build_clips(clips)
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh_clips())

        top = ttk.Frame(main)
        top.pack(fill="x")
        # стримеры
        box = ttk.LabelFrame(top, text=" За кем следим (Twitch и YouTube — одновременно) ", padding=6)
        box.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.platforms = ttk.Notebook(box)
        self.platforms.pack(fill="both", expand=True)
        tw_names, yt_names = split_platforms(self._read_streamers())
        self.tw_text = self._platform_tab("  Twitch  ", "Ник из ссылки: twitch.tv/kaicenat → kaicenat", tw_names)
        self.yt_text = self._platform_tab("  YouTube  ", "Ник канала: youtube.com/@MrBeast → MrBeast", yt_names)
        self._build_queue_tab()
        self._update_platform_titles()
        ttk.Button(box, text="✔  Применить список (можно и во время слежки)",
                   command=self.apply_streamers).pack(fill="x", pady=(6, 0))

        # настройки
        opt = ttk.LabelFrame(top, text=" Что делать с клипом ", padding=6)
        opt.pack(side="left", fill="both", expand=True)
        self.v = {}
        for key, text in (("subs", "Субтитры (речь стримера)"),
                          ("caption", "Надпись-плашка с подписью к моменту"),
                          ("facecam", "Вебка стримера сверху"),
                          ("audio", "Учитывать громкость (крики, взрывы)")):
            self.v[key] = tk.BooleanVar(value=bool(self.cfg.get(key)))
            ttk.Checkbutton(opt, text=text, variable=self.v[key]).pack(anchor="w", pady=2)
        grid = ttk.Frame(opt)
        grid.pack(anchor="w", pady=(6, 0))
        digits = (self.root.register(lambda p: p == "" or (p.isdigit() and len(p) <= 3)), "%P")
        for r, (key, text, values, editable) in enumerate((
                ("top", "Клипов за час стрима:", ["1", "2", "3", "5", "10", "20", "50"], True),
                ("length", "Длина клипа, сек:", ["10", "15", "25", "35", "45", "60"], True),
                ("quality", "Качество:", ["720", "1080"], False))):
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
        ttk.Label(grid, text="Игра в кадре:").grid(row=3, column=0, sticky="w", pady=2)
        gv = self.cfg.get("game_view")
        self.v["game_view"] = tk.StringVar(value=gv if gv in GAME_VIEW else "целиком")
        ttk.Combobox(grid, textvariable=self.v["game_view"], values=list(GAME_VIEW), width=12,
                     state="readonly").grid(row=3, column=1, sticky="w", padx=6)
        ttk.Label(grid, text="числа можно вписать свои;\nменяются и во время работы",
                  foreground="#666").grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))

        # ключ Claude
        keyf = ttk.LabelFrame(sett, text=" Ключ Claude API для умных надписей (необязательно) ", padding=6)
        keyf.pack(fill="x", pady=6)
        self.key = tk.StringVar(value=self._read_key())
        ttk.Entry(keyf, textvariable=self.key, show="•").pack(side="left", fill="x", expand=True)
        ttk.Button(keyf, text="Сохранить ключ", command=self.save_key).pack(side="left", padx=6)
        self.key_status = ttk.Label(keyf, text="")
        self.key_status.pack(side="left")
        self._update_key_status()
        # вход в YouTube из браузера — чтобы YouTube не считал программу ботом (часто бывает через VPN)
        ytf = ttk.Frame(sett)
        ytf.pack(fill="x", pady=(0, 6))
        ttk.Label(ytf, text="Вход в YouTube через браузер:").pack(side="left")
        yb = self.cfg.get("yt_browser")
        self.v["yt_browser"] = tk.StringVar(value=yb if yb in YT_BROWSERS else "не брать")
        ttk.Combobox(ytf, textvariable=self.v["yt_browser"], values=list(YT_BROWSERS), width=12,
                     state="readonly").pack(side="left", padx=6)
        ttk.Label(ytf, text="нужно, если YouTube считает программу ботом (лучше Firefox, войди в нём в YouTube)",
                  foreground="#666").pack(side="left")

        # водяной знак
        wm = ttk.LabelFrame(sett, text=" Водяной знак — чтобы клипы не крали ", padding=6)
        wm.pack(fill="x", pady=(0, 6))
        r1 = ttk.Frame(wm)
        r1.pack(fill="x")
        self.v["wm_on"] = tk.BooleanVar(value=bool(self.cfg.get("wm_on")))
        ttk.Checkbutton(r1, text="Ставить", variable=self.v["wm_on"]).pack(side="left")
        ttk.Label(r1, text="  Текст:").pack(side="left")
        self.v["wm_text"] = tk.StringVar(value=self.cfg.get("wm_text", ""))
        ttk.Entry(r1, textvariable=self.v["wm_text"], width=20).pack(side="left", padx=4)
        ttk.Label(r1, text="(например @твой_канал)", foreground="#666").pack(side="left")
        self.v["wm_image"] = tk.StringVar(value=self.cfg.get("wm_image", ""))
        ttk.Button(r1, text="✕", width=3, command=lambda: self.v["wm_image"].set("")).pack(side="right")
        ttk.Button(r1, text="Логотип…", command=self.choose_logo).pack(side="right", padx=4)
        self.logo_label = ttk.Label(r1, text="", foreground="#666")
        self.logo_label.pack(side="right")
        self.v["wm_image"].trace_add("write", lambda *a: self._update_logo_label())
        self._update_logo_label()
        r2 = ttk.Frame(wm)
        r2.pack(fill="x", pady=(4, 0))
        ttk.Label(r2, text="Где:").pack(side="left")
        self.v["wm_pos"] = tk.StringVar(value=self.cfg.get("wm_pos") if self.cfg.get("wm_pos") in WM_POS
                                        else "плавает по экрану")
        ttk.Combobox(r2, textvariable=self.v["wm_pos"], values=list(WM_POS), width=18,
                     state="readonly").pack(side="left", padx=4)
        ttk.Label(r2, text="  Заметность:").pack(side="left")
        self.v["wm_op"] = tk.StringVar(value=self.cfg.get("wm_op") if self.cfg.get("wm_op") in WM_OP else "средне")
        ttk.Combobox(r2, textvariable=self.v["wm_op"], values=list(WM_OP), width=9,
                     state="readonly").pack(side="left", padx=4)
        ttk.Label(r2, text="  «плавает» — лучшая защита: знак нельзя обрезать или замазать",
                  foreground="#666").pack(side="left")

        self._build_telegram(sett)

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
        fromrow = ttk.Frame(main)
        fromrow.pack(fill="x", pady=(0, 4))
        ttk.Label(fromrow, text="Начать анализ стрима с:").pack(side="left")
        self.v["start_from"] = tk.StringVar(value=self.cfg.get("start_from") or "с начала")
        ttk.Combobox(fromrow, textvariable=self.v["start_from"], width=11,
                     values=["с начала", "сейчас", "0:30", "1:00", "1:30", "2:00", "3:00", "4:00"]
                     ).pack(side="left", padx=6)
        ttk.Label(fromrow, foreground="#666",
                  text="часы:минуты от начала стрима. Для ссылки и для уже идущих стримов Twitch").pack(side="left")

        # журнал
        logf = ttk.LabelFrame(main, text=" Что происходит ", padding=6)
        logf.pack(fill="both", expand=True, pady=(6, 0))
        self.log = ScrolledText(logf, height=8, font=("Consolas", 10), state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)
        bottom = ttk.Frame(main)
        bottom.pack(side="bottom", fill="x", pady=(4, 0), before=logf)
        self.v["autoupdate"] = tk.BooleanVar(value=bool(self.cfg.get("autoupdate", True)))
        ttk.Checkbutton(bottom, text="Обновляться автоматически", variable=self.v["autoupdate"]).pack(side="right")
        ttk.Button(bottom, text="⟳ Проверить обновления",
                   command=lambda: self.check_updates(manual=True)).pack(side="right", padx=6)
        self.status = ttk.Label(bottom, text="Готово. Не забудь включить VPN.", anchor="w", width=10)
        self.status.pack(side="left", fill="x", expand=True)
        # плашка «есть новая версия» (показывается, когда нужно)
        self.update_bar = tk.Frame(self.root, bg="#fff3c4")
        self.update_label = tk.Label(self.update_bar, bg="#fff3c4", font=("Segoe UI", 10, "bold"))
        self.update_label.pack(side="left", padx=10, pady=6)
        ttk.Button(self.update_bar, text="Обновить сейчас", command=self.install_update).pack(side="right", padx=8)
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
            m.add_command(label="Вырезать        Ctrl+X", command=lambda: w.event_generate("<<Cut>>"))
        m.add_command(label="Копировать     Ctrl+C", command=lambda: w.event_generate("<<Copy>>"))
        if not readonly:
            m.add_command(label="Вставить          Ctrl+V", command=lambda: w.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="Выделить всё   Ctrl+A", command=lambda: self._select_all(w))
        m.tk_popup(e.x_root, e.y_root)
        return "break"

    def _clips_menu(self, e):
        iid = self.tree.identify_row(e.y)
        if iid and iid not in self.tree.selection():
            self.tree.selection_set(iid)
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="▶  Смотреть", command=self.play_clip)
        m.add_command(label="📋  Копировать надпись   Ctrl+C", command=self.copy_caption)
        m.add_command(label="✔  Выложен / не выложен", command=self.toggle_posted)
        m.add_command(label="📂  Показать в папке", command=self.reveal_clip)
        m.add_command(label="🎥  Указать вебку этого стримера", command=self.pick_facecam)
        m.add_separator()
        m.add_command(label="🗑  Удалить   Delete", command=self.delete_clip)
        m.tk_popup(e.x_root, e.y_root)

    # ---------- файлы ----------
    def _platform_tab(self, title: str, hint: str, names: list[str]) -> tk.Text:
        f = ttk.Frame(self.platforms, padding=4)
        self.platforms.add(f, text=title)
        ttk.Label(f, text=hint + "  (по одному в строке)", foreground="#666").pack(anchor="w")
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
        self.platforms.add(f, text="  Очередь  ")
        ttk.Label(f, text="Кто выше — того программа обрабатывает первым", foreground="#666").pack(anchor="w")
        row = ttk.Frame(f)
        row.pack(fill="both", expand=True)
        self.queue_list = tk.Listbox(row, height=6, font=("Segoe UI", 11), activestyle="none", exportselection=False)
        self.queue_list.pack(side="left", fill="both", expand=True)
        side = ttk.Frame(row)
        side.pack(side="left", fill="y", padx=(6, 0))
        ttk.Button(side, text="⏫ Первым", command=lambda: self._queue_move("top")).pack(fill="x")
        ttk.Button(side, text="▲ Выше", command=lambda: self._queue_move(-1)).pack(fill="x", pady=4)
        ttk.Button(side, text="▼ Ниже", command=lambda: self._queue_move(1)).pack(fill="x")
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
        for i, k in enumerate(self.queue_keys, 1):
            yt = k.startswith("@") or "youtube.com" in k or "youtu.be" in k
            orig = shown.get(k, k)
            name = orig.lstrip("@") if not orig.startswith("http") else orig.rstrip("/").split("/")[-1]
            self.queue_list.insert("end", f"{i}. {'YouTube' if yt else 'Twitch'} — {name}")
        if sel and sel[0] < len(self.queue_keys):
            self.queue_list.selection_set(sel[0])

    def _queue_move(self, delta):
        sel = self.queue_list.curselection()
        if not sel:
            messagebox.showinfo("Очередь", "Выбери стримера в списке.")
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
            self._append("Очередь изменена — применится на следующем круге проверки: "
                         + " → ".join(k.lstrip("@") for k in keys) + "\n")

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
        tg = ttk.LabelFrame(parent, text=" 📱 Клипы на телефон (Telegram) ", padding=6)
        tg.pack(fill="x", pady=(0, 6))
        ttk.Label(tg, justify="left", foreground="#666", text=(
            "1) В Telegram найди @BotFather → /newbot → придумай имя → он пришлёт ключ (токен). Вставь его сюда.\n"
            "2) Папки по датам (лучше): создай группу → в её настройках включи «Темы» → добавь туда бота\n"
            "    администратором с правом «Управление темами» → напиши в группе любое сообщение.\n"
            "    Без группы: просто открой бота и нажми «Старт».   3) Нажми «Подключить».\n"
            "Клипы приходят ФАЙЛАМИ (без потери качества); в группе бот сам заводит тему-папку на каждый день."
        )).pack(anchor="w")
        row = ttk.Frame(tg)
        row.pack(fill="x", pady=(6, 0))
        self.tg_on = tk.BooleanVar(value=bool(cfg.get("on")))
        ttk.Checkbutton(row, text="Отправлять клипы", variable=self.tg_on, command=self._tg_toggle).pack(side="left")
        ttk.Label(row, text="  Ключ бота:").pack(side="left")
        self.tg_token = tk.StringVar(value=cfg.get("token", ""))
        ttk.Entry(row, textvariable=self.tg_token, show="•", width=24).pack(side="left", padx=4)
        ttk.Button(row, text="Подключить", command=self._tg_connect).pack(side="left")
        ttk.Button(row, text="Проверить", command=self._tg_test).pack(side="left", padx=4)
        self.tg_status = ttk.Label(row, text=("✔ подключено: " + cfg.get("name", "")) if cfg.get("chat_id")
                                   else "не подключено", foreground="#666")
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
            messagebox.showinfo("Telegram", "Сначала вставь ключ бота от @BotFather.")
            return
        self.tg_status.config(text="подключаю...")

        def work():
            try:
                chat_id, name, forum = telegram.find_chat(token)
                telegram.save({"token": token, "chat_id": chat_id, "name": name, "on": True, "forum": forum})
                telegram.send_text("✅ Stream Clipper подключён! " + (
                    "Клипы будут складываться в темы-папки по датам." if forum else
                    "Сюда будут приходить готовые клипы файлами (для папок по датам подключи группу с темами)."))
                label = f"✔ группа «{name}» (папки по датам)" if forum else f"✔ подключено: {name}"
                self.root.after(0, lambda: (self.tg_on.set(True), self.tg_status.config(text=label)))
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda: (self.tg_status.config(text="не подключено"),
                                            messagebox.showwarning("Telegram", f"Не получилось подключить:\n{err}")))
        threading.Thread(target=work, daemon=True).start()

    def _tg_test(self):
        from . import telegram

        def work():
            try:
                telegram.send_text("👋 Проверка связи от Stream Clipper")
                self.root.after(0, lambda: self.tg_status.config(text="✔ сообщение отправлено — проверь Telegram"))
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda: messagebox.showwarning("Telegram", f"Не отправилось:\n{err}"))
        threading.Thread(target=work, daemon=True).start()

    def choose_logo(self):
        path = filedialog.askopenfilename(title="Логотип для водяного знака",
                                          filetypes=[("Картинки", "*.png *.jpg *.jpeg *.webp"), ("Все файлы", "*.*")])
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
        self.logo_label.config(text="логотип выбран ✔" if p and os.path.exists(p) else "без логотипа")

    def _update_key_status(self):
        ok = bool(self.key.get().strip())
        self.key_status.config(text="✔ ключ есть" if ok else "нет ключа — надписи по шаблону")

    def _save_settings(self):
        self.cfg = {k: (v.get()) for k, v in self.v.items()}
        with open(SETTINGS, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=1)

    # ---------- запуск ----------
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
                json.dump({"top": top, "pre": pre, "post": post}, f)
        except OSError:
            return
        self._append(f"Настройки изменены: {top} клипов за час, по {pre + post} с — применятся к следующим клипам.\n")

    def _flags(self) -> list[str]:
        self._save_settings()
        c = self.cfg
        top, pre, post = self._clip_numbers()
        f = ["-n", str(top), "--pre", str(pre), "--post", str(post),
             "--max-height", c["quality"], "--game-view", GAME_VIEW.get(c.get("game_view"), "full"),
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
        try:
            start = paths.parse_start(c.get("start_from"))
        except ValueError as e:
            messagebox.showwarning("Время", str(e))
            start = None
        if start == "now":
            f += ["--from", "сейчас"]
        elif start:
            f += ["--from", f"{int(start // 3600)}:{int(start % 3600 // 60):02d}"]
        browser = YT_BROWSERS.get(c.get("yt_browser"), "")
        if browser:
            f += ["--cookies-browser", browser]
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
            self._append(f"Не удалось запустить: {e}\n")
            self.proc = None
            return
        self._set_running(True, what)
        threading.Thread(target=self._reader, args=(self.proc,), daemon=True).start()

    def apply_streamers(self):
        names = self._save_streamers()
        if self.proc:
            self._append("Список стримеров обновлён: " + (", ".join(names) or "пусто")
                         + ". Программа подхватит его через несколько секунд.\n")
        else:
            self.status.config(text="Список сохранён: " + (", ".join(names) or "пусто"))

    def start_watch(self):
        names = self._save_streamers()
        if not names:
            messagebox.showwarning("Нет стримеров", "Впиши хотя бы одного стримера во вкладку Twitch или YouTube.")
            return
        self._run(["watch", *self._flags()], "Слежу за: " + ", ".join(names), job=["watch"])

    def start_vod(self):
        url = self.url.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning("Нет ссылки", "Вставь ссылку на запись стрима (twitch.tv/videos/... или youtube.com/watch?v=...).")
            return
        self._run(["vod", url, *self._flags()], "Нарезаю " + url, job=["vod", url])

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
            self._append("\nОстанавливаю аккуратно: дорежу начатое и сохраню прогресс, чтобы потом продолжить "
                         "с этого места. Нажми «Стоп» ещё раз, чтобы остановить сразу.\n")
            self.b_stop.config(text="■  Стоп сразу")
            self._force_job = self.root.after(5 * 60 * 1000, self.force_stop)
            return
        self.force_stop()

    def force_stop(self):
        p = self.proc
        if not p:
            return
        self._append("\nОстанавливаю сразу...\n")
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
                    self.job = None
                    self.stopping = False
                    if getattr(self, "_force_job", None):
                        self.root.after_cancel(self._force_job)
                        self._force_job = None
                    self.b_stop.config(text="■  Стоп")
                    self._set_running(False)
                    if self.updating:  # остановились ради обновления — перезапускаемся и продолжим
                        self._restart()
                        return
                    if getattr(self, "restart_worker", False):  # обновилась только рабочая часть
                        self.restart_worker = False
                        job = self._last_job
                        self._append("=== Продолжаю работу на новой версии ===\n")
                        if job and job[0] == "vod" and len(job) > 1:
                            self.url.set(job[1])
                            self.root.after(500, self.start_vod)
                        else:
                            self.root.after(500, self.start_watch)
                        continue
                    if self.pending_update and self.v["autoupdate"].get():
                        self.root.after(1000, self.install_update)
                else:
                    self._append(item)
                    if "готово ->" in item:
                        self.root.after(500, self.refresh_clips)
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
                messagebox.showwarning("Обновление", f"Не удалось проверить обновления (интернет/VPN?):\n{err}")
            return
        if not info:
            if manual:
                messagebox.showinfo("Обновление", "У тебя последняя версия.")
            return
        self.pending_update = info
        if self.v["autoupdate"].get():
            self.install_update(auto=True)  # и во время работы: она продолжится после перезапуска
            return
        self.update_label.config(text=f"Доступна новая версия программы (от {info['date']})")
        self.update_bar.pack(side="top", fill="x", before=self.nb)

    def install_update(self, auto: bool = False):
        info = self.pending_update
        if not info or self.updating:
            return
        recs = paths.recordings_active() if self.proc else []
        if auto and recs:
            # идёт запись YouTube-эфира: перезапуск дал бы дыру в записи — ждём конца эфира
            self.update_label.config(text=f"Новая версия ждёт конца записи эфира ({', '.join(recs)[:40]})")
            self.update_bar.pack(side="top", fill="x", before=self.nb)
            if not getattr(self, "_deferred_logged", False):
                self._append("Есть обновление, но сейчас идёт запись эфира — поставлю его, когда эфир закончится.\n")
                self._deferred_logged = True
            self.root.after(3 * 60 * 1000, lambda: self.install_update(auto=True))
            return
        self._deferred_logged = False
        self.updating = True
        self._save_settings()
        self._append(f"\n=== Обновляю программу (версия от {info['date']}) ===\n")
        self.update_bar.pack_forget()

        def work():
            try:
                changed = updater.apply(info["sha"], log=lambda m: self.lines.put(m + "\n"))
            except Exception as e:
                self.lines.put(f"Обновление не удалось: {e}\n")
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
                self._append("Обновление установлено (менять ничего не пришлось).\n")
            elif self.proc:
                self.restart_worker = True
                self._append("Обновление установлено. Перезапускаю только рабочую часть "
                             "(окно не закрывается, работа продолжится сама)...\n")
                try:
                    open(paths.stop_request_path(), "w").close()
                except OSError:
                    pass
            else:
                self._append("Обновление установлено — окно перезапускать не нужно.\n")
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
        self._append("Аккуратно останавливаю работу (дорезаю начатое) — после перезапуска она продолжится сама...\n")
        try:
            open(paths.stop_request_path(), "w").close()
        except OSError:
            pass
        self.root.after(10 * 60 * 1000, self._force_stop_if_stuck)

    def _force_stop_if_stuck(self):
        if self.updating and self.proc:
            self._append("Работа не остановилась за 10 минут — останавливаю принудительно.\n")
            self.force_stop()

    def _resume_after_update(self):
        try:
            with open(RESUME, encoding="utf-8") as f:
                job = json.load(f)
            os.remove(RESUME)
        except Exception:
            return
        self._append("\n=== Программа обновлена — продолжаю работу с того же места ===\n")
        if job and job[0] == "vod" and len(job) > 1:
            self.url.set(job[1])
            self.start_vod()
        else:
            self.start_watch()

    def _restart(self):
        self._append("Перезапускаю программу...\n")
        flags = 0x08000000 if os.name == "nt" else 0
        try:
            subprocess.Popen([sys.executable, "-m", "stream_clipper.gui"], cwd=PROG, creationflags=flags)
        except Exception as e:
            messagebox.showinfo("Обновление", f"Обновление установлено. Открой программу заново.\n({e})")
        self.root.destroy()

    # ---------- вкладка «Клипы» ----------
    def _build_clips(self, parent):
        self.images: dict = {}
        bar = ttk.Frame(parent)
        bar.pack(fill="x")
        ttk.Label(bar, text="Дата:").pack(side="left")
        self.date_var = tk.StringVar()
        self.date_box = ttk.Combobox(bar, textvariable=self.date_var, width=12, state="readonly")
        self.date_box.pack(side="left", padx=(4, 12))
        self.date_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_clips())
        ttk.Label(bar, text="Стример:").pack(side="left")
        self.streamer_var = tk.StringVar(value="Все")
        self.streamer_box = ttk.Combobox(bar, textvariable=self.streamer_var, width=16, state="readonly")
        self.streamer_box.pack(side="left", padx=(4, 12))
        self.streamer_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_clips())
        self.hide_posted = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Скрыть выложенные", variable=self.hide_posted,
                        command=self.refresh_clips).pack(side="left")
        ttk.Button(bar, text="⟳ Обновить", command=self.refresh_clips).pack(side="right")

        style = ttk.Style()
        style.configure("Clips.Treeview", rowheight=136, font=("Segoe UI", 10))
        style.configure("Clips.Treeview.Heading", font=("Segoe UI", 10, "bold"))
        # кнопки и подпись закрепляем внизу, список занимает остальное место
        self.clips_info = ttk.Label(parent, text="", anchor="w")
        self.clips_info.pack(side="bottom", fill="x", pady=(6, 0))
        btns = ttk.Frame(parent)
        btns.pack(side="bottom", fill="x")
        for text, cmd in (("▶  Смотреть", self.play_clip), ("📋  Копировать надпись", self.copy_caption),
                          ("✔  Выложен / не выложен", self.toggle_posted), ("📂  Показать в папке", self.reveal_clip),
                          ("🎥  Указать вебку", self.pick_facecam), ("🗑  Удалить", self.delete_clip)):
            ttk.Button(btns, text=text, command=cmd).pack(side="left", padx=(0, 6))
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=6)
        cols = ("streamer", "moment", "caption", "created", "status")
        self.tree = ttk.Treeview(frame, columns=cols, show="tree headings", style="Clips.Treeview",
                                 selectmode="extended", height=3)
        self.tree.heading("#0", text="Превью")
        self.tree.column("#0", width=96, stretch=False)
        for c, title, w in (("streamer", "Стример", 120), ("moment", "Момент", 80), ("caption", "Надпись", 300),
                            ("created", "Создан", 70), ("status", "Статус", 100)):
            self.tree.heading(c, text=title)
            self.tree.column(c, width=w, stretch=(c == "caption"))
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.play_clip())
        self.tree.bind("<Return>", lambda e: self.play_clip())
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
        self.date_box.config(values=dates)
        if dates and self.date_var.get() not in dates:
            self.date_var.set(dates[0])
        date = self.date_var.get()
        clips = library.list_clips(date) if date else []
        names = sorted({c.get("channel", "") for c in clips})
        self.streamer_box.config(values=["Все", *names])
        if self.streamer_var.get() not in ["Все", *names]:
            self.streamer_var.set("Все")
        sel_paths = {self.clip_by_iid[i]["path"] for i in self.tree.selection() if i in self.clip_by_iid}
        self.tree.delete(*self.tree.get_children())
        self.clip_by_iid = {}
        missing = []
        shown = 0
        for c in clips:
            if self.streamer_var.get() != "Все" and c.get("channel") != self.streamer_var.get():
                continue
            if self.hide_posted.get() and c["posted"]:
                continue
            img = self._thumb(c["path"])
            if img is None:
                missing.append(c["path"])
            sec = int(c.get("moment", c.get("start", 0)))
            values = (c.get("channel", ""), f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}",
                      c.get("caption", "") or "—", c.get("created", ""), "✔ выложен" if c["posted"] else "новый")
            iid = self.tree.insert("", "end", text="", image=img or "", values=values)
            self.clip_by_iid[iid] = c
            if c["path"] in sel_paths:
                self.tree.selection_add(iid)
            shown += 1
        posted = sum(1 for c in clips if c["posted"])
        self.clips_info.config(text=f"Клипов за {date or '—'}: {len(clips)}, выложено: {posted}. "
                                    f"Двойной клик — посмотреть клип.")
        self.nb.tab(1, text=f"  Клипы ({len(clips) - posted} новых)  " if clips else "  Клипы  ")
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
            messagebox.showinfo("Клипы", "Сначала выбери клип в списке.")
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
            self.clips_info.config(text="Надпись скопирована — вставь её в название ролика (Ctrl+V).")

    def toggle_posted(self):
        sel = self._selected()
        if sel:
            value = not all(c["posted"] for c in sel)
            for c in sel:
                library.set_posted(c["path"], value)
            self.refresh_clips()

    def reveal_clip(self):
        for c in self._selected()[:1]:
            if os.name == "nt":
                subprocess.Popen(["explorer", "/select,", c["path"]])
            else:
                self._open(os.path.dirname(c["path"]))

    def delete_clip(self):
        sel = self._selected()
        if sel and messagebox.askyesno("Удалить", f"Удалить клипов: {len(sel)}? Файлы удалятся с диска."):
            for c in sel:
                for p in (c["path"], library.thumb_path(c["path"])):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
                library.set_posted(c["path"], False)
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
            messagebox.showinfo("Вебка", f"Пока нет кадра со стрима {channel}. Он появится, когда программа "
                                         f"нарежет следующий клип этого стримера.")
            return
        win = tk.Toplevel(self.root)
        win.title(f"Вебка стримера {channel}")
        win.transient(self.root)
        img = tk.PhotoImage(file=frame)
        W, H = img.width(), img.height()
        ttk.Label(win, text="Обведи мышкой вебку стримера (зажми левую кнопку и тяни). "
                            "Рамка будет использоваться для всех следующих клипов.",
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
                messagebox.showinfo("Вебка", "Сначала обведи вебку мышкой.", parent=win)
                return
            facecam.set_manual(channel, tuple(round(v, 4) for v in state["box"]))
            self._append(f"Вебка стримера {channel} задана вручную — применится к следующим клипам.\n")
            win.destroy()

        def no_cam():
            facecam.set_manual(channel, None, no_cam=True)
            self._append(f"Для {channel}: вебки нет — игра будет на размытом фоне.\n")
            win.destroy()

        def auto():
            facecam.set_manual(channel, None)
            self._append(f"Для {channel}: вебка снова ищется автоматически.\n")
            win.destroy()
        bar = ttk.Frame(win, padding=6)
        bar.pack(fill="x")
        ttk.Button(bar, text="✔  Сохранить рамку", command=save).pack(side="left")
        ttk.Button(bar, text="У этого стримера нет вебки", command=no_cam).pack(side="left", padx=6)
        ttk.Button(bar, text="Искать автоматически", command=auto).pack(side="left")
        ttk.Button(bar, text="Отмена", command=win.destroy).pack(side="right")
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
        if self.proc and not messagebox.askyesno("Выход", "Программа сейчас работает. Остановить и закрыть?\n"
                                                          "(Лучше сначала нажать «Стоп» — тогда прогресс сохранится.)"):
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
