@echo off
cd /d "%~dp0"
python -m stream_clipper.shortcut
if errorlevel 1 (
  echo ERROR. Send the text above to Claude.
) else (
  echo Done! Look for "Stream Clipper" on your desktop.
)
pause
