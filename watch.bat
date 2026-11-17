@echo off
chcp 65001 >nul
rem Впиши сюда каналы стримеров через пробел:
set CHANNELS=kaicenat xqc
python -m stream_clipper watch %CHANNELS% --layout blur --zoom 1.3 --subs -n 8
pause
