#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel"
ISO_PATH="${PROJECT_DIR}/microos/build/microos.iso"
WORK_DIR="/tmp/microos_fast_update"

echo "=== Fast Updating MicroOS ISO with Wi-Fi Scanner Engine ==="

# 1. Clean previous workdir
umount -lf "$WORK_DIR/iso_mnt" 2>/dev/null || true
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/iso_mnt" "$WORK_DIR/rootfs"

# 2. Extract squashfs from existing ISO
echo "[1/4] Extracting filesystem.squashfs from microos.iso..."
mount -o loop,ro "$ISO_PATH" "$WORK_DIR/iso_mnt"
unsquashfs -f -d "$WORK_DIR/rootfs" "$WORK_DIR/iso_mnt/live/filesystem.squashfs"
umount "$WORK_DIR/iso_mnt"

# 3. Copy updated Wi-Fi scanner and micro-wifi files
echo "[2/4] Injecting updated Wi-Fi Scanner and MicroShell tools..."
cp "${PROJECT_DIR}/microos/wifi-scanner/wifi_scanner.py" "$WORK_DIR/rootfs/opt/microos/wifi-scanner/wifi_scanner.py"
cp "${PROJECT_DIR}/microos/microshell/bin/micro-wifi" "$WORK_DIR/rootfs/opt/microos/microshell/bin/micro-wifi"
cp "${PROJECT_DIR}/microos/microshell/bin/micro-wifi" "$WORK_DIR/rootfs/usr/local/bin/micro-wifi"

chmod +x "$WORK_DIR/rootfs/opt/microos/wifi-scanner/wifi_scanner.py"
chmod +x "$WORK_DIR/rootfs/opt/microos/microshell/bin/micro-wifi"
chmod +x "$WORK_DIR/rootfs/usr/local/bin/micro-wifi"

# 4. Pack squashfs
echo "[3/4] Compressing updated squashfs..."
rm -f "$WORK_DIR/filesystem.squashfs"
mksquashfs "$WORK_DIR/rootfs" "$WORK_DIR/filesystem.squashfs" -comp gzip -noappend

# 5. Inject into ISO with xorriso preserving El Torito MBR catalog
echo "[4/4] Writing bootable microos.iso with xorriso..."
xorriso -dev "$ISO_PATH" \
    -map "$WORK_DIR/filesystem.squashfs" /live/filesystem.squashfs \
    -boot_image any replay \
    -commit

# Clean temp workdir
rm -rf "$WORK_DIR"

echo "=== [SUCCESS] MicroOS ISO updated in ~30 seconds! ==="
