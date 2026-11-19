"""Автообновление программы с GitHub (репозиторий открытый — пароль не нужен)."""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from datetime import datetime

from . import paths
from .i18n import T

REPO = "miiranov21/miiranov"
BRANCH = "claude/tender-cerf-agbshu"
# Эти файлы — твои: при обновлении не трогаем
KEEP = {"streamers.txt", "settings.json", "claude_key.txt", "version.txt"}
UA = {"User-Agent": "stream-clipper-updater", "Accept": "application/vnd.github+json"}


def _version_file(root: str) -> str:
    return os.path.join(root, "version.txt")


def local_version(root: str | None = None) -> str:
    try:
        return open(_version_file(root or paths.program_dir()), encoding="utf-8").read().strip()
    except OSError:
        return ""


def _sha_via_git() -> str:
    """Номер последней версии так же, как спрашивает обычный git — без лимита API GitHub
    (у API всего 60 запросов в час на адрес, а через общий VPN он быстро кончается)."""
    url = f"https://github.com/{REPO}.git/info/refs?service=git-upload-pack"
    req = urllib.request.Request(url, headers={"User-Agent": "git/2.45.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read().decode("utf-8", errors="replace")
    ref = "refs/heads/" + BRANCH
    for line in data.split("\n"):
        parts = line.split(" ")
        if len(parts) >= 2 and parts[1].split("\x00")[0] == ref:
            return parts[0][-40:]
    raise RuntimeError(T("ветка с обновлениями не найдена"))


def _sha_via_api() -> tuple[str, str]:
    url = f"https://api.github.com/repos/{REPO}/commits/{BRANCH.replace('/', '%2F')}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        data = json.load(r)
    when = data.get("commit", {}).get("committer", {}).get("date", "")
    try:
        when = datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone().strftime("%d.%m %H:%M")
    except ValueError:
        pass
    return data["sha"], when


def check(root: str | None = None) -> dict | None:
    """Есть ли новая версия. Возвращает {'sha', 'date'} или None (уже последняя)."""
    try:
        sha, when = _sha_via_git(), datetime.now().strftime("%d.%m %H:%M")
    except Exception:
        sha, when = _sha_via_api()  # запасной путь
    if sha == local_version(root):
        return None
    return {"sha": sha, "date": when}


def apply(sha: str, root: str | None = None, log=print) -> list[str]:
    """Скачивает версию и раскладывает файлы поверх программы. Возвращает список изменившихся файлов."""
    root = root or paths.program_dir()
    url = f"https://codeload.github.com/{REPO}/zip/{sha}"
    log(T("Скачиваю обновление..."))
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]}),
                                timeout=120) as r:
        data = r.read()
    old_req = _read(os.path.join(root, "requirements.txt"))
    changed: list[str] = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        top = names[0].split("/")[0] + "/"
        for name in names:
            rel = name[len(top):]
            if not rel or name.endswith("/"):
                continue
            dest = os.path.join(root, *rel.split("/"))
            if os.path.basename(rel) in KEEP and os.path.exists(dest):
                continue
            content = z.read(name)
            try:
                with open(dest, "rb") as f:
                    if f.read() == content:
                        continue  # файл не поменялся
            except OSError:
                pass
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            tmp = dest + ".new"
            with open(tmp, "wb") as out:
                out.write(content)
            os.replace(tmp, dest)
            changed.append(rel)
    with open(_version_file(root), "w", encoding="utf-8") as f:
        f.write(sha)
    if _read(os.path.join(root, "requirements.txt")) != old_req:
        log(T("Ставлю новые библиотеки..."))
        flags = 0x08000000 if os.name == "nt" else 0
        subprocess.run([python_exe(), "-m", "pip", "install", "-q", "-r", os.path.join(root, "requirements.txt")],
                       cwd=root, creationflags=flags)
    log(T("Обновление установлено."))
    return changed


# файлы, которые использует само окно программы: если поменялись они — окно надо перезапустить
WINDOW_FILES = {"stream_clipper/gui.py", "stream_clipper/updater.py", "stream_clipper/library.py",
                "stream_clipper/paths.py", "stream_clipper/facecam.py", "stream_clipper/__init__.py"}


def needs_window_restart(changed: list[str]) -> bool:
    return any(c.replace("\\", "/") in WINDOW_FILES for c in changed)


def _read(p: str) -> str:
    try:
        return open(p, encoding="utf-8").read()
    except OSError:
        return ""


def python_exe() -> str:
    d, name = os.path.split(sys.executable)
    if name.lower() == "pythonw.exe" and os.path.exists(os.path.join(d, "python.exe")):
        return os.path.join(d, "python.exe")
    return sys.executable


def main() -> None:
    info = check()
    if not info:
        print(T("У тебя последняя версия."))
        return
    print(T('Есть новая версия от {0}.').format(info['date']))
    apply(info["sha"])


if __name__ == "__main__":
    main()
