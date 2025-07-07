@echo off
REM START.bat
REM Version: 32.5.0
REM Last modified: 2025-07-06
REM This is the official script to launch the KYO QA ServiceNow Knowledge Tool.

ECHO.
ECHO --- Starting KYO QA ServiceNow Knowledge Tool ---
ECHO.

REM Run the correct and reliable Python startup script.
python start_tool.py

ECHO.
ECHO --- Application has closed. ---
pause
