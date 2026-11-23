@echo off
cd /d "%~dp0"
title Micro Research Lab - Multi-Core Scheduling Suite

set "PY=C:\Users\diwak\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" microos\research-lab\gui.py
