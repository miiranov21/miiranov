"""Панель «Что происходит» — понятная картинка вместо сплошного текста журнала.

Сверху — карточки стримеров (что с каждым сейчас происходит, до какого времени разобран стрим, сколько
клипов, превью последнего клипа). Ниже — лента событий с иконками: начал стримера, клип готов, переходим
к следующему, предупреждения. Полный текстовый журнал никуда не делся — он за кнопкой «Подробный журнал».
Строки журнала рабочей части разбираются здесь по шаблонам (рабочая часть пишет по-русски).
"""
from __future__ import annotations

import os
import re
import time
import tkinter as tk
from tkinter import ttk

from . import library
from .i18n import T, tr_line

PLATFORM_COLOR = {"twitch": "#9147ff", "youtube": "#ff2b2b"}
STATUS = {  # значок, текст
    "waiting": ("⏳", "жду эфира или новой записи"),
    "analyzing": ("🔍", "разбираю запись стрима"),
    "recording": ("🔴", "в эфире — пишу и нарезаю"),
    "ending": ("⏹", "стрим закончился — дорезаю"),
    "done": ("✔", "разобрано"),
    "stopped": ("⏸", "остановлено"),
    "error": ("⚠", "ошибка — см. ленту ниже"),
}


def _key(name: str) -> str:
    return (name or "").strip().lower().lstrip("@")


class ActivityPanel(ttk.Frame):
    MAX_EVENTS = 60

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        pal = app.pal or {}
        self.c_panel = pal.get("panel", "#ffffff")
        self.c_field = pal.get("field", "#f4f4f4")
        self.c_fg = pal.get("fg", "#111111")
        self.c_muted = pal.get("muted", "#777777")
        self.c_accent = pal.get("accent", "#3b82f6")
        self.cards: dict = {}      # ключ стримера -> данные и виджеты карточки
        self.order: list = []
        self.current = None        # над каким стримером сейчас идёт работа
        self.last_path = None      # путь последнего готового клипа (строка «готово -> ...» идёт перед «✅»)
        self.images: list = []     # чтобы картинки не пропадали
        self.cards_box = ttk.Frame(self)
        self.cards_box.pack(fill="x")
        self.empty = ttk.Label(self.cards_box, foreground=self.c_muted, text=T(
            "Нажми «Следить за стримерами» или «Нарезать» — здесь будет видно, что происходит."))
        self.empty.pack(anchor="w", pady=4)
        ttk.Separator(self).pack(fill="x", pady=(6, 4))
        feed_wrap = ttk.Frame(self)
        feed_wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(feed_wrap, highlightthickness=0, bg=self.c_field, height=150)
        sb = ttk.Scrollbar(feed_wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.feed = tk.Frame(self.canvas, bg=self.c_field)
        self._feed_win = self.canvas.create_window(0, 0, window=self.feed, anchor="nw")
        self.feed.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._feed_win, width=e.width))
        for w in (self.canvas, self.feed):
            w.bind("<MouseWheel>", self._wheel)
        self.after(5000, self._tick)

    # ---------- карточки ----------
    def _wheel(self, e):
        self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def card(self, name: str, kind: str = "") -> dict:
        k = _key(name)
        if k in self.cards:
            c = self.cards[k]
            if kind and not c["kind"]:
                c["kind"] = kind
                self._draw_avatar(c)
            return c
        if self.empty.winfo_exists():
            self.empty.destroy()
        kind = kind or ("youtube" if name.startswith("@") else "")
        fr = tk.Frame(self.cards_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_muted,
                      padx=8, pady=6)
        av = tk.Canvas(fr, width=40, height=40, bg=self.c_panel, highlightthickness=0)
        av.grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, 8))
        title = tk.Label(fr, text=name.lstrip("@"), bg=self.c_panel, fg=self.c_fg, font=("Segoe UI", 11, "bold"),
                         anchor="w")
        title.grid(row=0, column=1, sticky="w")
        status = tk.Label(fr, text="", bg=self.c_panel, fg=self.c_fg, font=("Segoe UI", 10), anchor="w")
        status.grid(row=1, column=1, sticky="w")
        detail = tk.Label(fr, text="", bg=self.c_panel, fg=self.c_muted, font=("Segoe UI", 9), anchor="w")
        detail.grid(row=2, column=1, sticky="w")
        thumb = tk.Label(fr, bg=self.c_panel)
        thumb.grid(row=0, column=2, rowspan=3, sticky="e", padx=(10, 0))
        fr.columnconfigure(1, weight=1)
        c = {"name": name.lstrip("@"), "kind": kind, "frame": fr, "avatar": av, "status": status, "detail": detail,
             "thumb": thumb, "state": "waiting", "clips": 0, "upto": None, "what": ""}
        self.cards[k] = c
        self.order.append(k)
        self._draw_avatar(c)
        self._set(c, "waiting")
        self._layout()
        return c

    def _draw_avatar(self, c):
        av = c["avatar"]
        av.delete("all")
        color = PLATFORM_COLOR.get(c["kind"], self.c_accent)
        av.create_oval(2, 2, 38, 38, fill=color, outline="")
        av.create_text(20, 20, text=(c["name"][:1] or "?").upper(), fill="#ffffff", font=("Segoe UI", 15, "bold"))

    def _layout(self):
        cols = 3
        for i, k in enumerate(self.order):
            self.cards[k]["frame"].grid(row=i // cols, column=i % cols, sticky="ew", padx=4, pady=4)
        for col in range(cols):
            self.cards_box.columnconfigure(col, weight=1, uniform="cards")

    def _set(self, c, state: str | None = None, what: str | None = None):
        if state:
            c["state"] = state
        if what is not None:
            c["what"] = what
        icon, text = STATUS[c["state"]]
        c["status"].config(text=f"{icon}  {T(text)}",
                           fg="#ff4d4d" if c["state"] == "recording" else ("#f0a020" if c["state"] == "error" else self.c_fg))
        parts = []
        if c["what"] and c["state"] in ("analyzing", "recording", "ending"):
            parts.append(T(c["what"]))
        if c["upto"]:
            parts.append(T("разобрано до {0}").format(c["upto"]))
        if c["clips"]:
            parts.append(T("клипов: {0}").format(c["clips"]))
        c["detail"].config(text="  ·  ".join(parts))
        border = self.c_accent if c["state"] in ("analyzing", "recording", "ending") else self.c_muted
        c["frame"].config(highlightbackground=border, highlightthickness=2 if border == self.c_accent else 1)

    def _thumb(self, path: str, height: int = 64):
        tp = library.thumb_path(path)
        if not os.path.exists(tp):
            library.make_thumb(path)
        if not os.path.exists(tp):
            return None
        try:
            img = tk.PhotoImage(file=tp)
            while img.height() > height:
                img = img.subsample(2)
        except tk.TclError:
            return None
        self.images.append(img)
        self.images = self.images[-200:]
        return img

    # ---------- лента событий ----------
    def event(self, icon: str, text: str, path: str | None = None, kind: str = "info"):
        """Строка ленты: значок · текст · время справа (новые — сверху); у клипа — превью, клик открывает его."""
        bg = self.c_field
        row = tk.Frame(self.feed, bg=bg, pady=1)
        slaves = self.feed.pack_slaves()
        if slaves:
            row.pack(fill="x", padx=6, before=slaves[0])
        else:
            row.pack(fill="x", padx=6)
        color = {"warn": "#f0a020", "error": "#ff4d4d"}.get(kind, self.c_fg)
        widgets = [row]
        widgets.append(tk.Label(row, text=icon, bg=bg, font=("Segoe UI Emoji", 12), width=2))
        widgets[-1].pack(side="left", padx=(0, 4))
        widgets.append(tk.Label(row, text=time.strftime("%H:%M"), bg=bg, fg=self.c_muted, font=("Segoe UI", 9)))
        widgets[-1].pack(side="right", padx=(6, 0))
        if path:
            img = self._thumb(path, 40)
            if img:
                widgets.append(tk.Label(row, image=img, bg=bg))
                widgets[-1].pack(side="right", padx=4)
        widgets.append(tk.Label(row, text=text, bg=bg, fg=color, anchor="w", justify="left", wraplength=760,
                                font=("Segoe UI", 10, "bold" if kind == "clip" else "normal")))
        widgets[-1].pack(side="left", fill="x", expand=True)
        for w in widgets:
            w.bind("<MouseWheel>", self._wheel)
            if path:
                w.configure(cursor="hand2")
                w.bind("<Button-1>", lambda e, p=path: self.app.show_clip(p))
        for old in self.feed.pack_slaves()[self.MAX_EVENTS:]:
            old.destroy()
        self.canvas.yview_moveto(0)

    # ---------- разбор строк журнала рабочей части ----------
    def worker_line(self, raw: str) -> bool:
        """Возвращает True, если строка превратилась во что-то видимое (карточку/событие)."""
        line = raw.strip()
        if not line:
            return False
        m = re.match(r"^👀 Слежу за: (.+)$", line)
        if m:
            names = []
            for part in m.group(1).split(", "):
                mm = re.match(r"^(.+?) \((twitch|youtube)\)$", part.strip())
                nm, kind = (mm.group(1), mm.group(2)) if mm else (part.strip(), "")
                self.card(nm, kind)
                names.append(nm.lstrip("@"))
            self.event("👀", T("Слежу за: {0}").format(", ".join(names)))
            return True
        m = re.match(r"^▶ (.+?): начинаю работу(?: \(стрим идёт\))? — «(.*)»$", line)
        if m:
            name, title = m.group(1), m.group(2)
            self._switch_to(name)
            c = self.card(name)
            self._set(c, "analyzing", "начинаю")
            self.event("▶", T("Начинаю {0} — «{1}»").format(c["name"], title))
            return True
        m = re.match(r"^▶ (.+?): (начинаю|продолжаю) запись эфира(?: «(.*)»)?$", line)
        if m:
            c = self.card(m.group(1))
            self.current = _key(m.group(1))
            self._set(c, "recording", "пишу эфир")
            self.event("🔴", T("{0} в эфире — пишу и нарезаю по ходу").format(c["name"]))
            return True
        m = re.match(r"^🔴 (.+?) в эфире$", line)
        if m:
            c = self.card(m.group(1))
            self._set(c, "recording", "")
            self.event("🔴", T("{0} начал эфир").format(c["name"]))
            return True
        m = re.match(r"^⏹ (.+?): стрим закончился", line)
        if m:
            c = self.card(m.group(1))
            self._set(c, "ending", "дорезаю последнее")
            self.event("⏹", T("{0}: стрим закончился — дорезаю последнее").format(c["name"]))
            return True
        m = re.match(r"^(?:\[\d+/\d+\] )?готово -> (.+)$", line)
        if m:
            self.last_path = m.group(1).strip()
            return False
        m = re.match(r"^✅ (.+?): клип (\S+) готов — «(.*)»$", line)
        if m:
            c = self.card(m.group(1))
            c["clips"] += 1
            path = self.last_path if self.last_path and os.path.exists(self.last_path) else None
            if path:
                img = self._thumb(path, 64)
                if img:
                    c["thumb"].config(image=img)
            self._set(c)
            self.event("✅", T("{0}: клип {1} готов — «{2}»").format(c["name"], m.group(2), m.group(3)), path, "clip")
            self.last_path = None
            return True
        m = re.match(r"^\[(.+?)\] промежуточная нарезка во время эфира$", line)
        if m:
            c = self.card(m.group(1))
            self.current = _key(m.group(1))
            self._set(c, "recording", "нарезаю записанное")
            return True
        m = re.match(r"^⚠ клип (\S+): возможные нарушения правил — (.+?) \(", line)
        if m:
            who = self.cards.get(self.current, {}).get("name", "")
            self.event("⚠", T("{0}: в клипе {1} возможны нарушения правил — {2}. Проверь во вкладке «Клипы».")
                       .format(who, m.group(1), tr_line(m.group(2))), kind="warn")
            return True
        m = re.match(r"^Новые настройки подхвачены: (.+)$", line)
        if m:
            self.event("⚙", T("Настройки применены: {0}").format(tr_line(m.group(1))))
            return True
        # что делается прямо сейчас — в строку карточки (без ленты)
        c = self.cards.get(self.current)
        if c:
            for rx, what in ((r"^\[\d+/\d+\] качаю кусок", "качаю кусок для клипа"),
                             (r"^распознаю речь", "делаю субтитры"),
                             (r"^анализирую звук и картинку", "слушаю звук и смотрю картинку"),
                             (r"^чат: \d+ сообщений", "читаю чат"),
                             (r"^скачиваю чат", "читаю чат"),
                             (r"^Ищу моменты", "ищу интересные моменты"),
                             (r"^подпись:", "придумываю надпись"),
                             (r"^вебка ", "ставлю вебку")):
                if re.match(rx, line):
                    self._set(c, what=what)
                    return False
        if re.search(r"ОШИБКА|не смог|не получил|нет связи|не бот|ошибка обработки", line):
            mm = re.match(r"^\[(.+?)\] (.+)$", line)
            if mm and _key(mm.group(1)) in self.cards:
                c = self.cards[_key(mm.group(1))]
                self._set(c, "error", "")
                text = re.sub(r"^\[.+?\]\s*", "", tr_line(line))  # переводим строку целиком, потом убираем «[ник]»
                self.event("❌", f"{c['name']}: {text}"[:220], kind="error")
            else:
                self.event("❌", tr_line(line)[:220], kind="error")
            return True
        return False

    def _switch_to(self, name: str):
        """Начали разбирать другого стримера — прежний (записи разбираются по очереди) уже готов."""
        k = _key(name)
        for ok, c in self.cards.items():
            if ok != k and c["state"] == "analyzing":
                self._set(c, "done", "")
                self.event("⏭", T("{0} разобран — переходим к {1}").format(c["name"], name.lstrip("@")))
        self.current = k

    def stopped(self):
        for c in self.cards.values():
            if c["state"] in ("analyzing", "recording", "ending", "waiting"):
                self._set(c, "stopped", "")
        self.event("⏸", T("Работа остановлена"))

    def info(self, text: str, icon: str = "ℹ"):
        t = text.strip().strip("=").strip()
        if t:
            self.event(icon, t)

    def _tick(self):
        """Раз в несколько секунд — «разобрано до» из памяти программы."""
        try:
            if self.cards:
                from . import progress
                data = progress.load()
                for k, c in self.cards.items():
                    entries = [e for e in data.values() if _key(e.get("channel", "")) == k]
                    if entries:
                        e = max(entries, key=lambda e: e.get("updated", 0))
                        sm = progress.summary(e)
                        up = progress.fmt(sm["upto"]) if sm["upto"] else None
                        if up != c["upto"]:
                            c["upto"] = up
                            self._set(c)
        except Exception:
            pass
        self.after(5000, self._tick)
