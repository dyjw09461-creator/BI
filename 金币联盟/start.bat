@echo off
setlocal
set "APP_DIR=%~dp0"
set "PORT=5102"
set "PYTHON_EXE=C:\Users\PXHONY\AppData\Local\Programs\Python\Python310\python.exe"
set "RUN_CODE=from app import app; app.run(host='127.0.0.1', port=5102, debug=False)"

if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo Gold mall already running: http://127.0.0.1:%PORT%, PID: %%p
    exit /b 0
)

if not exist "%APP_DIR%logs" mkdir "%APP_DIR%logs"
if exist "%APP_DIR%logs\mall_5102.out.log" del "%APP_DIR%logs\mall_5102.out.log"
if exist "%APP_DIR%logs\mall_5102.err.log" del "%APP_DIR%logs\mall_5102.err.log"

start "gold-mall-5102" /min /D "%APP_DIR%" cmd /c ""%PYTHON_EXE%" -c "%RUN_CODE%" > "logs\mall_5102.out.log" 2> "logs\mall_5102.err.log""

ping 127.0.0.1 -n 6 > nul

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo Gold mall started: http://127.0.0.1:%PORT%, PID: %%p
    echo Logs: %APP_DIR%logs\mall_5102.out.log, %APP_DIR%logs\mall_5102.err.log
    exit /b 0
)

echo Gold mall failed to start. Check logs\mall_5102.err.log
if exist "%APP_DIR%logs\mall_5102.err.log" type "%APP_DIR%logs\mall_5102.err.log"
exit /b 1
