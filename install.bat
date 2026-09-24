::------------------------------------------------------------
:: Prevent environment variable leakage into the parent shell
::------------------------------------------------------------
@echo off
setlocal

::------------------------------------------------------------
:: ANSI color + symbol setup
::------------------------------------------------------------
chcp 65001 >nul
for /f %%a in ('echo prompt $E^| cmd /Q /V:ON /P') do set "ESC=%%a"
set "GREEN=%ESC%[92m"
set "RED=%ESC%[91m"
set "YELLOW=%ESC%[93m"
set "CYAN=%ESC%[96m"
set "RESET=%ESC%[0m"
set "OK=%GREEN%  [✔]%RESET%"
set "ERR=%RED%  [✘]%RESET%"
set "WAIT=%CYAN%  [→]%RESET%"
set "WARN=%YELLOW%  [!]%RESET%"

::------------------------------------------------------------
:: Check Python availability
::------------------------------------------------------------
where python >nul 2>&1
if errorlevel 1 (
    echo %ERR% Python not found on PATH.
    pause
)
echo %OK% Python found.

::------------------------------------------------------------
:: Remove old virtual environment if it exists
::------------------------------------------------------------
if exist venv\ (
    echo %WARN% Removing old virtual environment...
    RMDIR /s /q venv\
    if errorlevel 1 (
        echo %ERR% Could not remove old virtual environment directory.
        pause
    )
    echo %OK% Old virtual environment removed.
)

::------------------------------------------------------------
:: Creating virtual environment
::------------------------------------------------------------
set STEP=Creating virtual environment
echo %WAIT% Creating virtual environment...
python -m venv venv
if errorlevel 1 (
        echo %ERR% Could not create virtual environment.
        pause
)
echo %OK% Virtual environment created.

::------------------------------------------------------------
:: Activating virtual environment
::------------------------------------------------------------
set STEP=Activating virtual environment
echo %WAIT% Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
        echo %ERR% Could not Activate virtual environment.
        pause
)
echo %OK% Virtual environment activated.

::------------------------------------------------------------
:: Setting up setuptools
::------------------------------------------------------------
set STEP=Setting up setuptools
echo %WAIT% Setting up setuptools...
pip install --no-index --find-links=wheelhouse setuptools==63.2.0 wheel
if errorlevel 1 (
        echo %ERR% Could not finalize setuptools.
        pause
)
echo %OK% Setuptools ready.

::------------------------------------------------------------
:: Installing project dependencies from wheelhouse
::------------------------------------------------------------
set STEP=Installing project dependencies
echo %WAIT% Installing project dependencies...
pip install --no-index --find-links=wheelhouse .
if errorlevel 1 (
        echo %ERR% Could not Install project dependencies.
        pause
)
echo %OK% Dependencies installed.

::------------------------------------------------------------
echo.
echo %OK%  PyPLECS is ready to use!
echo %OK%  Run: call venv\Scripts\activate.bat to activate venv if not done yet

::------------------------------------------------------------
::pause keeps the window open, and `exit /b 1` runs cleanly right after
pause
::exit /b 1
