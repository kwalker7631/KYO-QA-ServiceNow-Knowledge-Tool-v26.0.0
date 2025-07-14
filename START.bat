@echo off
title KYO QA Tool Launcher v26.0.0
color 0A

echo.
echo ================================================================
echo   KYO QA ServiceNow Knowledge Tool v26.0.0
echo   Starting Application...
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.9+ and add it to your PATH
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Try to start with the simple launcher first
if exist "launcher.py" (
    echo Using simple launcher...
    python launcher.py
) else if exist "kyo_qa_tool_app.py" (
    echo Using direct application launch...
    python kyo_qa_tool_app.py
) else (
    echo ERROR: Application files not found
    echo Please ensure kyo_qa_tool_app.py or launcher.py exists
    echo.
    pause
    exit /b 1
)

echo.
echo Application has closed.
pause