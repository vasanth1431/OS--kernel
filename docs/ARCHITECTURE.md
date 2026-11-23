# MicroOS System Architecture

**Developer**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Course**: 25PCCS201 Operating Systems Research Activity  
**Platform**: MicroOS v1.0 (Ubuntu 24.04 LTS Base)

---

## 1. Architectural Overview

MicroOS is constructed using a layered architectural model, separating hardware abstraction, core kernel services, system daemons, userland engineering utilities, and GUI presentation:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MICROOS USER INTERFACE LAYER                    │
│   Micro Hub   │  Micro Monitor  │  Network Center  │  Wi-Fi Scanner    │
│   Micro Control Center  │  Micro Research Lab  │  Process Panic        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ X11 / GTK3 / Tkinter
┌───────────────────────────────────▼────────────────────────────────────┐
│                    DESKTOP & WINDOW MANAGEMENT LAYER                   │
│   XFCE 4.18 Session  │  Xfwm4 Window Manager  │  LightDM Display Mgr   │
│   Asymmetric Left Panel  │  Right Telemetry Panel  │  4 Workspaces     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ POSIX System Calls / D-Bus
┌───────────────────────────────────▼────────────────────────────────────┐
│                    SYSTEM SERVICES & DAEMONS LAYER                     │
│   systemd (PID 1)   │  NetworkManager Daemon  │  wpa_supplicant        │
│   PipeWire Audio    │  udev Hardware Manager  │  dbus-daemon           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ System Call Interface (syscalls)
┌───────────────────────────────────▼────────────────────────────────────┐
│                       LINUX KERNEL 6.8 LTS LAYER                       │
│   Multi-Core EEVDF/CFS CPU Scheduler  │  Virtual Memory & Page Paging  │
│   VFS (Ext4, Squashfs, Overlayfs)     │  TCP/IP Networking & Sockets   │
│   mac80211 / cfg80211 Wireless Stack  │  Device Drivers & Firmware     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         PHYSICAL / VIRTUAL HARDWARE                    │
│   x86_64 CPU (Multi-Core)  │  RAM (16 GB Host / 4 GB VM)               │
│   VirtualBox NAT/Bridged NIC (Intel PRO/1000)  │  VMSVGA GPU (128 MB)  │
│   USB 3.0 Controller (xHCI) for Real USB Wi-Fi Dongle Passthrough      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Subsystem Deconstructions

### 2.1 Boot & Live Media Architecture
MicroOS live media uses an **OverlayFS + Squashfs** layered filesystem:
1. **Lower Layer (Read-Only)**: `filesystem.squashfs` containing the base Ubuntu 24.04 system, XFCE desktop, and MicroOS tool suites compressed via XZ.
2. **Upper Layer (Read-Write)**: A `tmpfs` RAM-backed overlay mounted during boot by `live-boot`. All user modifications, file creations, and configuration changes are written to volatile RAM or persisted if a persistent storage block device is attached.
3. **GRUB 2 Hybrid Boot**: Configured with both BIOS MBR boot code (`boot.img` / `core.img`) and standard UEFI 64-bit binaries (`EFI/BOOT/BOOTX64.EFI`), enabling universal bootability across legacy and modern UEFI hardware.

### 2.2 MicroShell Execution Environment
MicroShell is a customized GNU Bash 5.2 shell configured via `/opt/microos/microshell/microshellrc`. It replaces generic shell prompts with a prompt that tracks:
- User identity (`user@microos`)
- Current working directory with home-relative paths (`~/projects`)
- Active Git branch parsed via sed
- Custom diagnostic suite symlinked into `/usr/local/bin` to allow direct execution from any directory without PATH exports.

### 2.3 IPC and D-Bus Interfacing
MicroOS GUI utilities communicate with underlying system daemons via:
- **System D-Bus**: Used by Micro Network Center and Wi-Fi Scanner to communicate with `org.freedesktop.NetworkManager`.
- **Unix Domain Sockets & /proc**: Used by Micro Monitor to poll `/proc/stat`, `/proc/meminfo`, and `/proc/net/dev` with minimal kernel transition overhead.
- **Subprocess Streaming**: Used by Micro Research Lab to spawn multi-core worker processes, enforce barriers, and collect execution metrics through `multiprocessing.Queue`.
