@echo off
cd /d "%~dp0"
rem Channels separated by spaces: Twitch = login (kaicenat), YouTube = @handle (@MrBeast)
set CHANNELS=kaicenat xqc @MrBeast
rem Folder for shorts (date folders are created automatically):
set OUT=D:\Shorts
python -m stream_clipper watch %CHANNELS% -o "%OUT%" --layout blur --zoom 1.3 -n 8
pause
