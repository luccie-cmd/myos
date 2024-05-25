#include "io.h"
#include <stdio.h>
#include <debug.h>

#define UNUSED_PORT         0x80

void i686_iowait()
{
    i686_outb(UNUSED_PORT, 0);
}

void i686_kernel_panic(const char* MODULE, Registers* regs){
    printf("%s  eax=%d  ebx=%d  ecx=%d  edx=%d  esi=%d  edi=%d\n", 
        MODULE, regs->eax, regs->ebx, regs->ecx, regs->edx, regs->esi, regs->edi);
    printf("%s  esp=%d  ebp=%d  eip=%d  eflags=%d  cs=%d  ds=%d  ss=%d\n", 
        MODULE, regs->esp, regs->ebp, regs->eip, regs->eflags, regs->cs, regs->ds, regs->ss);
    printf("%s  interrupt=%d  errorcode=%d\n", MODULE, regs->interrupt, regs->error);
    printf("KERNEL PANIC!\n");
    log_crit(MODULE, "eax=%d  ebx=%d  ecx=%d  edx=%d  esi=%d  edi=%d", 
        regs->eax, regs->ebx, regs->ecx, regs->edx, regs->esi, regs->edi);
    log_crit(MODULE, "esp=%d  ebp=%d  eip=%d  eflags=%d  cs=%d  ds=%d  ss=%d", 
        regs->esp, regs->ebp, regs->eip, regs->eflags, regs->cs, regs->ds, regs->ss);
    log_crit(MODULE, "interrupt=%d  errorcode=%d", regs->interrupt, regs->error);
    i686_Panic();
}

void i686_GetCurrentRegisters(Registers* regs);