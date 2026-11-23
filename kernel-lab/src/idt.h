#ifndef IDT_H
#define IDT_H

#include <stdint.h>

struct idt_entry_struct {
    uint16_t base_lo;
    uint16_t sel;
    uint8_t  always0;
    uint8_t  flags;
    uint16_t base_hi;
} __attribute__((packed));

struct idt_ptr_struct {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed));

struct registers_struct {
    uint32_t ds;
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax;
    uint32_t int_no, err_code;
    uint32_t eip, cs, eflags, useresp, ss;
};

typedef void (*isr_t)(struct registers_struct*);

void idt_init(void);
void register_interrupt_handler(uint8_t n, isr_t handler);

#endif
