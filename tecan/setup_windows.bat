@echo off
setlocal
cd /d "%~dp0"

where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda is not available in this terminal.
    echo Open Miniforge Prompt and run this script again.
    exit /b 1
)

call conda env list | findstr /R /C:"^research " >nul
if not errorlevel 1 (
    echo ERROR: Environment 'research' already exists.
    echo No changes were made. Review the existing environment before updating it.
    exit /b 1
)

echo Creating Conda environment 'research'...
call conda env create -f environment.yml
if errorlevel 1 (
    echo ERROR: Environment creation failed.
    exit /b 1
)

echo Verifying Python and tecancavro...
call conda run -n research python -c "import sys; import serial; from tecancavro.models import XE1000; print('Python:', sys.executable); print('tecancavro: OK')"
if errorlevel 1 (
    echo ERROR: Verification failed.
    exit /b 1
)

echo.
echo SETUP COMPLETE. In VS Code select the research environment interpreter.
echo To run scripts in Miniforge Prompt: conda activate research
endlocal
