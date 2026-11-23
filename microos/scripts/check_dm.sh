#!/bin/bash
set -e
umount -lf /tmp/check_iso 2>/dev/null || true
mkdir -p /tmp/check_iso
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/os kernel/micro-os/build/micro-os.iso" /tmp/check_iso
unsquashfs -cat /tmp/check_iso/live/filesystem.squashfs etc/passwd | grep -E "user|vasanth"
unsquashfs -cat /tmp/check_iso/live/filesystem.squashfs etc/group | grep "nopasswdlogin" || true
unsquashfs -cat /tmp/check_iso/live/filesystem.squashfs etc/shadow | grep -E "user|vasanth"
unsquashfs -cat /tmp/check_iso/live/filesystem.squashfs etc/lightdm/lightdm.conf | grep -v "^#" | grep -v "^$" || true
umount /tmp/check_iso
