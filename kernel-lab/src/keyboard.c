#include "keyboard.h"
#include "idt.h"
#include "io.h"
#include "vga.h"
#include "shell.h"

#define KBD_DATA_PORT 0x60

static const char kbd_us[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
  '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0,  'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',
    0, '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/',   0,
  '*',   0, ' ',   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0, '-',   0,   0,   0, '+',   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0
};

static void keyboard_callback(struct registers_struct* regs) {
    (void)regs;
    uint8_t scancode = inb(KBD_DATA_PORT);
    // Ignore key release codes (scancode & 0x80)
    if (!(scancode & 0x80)) {
        char c = kbd_us[scancode];
        if (c != 0) {
            shell_handle_char(c);
        }
    }
}

void keyboard_init(void) {
    register_interrupt_handler(33, keyboard_callback); // IRQ1 = INT 33
}
