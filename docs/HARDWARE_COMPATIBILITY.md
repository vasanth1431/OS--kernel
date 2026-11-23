# MicroOS Hardware Compatibility Guide

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Target Architecture**: x86_64 (AMD64 / Intel 64)

---

## 1. System Requirements

| Hardware Component | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **Processor** | Dual-core 64-bit x86 processor | Quad-core (or 8-thread) x86_64 |
| **System Memory (RAM)** | 2 GB RAM (for live headless) | 4 GB to 8 GB RAM (for GUI & multi-core lab) |
| **Host Storage** | 15 GB free disk space (for build) | 25 GB SSD storage |
| **VirtualBox Version** | Oracle VirtualBox 6.1+ | VirtualBox 7.0+ with Extension Pack |
| **Graphics Controller** | VMSVGA / Standard SVGA (32 MB) | VMSVGA (128 MB VRAM) |
| **Display Resolution** | 1024 × 768 | 1920 × 1080 (Full HD) |

---

## 2. Wireless Hardware Support Matrix

When running bare-metal or passing USB dongles to VirtualBox:

| Chipset Family | Linux Kernel Driver | Support Status in MicroOS |
| :--- | :--- | :--- |
| **Atheros AR9271** | `ath9k_htc` | **Full Out-of-the-Box Support** (Monitor Mode & AP Injection) |
| **Ralink RT5370 / RT3070** | `rt2800usb` | **Full Out-of-the-Box Support** |
| **MediaTek MT7601U** | `mt7601u` | **Full Out-of-the-Box Support** |
| **Realtek RTL8188EUS / RTL8192CU** | `r8188eu` / `rtl8192cu` | **Supported** via `linux-firmware` package |
| **Intel Wi-Fi 6 / 6E (AX200/AX210)** | `iwlwifi` | **Supported** on bare-metal hosts |
| **VirtualBox Virtual Ethernet** | `e1000` / `virtio-net` | **Native Support** for NAT/Bridged internet |
