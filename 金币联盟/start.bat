@echo off
setlocal
chcp 65001 > nul
set "APP_DIR=%~dp0"
set "PORT=5102"
set "PYTHON_EXE=C:\Users\PXHONY\AppData\Local\Programs\Python\Python310\python.exe"

if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

title Gold Mall Flask Server 5102
echo.
echo ============================================================
echo  Gold Mall is starting...
echo  URL: http://127.0.0.1:%PORT%
echo  Stop: close this window or run stop.bat
echo ============================================================
echo.

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo Gold Mall is already running on port %PORT%, PID: %%p
    echo Opening browser...
    start "" "http://127.0.0.1:%PORT%/"
    pause
    exit /b 0
)

cd /d "%APP_DIR%"
set "FLASK_APP=app.py"
start "" /min cmd /c "timeout /t 3 /nobreak > nul & start "" http://127.0.0.1:%PORT%/"
"%PYTHON_EXE%" -m flask run --host 127.0.0.1 --port %PORT%
pause
