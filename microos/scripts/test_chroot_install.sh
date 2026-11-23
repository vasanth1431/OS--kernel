#!/bin/bash
set -e

WORK_DIR="/tmp/test_chroot"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/iso" "$WORK_DIR/sq"
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" "$WORK_DIR/iso"
unsquashfs -f -d "$WORK_DIR/sq" "$WORK_DIR/iso/live/filesystem.squashfs"
umount "$WORK_DIR/iso"

ROOT="$WORK_DIR/sq"
echo "=== Testing network inside chroot ==="
cp /etc/resolv.conf "$ROOT/etc/resolv.conf"
mount -t proc /proc "$ROOT/proc"
mount -t sysfs /sys "$ROOT/sys"
mount --bind /dev "$ROOT/dev"
mount --bind /dev/pts "$ROOT/dev/pts"

echo "Running apt-get update inside chroot..."
chroot "$ROOT" apt-get update || true
echo "Attempting to install python3-tk..."
chroot "$ROOT" apt-get install -y python3-tk python3-pil || true

echo "Checking if python3 -c 'import tkinter' works:"
chroot "$ROOT" python3 -c "import tkinter; print('TKINTER_SUCCESS')" || true

umount "$ROOT/dev/pts" || true
umount "$ROOT/dev" || true
umount "$ROOT/sys" || true
umount "$ROOT/proc" || true
rm -rf "$WORK_DIR"
