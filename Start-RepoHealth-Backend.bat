@echo off
setlocal EnableExtensions
set "ROOT=%~1"
set "PYTHON_EXE=%~2"
set "BACKEND_PORT=%~3"

title Repo Health Backend :%BACKEND_PORT%
pushd "%ROOT%" || (
  echo [ERROR] Cannot enter project directory: %ROOT%
  pause
  exit /b 1
)

"%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload

echo.
echo [ERROR] Backend service stopped. Check the message above.
pause
