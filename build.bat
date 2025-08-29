@echo off
REM Build script for Python GUI Menu Application (Windows)
REM This is a simple wrapper that calls the Python build script

echo ================================================
echo Building Python GUI Menu Application
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later and add it to your PATH
    pause
    exit /b 1
)

REM Check if build requirements file exists
if not exist "requirements_build.txt" (
    echo ERROR: requirements_build.txt not found
    echo Please make sure you're running this from the project directory
    pause
    exit /b 1
)

REM Run the Python build script
echo Running Python build script...
python build.py

if errorlevel 1 (
    echo.
    echo Build failed. Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Build completed! Check the output above for details.
pause
