# MicroOS (v1.0) – Beyond the Ordinary Desktop

[![Operating System](https://img.shields.io/badge/OS-MicroOS_v1.0-00b4d8.svg)](#)
[![Base](https://img.shields.io/badge/Base-Ubuntu_24.04_LTS-e95420.svg)](#)
[![Desktop](https://img.shields.io/badge/Desktop-XFCE_Asymmetric-1e2227.svg)](#)
[![Architecture](https://img.shields.io/badge/Arch-x86__64-343a40.svg)](#)
[![Research](https://img.shields.io/badge/Research-Multi--Core_Scheduling-ffb703.svg)](#)

**MicroOS** is an independent, modular Linux engineering and research operating system designed for systems programming, networking and wireless management, operating systems experimentation, process analysis, and academic research.

Developed by **Tadigotla Vasanth Diwakar** (USN: `25BTRCL270`, CSE-AIML-E) for the **25PCCS201: Operating Systems Research Activity** at FET Campus, Jain (Deemed-to-be University).

---

## 🚀 Key Highlights & Features

1. **Independent Linux Distribution (Ubuntu 24.04 LTS Base)**:
   - Full live bootable ISO (`microos/build/microos.iso`) built via reproducible chroot/live-build workflow.
   - Dual boot support: UEFI and BIOS via custom GRUB.
   - Standard package management via APT, LightDM display manager, and customized XFCE desktop.

2. **Original Visual Identity & Asymmetric Desktop**:
   - Deep graphite (`#14171a`) and charcoal (`#1e2227`) base with electric teal (`#00b4d8`) and amber (`#ffb703`) accents.
   - Vertical engineering dock on the left, telemetry panel on the right, and bottom workspace manager.
   - Four dedicated virtual workspaces: **Development**, **Networking**, **Research**, and **System Administration**.

3. **MicroShell Terminal Suite**:
   - Custom Bash environment with telemetry prompt, Git status, and aliases.
   - 12 real Linux CLI utilities (`micro-info`, `micro-status`, `micro-health`, `micro-network`, `micro-wifi`, `micro-ip`, `micro-internet`, `micro-process`, `micro-storage`, `micro-apps`, `micro-update`, `micro-help`).

4. **Micro Network Center & Micro Wi-Fi Scanner**:
   - Genuine NetworkManager D-Bus and CLI integration.
   - Live hardware wireless adapter detection, rfkill state inspection, and nearby SSID scanning.
   - Secure WPA2/WPA3 authentication without logging or leaking credentials.
   - Comprehensive VirtualBox networking guide (NAT, Bridged, and direct USB Wi-Fi adapter passthrough).

5. **Integrated Academic Research Lab**:
   - Research topic: *"Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution on Execution Performance"*.
   - Rigorous benchmarking comparing affinity modes (`none`, `spread`, `single`), workload distributions (`block`, `rr`, `dynamic`), and worker counts (1, 2, 4, 8).
   - Generates CSV/JSON reports, speedup curves, and load imbalance charts using Matplotlib.

6. **Process Panic (Original OS Puzzle Game)**:
   - Engaging graphical OS scheduling game where the player acts as the CPU scheduler managing process queues, priority inversion, burst times, and memory limits before an OOM kernel panic occurs.

7. **Educational Bare-Metal Kernel Lab**:
   - A standalone freestanding x86 kernel in C/Assembly featuring a Multiboot header, GDT, IDT, PIC, PS/2 keyboard driver, and interactive text shell.

---

## 📂 Repository Structure

```text
MicroOS/
├── Start-MicroOS.bat            # One-click Windows VirtualBox VM creator & launcher
├── start-microos.sh             # Linux VirtualBox launcher
├── README.md                    # Project overview and quick start guide
├── .gitignore                   # Excludes ISOs, VDIs, caches, and binaries
├── microos/
│   ├── build.sh                 # Reproducible Ubuntu 24.04 Live ISO generation script
│   ├── desktop/                 # Visual identity, themes, icons, wallpapers, lightdm
│   ├── microshell/              # Shell configs and 12 executable micro-* CLI commands
│   ├── network-center/          # Micro Network Center GUI & daemon
│   ├── wifi-scanner/            # Micro Wi-Fi Scanner & authentication dialog
│   ├── system-monitor/          # Micro Monitor (/proc real-time metrics GUI)
│   ├── control-center/          # Micro Control Center (10 system configuration panels)
│   ├── application-hub/         # Micro Hub application launcher
│   ├── process-panic/           # Process Panic educational OS puzzle game
│   ├── research-lab/            # Multi-core scheduling benchmark suite & analyzer
│   └── scripts/                 # System verification and testing scripts
├── kernel-lab/                  # Freestanding educational bare-metal x86 kernel
│   ├── src/                     # C and assembly source files
│   ├── linker.ld                # Kernel linker script
│   ├── Makefile                 # Kernel build automation
│   └── README.md                # Kernel architecture explanation
├── submissions/                 # Continuous Assessment submissions (CA-2, CA-3, CA-5 & Lab Record)
│   ├── CA2_Performance_Investigation_25BTRCL270.pdf      # CA-2 Submission PDF (18 Pages)
│   ├── CA3_Design_and_Debugging_Challenge_25BTRCL270.pdf # CA-3 Submission PDF (8 Pages)
│   ├── CA5_Linux_Systems_Engineering_25BTRCL270.pdf      # CA-5 Submission PDF (11 Pages)
│   ├── OS_Lab_Record_Vasanth_25BTRCL270.pdf              # OS Laboratory Record PDF (7 Pages)
│   ├── OS_LAB_RECORD.md                                  # Complete Lab Experiments & Terminal Logs (Markdown)
│   ├── ca2_sched_exp.py                                  # CA-2 Python Benchmark Script
│   ├── ca3_multicore_scheduler_debug.py                  # CA-3 Defect Diagnosis & Repair Script
│   ├── ca5_multicore_scheduling.py                       # CA-5 Linux Systems Engineering Script
│   └── README.md                                         # Submissions Index & Evaluation Guide
└── docs/                        # Complete 18-chapter engineering documentation suite
    ├── PROJECT_OVERVIEW.md
    ├── ARCHITECTURE.md
    ├── DESKTOP_DESIGN.md
    ├── MICROSHELL.md
    ├── NETWORK_ARCHITECTURE.md
    ├── NETWORK_IMPLEMENTATION.md
    ├── WIFI_IMPLEMENTATION.md
    ├── VIRTUALBOX_NETWORKING.md
    ├── WIFI_TROUBLESHOOTING.md
    ├── BROWSER_CONFIGURATION.md
    ├── SYSTEM_MONITOR.md
    ├── CONTROL_CENTER.md
    ├── RESEARCH_ANALYSIS.md
    ├── VIVA_GUIDE.md
    ├── TESTING_REPORT.md
    ├── INSTALLATION.md
    ├── HARDWARE_COMPATIBILITY.md
    ├── KERNEL_LAB.md
    └── TROUBLESHOOTING.md
```

---

## ⚡ Quick Start

### 1. Launching MicroOS on Windows (VirtualBox)
Run `Start-MicroOS.bat` as Administrator or standard user with VirtualBox installed:
```cmd
Start-MicroOS.bat
```
The script automatically verifies your VirtualBox installation, provisions a virtual machine (`MicroOS-v1.0`) with 4GB RAM, 2 CPU cores, 20GB VDI storage, attaches the ISO, sets up NAT networking with USB 3.0 controller support, and powers on the machine.

### 2. Building the ISO on Linux (Ubuntu 24.04 Host)
```bash
cd microos
sudo ./build.sh
```
The output image will be generated at `microos/build/microos.iso`.

### 3. Running the Multi-Core Scheduling Research Experiment
Inside MicroOS (or on any Linux system with Python 3):
```bash
cd microos/research-lab
python3 run_benchmarks.py
python3 generate_graphs.py
```
View the generated reports in `microos/research-lab/reports/` and analysis in `docs/RESEARCH_ANALYSIS.md`.

---

## 📜 Academic Research Attribution
- **Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)
- **Institution**: Jain University, Faculty of Engineering & Technology (FET Campus)
- **Subject**: 25PCCS201 Operating Systems Research Activity
- **Topic**: *Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution on Execution Performance*
