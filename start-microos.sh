#!/usr/bin/env bash
# ==============================================================================
# MicroOS v1.0 - Linux VirtualBox Launcher
# Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_NAME="MicroOS-v1.0"
RAM_MB=4096
CPUS=2
VRAM_MB=128
DISK_SIZE_MB=20480
ISO_PATH="${SCRIPT_DIR}/microos/build/microos.iso"

echo "==============================================================================="
echo "               MICROOS v1.0 - LINUX VIRTUALBOX LAUNCHER"
echo "==============================================================================="

if ! command -v VBoxManage &>/dev/null; then
    echo "[ERROR] VBoxManage not found. Please install VirtualBox on your host:"
    echo "  sudo apt update && sudo apt install virtualbox"
    exit 1
fi

if [[ ! -f "$ISO_PATH" ]]; then
    if [[ -f "${SCRIPT_DIR}/microos.iso" ]]; then
        ISO_PATH="${SCRIPT_DIR}/microos.iso"
    else
        echo "[ERROR] ISO file not found at: $ISO_PATH"
        echo "Build the ISO first with: cd microos && sudo ./build.sh"
        exit 1
    fi
fi

echo "[OK] Found ISO: $ISO_PATH"

if VBoxManage showvminfo "$VM_NAME" &>/dev/null; then
    echo "[INFO] VM '$VM_NAME' already registered."
else
    echo "[SETUP] Creating VM '$VM_NAME'..."
    VBoxManage createvm --name "$VM_NAME" --ostype "Ubuntu_64" --register
    VBoxManage modifyvm "$VM_NAME" --memory "$RAM_MB" --cpus "$CPUS" --vram "$VRAM_MB"
    VBoxManage modifyvm "$VM_NAME" --graphicscontroller vmsvga --accelerate3d off
    VBoxManage modifyvm "$VM_NAME" --boot1 dvd --boot2 disk --boot3 none --boot4 none
    VBoxManage modifyvm "$VM_NAME" --nic1 nat
    VBoxManage modifyvm "$VM_NAME" --usb-xhci on
    VBoxManage modifyvm "$VM_NAME" --clipboard-mode bidirectional --drag-and-drop bidirectional

    VM_FOLDER="$(VBoxManage list systemproperties | awk -F': +' '/Default machine folder/{print $2}')/${VM_NAME}"
    mkdir -p "$VM_FOLDER"
    VDI_PATH="${VM_FOLDER}/${VM_NAME}.vdi"

    VBoxManage storagectl "$VM_NAME" --name "SATA Controller" --add sata --controller IntelAhci --bootable on
    if [[ ! -f "$VDI_PATH" ]]; then
        VBoxManage createmedium disk --filename "$VDI_PATH" --size "$DISK_SIZE_MB" --format VDI
    fi
    VBoxManage storageattach "$VM_NAME" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "$VDI_PATH"
    VBoxManage storageattach "$VM_NAME" --storagectl "SATA Controller" --port 1 --device 0 --type dvddrive --medium "$ISO_PATH"
    echo "[OK] VM configured."
fi

echo "Attaching optical ISO medium..."
VBoxManage storageattach "$VM_NAME" --storagectl "SATA Controller" --port 1 --device 0 --type dvddrive --medium "$ISO_PATH" || true

echo "Starting MicroOS Virtual Machine..."
VBoxManage startvm "$VM_NAME"
echo "[SUCCESS] VirtualBox VM '$VM_NAME' initiated."
