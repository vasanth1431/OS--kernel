#!/bin/bash
set -e
umount -lf /tmp/check_iso 2>/dev/null || true
mkdir -p /tmp/check_iso
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" /tmp/check_iso
echo "=== XFCE Panel Plugins in squashfs ==="
unsquashfs -l /tmp/check_iso/live/filesystem.squashfs | grep "panel/plugins" || true
echo "=== Default XFCE Panel Configs ==="
unsquashfs -l /tmp/check_iso/live/filesystem.squashfs | grep "xfce4-panel.xml" || true
umount /tmp/check_iso
