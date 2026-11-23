@echo off
cd /d "%~dp0"
title Micro Control Center - System Configuration

set "PY=C:\Users\diwak\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" microos\control-center\control_center.py
