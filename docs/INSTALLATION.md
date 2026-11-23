# MicroOS Installation & Deployment Guide

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Targets**: Oracle VirtualBox (Windows Host) & Ubuntu Build Environment

---

## 1. Quick Launch on Windows via VirtualBox

### Prerequisites:
1. Windows 10 or 11 (64-bit).
2. [Oracle VM VirtualBox](https://www.virtualbox.org/) (version 7.0 or newer).
3. 16 GB Host RAM (MicroOS VM is allocated 4 GB RAM and 2 CPU cores).

### Launch Steps:
1. Double-click `Start-MicroOS.bat` in the repository root.
2. The script will automatically:
   - Locate `VBoxManage.exe` in `C:\Program Files\Oracle\VirtualBox\`.
   - Verify the presence of `microos/build/microos.iso`.
   - Check if the VM `MicroOS-v1.0` is already registered. If not, it creates a new VM with:
     - 4096 MB RAM, 2 CPUs, 128 MB VMSVGA VRAM.
     - 20 GB dynamic VDI virtual disk.
     - SATA storage controller with `microos.iso` attached as a bootable live medium.
     - NAT networking with USB 3.0 (xHCI) enabled.
   - Power on the virtual machine.
3. MicroOS will boot into the LightDM login screen and automatically enter the XFCE desktop as user `microos`.

---

## 2. Compiling the Live ISO on Linux (Ubuntu 24.04 Host)

To compile a fresh live ISO image from source code:

```bash
# 1. Clone repository and navigate to build directory
git clone https://github.com/diwakar/microos.git
cd microos/microos

# 2. Execute automated build script with root privileges
sudo ./build.sh
```

### Build Output:
- The script bootstraps Ubuntu 24.04 LTS (noble), installs XFCE, LightDM, Firefox, NetworkManager, and the MicroOS tool suites, compresses the filesystem into `filesystem.squashfs`, and outputs the hybrid bootable ISO image to:
  `microos/build/microos.iso`
- A build report is recorded in `microos/build/build_report.txt`.

---

## 3. Installing to Virtual Disk (Persistent Installation)

Inside the running MicroOS live desktop:
1. Open terminal and partition the virtual disk (`/dev/sda`):
   ```bash
   sudo parted -s /dev/sda mklabel gpt mkpart primary ext4 1MiB 100%
   sudo mkfs.ext4 /dev/sda1
   ```
2. Mount and copy root files:
   ```bash
   sudo mount /dev/sda1 /mnt
   sudo rsync -aAXv --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} / /mnt
   ```
3. Install GRUB to virtual disk:
   ```bash
   sudo grub-install --target=i386-pc /dev/sda
   sudo update-grub
   ```
4. Eject the live ISO in VirtualBox and reboot directly from the virtual hard drive.
