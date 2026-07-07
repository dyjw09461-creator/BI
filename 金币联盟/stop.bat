@echo off
setlocal
set "PORT=5102"
set "FOUND="

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    set "FOUND=1"
    echo Stopping Gold mall on port %PORT%, PID: %%p
    taskkill /PID %%p /F > nul
)

if not defined FOUND (
    echo Gold mall is not listening on port %PORT%.
    exit /b 0
)

ping 127.0.0.1 -n 3 > nul

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo Port %PORT% is still occupied by PID: %%p
    exit /b 1
)

echo Gold mall stopped. Port %PORT% released.
exit /b 0
