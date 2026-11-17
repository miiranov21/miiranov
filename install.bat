@echo off
cd /d "%~dp0"
echo === Installing Python packages ===
python -m pip install -U pip
python -m pip install -U -r requirements.txt
if errorlevel 1 goto piperr
echo.
echo === Checking ffmpeg ===
where ffmpeg >nul 2>nul
if errorlevel 1 goto noffmpeg
echo ffmpeg found.
goto done
:noffmpeg
echo ffmpeg not found, installing with winget...
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
echo.
echo ffmpeg installed. CLOSE this window and open a NEW one so ffmpeg is in PATH.
goto done
:piperr
echo.
echo ERROR: pip install failed. Send the text above to Claude.
:done
echo.
echo Optional, for subtitles: python -m pip install faster-whisper
pause
