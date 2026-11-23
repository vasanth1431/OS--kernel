# MicroOS Troubleshooting & Diagnostic Guide

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Scope**: VirtualBox VM runtime, networking, ISO build, and research module diagnostics

---

## 1. VirtualBox Virtual Machine Issues

### Symptom: `Start-MicroOS.bat` reports "Oracle VirtualBox was not detected"
- **Cause**: VirtualBox is not installed or installed in a non-standard directory.
- **Fix**: Install VirtualBox from [virtualbox.org](https://www.virtualbox.org/). If installed elsewhere, set the environment variable:
  ```cmd
  set "VBOX_MSI_INSTALL_PATH=D:\YourPath\VirtualBox\"
  ```

### Symptom: VM fails to boot with "VT-x/AMD-V is not available"
- **Cause**: Hardware virtualization is disabled in the Windows host BIOS/UEFI, or Windows Hyper-V is conflicting.
- **Fix**:
  1. Reboot into host BIOS and enable **Intel Virtualization Technology (Intel VT-x)** or **AMD-V (SVM Mode)**.
  2. If using Windows 11 with Core Isolation / Memory Integrity, ensure VirtualBox 7.0+ is used.

### Symptom: Screen resolution is small (1024x768) in VirtualBox
- **Fix**: Open Micro Control Center -> **Display**, or run:
  ```bash
  xrandr -s 1920x1080
  ```

---

## 2. Networking & Wi-Fi Issues

### Symptom: Internet is working in Firefox, but Micro Wi-Fi Scanner shows no networks
- **Cause**: By design, VirtualBox NAT mode emulates a virtual Ethernet cable (`enp0s3`). The guest VM cannot scan host physical Wi-Fi channels through virtual Ethernet.
- **Fix**: Plug a USB Wi-Fi adapter into your PC and attach it to the VM via `Devices -> USB` in the VirtualBox window.

### Symptom: DNS lookup fails ("Limited Connectivity")
- **Fix**: Run `micro-internet` to see which stage failed. If DNS is failing, reset `/etc/resolv.conf`:
  ```bash
  echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
  ```

---

## 3. ISO Build Issues on Linux Host

### Symptom: `build.sh` fails with "debootstrap: command not found"
- **Fix**: Install prerequisite packaging tools:
  ```bash
  sudo apt update && sudo apt install -y debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools
  ```

### Symptom: Build runs out of space
- **Fix**: The build system requires at least 15 GB free disk space for the chroot and squashfs image. Clean up old build caches with:
  ```bash
  sudo rm -rf microos/build/chroot microos/build/iso
  ```

---

## 4. Multi-Core Research Lab Issues

### Symptom: "Backend: python" instead of "Backend: rust"
- **Explanation**: This is normal when the optional Rust/C extension has not been compiled with `maturin` or `setuptools`. The pure-Python fallback produces identical mathematical scheduling behavior and measures true multi-core process concurrency.
- **Fix (Optional compilation)**:
  ```bash
  cd microos/research-lab
  python3 setup.py build_ext --inplace
  ```
