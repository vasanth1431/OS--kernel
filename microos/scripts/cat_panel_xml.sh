#!/bin/bash
set -e
umount -lf /tmp/check_iso 2>/dev/null || true
mkdir -p /tmp/check_iso
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" /tmp/check_iso
unsquashfs -cat /tmp/check_iso/live/filesystem.squashfs etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
umount /tmp/check_iso
