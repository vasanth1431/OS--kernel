# MicroShell Specification & Command Manual

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Shell Core**: GNU Bash 5.2 (x86_64-pc-linux-gnu)  
**Configuration**: `/opt/microos/microshell/microshellrc`  
**Binary Location**: `/usr/local/bin/micro-*`

---

## 1. MicroShell Overview

MicroShell is a customized, production-grade Bash environment. It retains 100% compatibility with standard POSIX and Linux commands (`ls`, `grep`, `find`, `top`, `htop`, `curl`, `ip`, `nmcli`, `systemctl`, `apt`), while augmenting the shell with 12 custom diagnostic and telemetry commands.

### Prompt Format:
```text
user@microos:~/projects (main)$
```
- **Teal**: Username and hostname (`user@microos`).
- **Amber**: Working directory (`~/projects`).
- **Green**: Active Git branch detected via internal parser (`(main)`).

---

## 2. Command Index

MicroOS provides 12 standalone executable utilities installed to `/usr/local/bin`:

### 1. `micro-info`
Displays distribution identity, base operating system version, Linux kernel release, CPU hardware architecture, hostname, and active desktop environment.
```bash
micro-info
```

### 2. `micro-status`
Provides a real-time snapshot of system resource utilization:
- 1-minute, 5-minute, and 15-minute load averages from `/proc/loadavg`.
- RAM and Swap memory utilization calculated from `/proc/meminfo`.
- Root filesystem storage status via `df -h /`.
- Top 3 CPU-consuming processes.

### 3. `micro-health`
Runs automated system health heuristic checks:
- Flags memory warnings if RAM consumption exceeds 75% (warning) or 90% (critical).
- Flags storage warnings if root disk usage exceeds 80%.
- Flags CPU saturation warnings if 1-minute load average exceeds available logical cores.
- Detects zombie/defunct processes.

### 4. `micro-network`
Queries NetworkManager and kernel routing tables:
- Lists all active and inactive network interfaces (`ip -br link`).
- Shows active NetworkManager connections.
- Displays IP addresses and default gateway routes.

### 5. `micro-wifi`
Dedicated wireless hardware diagnostic:
- Inspects `rfkill` hardware and software kill-switch states.
- Identifies active 802.11 wireless devices (`iw dev`).
- Executes `nmcli device wifi list` to display nearby SSIDs, signal strengths, security types, channels, and frequencies.
- If no wireless card is found (e.g. VirtualBox NAT mode), prints instructions on passing through a USB Wi-Fi dongle.

### 6. `micro-ip`
Detailed IP configuration command:
- Local IPv4 and IPv6 addresses per interface with CIDR prefixes.
- Default gateway IP.
- DNS nameservers configured in `/etc/resolv.conf`.
- Public WAN IP queried via external HTTPS lookup (with timeout fallback).

### 7. `micro-internet`
A 3-tier internet connectivity diagnostic:
1. **Tier 1 (Gateway)**: Pings local default gateway.
2. **Tier 2 (IP Reachability)**: Pings external IP `1.1.1.1` to confirm routing outside LAN.
3. **Tier 3 (DNS & HTTPS)**: Queries `example.com` to confirm DNS resolution and TLS handshakes.
- Categorizes status into: `CONNECTED`, `LIMITED CONNECTIVITY`, or `DISCONNECTED`.

### 8. `micro-process`
Displays the active process table sorted by CPU and memory consumption, showing PID, owner username, CPU%, MEM%, VSZ, RSS, execution status, and command name.

### 9. `micro-storage`
Displays block devices, partitions, filesystem types, and mount points using `lsblk` and `df -h`.

### 10. `micro-apps`
Lists installed MicroOS engineering tools and verifies host system utilities (`gcc`, `python3`, `git`, `thunar`, `firefox`, `htop`).

### 11. `micro-update`
Refreshes the APT package index cache and counts upgradable security/system packages.

### 12. `micro-help`
Displays the full command manual, syntax references, and practical examples.
