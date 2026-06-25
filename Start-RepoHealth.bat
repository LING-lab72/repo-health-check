@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "BACKEND_PORT=8002"
set "FRONTEND_PORT=5174"
set "FRONTEND_HOST=127.0.0.1"
set "FRONTEND_URL=http://127.0.0.1:%FRONTEND_PORT%/?theme=dark"
set "LOG_DIR=%TEMP%\repo-health-check"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul

echo ========================================
echo Repo Health Check - local dev launcher
echo ========================================
echo Project : %ROOT%
echo Backend : http://127.0.0.1:%BACKEND_PORT%
echo Frontend: %FRONTEND_URL%
echo Logs    : %LOG_DIR%
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python was not found in PATH.
  echo Install Python or add it to PATH, then run this file again.
  pause
  exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm.cmd was not found in PATH.
  echo Install Node.js, then run this file again.
  pause
  exit /b 1
)

if not exist "%ROOT%.env" (
  if exist "%ROOT%.env.example" (
    echo [INFO] .env was not found. Creating it from .env.example.
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
  )
)

echo [INFO] Starting backend window...
start "Repo Health Backend :%BACKEND_PORT%" cmd /k "cd /d ""%ROOT%"" && python -m uvicorn backend.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload"

echo [INFO] Starting frontend window...
start "Repo Health Frontend :%FRONTEND_PORT%" cmd /k "cd /d ""%ROOT%frontend"" && if not exist node_modules (npm.cmd install) && npm.cmd run dev -- --host %FRONTEND_HOST%"

echo.
echo [INFO] Waiting for backend and frontend to become ready...
echo This can take a while on the first run because npm install may need time.

set "BACKEND_READY=0"
set "FRONTEND_READY=0"

for /L %%i in (1,1,90) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:%BACKEND_PORT%/health' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 set "BACKEND_READY=1"

  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%FRONTEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 set "FRONTEND_READY=1"

  if "!BACKEND_READY!"=="1" if "!FRONTEND_READY!"=="1" goto ready
  timeout /t 2 /nobreak >nul
)

echo.
echo [ERROR] Services did not become ready in time.
echo Check the two opened terminal windows for errors.
echo.
echo Common fixes:
echo - If port 5174 or 8002 is already in use, close the old terminal window.
echo - If npm install is still running, wait for it to finish and open %FRONTEND_URL% manually.
echo - If Python dependency is missing, run: pip install -r backend\requirements.txt
pause
exit /b 1

:ready
echo.
echo [OK] Backend and frontend are ready.
echo [INFO] Opening browser: %FRONTEND_URL%
start "" "%FRONTEND_URL%"
echo.
echo Keep the two opened terminal windows running while using the app.
echo Close those windows or press Ctrl+C inside them to stop the services.
pause
