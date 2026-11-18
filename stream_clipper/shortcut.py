"""Создаёт ярлык «Stream Clipper» на рабочем столе (Windows)."""
from __future__ import annotations

import os
import subprocess
import sys

from . import paths


def make_desktop_shortcut() -> str:
    d, name = os.path.split(sys.executable)
    pythonw = os.path.join(d, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    lnk = os.path.join(paths.desktop_dir(), "Stream Clipper.lnk")
    prog = paths.program_dir()

    def q(s: str) -> str:
        return "'" + s.replace("'", "''") + "'"

    ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut({q(lnk)});"
          f"$s.TargetPath={q(pythonw)};$s.Arguments='-m stream_clipper.gui';"
          f"$s.WorkingDirectory={q(prog)};$s.IconLocation={q(os.path.join(prog, 'icon.ico'))};"
          f"$s.Description='Stream Clipper';$s.Save()")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], check=True)
    return lnk


if __name__ == "__main__":
    print("Ярлык создан:", make_desktop_shortcut())
