#pragma once

#include <stdint.h>

typedef struct {
    uint64_t Begin, Length;
    uint32_t Type;
    uint32_t ACPI;
    // Memory allocator
    uint32_t UsedLength;
    pid_t pid;
} MemoryRegion;

typedef struct  {
    int RegionCount;
    MemoryRegion* Regions;
} MemoryInfo;

typedef struct {
    MemoryInfo Memory;
    uint8_t BootDevice;
} BootParams;