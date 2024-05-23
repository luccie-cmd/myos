#pragma once
#include <stdint.h>
#include <boot/bootparams.h>

typedef uint32_t pid_t;

void i686_Memory_initMemory(BootParams* params);
// uint32_t nextFreeMemoryRegion();