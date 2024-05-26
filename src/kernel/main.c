#include <stdint.h>
#include "stdio.h"
#include <hal/hal.h>
#include <arch/i686/irq.h>
#include <debug.h>
#include "memory.h"
#include <arch/i686/io.h>
#include "process.h"
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

    printf("Main: Boot device: %x\n", bootParams->BootDevice);
    printf("Main: Memory region count: %d\n", bootParams->Memory.RegionCount);
    for (int i = 0; i < bootParams->Memory.RegionCount; i++) 
    {
        printf("Main: MEM: start=0x%llx length=0x%llx end=0x%llx type=%x\n ", 
            bootParams->Memory.Regions[i].Begin,
            bootParams->Memory.Regions[i].Length,
            bootParams->Memory.Regions[i].Begin+bootParams->Memory.Regions[i].Length,
            bootParams->Memory.Regions[i].Type);
    }

    printf("Aurora OS v0.1\n");

    Process_t *terminal = NewProcess("/bin/kernel_apps/terminal.elf");
    StartProcess(terminal);
    DeleteProcess(terminal);
end:
    for (;;);
}
