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


def check(root: str | None = None) -> dict | None:
    """Есть ли новая версия. Возвращает {'sha', 'date'} или None (уже последняя)."""
    url = f"https://api.github.com/repos/{REPO}/commits/{BRANCH.replace('/', '%2F')}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        data = json.load(r)
    sha = data["sha"]
    if sha == local_version(root):
        return None
    when = data.get("commit", {}).get("committer", {}).get("date", "")
    try:
        when = datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone().strftime("%d.%m %H:%M")
    except ValueError:
        pass
    return {"sha": sha, "date": when}


def apply(sha: str, root: str | None = None, log=print) -> bool:
    """Скачивает версию и раскладывает файлы поверх программы. True — если поменялись библиотеки."""
    root = root or paths.program_dir()
    url = f"https://codeload.github.com/{REPO}/zip/{sha}"
    log("Скачиваю обновление...")
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]}),
                                timeout=120) as r:
        data = r.read()
    old_req = _read(os.path.join(root, "requirements.txt"))
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
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            tmp = dest + ".new"
            with z.open(name) as src, open(tmp, "wb") as out:
                shutil.copyfileobj(src, out)
            os.replace(tmp, dest)
    with open(_version_file(root), "w", encoding="utf-8") as f:
        f.write(sha)
    changed = _read(os.path.join(root, "requirements.txt")) != old_req
    if changed:
        log("Ставлю новые библиотеки...")
        flags = 0x08000000 if os.name == "nt" else 0
        subprocess.run([python_exe(), "-m", "pip", "install", "-q", "-r", os.path.join(root, "requirements.txt")],
                       cwd=root, creationflags=flags)
    log("Обновление установлено.")
    return changed


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
        print("У тебя последняя версия.")
        return
    print(f"Есть новая версия от {info['date']}.")
    apply(info["sha"])


if __name__ == "__main__":
    main()
