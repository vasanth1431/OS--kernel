# MicroOS Wi-Fi Implementation & Hardware Discovery

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Application**: `microos/wifi-scanner/wifi_scanner.py`  
**Tool**: `micro-wifi`

---

## 1. Hardware Discovery & Radio Kill-Switch Inspection

Before attempting to scan for wireless SSIDs, MicroOS executes a hardware validation pipeline:

### 1.1 Radio Block Inspection via `rfkill`
The scanner inspects the Linux radio subsystem to detect physical or software cut-offs:
```bash
rfkill list wifi
```
- **Soft blocked: yes**: Wireless is disabled via software (e.g., flight mode). Resolved with `rfkill unblock wifi`.
- **Hard blocked: yes**: Physical hardware toggle switch or BIOS latch is disconnected.

### 1.2 Interface Discovery
The application scans `/sys/class/net/` and executes `iw dev` to find physical PHY wireless interfaces (e.g. `wlan0`, `wlx000f00...`).

---

## 2. Real Wi-Fi Network Scanning

Scanning is conducted via `nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY,CHAN,BSSID device wifi list`.
- **In-Use**: Marked with `*` for the currently associated BSSID.
- **SSID**: Human-readable network identifier.
- **Signal**: Actual RSSI mapped to percentage (0–100%).
- **Security**: Protocols negotiated (WPA2-PSK, WPA3-SAE, WEP, Open).
- **Channel**: Frequency band channel (Channels 1–14 on 2.4 GHz; 36–165 on 5 GHz).
- **BSSID**: Hardware MAC address of the Access Point.

---

## 3. Secure Authentication Dialog

When an encrypted network is selected, a dedicated authentication modal is spawned:
1. Validates that passwords are not stored in unencrypted bash history or process arguments.
2. Interacts with NetworkManager via non-logging subprocess execution.
3. Provides visual feedback during DHCP discovery and 4-way WPA handshake.
4. On success, persists the connection profile in `/etc/NetworkManager/system-connections/` for automatic reconnection upon subsequent reboots.
