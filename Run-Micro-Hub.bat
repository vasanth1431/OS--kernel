@echo off
cd /d "%~dp0"
title Micro Hub - Application Launcher

set "PY=C:\Users\diwak\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" microos\application-hub\application_hub.py
