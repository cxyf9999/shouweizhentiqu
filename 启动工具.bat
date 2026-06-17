@echo off
chcp 65001 >nul
echo Starting Video Frame Extractor...
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" "%~dp0首尾帧提取工具.py"
if errorlevel 1 (
    echo.
    pause
)
