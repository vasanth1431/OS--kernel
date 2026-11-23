#include "vga.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY ((volatile uint16_t*)0xB8000)

static size_t vga_row;
static size_t vga_column;
static uint8_t vga_current_color;
static volatile uint16_t* const vga_buffer = VGA_MEMORY;

static inline uint8_t vga_entry_color(enum vga_color fg, enum vga_color bg) {
    return fg | (bg << 4);
}

static inline uint16_t vga_entry(unsigned char uc, uint8_t color) {
    return (uint16_t)uc | ((uint16_t)color << 8);
}

static void update_cursor(int x, int y) {
    uint16_t pos = y * VGA_WIDTH + x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (uint8_t)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (uint8_t)((pos >> 8) & 0xFF));
}

void vga_init(void) {
    vga_row = 0;
    vga_column = 0;
    vga_current_color = vga_entry_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK);
    vga_clear();
}

void vga_set_color(uint8_t fg, uint8_t bg) {
    vga_current_color = vga_entry_color((enum vga_color)fg, (enum vga_color)bg);
}

void vga_clear(void) {
    for (size_t y = 0; y < VGA_HEIGHT; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            const size_t index = y * VGA_WIDTH + x;
            vga_buffer[index] = vga_entry(' ', vga_current_color);
        }
    }
    vga_row = 0;
    vga_column = 0;
    update_cursor(0, 0);
}

static void scroll(void) {
    for (size_t y = 0; y < VGA_HEIGHT - 1; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            vga_buffer[y * VGA_WIDTH + x] = vga_buffer[(y + 1) * VGA_WIDTH + x];
        }
    }
    for (size_t x = 0; x < VGA_WIDTH; x++) {
        vga_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + x] = vga_entry(' ', vga_current_color);
    }
    vga_row = VGA_HEIGHT - 1;
}

void vga_putc(char c) {
    if (c == '\n') {
        vga_column = 0;
        if (++vga_row == VGA_HEIGHT) {
            scroll();
        }
    } else if (c == '\r') {
        vga_column = 0;
    } else if (c == '\b') {
        if (vga_column > 0) {
            vga_column--;
            const size_t index = vga_row * VGA_WIDTH + vga_column;
            vga_buffer[index] = vga_entry(' ', vga_current_color);
        }
    } else {
        const size_t index = vga_row * VGA_WIDTH + vga_column;
        vga_buffer[index] = vga_entry(c, vga_current_color);
        if (++vga_column == VGA_WIDTH) {
            vga_column = 0;
            if (++vga_row == VGA_HEIGHT) {
                scroll();
            }
        }
    }
    update_cursor(vga_column, vga_row);
}

void vga_puts(const char* str) {
    while (*str) {
        vga_putc(*str++);
    }
}

void vga_print_hex(uint32_t n) {
    vga_puts("0x");
    char hex_chars[] = "0123456789ABCDEF";
    for (int i = 28; i >= 0; i -= 4) {
        vga_putc(hex_chars[(n >> i) & 0xF]);
    }
}

void vga_print_dec(uint32_t n) {
    if (n == 0) {
        vga_putc('0');
        return;
    }
    char buf[12];
    int i = 0;
    while (n > 0) {
        buf[i++] = (n % 10) + '0';
        n /= 10;
    }
    while (i > 0) {
        vga_putc(buf[--i]);
    }
}
