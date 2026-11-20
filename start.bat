@echo off
rem Start Read it For Me (with the free Kokoro AI voice) and open it in the browser.
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" goto setup
if not exist "models\kokoro-v1.0.onnx" goto setup
if not exist "models\voices-v1.0.bin" goto setup
goto run

:setup
echo First run: setting things up, one time only...
call setup.bat
if errorlevel 1 (
  pause
  exit /b 1
)

:run
.venv\Scripts\python.exe server.py %*
if errorlevel 1 pause
