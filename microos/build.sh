#!/usr/bin/env bash
# ==============================================================================
# MicroOS v1.0 - Automated Reproducible Live ISO Build System
# Base: Ubuntu 24.04 LTS (Noble Numbat) x86_64
# Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
# Institution: Jain University, FET Campus - 25PCCS201 OS Activity
# Output: microos/build/microos.iso
# ==============================================================================

set -euo pipefail

# Visual ANSI Styling
C_RESET='\033[0m'
C_BOLD='\033[1m'
C_TEAL='\033[38;5;39m'
C_AMBER='\033[38;5;214m'
C_GREEN='\033[38;5;76m'
C_RED='\033[38;5;196m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
CHROOT_DIR="${BUILD_DIR}/chroot"
ISO_DIR="${BUILD_DIR}/iso"
LOG_FILE="${BUILD_DIR}/build.log"
REPORT_FILE="${BUILD_DIR}/build_report.txt"
TARGET_ISO="${BUILD_DIR}/microos.iso"

DISTRO_NAME="MicroOS"
DISTRO_VERSION="1.0"
UBUNTU_RELEASE="noble"
MIRROR_URL="http://archive.ubuntu.com/ubuntu/"

log() {
    echo -e "${C_BOLD}${C_TEAL}[MicroOS Build]${C_RESET} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

warn() {
    echo -e "${C_BOLD}${C_AMBER}[WARNING]${C_RESET} $1"
    echo "[WARNING] $1" >> "$LOG_FILE"
}

err() {
    echo -e "${C_BOLD}${C_RED}[ERROR]${C_RESET} $1" >&2
    echo "[ERROR] $1" >> "$LOG_FILE"
    exit 1
}

# ------------------------------------------------------------------------------
# STEP 0: Cleanup Trap to protect Host System
# ------------------------------------------------------------------------------
cleanup() {
    log "Executing build cleanup handler..."
    if [ -d "$CHROOT_DIR" ]; then
        for mp in dev/pts dev proc sys run; do
            if mountpoint -q "${CHROOT_DIR}/${mp}" 2>/dev/null; then
                umount -lf "${CHROOT_DIR}/${mp}" 2>/dev/null || true
            fi
        done
    fi
}
trap cleanup EXIT INT TERM

# ------------------------------------------------------------------------------
# STEP 1: Pre-flight Verification
# ------------------------------------------------------------------------------
mkdir -p "$BUILD_DIR"
: > "$LOG_FILE"

log "Starting MicroOS v1.0 ISO compilation pipeline..."

if [ "$EUID" -ne 0 ]; then
    err "This build script must be executed with root privileges. Run: sudo ./build.sh"
fi

# Check storage (require >= 15 GB free)
AVAILABLE_KB=$(df -k "$BUILD_DIR" | awk 'NR==2 {print $4}')
REQUIRED_KB=$((15 * 1024 * 1024))
if [ "$AVAILABLE_KB" -lt "$REQUIRED_KB" ]; then
    warn "Less than 15 GB free disk space detected. Build may fail if space runs out."
fi

# Check required host host utilities
REQUIRED_TOOLS=(debootstrap mksquashfs xorriso grub-mkrescue mtools)
MISSING_TOOLS=()
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &>/dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    log "Installing missing build dependencies on host: ${MISSING_TOOLS[*]}..."
    apt-get update -qq
    apt-get install -y -qq "${MISSING_TOOLS[@]}" debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools
fi

# ------------------------------------------------------------------------------
# STEP 2: Debootstrap Base System
# ------------------------------------------------------------------------------
if [ ! -f "${CHROOT_DIR}/bin/bash" ]; then
    log "Bootstrapping Ubuntu 24.04 LTS (${UBUNTU_RELEASE}) base image..."
    debootstrap --arch=amd64 --variant=minbase "$UBUNTU_RELEASE" "$CHROOT_DIR" "$MIRROR_URL" >> "$LOG_FILE" 2>&1
else
    log "Existing bootstrap found at ${CHROOT_DIR}. Reusing."
fi

# ------------------------------------------------------------------------------
# STEP 3: Mount Virtual Filesystems for Chroot Execution
# ------------------------------------------------------------------------------
log "Binding virtual kernel filesystems to chroot..."
mount --bind /dev "${CHROOT_DIR}/dev"
mount --bind /dev/pts "${CHROOT_DIR}/dev/pts"
mount -t proc proc "${CHROOT_DIR}/proc"
mount -t sysfs sysfs "${CHROOT_DIR}/sys"

# Configure Host DNS for chroot package downloads
cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"

# ------------------------------------------------------------------------------
# STEP 4: In-Chroot Provisioning Script
# ------------------------------------------------------------------------------
log "Configuring repositories, kernel, XFCE desktop, LightDM, and networking..."

cat << 'IN_CHROOT_EOF' > "${CHROOT_DIR}/tmp/provision.sh"
#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# Repositories
cat << 'REPOS_EOF' > /etc/apt/sources.list
deb http://archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse
REPOS_EOF

apt-get update -qq

# System Core & Hardened Kernel
apt-get install -y -qq \
    linux-image-generic \
    linux-headers-generic \
    linux-firmware \
    live-boot \
    systemd-sysv \
    sudo \
    curl \
    wget \
    git \
    nano \
    htop \
    pciutils \
    usbutils \
    rfkill \
    iw \
    wireless-tools \
    wpasupplicant \
    network-manager \
    iproute2 \
    net-tools \
    python3 \
    python3-tk \
    python3-pip \
    python3-matplotlib \
    build-essential

# Desktop & Display Manager
apt-get install -y -qq \
    xfce4 \
    xfce4-goodies \
    lightdm \
    lightdm-gtk-greeter \
    thunar \
    xfce4-terminal \
    firefox \
    pipewire \
    alsa-utils

# Create standard user 'microos'
if ! id "microos" &>/dev/null; then
    useradd -m -s /bin/bash -G sudo,netdev,audio,video microos
    echo "microos:microos" | chpasswd
    echo "root:microos" | chpasswd
fi

# Allow passwordless sudo for live session
echo "microos ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/microos
chmod 0440 /etc/sudoers.d/microos

# Set Hostname
echo "microos" > /etc/hostname
cat << 'HOSTS_EOF' > /etc/hosts
127.0.0.1   localhost
127.0.1.1   microos
HOSTS_EOF

# LightDM Autologin configuration
cat << 'LIGHTDM_EOF' > /etc/lightdm/lightdm.conf.d/80-microos.conf
[Seat:*]
autologin-user=microos
autologin-user-timeout=0
user-session=xfce
greeter-session=lightdm-gtk-greeter
LIGHTDM_EOF

# Clean APT caches
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
IN_CHROOT_EOF

chmod +x "${CHROOT_DIR}/tmp/provision.sh"
chroot "$CHROOT_DIR" /tmp/provision.sh >> "$LOG_FILE" 2>&1
rm -f "${CHROOT_DIR}/tmp/provision.sh"

# ------------------------------------------------------------------------------
# STEP 5: Deploy MicroOS Engineering Suite to Chroot
# ------------------------------------------------------------------------------
log "Deploying MicroOS engineering applications, MicroShell, and desktop profiles..."

OPT_DIR="${CHROOT_DIR}/opt/microos"
mkdir -p "$OPT_DIR"
cp -r "${SCRIPT_DIR}/microshell" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/network-center" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/wifi-scanner" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/system-monitor" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/control-center" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/application-hub" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/process-panic" "$OPT_DIR/"
cp -r "${SCRIPT_DIR}/research-lab" "$OPT_DIR/"

# Install executable symlinks to /usr/local/bin
mkdir -p "${CHROOT_DIR}/usr/local/bin"
cp "${SCRIPT_DIR}/microshell/bin/"* "${CHROOT_DIR}/usr/local/bin/"
chmod +x "${CHROOT_DIR}/usr/local/bin/"*

# Wrappers for GUI apps
cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/micro-network-center"
#!/bin/sh
exec python3 /opt/microos/network-center/network_center.py "$@"
EOF

cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/micro-wifi-scanner"
#!/bin/sh
exec python3 /opt/microos/wifi-scanner/wifi_scanner.py "$@"
EOF

cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/micro-monitor"
#!/bin/sh
exec python3 /opt/microos/system-monitor/system_monitor.py "$@"
EOF

cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/micro-control-center"
#!/bin/sh
exec python3 /opt/microos/control-center/control_center.py "$@"
EOF

cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/micro-hub"
#!/bin/sh
exec python3 /opt/microos/application-hub/application_hub.py "$@"
EOF

cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/process-panic"
#!/bin/sh
exec python3 /opt/microos/process-panic/main.py "$@"
EOF

cat << 'EOF' > "${CHROOT_DIR}/usr/local/bin/micro-research-lab"
#!/bin/sh
exec python3 /opt/microos/research-lab/gui.py "$@"
EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/"*

# Deploy MicroShell rc to user and skeleton
cp "${SCRIPT_DIR}/microshell/microshellrc" "${CHROOT_DIR}/etc/skel/.microshellrc"
cp "${SCRIPT_DIR}/microshell/microshellrc" "${CHROOT_DIR}/home/microos/.microshellrc"
echo 'source ~/.microshellrc' >> "${CHROOT_DIR}/etc/skel/.bashrc"
echo 'source ~/.microshellrc' >> "${CHROOT_DIR}/home/microos/.bashrc"

# Deploy .desktop launchers
mkdir -p "${CHROOT_DIR}/usr/share/applications"
mkdir -p "${CHROOT_DIR}/etc/skel/Desktop"
mkdir -p "${CHROOT_DIR}/home/microos/Desktop"

if [ -d "${SCRIPT_DIR}/desktop/applications" ]; then
    cp "${SCRIPT_DIR}/desktop/applications/"*.desktop "${CHROOT_DIR}/usr/share/applications/"
    cp "${SCRIPT_DIR}/desktop/applications/"*.desktop "${CHROOT_DIR}/etc/skel/Desktop/"
    cp "${SCRIPT_DIR}/desktop/applications/"*.desktop "${CHROOT_DIR}/home/microos/Desktop/"
    chmod +x "${CHROOT_DIR}/home/microos/Desktop/"*.desktop || true
fi

# Fix home permissions
chroot "$CHROOT_DIR" chown -R microos:microos /home/microos

# ------------------------------------------------------------------------------
# STEP 6: Unmount Virtual Filesystems Before Squashfs Compression
# ------------------------------------------------------------------------------
log "Unmounting chroot bindings..."
umount -lf "${CHROOT_DIR}/dev/pts" 2>/dev/null || true
umount -lf "${CHROOT_DIR}/dev" 2>/dev/null || true
umount -lf "${CHROOT_DIR}/proc" 2>/dev/null || true
umount -lf "${CHROOT_DIR}/sys" 2>/dev/null || true

# ------------------------------------------------------------------------------
# STEP 7: Build Live ISO Structure
# ------------------------------------------------------------------------------
log "Creating Live ISO filesystem layout..."
rm -rf "$ISO_DIR"
mkdir -p "${ISO_DIR}/live"
mkdir -p "${ISO_DIR}/boot/grub"

# Copy Kernel & Initrd to ISO boot directory
VMLINUZ=$(ls -1 "${CHROOT_DIR}/boot/vmlinuz-"* | sort -V | tail -n1)
INITRD=$(ls -1 "${CHROOT_DIR}/boot/initrd.img-"* | sort -V | tail -n1)

cp "$VMLINUZ" "${ISO_DIR}/live/vmlinuz"
cp "$INITRD" "${ISO_DIR}/live/initrd"

# Generate filesystem.squashfs
log "Compressing root filesystem into filesystem.squashfs (XZ compression)..."
rm -f "${ISO_DIR}/live/filesystem.squashfs"
mksquashfs "$CHROOT_DIR" "${ISO_DIR}/live/filesystem.squashfs" -comp xz -e boot >> "$LOG_FILE" 2>&1

# Create GRUB configuration for Live Boot
cat << 'GRUB_CFG_EOF' > "${ISO_DIR}/boot/grub/grub.cfg
set timeout=5
set default=0

insmod efi_gop
insmod font
if loadfont /boot/grub/fonts/unicode.pf2 ; then
    insmod gfxterm
    set gfxmode=auto
    set gfxpayload=keep
    terminal_output gfxterm
fi

menuentry "MicroOS v1.0 (Live Engineering Desktop - Asymmetric XFCE)" {
    linux /live/vmlinuz boot=live quiet splash ---
    initrd /live/initrd
}

menuentry "MicroOS v1.0 (Safe Graphics / Failsafe Mode)" {
    linux /live/vmlinuz boot=live nomodeset quiet splash ---
    initrd /live/initrd
}
GRUB_CFG_EOF

# ------------------------------------------------------------------------------
# STEP 8: Generate Hybrid Bootable ISO (BIOS + UEFI)
# ------------------------------------------------------------------------------
log "Generating hybrid bootable ISO image via grub-mkrescue / xorriso..."
rm -f "$TARGET_ISO"
grub-mkrescue -o "$TARGET_ISO" "$ISO_DIR" >> "$LOG_FILE" 2>&1

if [ ! -f "$TARGET_ISO" ]; then
    err "ISO generation failed. Review ${LOG_FILE} for diagnostic details."
fi

ISO_SIZE_BYTES=$(stat -c%s "$TARGET_ISO")
ISO_SIZE_MB=$((ISO_SIZE_BYTES / 1048576))
MD5_SUM=$(md5sum "$TARGET_ISO" | awk '{print $1}')

# ------------------------------------------------------------------------------
# STEP 9: Build Report Generation
# ------------------------------------------------------------------------------
cat << REPORT_EOF > "$REPORT_FILE"
===============================================================================
                       MICROOS v1.0 BUILD REPORT
===============================================================================
Distribution:         MicroOS 1.0 (Beyond the Ordinary Desktop)
Base System:          Ubuntu 24.04 LTS (Noble Numbat) x86_64
Developer:            Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
Institution:          Jain University, FET Campus - 25PCCS201 OS Activity
Build Timestamp:      $(date +'%Y-%m-%d %H:%M:%S %Z')
Output Target:        ${TARGET_ISO}
File Size:            ${ISO_SIZE_MB} MB (${ISO_SIZE_BYTES} bytes)
MD5 Checksum:         ${MD5_SUM}

Included Components:
  - Kernel:           Linux 6.8 LTS (generic x86_64)
  - Desktop:          XFCE 4.18 with Asymmetric Engineering Layout
  - Display Manager:  LightDM with custom Graphite/Teal Greeter
  - Terminal Suite:   MicroShell with 12 micro-* diagnostic utilities
  - Networking:       NetworkManager, Wi-Fi Scanner, VirtualBox USB passthrough
  - Research Lab:     Multi-Core Scheduling (Affinity & Workload Distribution)
  - OS Game:          Process Panic
  - Browser:          Mozilla Firefox
===============================================================================
REPORT_EOF

log "Build completed successfully!"
echo -e "${C_BOLD}${C_GREEN}===============================================================================${C_RESET}"
echo -e "${C_BOLD}${C_GREEN} [SUCCESS] MicroOS Live ISO generated: ${TARGET_ISO}${C_RESET}"
echo -e " ISO Size: ${ISO_SIZE_MB} MB | MD5: ${MD5_SUM}"
echo -e " Report saved to: ${REPORT_FILE}"
echo -e "${C_BOLD}${C_GREEN}===============================================================================${C_RESET}"
