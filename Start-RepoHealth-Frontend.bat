@echo off
setlocal EnableExtensions
set "ROOT=%~1"
set "NODE_EXE=%~2"
set "FRONTEND_HOST=%~3"

title Repo Health Frontend
pushd "%ROOT%frontend" || (
  echo [ERROR] Cannot enter frontend directory: %ROOT%frontend
  pause
  exit /b 1
)

if not exist "node_modules\vite\bin\vite.js" (
  echo [ERROR] Vite was not found. Please run the main Start-RepoHealth.bat again so it can install dependencies.
  pause
  exit /b 1
)

"%NODE_EXE%" node_modules\vite\bin\vite.js --host %FRONTEND_HOST%

echo.
echo [ERROR] Frontend service stopped. Check the message above.
pause
