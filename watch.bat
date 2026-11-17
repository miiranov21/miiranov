@echo off
chcp 65001 >nul
rem Каналы через пробел: Twitch — логин (kaicenat), YouTube — @handle (@MrBeast)
set CHANNELS=kaicenat xqc @MrBeast
rem Папка, куда складывать шортсы (папки по датам создадутся сами):
set OUT=D:\Shorts
python -m stream_clipper watch %CHANNELS% -o "%OUT%" --layout blur --zoom 1.3 --subs -n 8
pause
