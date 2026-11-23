# Micro Monitor – System Monitoring Specification

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Application**: `microos/system-monitor/system_monitor.py`  
**Command**: `micro-monitor`

---

## 1. System Telemetry Architecture

Micro Monitor interfaces directly with Linux virtual filesystems (`/proc` and `/sys`):

| Metric | Source File | Computation Logic |
| :--- | :--- | :--- |
| **CPU Busy %** | `/proc/stat` | $\Delta(\text{user} + \text{nice} + \text{system}) / \Delta \text{total} \times 100$ |
| **Memory (RAM)** | `/proc/meminfo` | $\text{Used} = \text{MemTotal} - \text{MemAvailable}$ |
| **Swap Space** | `/proc/meminfo` | $\text{Used} = \text{SwapTotal} - \text{SwapFree}$ |
| **Storage Usage** | `statvfs("/")` | $\text{Used} = (\text{blocks} - \text{bavail}) \times \text{frsize}$ |
| **System Uptime** | `/proc/uptime` | Seconds converted to hours, minutes, seconds |
| **Process Table** | `/proc/[pid]/` & `ps` | PID, user, CPU%, MEM%, RSS memory, status, command |

---

## 2. Interactive Features

1. **Real-Time Sparkline Canvas**:
   - Maintains a rolling 30-second history buffer.
   - Dual-channel plotting: CPU utilization (Electric Teal line) and Memory utilization (Mint Green line).
2. **Process Management**:
   - Filter processes instantly by name, PID, or owning user.
   - Click column headers (`PID`, `CPU %`, `MEM %`) to sort descending or ascending.
   - Terminate processes by sending standard POSIX signals (`SIGTERM` via `os.kill`).
