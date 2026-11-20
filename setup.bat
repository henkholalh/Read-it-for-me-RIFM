@echo off
rem One-time setup (Windows): creates a Python environment and downloads the Kokoro voice model (~350 MB).
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto install
echo Creating Python environment...

where uv >nul 2>nul
if not errorlevel 1 (
  uv venv --python 3.12 .venv
  if errorlevel 1 goto fail
  goto install
)

rem Find Python 3.10 - 3.13 (onnxruntime does not support newer versions yet)
set "PY="
for %%V in (3.12 3.13 3.11 3.10) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; sys.exit(not (3,10) <= sys.version_info[:2] <= (3,13))" >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo.
  echo Python 3.10 to 3.13 is required.
  echo Install Python 3.12 from https://www.python.org/downloads/windows/
  echo and tick "Add python.exe to PATH" during installation, then run this again.
  goto fail
)
echo Using %PY%
%PY% -m venv .venv
if errorlevel 1 goto fail

:install
echo Installing packages...
where uv >nul 2>nul
if not errorlevel 1 (
  uv pip install --python .venv\Scripts\python.exe -q -r requirements.txt
) else (
  .venv\Scripts\python.exe -m pip install -q --upgrade pip
  .venv\Scripts\python.exe -m pip install -q -r requirements.txt
)
if errorlevel 1 goto fail

set PYTHONUTF8=1
.venv\Scripts\python.exe download_models.py
if errorlevel 1 goto fail

echo.
echo Setup complete. Start the app by double-clicking "Read it For Me.bat".
exit /b 0

:fail
echo.
echo Setup failed. See the message above.
exit /b 1
