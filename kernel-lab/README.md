# Educational Bare-Metal Kernel Lab

**Developer**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Course**: 25PCCS201 Operating Systems Research Activity  
**Institution**: Faculty of Engineering & Technology, Jain (Deemed-to-be University)

---

## 🔬 Conceptual Architecture & Fundamental Distinctions

It is essential in Operating Systems engineering to clearly distinguish between three layers that are frequently confused:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        1. LINUX DISTRIBUTION                          │
│  (e.g., MicroOS v1.0, Ubuntu 24.04 LTS, Debian, Fedora, Arch)          │
│  Complete OS packaging: Desktop Environment (XFCE), Display Manager    │
│  (LightDM), System Utilities (systemd, NetworkManager), Package Mgr    │
│  (APT), Compilers, MicroShell, Firefox, and User Applications.         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                          2. LINUX KERNEL                               │
│  (e.g., Linux 6.8.0-generic x86_64)                                    │
│  Monolithic production kernel managing hardware drivers, virtual       │
│  memory paging, multi-core CFS/EEVDF scheduling, POSIX system calls,   │
│  network stack (TCP/IP), and security domains.                         │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                   3. EDUCATIONAL BARE-METAL KERNEL                     │
│  (This module: kernel-lab/micro-kernel.bin)                            │
│  Freestanding x86 kernel compiled without standard libraries           │
│  (-ffreestanding -nostdlib). Boots directly on raw hardware or QEMU/   │
│  VirtualBox via Multiboot. Implements GDT, IDT, PIC, VGA, and PS/2.    │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Scientific Integrity Notice**:
> MicroOS (the Linux distribution) utilizes the hardened, production-grade Linux kernel (`v6.8 LTS`) to guarantee reliable VirtualBox virtualization, hardware acceleration, and Wi-Fi stack integration.  
> This `kernel-lab/` experiment is an independent educational module demonstrating low-level kernel development from scratch. We do not falsely claim that a customized Linux distribution replaces the core Linux kernel.

---

## 🛠 Features Implemented in the Bare-Metal Kernel

1. **Multiboot 1 Specification Header (`boot.s`)**:
   - Conforms to standard bootloader protocols (GRUB / QEMU `-kernel`).
   - Sets up a 16 KiB initial kernel stack and executes 32-bit protected mode.

2. **VGA 80x25 Text Mode Driver (`vga.c`, `vga.h`)**:
   - Memory-mapped I/O at physical address `0xB8000`.
   - Supports foreground/background colors, automatic newline handling, screen scrolling, and hardware cursor positioning via I/O ports `0x3D4` and `0x3D5`.

3. **Global Descriptor Table (`gdt.c`, `gdt.h`)**:
   - Flushes bootloader GDT and establishes a flat memory model:
     - Selector `0x08`: Kernel Code Segment (Base=0, Limit=4GB, Ring 0, Execute/Read).
     - Selector `0x10`: Kernel Data Segment (Base=0, Limit=4GB, Ring 0, Read/Write).

4. **Interrupt Descriptor Table & 8259 PIC Remap (`idt.c`, `pic.c`, `interrupts.s`)**:
   - Remaps master PIC to vector offset `0x20` (IRQ 0–7) and slave PIC to `0x28` (IRQ 8–15).
   - Installs assembly ISR gates for CPU exceptions (0–31) and hardware interrupts.

5. **PS/2 Keyboard Driver (`keyboard.c`)**:
   - Listens on IRQ1 (Vector `33`). Reads hardware scancodes from port `0x60` and translates them into ASCII characters via US-QWERTY mapping.

6. **Interactive Kernel Shell (`shell.c`)**:
   - Built-in command interpreter executing commands: `help`, `version`, `clear`, `cpu` (CPUID query), `panic` (division-by-zero exception test), and `reboot` (8042 controller pulse).

---

## 🚀 Building and Running the Bare-Metal Kernel

### Prerequisites (Ubuntu / Debian):
```bash
sudo apt update
sudo apt install build-essential gcc-multilib qemu-system-x86
```

### Compilation:
```bash
cd kernel-lab
make clean
make
```

### Emulation in QEMU:
```bash
qemu-system-i386 -kernel micro-kernel.bin
```

### Direct VirtualBox Boot:
To boot inside VirtualBox, create an ISO image using `grub-mkrescue`:
```bash
mkdir -p isodir/boot/grub
cp micro-kernel.bin isodir/boot/
cat << 'EOF' > isodir/boot/grub/grub.cfg
set timeout=0
set default=0
menuentry "MicroOS Bare-Metal Kernel" {
    multiboot /boot/micro-kernel.bin
    boot
}
EOF
grub-mkrescue -o kernel-lab.iso isodir
```
Attach `kernel-lab.iso` to a new 32-bit Other/Unknown VM in VirtualBox.
