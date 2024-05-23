#include "memory.h"
#include <stddef.h>
#include <stdio.h>
#include <debug.h>
#include <arch/i686/io.h>
#include <stdint.h>

// Define the data structures and global variables
#define MAX_MEMORY_REGIONS 256
#define PAGE_SIZE 1024
MemoryRegion memRegions[MAX_MEMORY_REGIONS];
size_t numMemRegions = 0;
size_t allocatedRegions = 0;

void* nextFreeMemory = NULL;
int currentRegionIndex = 0; // Track the current memory region index

void i686_Memory_initMemory(BootParams* params) {
    numMemRegions = 0;
    // Initialize the memory regions
    for (int i = 0; i < params->Memory.RegionCount; ++i) {
        if (params->Memory.Regions[i].Type == 1) {
            for (uint32_t j = 0; j < params->Memory.Regions[i].Length; j += PAGE_SIZE) {
                if(params->Memory.Regions[i].Begin + j == 0){
                    continue;
                }
                memRegions[numMemRegions].Begin = params->Memory.Regions[i].Begin + j;
                memRegions[numMemRegions].Length = PAGE_SIZE;
                memRegions[numMemRegions].Type = 0;
                memRegions[numMemRegions].pid = -1;
                numMemRegions++;
                if (numMemRegions >= MAX_MEMORY_REGIONS) {
                    log_err("Memory", "Exceeded maximum number of memory regions");
                    goto end;
                }
            }
        }
    }
    if (numMemRegions == 0) {
        log_err("Memory", "No usable memory regions found");
        return;
    }
end:
    nextFreeMemory = (void*)(uintptr_t)memRegions[0].Begin;
    log_info("Memory", "Allocated %d memory regions", numMemRegions);
}

void syscall_munmap(void* addr, uint32_t length, pid_t pid) {
    uintptr_t address = (uintptr_t)addr;
    size_t Nregions = length / PAGE_SIZE;
    if (length % PAGE_SIZE != 0) {
        Nregions += 1;
    }

    // Iterate through the memory regions to find the regions that start at the given address
    for (size_t i = 0; i < numMemRegions && Nregions > 0; i++) {
        if(memRegions[i].pid == pid){
            if (memRegions[i].Begin == address && memRegions[i].Type == 1) {
                // Mark the region as free
                memRegions[i].Type = 0;  // Type 0 indicates free memory
                allocatedRegions--;
                log_info("Memory", "Freed memory region starting at 0x%x remaining: %d", address, Nregions-1);
                address += PAGE_SIZE;
                Nregions--;
                log_info("Memory", "remaining regions %d", Nregions);
                if (Nregions == 0) {
                    return; // Exit the loop if all requested memory regions have been freed
                }
            }
        }
    }

    if (Nregions != 0) {
        log_err("Memory", "Attempted to free more memory than allocated starting at 0x%lx", address);
    }
}

void* syscall_mmap(uint32_t length, pid_t pid) {
    size_t Nregions = length / PAGE_SIZE;
    if (length % PAGE_SIZE != 0) {
        Nregions += 1;
    }

    if (allocatedRegions + Nregions > numMemRegions) {
        log_err("Memory", "Out of memory\n");
        return NULL;
    }

    void* addr = (void*)(uintptr_t)memRegions[allocatedRegions].Begin;
    for (size_t i = 0; i < Nregions; i++) {
        memRegions[allocatedRegions].pid = pid;
        memRegions[allocatedRegions++].Type = 1;  // Type 1 indicates allocated memory
        log_info("Memory", "Allocated memory region starting at 0x%x", addr+i*PAGE_SIZE);
    }

    return addr;
}