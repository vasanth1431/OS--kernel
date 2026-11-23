# MicroOS Wi-Fi Troubleshooting Guide

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Scope**: Wireless adapter diagnostics, rfkill unblocking, and connection repair

---

## 1. Diagnostic Decision Tree

```text
Are Wi-Fi networks appearing in Micro Wi-Fi Scanner?
  ├── YES: Ready to authenticate.
  └── NO: Check 'micro-wifi' in terminal.
        ├── Is wireless interface detected?
        │     ├── YES: Check rfkill status.
        │     │     ├── Soft-blocked: Run 'sudo rfkill unblock wifi'
        │     │     └── Hard-blocked: Enable physical Wi-Fi switch / BIOS toggle
        │     └── NO: Running inside VirtualBox NAT?
        │           ├── YES: Normal behavior. Use USB Wi-Fi dongle passthrough.
        │           └── NO: Missing Linux firmware. Run 'sudo apt install linux-firmware'.
```

---

## 2. Common Errors and Resolutions

### Error 1: "No physical wireless adapter detected"
- **Cause**: MicroOS is running inside VirtualBox with standard NAT or Bridged Ethernet.
- **Resolution**: This is expected behavior. Internet browsing (Firefox, APT) is fully functional over the virtual Ethernet cable (`enp0s3`). If physical Wi-Fi scanning is required for testing, pass a USB Wi-Fi dongle via `Devices -> USB`.

### Error 2: "Wi-Fi is Soft-Blocked"
- **Cause**: The operating system or desktop environment has set the radio state to disabled.
- **Resolution**:
  ```bash
  sudo rfkill unblock wifi
  sudo systemctl restart NetworkManager
  ```

### Error 3: "Authentication timed out / Secrets were required"
- **Cause**: Incorrect WPA/WPA2 pre-shared key, weak radio signal, or MAC filtering on the AP.
- **Resolution**:
  1. Verify the password by checking the "Show Password" box in the Micro Wi-Fi connection dialog.
  2. Move closer to the router or check whether the network requires an institutional captive portal.

### Error 4: "DNS Resolution Failed (Limited Connectivity)"
- **Cause**: DHCP succeeded, but DNS nameservers are unreachable or blocked.
- **Resolution**:
  Test direct external IP ping:
  ```bash
  ping -c 2 1.1.1.1
  ```
  If IP ping succeeds, edit `/etc/resolv.conf` to add Cloudflare or Google DNS:
  ```bash
  echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
  ```
