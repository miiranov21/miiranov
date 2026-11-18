@echo off
cd /d "%~dp0"
echo === Installing Python packages ===
python -m pip install -U -r requirements.txt
if errorlevel 1 goto piperr
echo.
echo === Checking ffmpeg (downloads it into the bin folder if missing) ===
python -c "from stream_clipper.ffmpeg_setup import ensure_ffmpeg; ensure_ffmpeg()"
echo.
echo === Creating desktop icon ===
python -m stream_clipper.shortcut
goto done
:piperr
echo.
echo ERROR: pip install failed. Send the text above to Claude.
:done
echo.
echo Optional, for subtitles: python -m pip install faster-whisper
pause
