#!/bin/bash
set -e
mkdir -p /tmp/check_iso
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" /tmp/check_iso
echo "=== ISO ROOT ==="
ls -la /tmp/check_iso
echo "=== LIVE DIR ==="
ls -lh /tmp/check_iso/live
umount /tmp/check_iso
