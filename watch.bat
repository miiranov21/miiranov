@echo off
chcp 65001 >nul
rem Впиши сюда каналы стримеров через пробел:
set CHANNELS=kaicenat xqc
rem Папка, куда складывать шортсы (папки по датам создадутся сами):
set OUT=D:\Shorts
python -m stream_clipper watch %CHANNELS% -o "%OUT%" --layout blur --zoom 1.3 --subs -n 8
pause
