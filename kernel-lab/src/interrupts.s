/*
 * Assembly Interrupt Service Routine (ISR) Stubs
 * Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)
 */

.macro ISR_NOERRCODE num
.global isr\num
isr\num:
    cli
    pushl $0
    pushl $\num
    jmp isr_common_stub
.endm

.macro ISR_ERRCODE num
.global isr\num
isr\num:
    cli
    pushl $\num
    jmp isr_common_stub
.endm

.macro IRQ_STUB num irq
.global irq\num
irq\num:
    cli
    pushl $0
    pushl $\irq
    jmp irq_common_stub
.endm

/* CPU Exceptions 0-31 */
ISR_NOERRCODE 0
ISR_NOERRCODE 1
ISR_NOERRCODE 2
ISR_NOERRCODE 3
ISR_NOERRCODE 4
ISR_NOERRCODE 5
ISR_NOERRCODE 6
ISR_NOERRCODE 7
ISR_ERRCODE   8
ISR_NOERRCODE 9
ISR_ERRCODE   10
ISR_ERRCODE   11
ISR_ERRCODE   12
ISR_ERRCODE   13
ISR_ERRCODE   14
ISR_NOERRCODE 15
ISR_NOERRCODE 16
ISR_NOERRCODE 17
ISR_NOERRCODE 18
ISR_NOERRCODE 19
ISR_NOERRCODE 20
ISR_NOERRCODE 21
ISR_NOERRCODE 22
ISR_NOERRCODE 23
ISR_NOERRCODE 24
ISR_NOERRCODE 25
ISR_NOERRCODE 26
ISR_NOERRCODE 27
ISR_NOERRCODE 28
ISR_NOERRCODE 29
ISR_NOERRCODE 30
ISR_NOERRCODE 31

/* Hardware IRQs (32-47) */
IRQ_STUB 0, 32
IRQ_STUB 1, 33
IRQ_STUB 2, 34
IRQ_STUB 3, 35
IRQ_STUB 4, 36
IRQ_STUB 5, 37
IRQ_STUB 6, 38
IRQ_STUB 7, 39
IRQ_STUB 8, 40
IRQ_STUB 9, 41
IRQ_STUB 10, 42
IRQ_STUB 11, 43
IRQ_STUB 12, 44
IRQ_STUB 13, 45
IRQ_STUB 14, 46
IRQ_STUB 15, 47

.extern isr_handler
isr_common_stub:
    pusha
    mov %ds, %ax
    pushl %eax
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    pushl %esp
    call isr_handler
    add $4, %esp
    popl %eax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    popa
    add $8, %esp
    sti
    iret

.extern irq_handler
irq_common_stub:
    pusha
    mov %ds, %ax
    pushl %eax
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    pushl %esp
    call irq_handler
    add $4, %esp
    popl %eax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    popa
    add $8, %esp
    sti
    iret
