# MicroOS Desktop Environment & Visual Identity

**Developer**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Desktop Base**: XFCE 4.18 with Asymmetric Engineering Configuration  
**Window Manager**: Xfwm4 with Compositing Enabled

---

## 1. Visual Identity Palette

MicroOS utilizes a dark engineering color scheme designed for long research and development sessions:

| Token | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Deep Graphite** | `#14171a` | Master background, desktop canvas, and shell backdrop |
| **Charcoal Panel** | `#1e2227` | Application panels, card surfaces, and sidebar container |
| **Electric Teal** | `#00b4d8` | Primary active accent, title highlights, focused controls |
| **Ocean Blue** | `#0077b6` | Secondary gradient accent and selection indicators |
| **Amber Gold** | `#ffb703` | Warnings, notifications, telemetry thresholds, score tags |
| **Mint Green** | `#2ec4b6` | Success status, memory availability, download indicators |
| **Crimson Alert** | `#e63946` | Critical hardware blocks, OOM panic, high CPU load |
| **Crisp Off-White** | `#e0e6ed` | Primary readable typography |
| **Muted Slate** | `#8892b0` | Subtitles, secondary descriptions, inactive borders |

---

## 2. Asymmetric Desktop Layout

MicroOS rejects the conventional bottom taskbar. The desktop is split into functional quadrants:

```text
┌──┬────────────────────────────────────────────────────────┬────────┐
│  │ MAIN WORKSPACE CANVAS                                  │ RIGHT  │
│  │                                                        │ TELE-  │
│L │ - Micro Hub Application Launcher                       │ METRY  │
│E │ - Active Engineering Windows                           │ PANEL  │
│F │ - Research Benchmark Terminals                         │        │
│T │ - Firefox Browser Sessions                             │ CPU %  │
│  │                                                        │ RAM MB │
│D │                                                        │ Up/Down│
│O │                                                        │ Disk   │
│C │                                                        │ Uptime │
│K │                                                        │ Clock  │
├──┴────────────────────────────────────────────────────────┴────────┤
│ BOTTOM STRIP: [Workspaces: Dev | Net | Research | SysAdmin] [Systray] │
└────────────────────────────────────────────────────────────────────┘
```

### 2.1 Left Vertical Dock
The left vertical panel (width: 48px) anchors the workstation:
- **Top Icon**: Micro Hub (Application Launcher).
- **Workspace Category Launchers**: Direct shortcuts to Firefox, Terminal, Thunar, Micro Monitor, and Research Lab.
- **Settings Launcher**: Opens Micro Control Center.

### 2.2 Right Telemetry Panel
A dedicated right-hand information panel displaying live system statistics:
- Real-time CPU utilization sparklines.
- Memory consumption meter (used vs. total).
- Live network interface upload/download speeds.
- Disk usage percentage and system uptime clock.

### 2.3 Virtual Workspaces
Four isolated workspaces configured via XFCE workspace manager:
1. **Workspace 1: Development**: Configured for MicroShell, text editors, Git, and GCC compilation.
2. **Workspace 2: Networking**: Dedicated to Micro Network Center, Wi-Fi Scanner, and packet captures.
3. **Workspace 3: Research**: Dedicated to the Multi-Core Scheduling Lab and Matplotlib graph analysis.
4. **Workspace 4: System Administration**: Configured for Micro Monitor, GParted, and system logs.

---

## 3. LightDM Login Screen
The LightDM login screen uses the custom `MicroOS-Dark` theme:
- Deep graphite geometric background with the central MicroOS emblem.
- Clean teal login credentials box with password visibility toggle.
- Session selector defaults to `MicroOS XFCE Session`.
- Clear user status and error messages on authentication failure.
