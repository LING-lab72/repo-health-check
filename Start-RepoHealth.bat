@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "BACKEND_PORT=8002"
set "FRONTEND_PORT=5174"
set "FRONTEND_HOST=127.0.0.1"
set "FRONTEND_URL=http://127.0.0.1:%FRONTEND_PORT%/?theme=dark"
set "BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%/health"
set "LOG_DIR=%TEMP%\repo-health-check"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul

set "PYTHON_EXE=python"
where python >nul 2>nul
if errorlevel 1 (
  if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  ) else (
    echo [ERROR] Python was not found in PATH.
    echo Install Python or add it to PATH, then run this file again.
    pause
    exit /b 1
  )
)

set "NODE_EXE="
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" (
  set "NODE_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
) else (
  for /f "delims=" %%P in ('where node.exe 2^>nul') do if not defined NODE_EXE set "NODE_EXE=%%P"
)
if not defined NODE_EXE (
  echo [ERROR] node.exe was not found.
  echo Install Node.js or add it to PATH, then run this file again.
  pause
  exit /b 1
)

set "PNPM_EXE="
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\pnpm.cmd" (
  set "PNPM_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\pnpm.cmd"
) else (
  for /f "delims=" %%P in ('where pnpm.cmd 2^>nul') do if not defined PNPM_EXE set "PNPM_EXE=%%P"
)

echo ======================================
echo Repo Health Check - local dev launcher
echo ======================================
echo Project : %ROOT%
echo Backend : http://127.0.0.1:%BACKEND_PORT%
echo Frontend: %FRONTEND_URL%
echo Logs    : %LOG_DIR%
echo Python  : %PYTHON_EXE%
echo Node    : %NODE_EXE%
echo pnpm    : %PNPM_EXE%
echo.

if not exist "%ROOT%backend\main.py" (
  echo [ERROR] backend\main.py was not found. Please keep this launcher in the project root.
  pause
  exit /b 1
)

if not exist "%ROOT%frontend\package.json" (
  echo [ERROR] frontend\package.json was not found. Please keep this launcher in the project root.
  pause
  exit /b 1
)

if not exist "%ROOT%.env" (
  if exist "%ROOT%.env.example" (
    echo [INFO] .env was not found. Creating it from .env.example.
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
  )
)

echo [INFO] Installing/checking backend dependencies...
pushd "%ROOT%" >nul
"%PYTHON_EXE%" -m pip install -r backend\requirements.txt > "%LOG_DIR%\backend-install.log" 2>&1
if errorlevel 1 (
  echo [ERROR] Backend dependency installation failed.
  echo Log: %LOG_DIR%\backend-install.log
  popd >nul
  pause
  exit /b 1
)
popd >nul

echo [INFO] Checking frontend dependencies...
pushd "%ROOT%frontend" >nul
if not exist node_modules\vite\bin\vite.js (
  if not defined PNPM_EXE (
    echo [ERROR] Frontend dependencies are missing and pnpm.cmd was not found.
    echo Please install dependencies manually in frontend folder.
    popd >nul
    pause
    exit /b 1
  )
  echo [INFO] Installing frontend dependencies with pnpm...
  call "%PNPM_EXE%" install > "%LOG_DIR%\frontend-install.log" 2>&1
  if errorlevel 1 (
    echo [ERROR] Frontend dependency installation failed.
    echo Log: %LOG_DIR%\frontend-install.log
    popd >nul
    pause
    exit /b 1
  )
)
popd >nul

set "BACKEND_READY=0"
set "FRONTEND_READY=0"

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%BACKEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 set "BACKEND_READY=1"

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%FRONTEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 set "FRONTEND_READY=1"

if "%BACKEND_READY%"=="1" (
  echo [INFO] Backend is already running.
) else (
  echo [INFO] Starting backend window...
  start "Repo Health Backend :%BACKEND_PORT%" "%ROOT%Start-RepoHealth-Backend.bat" "%ROOT%" "%PYTHON_EXE%" "%BACKEND_PORT%"
)

if "%FRONTEND_READY%"=="1" (
  echo [INFO] Frontend is already running.
) else (
  echo [INFO] Starting frontend window...
  start "Repo Health Frontend :%FRONTEND_PORT%" "%ROOT%Start-RepoHealth-Frontend.bat" "%ROOT%" "%NODE_EXE%" "%FRONTEND_HOST%"
)

echo.
echo [INFO] Waiting for backend and frontend to become ready...
echo This can take 20-60 seconds on the first run.

for /L %%i in (1,1,90) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%BACKEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 set "BACKEND_READY=1"

  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%FRONTEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 set "FRONTEND_READY=1"

  if "!BACKEND_READY!"=="1" if "!FRONTEND_READY!"=="1" goto ready
  timeout /t 2 /nobreak >nul
)

echo.
echo [ERROR] Services did not become ready in time.
echo Backend ready : !BACKEND_READY!
echo Frontend ready: !FRONTEND_READY!
echo.
echo Please check the backend/frontend terminal windows.
echo Backend install log : %LOG_DIR%\backend-install.log
echo Frontend install log: %LOG_DIR%\frontend-install.log
echo.
echo Common fixes:
echo - If port 5174 or 8002 is already in use, close the old terminal window.
echo - If your network is slow, wait for pnpm/pip to finish, then open %FRONTEND_URL% manually.
echo - If GitHub clone is slow, make sure your proxy in .env is correct.
pause
exit /b 1

:ready
echo.
echo [OK] Backend and frontend are ready.
echo [INFO] Opening browser: %FRONTEND_URL%
start "" "%FRONTEND_URL%"
echo.
echo Keep the backend and frontend terminal windows running while using the app.
echo Close those windows or press Ctrl+C inside them to stop the services.
pause

