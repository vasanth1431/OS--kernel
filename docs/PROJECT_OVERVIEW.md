# MicroOS Project Overview

**Operating System**: MicroOS (Version 1.0 – Beyond the Ordinary Desktop)  
**Developer**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`, Branch: CSE-AIML-E)  
**Course**: 25PCCS201 Operating Systems Research Activity  
**Institution**: Faculty of Engineering & Technology, Jain (Deemed-to-be University)  
**Host Target**: Oracle VirtualBox on Windows Host / Bare-Metal x86_64

---

## 1. Executive Summary

MicroOS is an independent, modular Linux engineering and operating systems research platform. Unlike consumer Linux distributions, MicroOS is specifically architected for systems programming, real hardware wireless discovery and authentication, multi-core scheduling experiments, real-time `/proc` telemetry, and academic research analysis.

MicroOS combines an Ubuntu 24.04 LTS (Noble Numbat) core with a customized, asymmetric XFCE engineering desktop, an original visual identity (Graphite, Charcoal, Electric Teal, and Amber), a dedicated terminal suite (**MicroShell**), genuine NetworkManager integration (**Micro Network Center** & **Micro Wi-Fi Scanner**), an educational OS puzzle game (**Process Panic**), a standalone bare-metal x86 kernel (**Kernel Lab**), and a comprehensive multi-core processor affinity research benchmark suite (**Micro Research Lab**).

---

## 2. Core Pillars & Design Philosophy

### 2.1 Complete Original Visual Identity
MicroOS rejects Windows 11 taskbar imitation, macOS floating docks, and generic KDE layouts. Instead, it adopts an **Asymmetric Engineering Workstation** paradigm:
- **Left Vertical Dock**: Fast application category switching and workspace routing.
- **Main Canvas**: Minimalist cards, documentation quick-launchers, and engineering tools.
- **Right Telemetry Panel**: Continuous real-time CPU, RAM, disk, and link speed telemetry.
- **Bottom Multi-Workspace Strip**: 4 isolated virtual workspaces:
  1. *Development*: Shells, compilers, build systems, Git.
  2. *Networking*: NetworkManager, Wi-Fi discovery, traffic analysis.
  3. *Research*: Multi-core scheduling benchmarks, statistical plots.
  4. *System Administration*: `/proc` monitoring, disk partition management, logs.

### 2.2 Genuine Hardware Interfacing (No Mockups)
Every piece of networking and system monitoring data in MicroOS is derived directly from Linux kernel interfaces (`/proc/stat`, `/proc/meminfo`, `/proc/net/dev`, `iproute2`, `nmcli`, `iw`, `rfkill`). When running inside Oracle VirtualBox, MicroOS provides transparent support for VirtualBox NAT/Bridged virtual Ethernet, while providing documented passthrough support for real USB Wi-Fi dongles to scan physical wireless access points.

### 2.3 Integrated Academic Research Module
MicroOS ships with a full research module on **Multi-Core Scheduling: Effect of Processor Affinity and Workload Distribution on Execution Performance**, implementing the exact algorithm benchmarks, synthetic workload generation, statistical summaries, and Matplotlib graphs developed by T. Vasanth Diwakar.

---

## 3. Technology Stack Summary

| Subsystem | MicroOS Implementation | Upstream Base / Technology |
| :--- | :--- | :--- |
| **Operating System Base** | MicroOS 1.0 Live ISO | Ubuntu 24.04 LTS (Noble Numbat) |
| **Linux Kernel** | 6.8.0-generic (x86_64) | Monolithic Linux Kernel |
| **Desktop Environment** | Asymmetric Engineering Workspace | XFCE 4.18 with Custom Themes & Panels |
| **Display Manager** | MicroOS Graphite/Teal Greeter | LightDM + lightdm-gtk-greeter |
| **Terminal Suite** | MicroShell | GNU Bash 5.2 + 12 Custom micro-* Utilities |
| **Network Management** | Micro Network Center & Wi-Fi Scanner | NetworkManager 1.44, D-Bus, nmcli, rfkill |
| **Web Browser** | Mozilla Firefox (Customized Portal) | Gecko / Mozilla Engine with Local Portal |
| **System Telemetry** | Micro Monitor | Linux `/proc` and `/sys` Virtual Filesystems |
| **OS Puzzle Game** | Process Panic | Python / Canvas OS Scheduling Simulator |
| **Academic Benchmark** | Micro Research Lab | Python `multiprocessing`, Rust PyO3 Kernel, Matplotlib |
| **Bare-Metal Kernel** | Educational Kernel Lab | Multiboot x86 Assembly & Freestanding C |
