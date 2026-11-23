@echo off
cd /d "%~dp0"
title Process Panic - OS Scheduling Challenge

set "PY=C:\Users\diwak\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" microos\process-panic\main.py
