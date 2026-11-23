#!/bin/bash
set -e
mkdir -p /tmp/check_iso
mount -o loop,ro "/mnt/c/Users/diwak/OneDrive/Documents/micro os kernel/microos/build/microos.iso" /tmp/check_iso
echo "=== ISOLINUX CFG FILES ==="
ls -la /tmp/check_iso/isolinux/
cat /tmp/check_iso/isolinux/isolinux.cfg || true
for f in /tmp/check_iso/isolinux/*.cfg; do
    echo "--- $f ---"
    cat "$f"
done
umount /tmp/check_iso
