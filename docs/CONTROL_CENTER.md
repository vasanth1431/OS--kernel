# Micro Control Center Specification

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Application**: `microos/control-center/control_center.py`  
**Command**: `micro-control-center`

---

## 1. Overview of 10 Functional Sections

Unlike generic desktop mockups, every section in Micro Control Center interfaces with functional Linux configuration tools:

1. **Appearance (`xfconf-query`)**:
   - Manages GTK themes (`MicroOS-Dark`, `Adwaita-dark`, `Greybird-dark`).
   - Sets desktop background wallpaper via `/backdrop/screen0/monitor0/workspace0/last-image`.
2. **Display & Graphics (`xrandr`)**:
   - Detects connected virtual/physical displays and active resolution.
   - Adjusts resolutions on the fly (`1920x1080`, `1600x900`, `1280x720`).
3. **Keyboard & Input (`setxkbmap`)**:
   - Switches keyboard keymaps (`us`, `gb`, `de`, `fr`, `in`).
4. **Mouse & Touchpad (`xset`)**:
   - Configures pointer acceleration threshold and scaling factor.
5. **Network & Routing (`systemctl`, `nmcli`)**:
   - Restarts NetworkManager service daemon (`systemctl restart NetworkManager`).
   - Direct launch link to Micro Network Center and Wi-Fi Scanner.
6. **Sound & Audio (`amixer`, PipeWire)**:
   - Real-time ALSA volume slider adjusting Master channel (`amixer set Master X%`).
   - Generates a 440 Hz test tone via `speaker-test` to verify sound driver routing.
7. **Storage & Disks (`lsblk`)**:
   - Inspects block devices, partitions, filesystem types, and mount points.
8. **Users & Security (`/etc/passwd`, `groups`)**:
   - Displays active username, UID, GID, and administrative `sudo` group memberships.
9. **System Information (`uname`, `lscpu`)**:
   - Full kernel version, system architecture, CPU model, and microarchitecture flags.
10. **Default Applications**:
    - Default browser, terminal emulator, and file manager association status.
