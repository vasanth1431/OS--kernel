#include "shell.h"
#include "vga.h"
#include "io.h"

#define CMD_BUFFER_SIZE 128
static char cmd_buf[CMD_BUFFER_SIZE];
static int cmd_len = 0;

static int strcmp(const char* s1, const char* s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

void shell_print_prompt(void) {
    vga_set_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK);
    vga_puts("micro-kernel");
    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
    vga_puts("> ");
    vga_set_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK);
}

void shell_init(void) {
    cmd_len = 0;
    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("MicroOS Bare-Metal Kernel Shell Initialized.\n");
    vga_puts("Type 'help' to view available kernel diagnostic commands.\n\n");
    shell_print_prompt();
}

static void execute_command(void) {
    vga_putc('\n');

    if (cmd_len == 0) {
        shell_print_prompt();
        return;
    }

    if (strcmp(cmd_buf, "help") == 0) {
        vga_set_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK);
        vga_puts("Available Bare-Metal Kernel Commands:\n");
        vga_puts("  help     - Display this command index\n");
        vga_puts("  version  - Show kernel architecture and author\n");
        vga_puts("  clear    - Clear VGA display buffer\n");
        vga_puts("  cpu      - Read CPUID vendor string\n");
        vga_puts("  panic    - Trigger deliberate test kernel panic\n");
        vga_puts("  reboot   - Soft reboot machine via 8042 keyboard controller\n");
    } else if (strcmp(cmd_buf, "version") == 0) {
        vga_set_color(VGA_COLOR_LIGHT_BROWN, VGA_COLOR_BLACK);
        vga_puts("MicroOS Freestanding Educational Kernel v0.1-alpha (x86)\n");
        vga_puts("Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)\n");
        vga_puts("Jain University, FET Campus - 25PCCS201 OS Activity\n");
    } else if (strcmp(cmd_buf, "clear") == 0) {
        vga_clear();
    } else if (strcmp(cmd_buf, "cpu") == 0) {
        uint32_t eax, ebx, ecx, edx;
        char vendor[13];
        __asm__ volatile ("cpuid" : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx) : "a"(0));
        *(uint32_t*)&vendor[0] = ebx;
        *(uint32_t*)&vendor[4] = edx;
        *(uint32_t*)&vendor[8] = ecx;
        vendor[12] = '\0';
        vga_puts("CPU Vendor ID: ");
        vga_puts(vendor);
        vga_putc('\n');
    } else if (strcmp(cmd_buf, "panic") == 0) {
        vga_set_color(VGA_COLOR_LIGHT_RED, VGA_COLOR_BLACK);
        vga_puts("[TEST KERNEL PANIC] Division by zero simulated!\n");
        int a = 1;
        int b = 0;
        int c = a / b;
        (void)c;
    } else if (strcmp(cmd_buf, "reboot") == 0) {
        vga_puts("Rebooting via 8042 PS/2 controller...\n");
        uint8_t good = 0x02;
        while (good & 0x02) good = inb(0x64);
        outb(0x64, 0xFE);
    } else {
        vga_set_color(VGA_COLOR_LIGHT_RED, VGA_COLOR_BLACK);
        vga_puts("Unknown command: '");
        vga_puts(cmd_buf);
        vga_puts("'. Type 'help' for assistance.\n");
    }

    cmd_len = 0;
    shell_print_prompt();
}

void shell_handle_char(char c) {
    if (c == '\n') {
        cmd_buf[cmd_len] = '\0';
        execute_command();
    } else if (c == '\b') {
        if (cmd_len > 0) {
            cmd_len--;
            vga_putc('\b');
        }
    } else {
        if (cmd_len < CMD_BUFFER_SIZE - 1) {
            cmd_buf[cmd_len++] = c;
            vga_putc(c);
        }
    }
}
