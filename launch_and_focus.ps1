# MicroOS v1.0 - Window Bring-To-Foreground & Pop-up Script
$ErrorActionPreference = "SilentlyContinue"

$vboxManage = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$vboxVM = "C:\Program Files\Oracle\VirtualBox\VirtualBoxVM.exe"
$vmName = "MicroOS-v1.0"

# Check VM state
$info = & $vboxManage showvminfo $vmName --machinereadable
$isVmRunning = $info -match 'VMState="running"'

if (-not $isVmRunning) {
    Write-Host "VM is not running. Starting VirtualBoxVM.exe --startvm '$vmName'..."
    Start-Process $vboxVM -ArgumentList "--startvm `"$vmName`""
} else {
    Write-Host "VM is already running."
}

# Compile Win32 window management helper
$code = @"
using System;
using System.Runtime.InteropServices;

public class Win32Focus {
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern void SwitchToThisWindow(IntPtr hWnd, bool fAltTab);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
    public static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
}
"@
Add-Type -TypeDefinition $code -Language CSharp

# Find the VM window handle
$found = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    $procs = Get-Process | Where-Object { 
        ($_.ProcessName -match "VirtualBox" -or $_.MainWindowTitle -match "MicroOS") -and $_.MainWindowHandle -ne 0 
    }
    
    foreach ($p in $procs) {
        if ($p.MainWindowTitle -match "MicroOS" -or $p.ProcessName -eq "VirtualBoxVM") {
            $h = $p.MainWindowHandle
            Write-Host "Found Window Handle: $h (Title: '$($p.MainWindowTitle)', Process: $($p.ProcessName))"
            
            # Restore & Maximize
            [Win32Focus]::ShowWindow($h, 9) | Out-Null # SW_RESTORE
            [Win32Focus]::ShowWindow($h, 3) | Out-Null # SW_MAXIMIZE
            
            # Pop to top of all windows
            [Win32Focus]::SetWindowPos($h, [Win32Focus]::HWND_TOPMOST, 0, 0, 0, 0, 0x0003) | Out-Null
            [Win32Focus]::SetWindowPos($h, [Win32Focus]::HWND_NOTOPMOST, 0, 0, 0, 0, 0x0003) | Out-Null
            
            # Bring to Foreground
            [Win32Focus]::SetForegroundWindow($h) | Out-Null
            [Win32Focus]::SwitchToThisWindow($h, $true)
            
            $found = $true
            break
        }
    }
    if ($found) { break }
}

if ($found) {
    Write-Host "[SUCCESS] MicroOS window brought to foreground and maximized!"
    [System.Console]::Beep(800, 300)
} else {
    Write-Host "[INFO] Window handle search completed."
}
