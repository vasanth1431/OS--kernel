#!/bin/bash
set -e
mkdir -p /tmp/check_iso /tmp/check_sq
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" /tmp/check_iso
unsquashfs -l /tmp/check_iso/live/filesystem.squashfs > /tmp/squashfs_files.txt
echo "=== Number of files ==="
wc -l /tmp/squashfs_files.txt
echo "=== Searching for snake, producer, desktop ==="
grep -i "snake" /tmp/squashfs_files.txt || echo "No snake found in file names"
grep -i "producer" /tmp/squashfs_files.txt || echo "No producer found in file names"
grep -i "desktop" /tmp/squashfs_files.txt | grep -E "home|skel|root|Desktop" | head -n 30 || true
echo "=== /etc/skel /home /root contents ==="
grep -E "squashfs-root/(etc/skel|root|home)" /tmp/squashfs_files.txt | head -n 30 || true
umount /tmp/check_iso
