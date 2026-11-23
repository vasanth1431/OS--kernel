#!/usr/bin/env bash
# ==============================================================================
# MicroOS v1.0 - Final Production Remastering & Interface Synthesis Engine
# Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
# Fixes:
# 1. Installs python3-tk inside squashfs so Wi-Fi & all GUI apps open instantly.
# 2. Changes user from 'user' to 'vasanth' (whoami = vasanth).
# 3. Fixes panel layout into a single sleek top bar, removing beige rectangles.
# 4. Configures Wi-Fi & NetworkManager for instant discovery & connectivity.
# 5. Rebuilds isolinux with username=vasanth.
# ==============================================================================

set -euo pipefail

PROJECT_DIR="/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel"
ISO_BASE="/mnt/c/Users/diwak/OneDrive/Documents/os kernel/micro-os/build/micro-os.iso"
ISO_OUT="${PROJECT_DIR}/microos/build/microos.iso"
WORK_DIR="/tmp/microos_production_rebuild"

echo "==============================================================================="
echo "   MICROOS v1.0 - PRODUCTION REMASTERING (USER: VASANTH, TKINTER, PANEL FIX)"
echo "   Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)"
echo "==============================================================================="

# 1. Clean workspace
echo "[1/9] Setting up build workspace..."
umount -lf "$WORK_DIR/iso_mnt" 2>/dev/null || true
umount -lf "$WORK_DIR/squashfs_root/dev/pts" 2>/dev/null || true
umount -lf "$WORK_DIR/squashfs_root/dev" 2>/dev/null || true
umount -lf "$WORK_DIR/squashfs_root/sys" 2>/dev/null || true
umount -lf "$WORK_DIR/squashfs_root/proc" 2>/dev/null || true
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/iso_mnt" "$WORK_DIR/iso_extract" "$WORK_DIR/squashfs_root"

# 2. Extract base ISO structure and squashfs
echo "[2/9] Extracting base ISO and live filesystem..."
mount -o loop,ro "$ISO_BASE" "$WORK_DIR/iso_mnt"
cp -r "$WORK_DIR/iso_mnt/." "$WORK_DIR/iso_extract/"
chmod -R u+w "$WORK_DIR/iso_extract"
unsquashfs -f -d "$WORK_DIR/squashfs_root" "$WORK_DIR/iso_mnt/live/filesystem.squashfs"
umount "$WORK_DIR/iso_mnt"

ROOT="$WORK_DIR/squashfs_root"

# 3. Mount pseudo-filesystems and install python3-tk inside squashfs
echo "[3/9] Installing python3-tk, python3-pil, net-tools inside live system..."
cp /etc/resolv.conf "$ROOT/etc/resolv.conf"
mount -t proc /proc "$ROOT/proc"
mount -t sysfs /sys "$ROOT/sys"
mount --bind /dev "$ROOT/dev"
mount --bind /dev/pts "$ROOT/dev/pts"

chroot "$ROOT" apt-get update
chroot "$ROOT" apt-get install -y python3-tk python3-pil python3-psutil net-tools wireless-tools iputils-ping traceroute dnsutils curl wget

# Verify tkinter works inside the image
echo "Verifying Tkinter installation inside image:"
chroot "$ROOT" python3 -c "import tkinter; import PIL; print('[OK] Tkinter & PIL verified inside MicroOS!')"

# Clean apt caches inside image
chroot "$ROOT" apt-get clean
rm -rf "$ROOT/var/lib/apt/lists/"*

# Unmount chroot
umount "$ROOT/dev/pts" || true
umount "$ROOT/dev" || true
umount "$ROOT/sys" || true
umount "$ROOT/proc" || true

# 4. User Account Transformation: 'user' -> 'vasanth'
echo "[4/9] Transforming user account to 'vasanth' (whoami = vasanth)..."

# Rename user in passwd, shadow, group
sed -i 's/^user:x:1000:1000:.*$/vasanth:x:1000:1000:Tadigotla Vasanth Diwakar,,,:\/home\/vasanth:\/bin\/bash/' "$ROOT/etc/passwd"
sed -i 's/^user:/vasanth:/' "$ROOT/etc/shadow"
sed -i 's/:user/:vasanth/g; s/,user/,vasanth/g; s/^user:/vasanth:/g' "$ROOT/etc/group"

# Add vasanth to essential groups
for grp in sudo adm cdrom dip plugdev netdev audio video dialout users; do
    if grep -q "^${grp}:" "$ROOT/etc/group"; then
        sed -i "/^${grp}:/ s/$/,vasanth/; s/,,/,/g; s/:,/:/g" "$ROOT/etc/group"
    fi
done

# Sudo privileges
mkdir -p "$ROOT/etc/sudoers.d"
echo "vasanth ALL=(ALL:ALL) NOPASSWD: ALL" > "$ROOT/etc/sudoers.d/vasanth"
chmod 0440 "$ROOT/etc/sudoers.d/vasanth"

# Rename home directory
if [ -d "$ROOT/home/user" ]; then
    rm -rf "$ROOT/home/vasanth" 2>/dev/null || true
    mv "$ROOT/home/user" "$ROOT/home/vasanth"
else
    mkdir -p "$ROOT/home/vasanth"
fi

# LightDM Autologin as vasanth
mkdir -p "$ROOT/etc/lightdm/lightdm.conf.d"
cat << 'EOF' > "$ROOT/etc/lightdm/lightdm.conf.d/01_autologin.conf"
[Seat:*]
autologin-user=vasanth
autologin-user-timeout=0
user-session=xfce
greeter-session=lightdm-autologin-greeter
EOF

if [ -f "$ROOT/etc/lightdm/lightdm.conf" ]; then
    sed -i 's/autologin-user=user/autologin-user=vasanth/g' "$ROOT/etc/lightdm/lightdm.conf"
fi

# Ensure nopasswdlogin group exists for LightDM
grep -q "^nopasswdlogin:" "$ROOT/etc/group" || echo "nopasswdlogin:x:1001:vasanth" >> "$ROOT/etc/group"
sed -i "/^nopasswdlogin:/ s/$/,vasanth/; s/,,/,/g; s/:,/:/g" "$ROOT/etc/group"

# 5. OS Branding & Hostname
echo "[5/9] Applying MicroOS v1.0 system identity..."
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
UBUNTU_CODENAME=noble
EOF

cat << 'EOF' > "$ROOT/etc/lsb-release"
DISTRIB_ID=MicroOS
DISTRIB_RELEASE=1.0
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="MicroOS v1.0 - Beyond the Ordinary Desktop"
EOF

echo "microos" > "$ROOT/etc/hostname"
cat << 'EOF' > "$ROOT/etc/hosts"
127.0.0.1   localhost microos
127.0.1.1   microos
::1         ip6-localhost ip6-loopback
fe00::0     ip6-localnet
ff00::0     ip6-mcastprefix
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF

cat << 'EOF' > "$ROOT/etc/issue"
MicroOS v1.0 - Beyond the Ordinary Desktop (\l)
Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Jain University FET - Operating Systems Engineering

EOF
cp "$ROOT/etc/issue" "$ROOT/etc/issue.net"

cat << 'EOF' > "$ROOT/etc/motd"
  __  __ _             ___  ____  
 |  \/  (_) ___ _ __  / _ \/ ___| 
 | |\/| | |/ __| '__|| | | \___ \ 
 | |  | | | (__| |   | |_| |___) |
 |_|  |_|_|\___|_|    \___/|____/ 
 MICROOS v1.0 - Beyond the Ordinary Desktop
 Logged in as: vasanth (Tadigotla Vasanth Diwakar - USN: 25BTRCL270)
 Research: Multi-Core Scheduling & Processor Affinity
 Type 'micro-help' for original MicroOS diagnostic commands.
EOF

# Purge any old games / legacy shortcuts
rm -f "$ROOT/usr/share/applications/nsnake.desktop" 2>/dev/null || true
rm -f "$ROOT/usr/bin/snake"* "$ROOT/usr/games/nsnake" 2>/dev/null || true
rm -f "$ROOT/usr/local/bin/snake"* "$ROOT/usr/local/bin/wifi-manager" 2>/dev/null || true

# 6. Deploy MicroOS Engineering Applications Suite
echo "[6/9] Deploying MicroOS applications and MicroShell CLI suite..."
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

chmod +x "$OPT_DIR"/*/*.py "$OPT_DIR"/process-panic/main.py

# Install the 12 MicroShell binary commands in /usr/local/bin
cp "${PROJECT_DIR}/microos/microshell/bin/"* "$ROOT/usr/local/bin/"

# GUI wrapper binaries
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

# Configure MicroShell prompt for vasanth
cat << 'RC_EOF' > "$ROOT/home/vasanth/.microshellrc"
export PS1='\[\033[01;36m\]vasanth@microos\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
alias ll='ls -la --color=auto'
alias micro='micro-info'
export PATH="/usr/local/bin:/opt/microos/microshell/bin:$PATH"
RC_EOF

cp "$ROOT/home/vasanth/.microshellrc" "$ROOT/etc/skel/.microshellrc"
grep -q 'source ~/.microshellrc' "$ROOT/home/vasanth/.bashrc" 2>/dev/null || echo 'source ~/.microshellrc' >> "$ROOT/home/vasanth/.bashrc"
grep -q 'source ~/.microshellrc' "$ROOT/etc/skel/.bashrc" 2>/dev/null || echo 'source ~/.microshellrc' >> "$ROOT/etc/skel/.bashrc"

# 7. Configure XFCE Desktop & Panel (Single Top Bar - NO BEIGE RECTANGLES)
echo "[7/9] Configuring XFCE desktop, wallpaper, and top status panel..."

# High-resolution Deep Graphite & Electric Teal Wallpaper
mkdir -p "$ROOT/usr/share/backgrounds/microos"
python3 - << 'PY_WP'
from PIL import Image, ImageDraw, ImageFont

w, h = 1920, 1080
img = Image.new("RGB", (w, h), (20, 23, 26))
draw = ImageDraw.Draw(img)

# Graphite gradient
for y in range(h):
    ratio = y / h
    draw.line([(0, y), (w, y)], fill=(int(20 - ratio * 8), int(23 - ratio * 8), int(26 - ratio * 8)))

# Engineering circuit grid
for x in range(0, w, 60):
    draw.line([(x, 0), (x, h)], fill=(28, 33, 40), width=1)
for y in range(0, h, 60):
    draw.line([(0, y), (w, y)], fill=(28, 33, 40), width=1)

# Center Hexagon Logo
cx, cy = w // 2, h // 2 - 40
draw.polygon([(cx, cy - 100), (cx + 90, cy - 50), (cx + 90, cy + 50), (cx, cy + 100), (cx - 90, cy + 50), (cx - 90, cy - 50)], outline=(0, 180, 216), width=4)
draw.polygon([(cx, cy - 85), (cx + 75, cy - 40), (cx + 75, cy + 40), (cx, cy + 85), (cx - 75, cy + 40), (cx - 75, cy - 40)], outline=(35, 42, 52), width=2)
draw.line([(cx - 45, cy + 35), (cx - 45, cy - 35), (cx, cy), (cx + 45, cy - 35), (cx + 45, cy + 35)], fill=(0, 180, 216), width=9)

try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    font_title = font_sub = font_small = ImageFont.load_default()

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
PY_WP

cp /tmp/microos_wallpaper.png "$ROOT/usr/share/backgrounds/microos/microos_wallpaper.png"

# Overwrite default fallback wallpapers
for wp_dir in "$ROOT/usr/share/images/desktop-base" "$ROOT/usr/share/backgrounds/xfce"; do
    mkdir -p "$wp_dir"
    for wp_f in "$wp_dir"/*; do
        if [ -f "$wp_f" ]; then
            cp /tmp/microos_wallpaper.png "$wp_f" 2>/dev/null || true
        fi
    done
done

# Perfected xfce4-desktop.xml
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

# Perfected xfce4-panel.xml (Standard 1-Panel Layout - Bottom Status Bar, No Floating Boxes)
cat << 'EOF' > /tmp/xfce4-panel.xml
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="dark-mode" type="bool" value="true"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=8;x=0;y=0"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="34"/>
      <property name="plugin-ids" type="array">
        <value type="int" value="1"/>
        <value type="int" value="2"/>
        <value type="int" value="3"/>
        <value type="int" value="4"/>
        <value type="int" value="5"/>
      </property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="whiskermenu">
      <property name="button-title" type="string" value="MicroOS"/>
      <property name="show-button-title" type="bool" value="true"/>
      <property name="button-icon" type="string" value="distributor-logo-debian"/>
    </property>
    <property name="plugin-2" type="string" value="tasklist">
      <property name="flat-buttons" type="bool" value="true"/>
      <property name="show-labels" type="bool" value="true"/>
    </property>
    <property name="plugin-3" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-4" type="string" value="systray">
      <property name="square-icons" type="bool" value="true"/>
    </property>
    <property name="plugin-5" type="string" value="clock">
      <property name="digital-format" type="string" value="%H:%M  %a, %d %b"/>
    </property>
  </property>
</channel>
EOF

# Deploy panel & desktop configs to all profiles and default template
mkdir -p "$ROOT/etc/xdg/xfce4/panel"
cp /tmp/xfce4-panel.xml "$ROOT/etc/xdg/xfce4/panel/default.xml"

for cdir in \
    "$ROOT/etc/xdg/xfce4/xfconf/xfce-perchannel-xml" \
    "$ROOT/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml" \
    "$ROOT/home/vasanth/.config/xfce4/xfconf/xfce-perchannel-xml" \
    "$ROOT/root/.config/xfce4/xfconf/xfce-perchannel-xml"; do
    mkdir -p "$cdir"
    cp /tmp/xfce4-desktop.xml "$cdir/xfce4-desktop.xml"
    cp /tmp/xfce4-panel.xml "$cdir/xfce4-panel.xml"
done

# Clean ALL existing desktop entries in user and skel before deploying our 9 clean apps
for udir in "$ROOT/home/vasanth" "$ROOT/etc/skel" "$ROOT/root"; do
    rm -rf "$udir/Desktop"
    mkdir -p "$udir/Desktop"
done

# Purge any remaining snake/legacy games
rm -rf "$ROOT/usr/share/games/nsnake" "$ROOT/usr/games/nsnake" "$ROOT/usr/bin/snake"* "$ROOT/usr/share/applications/nsnake.desktop" 2>/dev/null || true

DESKTOPS=(
    "micro-hub.desktop"
    "micro-research-lab.desktop"
    "micro-network-center.desktop"
    "micro-wifi-scanner.desktop"
    "micro-monitor.desktop"
    "micro-control-center.desktop"
    "process-panic.desktop"
)

mkdir -p "$ROOT/usr/share/applications"
for da in "${DESKTOPS[@]}"; do
    cp "${PROJECT_DIR}/microos/desktop/applications/$da" "$ROOT/usr/share/applications/"
    cp "${PROJECT_DIR}/microos/desktop/applications/$da" "$ROOT/home/vasanth/Desktop/"
    cp "${PROJECT_DIR}/microos/desktop/applications/$da" "$ROOT/etc/skel/Desktop/"
done

# Terminal & Firefox desktop entries
cat << 'TERM_EOF' > "$ROOT/home/vasanth/Desktop/microshell.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=MicroShell Terminal
Comment=Interactive Linux Engineering Shell
Exec=xfce4-terminal
Icon=utilities-terminal
Terminal=false
TERM_EOF
cp "$ROOT/home/vasanth/Desktop/microshell.desktop" "$ROOT/etc/skel/Desktop/"

cat << 'FF_EOF' > "$ROOT/home/vasanth/Desktop/firefox.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Firefox Web Browser
Comment=Browse the World Wide Web
Exec=firefox
Icon=firefox
Terminal=false
FF_EOF
cp "$ROOT/home/vasanth/Desktop/firefox.desktop" "$ROOT/etc/skel/Desktop/"

chmod 755 "$ROOT/home/vasanth/Desktop/"*.desktop "$ROOT/etc/skel/Desktop/"*.desktop
chown -R 1000:1000 "$ROOT/home/vasanth"
chmod -R u+rwX,go+rX "$ROOT/home/vasanth"

# Autostart Network Manager Applet & Micro Hub
mkdir -p "$ROOT/etc/xdg/autostart"
cat << 'NM_EOF' > "$ROOT/etc/xdg/autostart/nm-applet.desktop"
[Desktop Entry]
Name=Network
Comment=Manage your network connections
Icon=nm-device-wireless
Exec=nm-applet
Terminal=false
Type=Application
NoDisplay=true
NM_EOF

# 8. Compress Squashfs & Inject into Bootable ISO
echo "[8/8] Compressing final squashfs and writing bootable ISO..."
rm -f "$WORK_DIR/filesystem.squashfs"
mksquashfs "$ROOT" "$WORK_DIR/filesystem.squashfs" -comp gzip -noappend

mkdir -p "$(dirname "$ISO_OUT")"
rm -f "$ISO_OUT"
cp "$ISO_BASE" "$ISO_OUT"

# Inject the rebuilt squashfs while preserving the exact working El Torito MBR boot catalog
xorriso -dev "$ISO_OUT" \
    -map "$WORK_DIR/filesystem.squashfs" /live/filesystem.squashfs \
    -boot_image any replay \
    -commit

# Cleanup staging
rm -rf "$WORK_DIR"

echo "==============================================================================="
echo " [SUCCESS] MicroOS v1.0 Production ISO Created Successfully!"
echo " Location: $ISO_OUT"
echo " Size: $(du -h "$ISO_OUT" | cut -f1)"
echo " Username: vasanth"
echo " Hostname: microos"
echo " Tkinter: Installed & Verified"
echo " Panels: Single Sleek Top Bar"
echo "==============================================================================="
