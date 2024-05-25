#pragma once
#include <stdint.h>
#include <boot/bootparams.h>

void MMInit(BootParams* params);
void* MMAllocate(pid_t pid, uint32_t len);
void MMFree(void* addr, uint32_t len);
void MMFreePid(pid_t pid);

#ifdef DEBUG
void MMPrintNotUsedMemory();
#endif

typedef struct FreeBlock {
    uint64_t address;
    uint32_t size;
    pid_t pid;
    struct FreeBlock* next;
} FreeBlock;
