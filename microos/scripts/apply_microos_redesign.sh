#!/usr/bin/env bash
# ==============================================================================
# Master MicroOS v1.0 ISO Remastering Engine
# Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
# Replaces old generic desktop with original MicroOS identity, layout & apps
# ==============================================================================

set -euo pipefail

ISO_SRC="/mnt/c/Users/diwak/OneDrive/Documents/os kernel/micro-os/build/micro-os.iso"
PROJECT_DIR="/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel"
ISO_OUT="${PROJECT_DIR}/microos/build/microos.iso"
WORK_DIR="/tmp/microos_remaster"

echo "==============================================================================="
echo "        MICROOS v1.0 - REMASTERING ENGINE & DESKTOP REDESIGN"
echo "        Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)"
echo "==============================================================================="

# 1. Clean workspace
echo "[1/7] Cleaning temporary build staging..."
umount -lf "$WORK_DIR/iso_mnt" 2>/dev/null || true
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/iso_mnt" "$WORK_DIR/squashfs_root"

# 2. Extract base ISO squashfs
echo "[2/7] Mounting base ISO and extracting root filesystem..."
mount -o loop,ro "$ISO_SRC" "$WORK_DIR/iso_mnt"
unsquashfs -f -d "$WORK_DIR/squashfs_root" "$WORK_DIR/iso_mnt/live/filesystem.squashfs"
umount "$WORK_DIR/iso_mnt"
echo "[OK] Root filesystem extracted."

ROOT="$WORK_DIR/squashfs_root"

# 3. Purge OLD/legacy files (Snake Game, old dashboards, fake hardcoded wifi)
echo "[3/7] Purging old/copied legacy desktop entries and scripts..."
for user_dir in "$ROOT/etc/skel" "$ROOT/root" "$ROOT/home"/*; do
    if [ -d "$user_dir/Desktop" ]; then
        echo " Cleaning old shortcuts in $user_dir/Desktop..."
        rm -f "$user_dir/Desktop/"*snake* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*Snake* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*producer* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*Producer* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*boot-time* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*Boot* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*wifi* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*WiFi* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*dashboard* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*Dashboard* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*Kernel* 2>/dev/null || true
        rm -f "$user_dir/Desktop/"*.desktop 2>/dev/null || true
    fi
done

# Remove old binary scripts
rm -f "$ROOT/usr/local/bin/snake"* "$ROOT/usr/local/bin/wifi-manager" 2>/dev/null || true

# 4. Deploy NEW Original MicroOS Application Suite
echo "[4/7] Deploying new MicroOS engineering applications..."
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

# Install the 12 MicroShell binary commands
cp "${PROJECT_DIR}/microos/microshell/bin/"* "$ROOT/usr/local/bin/"
chmod +x "$ROOT/usr/local/bin/"*

# Install GUI application wrappers in /usr/local/bin
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

# 5. Deploy New Original Desktop Shortcuts (.desktop)
echo "[5/7] Installing new desktop launchers and visual identity..."
mkdir -p "$ROOT/usr/share/applications"

# Copy new .desktop entries to /usr/share/applications and all user Desktops
DESKTOPS=(
    "micro-hub.desktop"
    "micro-research-lab.desktop"
    "micro-network-center.desktop"
    "micro-wifi-scanner.desktop"
    "micro-monitor.desktop"
    "micro-control-center.desktop"
    "process-panic.desktop"
)

for dfile in "${DESKTOPS[@]}"; do
    if [ -f "${PROJECT_DIR}/microos/desktop/applications/$dfile" ]; then
        cp "${PROJECT_DIR}/microos/desktop/applications/$dfile" "$ROOT/usr/share/applications/"
        for user_dir in "$ROOT/etc/skel" "$ROOT/root" "$ROOT/home"/*; do
            if [ -d "$user_dir" ]; then
                mkdir -p "$user_dir/Desktop"
                cp "${PROJECT_DIR}/microos/desktop/applications/$dfile" "$user_dir/Desktop/"
                chmod +x "$user_dir/Desktop/$dfile"
            fi
        done
    fi
done

# Also ensure Terminal and Firefox shortcuts exist on Desktop
for user_dir in "$ROOT/etc/skel" "$ROOT/root" "$ROOT/home"/*; do
    if [ -d "$user_dir" ]; then
        # Terminal shortcut
        cat << 'TERM_EOF' > "$user_dir/Desktop/microshell.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=MicroShell Terminal
Comment=Interactive Linux Engineering Shell
Exec=xfce4-terminal
Icon=utilities-terminal
Terminal=false
TERM_EOF
        # Firefox shortcut
        cat << 'FF_EOF' > "$user_dir/Desktop/firefox.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Firefox Web Browser
Comment=Browse the World Wide Web
Exec=firefox
Icon=firefox
Terminal=false
FF_EOF
        chmod +x "$user_dir/Desktop/"*.desktop
    fi
done

# Install MicroShell prompt config
cp "${PROJECT_DIR}/microos/microshell/microshellrc" "$ROOT/etc/skel/.microshellrc"
echo 'source ~/.microshellrc' >> "$ROOT/etc/skel/.bashrc"
for user_dir in "$ROOT/root" "$ROOT/home"/*; do
    if [ -d "$user_dir" ]; then
        cp "${PROJECT_DIR}/microos/microshell/microshellrc" "$user_dir/.microshellrc"
        grep -q 'source ~/.microshellrc' "$user_dir/.bashrc" 2>/dev/null || echo 'source ~/.microshellrc' >> "$user_dir/.bashrc"
    fi
done

# Install Deep Graphite & Teal Wallpaper
echo " Generating custom Deep Graphite & Teal wallpaper..."
mkdir -p "$ROOT/usr/share/backgrounds/microos"
apt-get install -y -qq python3-pil 2>/dev/null || true
python3 - << 'PY_WP' || true
try:
    from PIL import Image, ImageDraw, ImageFont
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (20, 23, 26))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        ratio = y / h
        r = int(20 - ratio * 8)
        g = int(23 - ratio * 8)
        b = int(26 - ratio * 8)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(30, 36, 44), width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(30, 36, 44), width=1)

    cx, cy = w // 2, h // 2 - 40
    draw.polygon([(cx, cy - 90), (cx + 80, cy - 45), (cx + 80, cy + 45), (cx, cy + 90), (cx - 80, cy + 45), (cx - 80, cy - 45)], outline=(0, 180, 216), width=3)
    draw.polygon([(cx, cy - 75), (cx + 65, cy - 35), (cx + 65, cy + 35), (cx, cy + 75), (cx - 65, cy + 35), (cx - 65, cy - 35)], outline=(35, 42, 52), width=2)
    draw.line([(cx - 40, cy + 30), (cx - 40, cy - 30), (cx, cy), (cx + 40, cy - 30), (cx + 40, cy + 30)], fill=(0, 180, 216), width=8)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_small = font_title

    t1 = "MICROOS"
    bbox = draw.textbbox((0,0), t1, font=font_title)
    draw.text((cx - (bbox[2]-bbox[0])//2, cy + 120), t1, fill=(224, 230, 237), font=font_title)

    t2 = "BEYOND THE ORDINARY DESKTOP"
    bbox2 = draw.textbbox((0,0), t2, font=font_sub)
    draw.text((cx - (bbox2[2]-bbox2[0])//2, cy + 185), t2, fill=(0, 180, 216), font=font_sub)

    t3 = "Tadigotla Vasanth Diwakar  |  USN: 25BTRCL270  |  Jain University FET"
    bbox3 = draw.textbbox((0,0), t3, font=font_small)
    draw.text((cx - (bbox3[2]-bbox3[0])//2, h - 60), t3, fill=(136, 146, 176), font=font_small)

    img.save("/tmp/microos_wallpaper.png")
    print("Wallpaper rendered successfully.")
except Exception as e:
    print(f"PIL fallback: {e}")
PY_WP

if [ -f /tmp/microos_wallpaper.png ]; then
    cp /tmp/microos_wallpaper.png "$ROOT/usr/share/backgrounds/microos/microos_wallpaper.png"
    for wp_dest in "$ROOT/usr/share/images/desktop-base/"* "$ROOT/usr/share/backgrounds/xfce/"*; do
        if [ -f "$wp_dest" ]; then
            cp /tmp/microos_wallpaper.png "$wp_dest" 2>/dev/null || true
        fi
    done
fi

# 6. Repack Squashfs
echo "[6/7] Repacking compressed squashfs image (gzip)..."
rm -f "$WORK_DIR/filesystem.squashfs"
mksquashfs "$ROOT" "$WORK_DIR/filesystem.squashfs" -comp gzip -noappend

# 7. Remaster ISO with xorriso
echo "[7/7] Rebuilding bootable hybrid ISO image..."
mkdir -p "$(dirname "$ISO_OUT")"
cp "$ISO_SRC" "$ISO_OUT"
xorriso -dev "$ISO_OUT" \
    -map "$WORK_DIR/filesystem.squashfs" /live/filesystem.squashfs \
    -boot_image any replay \
    -commit

# Cleanup
rm -rf "$WORK_DIR"
echo "==============================================================================="
echo " [SUCCESS] Remastering complete! New MicroOS ISO generated at:"
echo "   $ISO_OUT"
echo "==============================================================================="
