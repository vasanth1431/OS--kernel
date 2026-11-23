# MicroOS Networking Architecture

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Core Daemon**: NetworkManager 1.44+  
**Subsystems**: D-Bus, wpa_supplicant, mac80211, cfg80211, iproute2, rfkill

---

## 1. Network Stack Architecture

MicroOS implements a multi-tier networking architecture designed to interface directly with physical and virtual networking hardware:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   USERLAND NETWORK APPLICATIONS                        │
│   Micro Network Center (GUI)    │    Micro Wi-Fi Scanner (GUI)         │
│   micro-network / micro-wifi    │    Mozilla Firefox (Web Client)      │
└───────────────────┬────────────────────────────┬───────────────────────┘
                    │                            │
                    │ D-Bus Method Calls         │ Standard POSIX Sockets
                    ▼                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      NETWORKMANAGER DAEMON                             │
│   Connection Profiles (/etc/NetworkManager/system-connections/)        │
│   Device State Tracker  │  DHCP Client (internal)  │  DNS Manager      │
└─────────┬───────────────────────────────┬──────────────────────────────┘
          │                               │
          │ Control Socket                │ Netlink Sockets (rtnetlink)
          ▼                               ▼
┌──────────────────┐            ┌────────────────────────────────────────┐
│  wpa_supplicant  │            │          LINUX KERNEL NETWORK          │
│  802.11 WPA2/WPA3│            │  iproute2 / TCP/IP Protocol Stack      │
│  Authentication  │            │  Routing Table, ARP, Netfilter         │
└─────────┬────────┘            └───────────────────┬────────────────────┘
          │ nl80211                                 │
          └─────────────────────┬───────────────────┘
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 NETWORK DEVICE DRIVERS & HARDWARE                      │
│   e1000 / virtio-net (VirtualBox Virtual Ethernet)                     │
│   ath9k_htc / rt2800usb / rtl8xxxu (USB Wi-Fi Passthrough Adapters)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Architecture Principles

### 2.1 Separation of Control and Data Planes
- **Data Plane**: Handled exclusively inside the Linux kernel network stack (`TCP/IP`, packet routing, socket buffers, ARP resolution).
- **Control Plane**: Managed by `NetworkManager` through `D-Bus`. The userland GUI tools (`network_center.py` and `wifi_scanner.py`) issue control signals to scan, authenticate, and configure routes without interfering with kernel packet paths.

### 2.2 Security & Credential Isolation
- Wi-Fi passwords and PSK credentials are never passed via shell command line arguments, preventing credential leakage in `/proc` or `ps aux`.
- MicroOS uses NetworkManager's secure D-Bus or piped input interfaces to feed secrets directly to `wpa_supplicant`.

### 2.3 Hardware State Reflection
- The architecture directly reads `/sys/class/net/` and `/proc/net/dev`.
- Wireless frequency, channel number, and signal decibels (dBm) are calculated from raw `nl80211` driver structures rather than fabricated software values.
