@echo off
title Global Perspectives - Foreign Policy TUI
echo ====================================================
echo  Setting up Global Perspectives Foreign Policy TUI...
echo ====================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is not found in your PATH. Please install Python 3.11+.
    pause
    exit /b %errorlevel%
)

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b %errorlevel%
    )
)

:: Activate virtual environment
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

:: Install dependencies
echo Installing requirements...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo ====================================================
echo  Starting TUI Aggregator...
echo ====================================================
echo.

python -m app.main

if %errorlevel% neq 0 (
    echo [ERROR] Application terminated with an error code.
    pause
)