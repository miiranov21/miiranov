@echo off
cd /d "%~dp0"
echo === Installing speech recognition for subtitles ===
rem PyYAML has no ready build for the newest Python: install its pure-Python version (no compiler needed)
set PYYAML_FORCE_LIBYAML=0
python -m pip install --no-binary pyyaml pyyaml
if errorlevel 1 goto err
python -m pip install -U ctranslate2 "huggingface-hub>=0.21" tokenizers av tqdm
if errorlevel 1 goto err
python -m pip install -U --no-deps faster-whisper
if errorlevel 1 goto err
echo.
echo Optional voice filter (may be unavailable for the newest Python - that is OK):
python -m pip install onnxruntime
echo.
python -c "import faster_whisper; print('Subtitles are ready.')"
echo Done. Subtitles turn on automatically. The first clip downloads a ~0.5 GB model (needs VPN/internet).
goto end
:err
echo.
echo ERROR. Send the text above to Claude.
:end
pause
