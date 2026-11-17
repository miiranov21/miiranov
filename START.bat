@echo off
cd /d "%~dp0"
title Stream Clipper
echo Stream Clipper: following streamers from streamers.txt
echo Clips: Desktop\YouTube\DATE\STREAMER
echo Keep VPN ON. Close this window or press Ctrl+C to stop.
echo.
:loop
python -m stream_clipper watch --layout blur --zoom 1.3 -n 8
echo.
echo Program stopped. Restarting in 30 seconds (close the window to quit)...
timeout /t 30
goto loop
