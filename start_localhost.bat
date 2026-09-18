@echo off
setlocal
cd /d "%~dp0"
set "API_PORT=5000"
start "SkillBridge - localhost" /b cmd /c "py -3 app.py"
start "" "http://localhost:5000"
echo SkillBridge is starting at http://localhost:5000
endlocal
