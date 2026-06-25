@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND_PORT=8002"
set "FRONTEND_HOST=127.0.0.1"
set "FRONTEND_URL=http://127.0.0.1:5174"

echo ========================================
echo Repo Health Check - local dev launcher
echo ========================================
echo Project: %ROOT%
echo Backend: http://127.0.0.1:%BACKEND_PORT%
echo Frontend: %FRONTEND_URL%
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
start "Repo Health Backend :8002" cmd /k "cd /d ""%ROOT%"" && python -m uvicorn backend.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload"

echo [INFO] Starting frontend window...
start "Repo Health Frontend :5174" cmd /k "cd /d ""%ROOT%frontend"" && if not exist node_modules npm.cmd install && npm.cmd run dev -- --host %FRONTEND_HOST%"

echo [INFO] Opening browser in a few seconds...
timeout /t 5 /nobreak >nul
start "" "%FRONTEND_URL%"

echo.
echo Started. Keep the two opened terminal windows running while using the app.
echo Close those windows or press Ctrl+C inside them to stop the services.
pause
