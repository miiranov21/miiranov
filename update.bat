@echo off
cd /d "%~dp0"
echo Checking for updates...
python -m stream_clipper.updater
pause
