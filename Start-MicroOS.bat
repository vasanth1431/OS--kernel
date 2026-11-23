@echo off
setlocal EnableDelayedExpansion

title MicroOS v1.0 - VirtualBox Engineering Launcher
echo ===============================================================================
echo                MICROOS v1.0 - BEYOND THE ORDINARY DESKTOP
echo         Modular Linux Engineering & Operating Systems Research Platform
echo         Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
echo ===============================================================================
echo.

:: 1. Locate VBoxManage executable
set "VBOX_PATH=C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
if not exist "%VBOX_PATH%" (
    if defined VBOX_MSI_INSTALL_PATH (
        set "VBOX_PATH=%VBOX_MSI_INSTALL_PATH%VBoxManage.exe"
    )
)

if not exist "%VBOX_PATH%" (
    where VBoxManage.exe >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%I in ('where VBoxManage.exe') do set "VBOX_PATH=%%I"
    ) else (
        echo [ERROR] Oracle VirtualBox was not detected on this system!
        echo Please install Oracle VM VirtualBox from https://www.virtualbox.org/
        pause
        exit /b 1
    )
)
echo [OK] VirtualBox detected at: "%VBOX_PATH%"

:: 2. Locate MicroOS ISO
set "ISO_PATH=%~dp0microos\build\microos.iso"
if not exist "%ISO_PATH%" (
    set "ISO_PATH=%~dp0microos.iso"
)

if not exist "%ISO_PATH%" (
    echo [ERROR] microos.iso could not be located in microos\build\microos.iso!
    pause
    exit /b 1
)
echo [OK] MicroOS ISO image verified: "%ISO_PATH%"

:: 3. VM Selection
set "VM_NAME=MicroOS-v1.0"

echo.
echo Ensuring VM is cleanly reset before launching...
"%VBOX_PATH%" controlvm "%VM_NAME%" poweroff >nul 2>&1
"%VBOX_PATH%" discardstate "%VM_NAME%" >nul 2>&1
"%VBOX_PATH%" storageattach "%VM_NAME%" --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "%ISO_PATH%" >nul 2>&1
"%VBOX_PATH%" modifyvm "%VM_NAME%" --boot1 dvd --boot2 disk --boot3 none --boot4 none >nul 2>&1

echo.
echo ===============================================================================
echo Starting MicroOS Virtual Machine with GUI Display...
echo ===============================================================================
echo.
"%VBOX_PATH%" startvm "%VM_NAME%" --type gui

if %errorlevel% neq 0 (
    echo [INFO] Trying fallback VM "MicroOS-Live"...
    "%VBOX_PATH%" startvm "MicroOS-Live" --type gui
)

echo.
echo [SUCCESS] Virtual machine launched. You can also click Start in the VirtualBox Manager window.
pause
