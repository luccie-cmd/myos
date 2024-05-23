#include <stdint.h>
#include "stdio.h"
#include "memory.h"
#include <hal/hal.h>
#include <arch/i686/syscall/syscall.h>
#include <arch/i686/irq.h>
#include <debug.h>
#include <boot/bootparams.h>

extern void _init();

void timer(Registers* regs)
{
    printf(".");
}

void start(BootParams* bootParams)
{   
    // call global constructors
    _init();

    HAL_Initialize(bootParams);

    log_info("Main:", "Boot device: %x", bootParams->BootDevice);
    log_info("Main:", "Memory region count: %d", bootParams->Memory.RegionCount);
    for (int i = 0; i < bootParams->Memory.RegionCount; i++) 
    {
        log_info("Main:", "MEM: start=0x%llx length=0x%llx end=0x%llx type=%x", 
            bootParams->Memory.Regions[i].Begin,
            bootParams->Memory.Regions[i].Length,
            bootParams->Memory.Regions[i].Begin+bootParams->Memory.Regions[i].Length,
            bootParams->Memory.Regions[i].Type);
    }

    printf("LUCCIE OS v0.1\n");
    printf("This operating system is under construction.\n");
    pid_t kernelPid = syscall_fork();
    if (kernelPid == -1){
        printf("KERNEL ERROR: Couldn't make a new pid!\n");
        goto end;
    }
    printf("terminal pid = %d\n", kernelPid);
    printf("Executing terminal\n");
    syscall_exec("/bin/terminal", kernelPid);
    printf("ERROR: Terminal returned which is not supposed to happen!!!\n");
    printf("KERNEL PANIC");
end:
    for (;;);
}
