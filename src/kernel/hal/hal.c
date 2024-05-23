#include "hal.h"
#include <debug.h>
#include <arch/i686/gdt.h>
#include <arch/i686/idt.h>
#include <arch/i686/isr.h>
#include <arch/i686/irq.h>
#include <arch/i686/vga_text.h>
#include <arch/i686/syscall/syscall.h>

void HAL_Initialize(BootParams* params)
{
    VGA_clrscr();
    i686_GDT_Initialize();
    i686_IDT_Initialize();
    i686_ISR_Initialize();
    i686_IRQ_Initialize();
    i686_SYSCALL_Initialize(params);
    i686_ISR_RegisterHandler(0x80, SyscallHandler);
}
