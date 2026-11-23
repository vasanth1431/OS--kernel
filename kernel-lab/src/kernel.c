/*
 * MicroOS Freestanding Educational Bare-Metal Kernel
 * Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
 * Course: 25PCCS201 Operating Systems Research Activity
 */

#include "vga.h"
#include "gdt.h"
#include "idt.h"
#include "keyboard.h"
#include "shell.h"

void kmain(uint32_t magic, uint32_t addr) {
    (void)addr;

    vga_init();

    // Verify multiboot magic
    if (magic != 0x2BADB002) {
        vga_set_color(VGA_COLOR_LIGHT_RED, VGA_COLOR_BLACK);
        vga_puts("[BOOT WARNING] Invalid Multiboot Magic Number: ");
        vga_print_hex(magic);
        vga_putc('\n');
    }

    vga_set_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK);
    vga_puts("===============================================================================\n");
    vga_puts("               MICROOS EDUCATIONAL BARE-METAL KERNEL v0.1                     \n");
    vga_puts("          Developer: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)               \n");
    vga_puts("===============================================================================\n\n");

    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
    vga_puts("[1/4] Initializing Global Descriptor Table (GDT)... ");
    gdt_init();
    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("[OK]\n");

    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
    vga_puts("[2/4] Initializing Interrupt Descriptor Table (IDT) & PIC... ");
    idt_init();
    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("[OK]\n");

    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
    vga_puts("[3/4] Registering PS/2 Keyboard Driver (IRQ1)... ");
    keyboard_init();
    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("[OK]\n");

    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
    vga_puts("[4/4] Enabling Hardware Interrupts (STI)... ");
    __asm__ volatile ("sti");
    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("[OK]\n\n");

    shell_init();

    // Idle halt loop
    for (;;) {
        __asm__ volatile ("hlt");
    }
}
