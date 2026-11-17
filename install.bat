@echo off
chcp 65001 >nul
echo Устанавливаю зависимости...
python -m pip install -U -r requirements.txt
where ffmpeg >nul 2>nul || (
  echo ffmpeg не найден, ставлю через winget...
  winget install -e --id Gyan.FFmpeg
  echo Перезапусти окно командной строки, чтобы ffmpeg появился в PATH.
)
echo.
echo Для авто-субтитров дополнительно: python -m pip install faster-whisper
pause
