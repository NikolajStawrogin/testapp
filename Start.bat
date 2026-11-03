@echo off
cd /d "%~dp0"
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 server.py
    goto end
)
python --version >nul 2>&1
if not errorlevel 1 (
    python server.py
    goto end
)
echo Zum lokalen Start wird Python 3 benoetigt.
echo Python 3 ist kostenlos unter https://www.python.org/downloads/ erhaeltlich.
echo Nach der Installation diese Datei erneut oeffnen.
:end
pause
