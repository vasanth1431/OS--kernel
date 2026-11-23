@echo off
cd /d "%~dp0"
title Micro Monitor - Real-Time System Telemetry

set "PY=C:\Users\diwak\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" microos\system-monitor\system_monitor.py
