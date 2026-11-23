# Educational Bare-Metal Kernel Lab

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Target Architecture**: x86 (IA-32 Protected Mode)  
**Location**: `kernel-lab/`

---

## 1. Educational Objectives

The Kernel Lab provides an educational, freestanding operating system kernel compiled directly to bare-metal machine code without the C standard library (`-ffreestanding -nostdlib`). It demonstrates:
1. Bootloader interface using the standard **Multiboot 1** specification (`0x1BADB002`).
2. Flat segmentation model via the **Global Descriptor Table (GDT)**.
3. Interrupt routing via the **Interrupt Descriptor Table (IDT)** and **8259 Programmable Interrupt Controller (PIC)**.
4. Direct video memory access via **VGA 80x25 text mode** (`0xB8000`).
5. Hardware device driver programming via **PS/2 Keyboard (IRQ1)** and I/O port manipulation (`inb` / `outb`).
6. Interactive kernel shell with basic system commands.

---

## 2. Kernel Memory Layout

```text
0x00000000 - 0x000003FF : Real Mode Interrupt Vector Table (IVT) - overridden
0x00000400 - 0x000004FF : BIOS Data Area (BDA)
0x000B8000 - 0x000B8FA0 : VGA Color Text Buffer (80 cols x 25 rows x 2 bytes)
0x00100000 (1 MB)       : Multiboot Header (.multiboot section)
0x00100020 +            : Kernel Executable Code (.text)
                         : Read-Only String Literals (.rodata)
                         : Initialized Global Data (.data)
                         : BSS & 16 KiB Kernel Stack (.bss)
```

---

## 3. Subsystem Implementation Details

### 3.1 Global Descriptor Table (GDT)
Three descriptor segments are established:
- **Null Descriptor (Index 0)**: Mandatory CPU fault boundary.
- **Kernel Code Segment (Index 1, Selector 0x08)**: Base `0x00000000`, Limit `0xFFFFFFFF`, Ring 0, Execute/Read.
- **Kernel Data Segment (Index 2, Selector 0x10)**: Base `0x00000000`, Limit `0xFFFFFFFF`, Ring 0, Read/Write.

### 3.2 Interrupt Descriptor Table (IDT) & 8259 PIC
The master and slave PICs are remapped from the default BIOS conflicts (vectors 0x08-0x0F) to vectors `0x20` (master) and `0x28` (slave).
- Vectors 0–31: CPU Hardware Exceptions (Division by Zero, General Protection Fault, Page Fault).
- Vector 32 (IRQ0): Programmable Interval Timer (PIT).
- Vector 33 (IRQ1): PS/2 Keyboard Controller.

### 3.3 VGA Text Driver
Characters are written as 16-bit word entries directly to `0xB8000`:
- High 8 bits: Attribute byte (foreground color `|` background color `<< 4`).
- Low 8 bits: ASCII character code.
The driver implements hardware cursor positioning via index register `0x3D4` and data register `0x3D5`.

### 3.4 Interactive Shell Commands
- `help`: Lists all available kernel commands.
- `version`: Displays kernel version and developer attribution.
- `cpu`: Invokes CPUID assembly instruction to extract processor vendor string.
- `clear`: Blanks the 80x25 VGA buffer and resets cursor to top-left.
- `panic`: Executes deliberate division by zero to verify CPU exception handler (ISR 0).
- `reboot`: Pulses the 8042 keyboard controller reset pin via port `0x64` (`0xFE`).
