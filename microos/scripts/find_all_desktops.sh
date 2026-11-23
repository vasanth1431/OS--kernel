#!/bin/bash
set -e
umount -lf /tmp/check_iso 2>/dev/null || true
mkdir -p /tmp/check_iso
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" /tmp/check_iso
unsquashfs -l /tmp/check_iso/live/filesystem.squashfs | grep -i "Desktop/" || true
echo "=== Searching for Snake ==="
unsquashfs -l /tmp/check_iso/live/filesystem.squashfs | grep -i "snake" || true
echo "=== Searching for Producer ==="
unsquashfs -l /tmp/check_iso/live/filesystem.squashfs | grep -i "producer" || true
echo "=== /etc/passwd ==="
unsquashfs -cat /tmp/check_iso/live/filesystem.squashfs etc/passwd | grep -E "user|vasanth" || true
umount /tmp/check_iso
