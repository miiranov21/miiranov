"""Загрузка клипа на YouTube через браузер: программа сама открывает страницу загрузки,
вставляет файл, название, описание и хэштеги — человеку остаётся нажать «Опубликовать».

Браузер (Edge или Chrome) запускается ОБЫЧНЫМ образом, но с отдельным профилем и «пультом управления»
(remote debugging). Поэтому вход в Google работает как в простом браузере: войти нужно один раз, дальше
профиль помнит аккаунт. Программа подключается к этому окну и заполняет поля.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time

from . import paths
from .i18n import T

PORT = 9333
UPLOAD_URL = "https://www.youtube.com/upload"
LOGIN_WAIT = 600  # сколько ждём, пока человек войдёт в Google в первый раз (секунд)

# все селекторы YouTube Studio в одном месте — если YouTube что-то поменяет, править только тут
SEL_FILE = 'input[type="file"]'
SEL_TITLE = "#title-textarea #textbox"
SEL_DESC = "#description-textarea #textbox"
SEL_NOT_KIDS = ('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], '
                'tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"]')
SEL_NEXT = "#next-button"
SEL_PUBLIC = 'tp-yt-paper-radio-button[name="PUBLIC"]'
SEL_DONE = "#done-button"


def profile_dir() -> str:
    return os.path.join(paths.default_work_dir(), "browser_profile")


def find_browser() -> str | None:
    """Edge есть на любом Windows; Chrome — если установлен. Можно указать свой путь в STREAM_CLIPPER_BROWSER."""
    env = os.environ.get("STREAM_CLIPPER_BROWSER")
    if env and os.path.exists(env):
        return env
    cands = []
    if os.name == "nt":
        for base in (os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     os.environ.get("LOCALAPPDATA", "")):
            if base:
                cands += [os.path.join(base, r"Google\Chrome\Application\chrome.exe"),
                          os.path.join(base, r"Microsoft\Edge\Application\msedge.exe")]
    elif sys.platform == "darwin":
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        cands += [shutil.which(n) or "" for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge")]
    return next((c for c in cands if c and os.path.exists(c)), None)


def have_playwright() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except Exception:
        return False


def install_playwright(log=print) -> bool:
    """Ставим пакет управления браузером (сам браузер не качается — берётся Edge/Chrome с компьютера)."""
    log(T("Ставлю модуль управления браузером (один раз, ~40 МБ)..."))
    exe = sys.executable
    if exe.lower().endswith("pythonw.exe"):
        exe = exe[:-5] + ".exe"
    r = subprocess.run([exe, "-m", "pip", "install", "-q", "playwright"], capture_output=True, text=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if r.returncode != 0:
        log(T("Не удалось поставить playwright: ") + (r.stderr or r.stdout)[-400:])
        return False
    import importlib
    importlib.invalidate_caches()
    return have_playwright()


def _port_open() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=0.5):
            return True
    except OSError:
        return False


def ensure_browser(log=print) -> bool:
    """Запускает отдельное окно браузера с «пультом», если оно ещё не открыто."""
    if _port_open():
        return True
    exe = find_browser()
    if not exe:
        log(T("Не нашёл Edge или Chrome на компьютере."))
        return False
    os.makedirs(profile_dir(), exist_ok=True)
    args = [exe, f"--remote-debugging-port={PORT}", f"--user-data-dir={profile_dir()}",
            "--no-first-run", "--no-default-browser-check", "about:blank"]
    if os.environ.get("STREAM_CLIPPER_BROWSER_ARGS"):  # для проверок
        args[1:1] = os.environ["STREAM_CLIPPER_BROWSER_ARGS"].split()
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    for _ in range(60):
        if _port_open():
            return True
        time.sleep(0.5)
    log(T("Браузер не ответил. Закрой все окна этого браузера и попробуй ещё раз."))
    return False


def _set_text(page, selector: str, text: str) -> None:
    box = page.locator(selector).first
    box.wait_for(state="visible", timeout=60000)
    box.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Delete")
    for i, line in enumerate(text.split("\n")):  # переносы строк — нажатием Enter, иначе YouTube их съедает
        if i:
            page.keyboard.press("Enter")
        if line:
            page.keyboard.insert_text(line)


def _try(step: str, fn, log) -> bool:
    try:
        fn()
        return True
    except Exception as e:
        log(T('Шаг «{0}» не получился ({1}) — сделай его вручную.').format(step, type(e).__name__))
        return False


def youtube_upload(file: str, title: str, description: str, log=print, url: str | None = None) -> bool:
    """Открывает страницу загрузки YouTube в отдельном окне и заполняет всё, кроме кнопки «Опубликовать».
    Возвращает True, если файл вставлен (дальше человек жмёт кнопку)."""
    url = url or os.environ.get("STREAM_CLIPPER_YT_UPLOAD_URL") or UPLOAD_URL
    if not have_playwright() and not install_playwright(log):
        return False
    if not ensure_browser(log):
        return False
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        blank = [p for p in ctx.pages if p.url in ("about:blank", "chrome://newtab/", "edge://newtab/")]
        page = blank[0] if blank else ctx.new_page()  # пустую стартовую вкладку используем, а не плодим новые
        page.bring_to_front()
        log(T("Открываю страницу загрузки YouTube..."))
        page.goto(url, wait_until="domcontentloaded")
        deadline = time.time() + LOGIN_WAIT
        asked = False
        while True:
            if page.locator(SEL_FILE).count():
                break
            if not asked and "accounts.google" in page.url:
                log(T("Войди в свой Google-аккаунт в открывшемся окне — это нужно только один раз."))
                asked = True
            if time.time() > deadline:
                log(T("Не дождался страницы загрузки (не вошёл в аккаунт?). Попробуй ещё раз."))
                return False
            page.wait_for_timeout(1000)
            if asked and "accounts.google" not in page.url and "upload" not in page.url \
                    and "studio.youtube" not in page.url:
                page.goto(url, wait_until="domcontentloaded")  # после входа Google может увести на главную
        page.locator(SEL_FILE).first.set_input_files(file)
        log(T("Файл вставлен, YouTube начал загрузку."))
        _try(T("название"), lambda: _set_text(page, SEL_TITLE, title[:100]), log)
        _try(T("описание"), lambda: _set_text(page, SEL_DESC, description[:5000]), log)
        if _try(T("«не для детей»"), lambda: page.locator(SEL_NOT_KIDS).first.click(timeout=20000), log):
            ok = True
            for _ in range(3):  # «Далее»: Детали → Элементы → Проверки → Доступ
                ok = _try(T("Далее"), lambda: (page.locator(SEL_NEXT).first.click(timeout=20000),
                                            page.wait_for_timeout(1200)), log)
                if not ok:
                    break
            if ok:
                _try(T("«Открытый доступ»"), lambda: page.locator(SEL_PUBLIC).first.click(timeout=20000), log)
        log(T("Готово: проверь и нажми «Опубликовать» в окне YouTube."))
        return True
