CC = gcc
AS = as
LD = ld

CFLAGS = -m32 -ffreestanding -fno-pie -fno-stack-protector -nostdlib -Wall -Wextra -O2 -Isrc
ASFLAGS = --32
LDFLAGS = -m elf_i386 -T linker.ld -nostdlib

OBJS = src/boot.o src/kernel.o src/vga.o src/gdt.o src/idt.o src/interrupts.o src/pic.o src/keyboard.o src/shell.o

all: micro-kernel.bin

src/boot.o: src/boot.s
	$(AS) $(ASFLAGS) $< -o $@

src/interrupts.o: src/interrupts.s
	$(AS) $(ASFLAGS) $< -o $@

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

micro-kernel.bin: $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

clean:
	rm -f src/*.o micro-kernel.bin

.PHONY: all clean
