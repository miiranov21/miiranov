@echo off
cd /d "%~dp0"
rem Channels separated by spaces: Twitch = login (evelone2004), YouTube = @handle (@MrBeast)
set CHANNELS=evelone2004
rem Clips go to Desktop\YouTube\DATE\STREAMER\
python -m stream_clipper watch %CHANNELS% --layout blur --zoom 1.3 -n 8
pause
