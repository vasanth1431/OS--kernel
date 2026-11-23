@echo off
cd /d "%~dp0"
title MicroOS - Automated Validation Test Suite

set "PY=C:\Users\diwak\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" microos\scripts\run_tests.py
echo.
pause
