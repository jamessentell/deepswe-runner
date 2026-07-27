@echo off
setlocal
cd /d "%~dp0"
uv run deepswe %*
exit /b %errorlevel%
