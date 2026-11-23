#include "gdt.h"

static struct gdt_entry_struct gdt_entries[3];
static struct gdt_ptr_struct   gdt_ptr;

extern void gdt_flush(uint32_t);

static void gdt_set_gate(int32_t num, uint32_t base, uint32_t limit, uint8_t access, uint8_t gran) {
    gdt_entries[num].base_low    = (base & 0xFFFF);
    gdt_entries[num].base_middle = (base >> 16) & 0xFF;
    gdt_entries[num].base_high   = (base >> 24) & 0xFF;

    gdt_entries[num].limit_low   = (limit & 0xFFFF);
    gdt_entries[num].granularity = (limit >> 16) & 0x0F;
    gdt_entries[num].granularity |= gran & 0xF0;
    gdt_entries[num].access      = access;
}

void gdt_init(void) {
    gdt_ptr.limit = (sizeof(struct gdt_entry_struct) * 3) - 1;
    gdt_ptr.base  = (uint32_t)&gdt_entries;

    // 0: Null descriptor
    gdt_set_gate(0, 0, 0, 0, 0);
    // 1: Kernel Code Segment (Base=0, Limit=4GB, Ring 0, Execute/Read)
    gdt_set_gate(1, 0, 0xFFFFFFFF, 0x9A, 0xCF);
    // 2: Kernel Data Segment (Base=0, Limit=4GB, Ring 0, Read/Write)
    gdt_set_gate(2, 0, 0xFFFFFFFF, 0x92, 0xCF);

    __asm__ volatile (
        "lgdt (%0)\n"
        "mov $0x10, %%ax\n"
        "mov %%ax, %%ds\n"
        "mov %%ax, %%es\n"
        "mov %%ax, %%fs\n"
        "mov %%ax, %%gs\n"
        "mov %%ax, %%ss\n"
        "ljmp $0x08, $1f\n"
        "1:\n"
        : : "r"(&gdt_ptr) : "eax"
    );
}
