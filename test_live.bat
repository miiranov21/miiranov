@echo off
cd /d "%~dp0"
rem Quick test on a streamer who is LIVE right now.
rem Put the channel login (the part after twitch.tv/) here:
set CHANNEL=evelone2004
python -m stream_clipper watch %CHANNEL% -o test_output -n 3 --preset veryfast
pause
