#!/bin/bash
set -e
WORK_DIR="/tmp/microos_check"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/iso" "$WORK_DIR/sq"
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" "$WORK_DIR/iso"
unsquashfs -f -d "$WORK_DIR/sq" "$WORK_DIR/iso/live/filesystem.squashfs" "home/user/.config/xfce4/*" "etc/skel/.config/xfce4/*" "etc/lightdm/*" "etc/os-release" "etc/hostname"
echo "=== os-release ==="
cat "$WORK_DIR/sq/etc/os-release" || true
echo "=== hostname ==="
cat "$WORK_DIR/sq/etc/hostname" || true
echo "=== home/user config ==="
ls -laR "$WORK_DIR/sq/home/user/.config" || true
if [ -f "$WORK_DIR/sq/home/user/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml" ]; then
    echo "=== panel.xml ==="
    cat "$WORK_DIR/sq/home/user/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml"
fi
umount "$WORK_DIR/iso"
rm -rf "$WORK_DIR"
