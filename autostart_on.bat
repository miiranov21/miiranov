@echo off
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
> "%STARTUP%\StreamClipper.bat" echo @start "Stream Clipper" /min "%~dp0START.bat"
echo Done: Stream Clipper will start automatically when Windows starts.
echo To turn it off, run autostart_off.bat
pause
