#!/usr/bin/env bash
# ==============================================================================
# MicroOS v1.0 - Complete Master Redesign & ISO Remastering Engine
# Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
# Completely replaces old legacy desktop, branding, icons, and interface
# ==============================================================================

set -euo pipefail

PROJECT_DIR="/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel"
ISO_BASE="/mnt/c/Users/diwak/OneDrive/Documents/os kernel/micro-os/build/micro-os.iso"
ISO_OUT="${PROJECT_DIR}/microos/build/microos.iso"
WORK_DIR="/tmp/microos_master_rebuild"

echo "==============================================================================="
echo "        MICROOS v1.0 - COMPLETE MASTER REDESIGN & INTERFACE ENGINE"
echo "        Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)"
echo "==============================================================================="

# 1. Clean workspace
echo "[1/8] Setting up build workspace..."
umount -lf "$WORK_DIR/iso_mnt" 2>/dev/null || true
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/iso_mnt" "$WORK_DIR/squashfs_root"

# 2. Extract base filesystem
echo "[2/8] Extracting live filesystem..."
mount -o loop,ro "$ISO_BASE" "$WORK_DIR/iso_mnt"
unsquashfs -f -d "$WORK_DIR/squashfs_root" "$WORK_DIR/iso_mnt/live/filesystem.squashfs"
umount "$WORK_DIR/iso_mnt"

ROOT="$WORK_DIR/squashfs_root"

# 3. Purge all legacy applications, games and old shortcuts
echo "[3/8] Purging legacy games, old desktop icons and copied assets..."
rm -f "$ROOT/usr/share/applications/nsnake.desktop" 2>/dev/null || true
rm -f "$ROOT/usr/bin/snake" "$ROOT/usr/games/nsnake" 2>/dev/null || true
rm -rf "$ROOT/usr/share/games/nsnake" 2>/dev/null || true
rm -f "$ROOT/usr/local/bin/snake"* "$ROOT/usr/local/bin/wifi-manager" 2>/dev/null || true

# Purge any desktop shortcuts from all existing users & templates
for udir in "$ROOT/etc/skel" "$ROOT/root" "$ROOT/home"/*; do
    if [ -d "$udir" ]; then
        rm -rf "$udir/Desktop"
        mkdir -p "$udir/Desktop"
        rm -rf "$udir/.cache" "$udir/.config/xfce4"
    fi
done

# 4. OS Identity & Hostname Customization
echo "[4/8] Configuring MicroOS v1.0 operating system identity..."

# /etc/os-release
cat << 'EOF' > "$ROOT/etc/os-release"
NAME="MicroOS"
PRETTY_NAME="MicroOS v1.0 - Beyond the Ordinary Desktop"
VERSION_ID="1.0"
VERSION="1.0 (Engineering Workstation)"
ID=microos
ID_LIKE="ubuntu debian"
HOME_URL="https://github.com/vasanth-diwakar/microos"
SUPPORT_URL="https://github.com/vasanth-diwakar/microos"
BUG_REPORT_URL="https://github.com/vasanth-diwakar/microos"
PRIVACY_POLICY_URL="https://github.com/vasanth-diwakar/microos"
UBUNTU_CODENAME=noble
EOF

# /etc/lsb-release
cat << 'EOF' > "$ROOT/etc/lsb-release"
DISTRIB_ID=MicroOS
DISTRIB_RELEASE=1.0
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="MicroOS v1.0 - Beyond the Ordinary Desktop"
EOF

# /etc/issue and /etc/issue.net
cat << 'EOF' > "$ROOT/etc/issue"
MicroOS v1.0 - Beyond the Ordinary Desktop (\l)
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Jain University FET - Operating Systems Research Activity

EOF
cp "$ROOT/etc/issue" "$ROOT/etc/issue.net"

# /etc/hostname and /etc/hosts
echo "microos" > "$ROOT/etc/hostname"
cat << 'EOF' > "$ROOT/etc/hosts"
127.0.0.1   localhost microos
127.0.1.1   microos

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

# /etc/motd
cat << 'EOF' > "$ROOT/etc/motd"
  __  __ _             ___  ____  
 |  \/  (_) ___ _ __  / _ \/ ___| 
 | |\/| | |/ __| '__|| | | \___ \ 
 | |  | | | (__| |   | |_| |___) |
 |_|  |_|_|\___|_|    \___/|____/ 
 MICROOS v1.0 - Beyond the Ordinary Desktop
 Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
 Research: Multi-Core Scheduling & Processor Affinity
 Type 'micro-help' for original MicroOS diagnostic commands.
EOF

# 5. Install MicroOS Applications Suite & 12 MicroShell commands
echo "[5/8] Installing MicroOS application suite and MicroShell binaries..."
OPT_DIR="$ROOT/opt/microos"
rm -rf "$OPT_DIR"
mkdir -p "$OPT_DIR"

cp -r "${PROJECT_DIR}/microos/microshell" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/network-center" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/wifi-scanner" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/system-monitor" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/control-center" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/application-hub" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/process-panic" "$OPT_DIR/"
cp -r "${PROJECT_DIR}/microos/research-lab" "$OPT_DIR/"

# Install the 12 MicroShell binary commands to /usr/local/bin
cp "${PROJECT_DIR}/microos/microshell/bin/"* "$ROOT/usr/local/bin/"

# Install GUI wrappers in /usr/local/bin
cat << 'EOF' > "$ROOT/usr/local/bin/micro-network-center"
#!/bin/sh
exec python3 /opt/microos/network-center/network_center.py "$@"
EOF

cat << 'EOF' > "$ROOT/usr/local/bin/micro-wifi-scanner"
#!/bin/sh
exec python3 /opt/microos/wifi-scanner/wifi_scanner.py "$@"
EOF

cat << 'EOF' > "$ROOT/usr/local/bin/micro-monitor"
#!/bin/sh
exec python3 /opt/microos/system-monitor/system_monitor.py "$@"
EOF

cat << 'EOF' > "$ROOT/usr/local/bin/micro-control-center"
#!/bin/sh
exec python3 /opt/microos/control-center/control_center.py "$@"
EOF

cat << 'EOF' > "$ROOT/usr/local/bin/micro-hub"
#!/bin/sh
exec python3 /opt/microos/application-hub/application_hub.py "$@"
EOF

cat << 'EOF' > "$ROOT/usr/local/bin/process-panic"
#!/bin/sh
exec python3 /opt/microos/process-panic/main.py "$@"
EOF

cat << 'EOF' > "$ROOT/usr/local/bin/micro-research-lab"
#!/bin/sh
exec python3 /opt/microos/research-lab/gui.py "$@"
EOF

chmod +x "$ROOT/usr/local/bin/"*

# Configure MicroShell environment in bashrc
cp "${PROJECT_DIR}/microos/microshell/microshellrc" "$ROOT/etc/skel/.microshellrc"
echo 'source ~/.microshellrc' >> "$ROOT/etc/skel/.bashrc"
for udir in "$ROOT/root" "$ROOT/home"/*; do
    if [ -d "$udir" ]; then
        cp "${PROJECT_DIR}/microos/microshell/microshellrc" "$udir/.microshellrc"
        grep -q 'source ~/.microshellrc' "$udir/.bashrc" 2>/dev/null || echo 'source ~/.microshellrc' >> "$udir/.bashrc"
    fi
done

# 6. Generate Deep Graphite & Teal Wallpaper & XFCE Configurations
echo "[6/8] Generating high-resolution Deep Graphite & Teal wallpaper..."
mkdir -p "$ROOT/usr/share/backgrounds/microos"
python3 - << 'PY_WP'
from PIL import Image, ImageDraw, ImageFont

w, h = 1920, 1080
img = Image.new("RGB", (w, h), (20, 23, 26))
draw = ImageDraw.Draw(img)

# Deep graphite gradient
for y in range(h):
    ratio = y / h
    r = int(20 - ratio * 8)
    g = int(23 - ratio * 8)
    b = int(26 - ratio * 8)
    draw.line([(0, y), (w, y)], fill=(r, g, b))

# Modern engineering grid
for x in range(0, w, 60):
    draw.line([(x, 0), (x, h)], fill=(28, 33, 40), width=1)
for y in range(0, h, 60):
    draw.line([(0, y), (w, y)], fill=(28, 33, 40), width=1)

# Center Hexagon & Logo
cx, cy = w // 2, h // 2 - 40
draw.polygon([(cx, cy - 100), (cx + 90, cy - 50), (cx + 90, cy + 50), (cx, cy + 100), (cx - 90, cy + 50), (cx - 90, cy - 50)], outline=(0, 180, 216), width=4)
draw.polygon([(cx, cy - 85), (cx + 75, cy - 40), (cx + 75, cy + 40), (cx, cy + 85), (cx - 75, cy + 40), (cx - 75, cy - 40)], outline=(35, 42, 52), width=2)
# Stylized 'M'
draw.line([(cx - 45, cy + 35), (cx - 45, cy - 35), (cx, cy), (cx + 45, cy - 35), (cx + 45, cy + 35)], fill=(0, 180, 216), width=9)

try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = font_title
    font_small = font_title

t1 = "MICROOS"
bbox = draw.textbbox((0,0), t1, font=font_title)
draw.text((cx - (bbox[2]-bbox[0])//2, cy + 130), t1, fill=(224, 230, 237), font=font_title)

t2 = "BEYOND THE ORDINARY DESKTOP"
bbox2 = draw.textbbox((0,0), t2, font=font_sub)
draw.text((cx - (bbox2[2]-bbox2[0])//2, cy + 195), t2, fill=(0, 180, 216), font=font_sub)

t3 = "Tadigotla Vasanth Diwakar  |  USN: 25BTRCL270  |  Jain University FET"
bbox3 = draw.textbbox((0,0), t3, font=font_small)
draw.text((cx - (bbox3[2]-bbox3[0])//2, h - 60), t3, fill=(136, 146, 176), font=font_small)

img.save("/tmp/microos_wallpaper.png")
print("High-res wallpaper generated.")
PY_WP

cp /tmp/microos_wallpaper.png "$ROOT/usr/share/backgrounds/microos/microos_wallpaper.png"

# Overwrite Debian/XFCE default wallpapers so any fallback is MicroOS
for wp_dir in "$ROOT/usr/share/images/desktop-base" "$ROOT/usr/share/backgrounds/xfce"; do
    mkdir -p "$wp_dir"
    for wp_f in "$wp_dir"/*; do
        if [ -f "$wp_f" ]; then
            cp /tmp/microos_wallpaper.png "$wp_f" 2>/dev/null || true
        fi
    done
done

# 7. Configure XFCE Configurations (xfce4-desktop.xml, xfce4-panel.xml, xsettings.xml)
echo "[7/8] Configuring XFCE desktop settings, panels, and appearance..."

# Generate xfce4-desktop.xml
cat << 'EOF' > /tmp/xfce4-desktop.xml
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
      <property name="monitor0" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/microos/microos_wallpaper.png"/>
        </property>
        <property name="workspace1" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/microos/microos_wallpaper.png"/>
        </property>
        <property name="workspace2" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/microos/microos_wallpaper.png"/>
        </property>
        <property name="workspace3" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/microos/microos_wallpaper.png"/>
        </property>
      </property>
      <property name="monitorVirtual-1" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/microos/microos_wallpaper.png"/>
        </property>
      </property>
    </property>
  </property>
  <property name="desktop-icons" type="empty">
    <property name="style" type="int" value="2"/>
    <property name="file-icons" type="empty">
      <property name="show-filesystem" type="bool" value="false"/>
      <property name="show-home" type="bool" value="false"/>
      <property name="show-trash" type="bool" value="false"/>
      <property name="show-removable" type="bool" value="false"/>
    </property>
  </property>
</channel>
EOF

# Generate xfce4-panel.xml (Asymmetric Layout: Vertical Left Sidebar + Top Bar)
cat << 'EOF' > /tmp/xfce4-panel.xml
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <value type="int" value="2"/>
  </property>
  <property name="panel-1" type="empty">
    <property name="position" type="string" value="p=1;x=0;y=0"/>
    <property name="length" type="uint" value="100"/>
    <property name="position-locked" type="bool" value="true"/>
    <property name="icon-size" type="uint" value="28"/>
    <property name="size" type="uint" value="48"/>
    <property name="mode" type="uint" value="2"/>
    <property name="plugin-ids" type="array">
      <value type="int" value="1"/>
      <value type="int" value="2"/>
      <value type="int" value="3"/>
      <value type="int" value="4"/>
      <value type="int" value="5"/>
      <value type="int" value="6"/>
      <value type="int" value="7"/>
      <value type="int" value="8"/>
      <value type="int" value="9"/>
      <value type="int" value="10"/>
      <value type="int" value="11"/>
    </property>
  </property>
  <property name="panel-2" type="empty">
    <property name="position" type="string" value="p=6;x=48;y=0"/>
    <property name="length" type="uint" value="100"/>
    <property name="position-locked" type="bool" value="true"/>
    <property name="size" type="uint" value="28"/>
    <property name="mode" type="uint" value="0"/>
    <property name="plugin-ids" type="array">
      <value type="int" value="20"/>
      <value type="int" value="21"/>
      <value type="int" value="22"/>
      <value type="int" value="23"/>
      <value type="int" value="24"/>
      <value type="int" value="25"/>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="applicationsmenu"/>
    <property name="plugin-2" type="string" value="separator"/>
    <property name="plugin-3" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="micro-hub.desktop"/>
      </property>
    </property>
    <property name="plugin-4" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="microshell.desktop"/>
      </property>
    </property>
    <property name="plugin-5" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="micro-research-lab.desktop"/>
      </property>
    </property>
    <property name="plugin-6" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="micro-network-center.desktop"/>
      </property>
    </property>
    <property name="plugin-7" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="micro-wifi-scanner.desktop"/>
      </property>
    </property>
    <property name="plugin-8" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="micro-monitor.desktop"/>
      </property>
    </property>
    <property name="plugin-9" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="micro-control-center.desktop"/>
      </property>
    </property>
    <property name="plugin-10" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="process-panic.desktop"/>
      </property>
    </property>
    <property name="plugin-11" type="string" value="actions"/>
    <property name="plugin-20" type="string" value="pager"/>
    <property name="plugin-21" type="string" value="tasklist"/>
    <property name="plugin-22" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-23" type="string" value="systray"/>
    <property name="plugin-24" type="string" value="clock"/>
    <property name="plugin-25" type="string" value="actions"/>
  </property>
</channel>
EOF

# Copy configurations to /etc/xdg and all user home directories
CONFIG_TARGETS=(
    "$ROOT/etc/xdg/xfce4/xfconf/xfce-perchannel-xml"
    "$ROOT/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml"
    "$ROOT/root/.config/xfce4/xfconf/xfce-perchannel-xml"
)

for cdir in "${CONFIG_TARGETS[@]}"; do
    mkdir -p "$cdir"
    cp /tmp/xfce4-desktop.xml "$cdir/xfce4-desktop.xml"
    cp /tmp/xfce4-panel.xml "$cdir/xfce4-panel.xml"
done

for udir in "$ROOT/home"/*; do
    if [ -d "$udir" ]; then
        mkdir -p "$udir/.config/xfce4/xfconf/xfce-perchannel-xml"
        cp /tmp/xfce4-desktop.xml "$udir/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml"
        cp /tmp/xfce4-panel.xml "$udir/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml"
    fi
done

# Deploy Desktop Shortcuts (.desktop)
DESKTOP_APPS=(
    "micro-hub.desktop"
    "micro-research-lab.desktop"
    "micro-network-center.desktop"
    "micro-wifi-scanner.desktop"
    "micro-monitor.desktop"
    "micro-control-center.desktop"
    "process-panic.desktop"
)

mkdir -p "$ROOT/usr/share/applications"
for da in "${DESKTOP_APPS[@]}"; do
    cp "${PROJECT_DIR}/microos/desktop/applications/$da" "$ROOT/usr/share/applications/"
    for udir in "$ROOT/etc/skel" "$ROOT/root" "$ROOT/home"/*; do
        if [ -d "$udir" ]; then
            mkdir -p "$udir/Desktop"
            cp "${PROJECT_DIR}/microos/desktop/applications/$da" "$udir/Desktop/"
            chmod 755 "$udir/Desktop/$da"
        fi
    done
done

# Add MicroShell Terminal shortcut
for udir in "$ROOT/etc/skel" "$ROOT/root" "$ROOT/home"/*; do
    if [ -d "$udir" ]; then
        cat << 'TERM_EOF' > "$udir/Desktop/microshell.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=MicroShell Terminal
Comment=Interactive Linux Engineering Shell
Exec=xfce4-terminal
Icon=utilities-terminal
Terminal=false
TERM_EOF

        cat << 'FF_EOF' > "$udir/Desktop/firefox.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Firefox Web Browser
Comment=Browse the World Wide Web
Exec=firefox
Icon=firefox
Terminal=false
FF_EOF
        chmod 755 "$udir/Desktop/"*.desktop
    fi
done

# Autostart Micro Hub Welcome Dashboard on login
mkdir -p "$ROOT/etc/xdg/autostart"
cat << 'AUTO_EOF' > "$ROOT/etc/xdg/autostart/micro-hub-welcome.desktop"
[Desktop Entry]
Type=Application
Name=Micro Hub Welcome Dashboard
Comment=Automatic MicroOS Engineering Dashboard
Exec=micro-hub
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
AUTO_EOF
chmod 755 "$ROOT/etc/xdg/autostart/micro-hub-welcome.desktop"

# Fix ownership
chown -R 1000:1000 "$ROOT/home/user" 2>/dev/null || true

# 8. Repack Squashfs & Rebuild ISO
echo "[8/8] Compressing squashfs and generating final bootable MicroOS ISO..."
rm -f "$WORK_DIR/filesystem.squashfs"
mksquashfs "$ROOT" "$WORK_DIR/filesystem.squashfs" -comp gzip -noappend

mkdir -p "$(dirname "$ISO_OUT")"
cp "$ISO_BASE" "$ISO_OUT"
xorriso -dev "$ISO_OUT" \
    -map "$WORK_DIR/filesystem.squashfs" /live/filesystem.squashfs \
    -boot_image any replay \
    -commit

rm -rf "$WORK_DIR"

echo "==============================================================================="
echo " [SUCCESS] Remastered ISO rebuild completed!"
echo " ISO Output: $ISO_OUT"
echo " Size: $(du -h "$ISO_OUT" | cut -f1)"
echo "==============================================================================="
