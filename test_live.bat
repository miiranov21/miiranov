@echo off
chcp 65001 >nul
rem Быстрая проверка на стримере, который СЕЙЧАС в эфире.
rem Впиши логин канала (то, что после twitch.tv/):
set CHANNEL=kaicenat
python -m stream_clipper watch %CHANNEL% -o test_output -n 3 --preset veryfast
pause
