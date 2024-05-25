#include "memory.h"
#include <stddef.h>
#include <stdio.h>
#include <debug.h>

#define PAGE_SIZE 128 // Save memory space
#define INT_TO_VOID(ptr) ((void*)(uintptr_t)(ptr))
#define VOID_TO_INT(ptr) ((uint64_t)(uintptr_t)(ptr))

#ifdef DEBUG
typedef struct{
    uint32_t type, addr, len;
    pid_t pid;
} UseMemory;

#define MAX_USE_MEMORY 100
UseMemory memUsed[MAX_USE_MEMORY];
#endif

MemoryInfo mem;
size_t current_region = 0;
void* nextAvailableAddr = (void*)-1;
FreeBlock* freeList = NULL;

// Finds a new memory region to allocate from
static MemoryRegion findNewRegion(int start_region) {
    for (int i = start_region; i < mem.RegionCount; ++i) {
        if (mem.Regions[i].Type == 1) { // Usable memory
            current_region = i;
            return mem.Regions[i];
        }
    }
    printf("KERNEL ERROR: Out of usable memory\n");
    log_warn("Memory", "TODO: Paging no idea how just do it");
    for(;;);
    // If no usable region is found, return an invalid region
    MemoryRegion invalid_region = {0};
    return invalid_region;
}

// Initialize the memory manager with the provided boot parameters
void MMInit(BootParams* params) {
    mem = params->Memory;
    MemoryRegion region = findNewRegion(0);
    nextAvailableAddr = INT_TO_VOID(region.Begin);
    if (nextAvailableAddr == INT_TO_VOID(-1)) {
        printf("No available memory\n");
        for (;;); // Infinite loop to halt the system
    }
    char* padding = MMAllocate(0, PAGE_SIZE); // Allocate 1 page of memory so that no other things will have a NULL address unless something went wrong
    log_info("Memory", "Allocated padding bytes at %d", VOID_TO_INT(padding));
}

// Update the next available address and handle region transitions
static void MMUpdate(int64_t len) {
    if (len > 0) {
        nextAvailableAddr += len;
        mem.Regions[current_region].UsedLength += len;
        if (VOID_TO_INT(nextAvailableAddr) >= mem.Regions[current_region].Begin + mem.Regions[current_region].Length) {
            MemoryRegion region = findNewRegion(current_region + 1);
            nextAvailableAddr = INT_TO_VOID(region.Begin);
        }
    } else {
        nextAvailableAddr += len;
        mem.Regions[current_region].UsedLength += len;
        if (VOID_TO_INT(nextAvailableAddr) < mem.Regions[current_region].Begin) {
            printf("ERROR: MEMORY UNDERFLOW!!!\n");
            for (;;); // Halt the system
        }
    }
}

// Allocate memory of the specified length for a given pid
void* MMAllocate(pid_t pid, uint32_t len) {
    if (len == 0) {
        log_info("Memory", "Why did somebody try to allocate 0 bytes");
        return NULL;
    }

    // Align length to page size
    if (len % PAGE_SIZE != 0) {
        len = (len / PAGE_SIZE + 1) * PAGE_SIZE;
    }

    size_t start_region = (pid == 0) ? 0 : 2; // Kernel uses first available region, others start from 2
    
    // Check the free list for a suitable block
    FreeBlock* prev = NULL;
    FreeBlock* current = freeList;
    while (current) {
        if (current->size >= len) {
            void* allocAddr = INT_TO_VOID(current->address);
            if (current->size > len) {
                current->address += len;
                current->size -= len;
            } else {
                if (prev) {
                    prev->next = current->next;
                } else {
                    freeList = current->next;
                }
            }
            return allocAddr;
        }
        prev = current;
        current = current->next;
    }

    // If no suitable block is found in the free list, allocate a new block
    MemoryRegion region = findNewRegion(start_region);
    if (VOID_TO_INT(nextAvailableAddr) + len > region.Begin + region.Length) {
        region = findNewRegion(current_region + 1);
        nextAvailableAddr = INT_TO_VOID(region.Begin);
        if (nextAvailableAddr == INT_TO_VOID(-1)) {
            printf("No available memory\n");
            return NULL;
        }
    }

    void* allocatedAddr = nextAvailableAddr;
#ifdef DEBUG
    memUsed[VOID_TO_INT(allocatedAddr)/PAGE_SIZE].pid = pid;
    memUsed[VOID_TO_INT(allocatedAddr)/PAGE_SIZE].type = 1;
    memUsed[VOID_TO_INT(allocatedAddr)/PAGE_SIZE].addr = VOID_TO_INT(allocatedAddr);
    memUsed[VOID_TO_INT(allocatedAddr)/PAGE_SIZE].len = len;
#endif
    MMUpdate(len);
    return allocatedAddr;
}

// Free the specified memory and add it to the free list
void MMFree(void* addr, uint32_t len) {
#ifdef DEBUG
    pid_t pid = -1;
    for(int i = 0; i < MAX_USE_MEMORY; ++i){
        if(memUsed[i].addr == VOID_TO_INT(addr)){
            pid = memUsed[i].pid;
        }
    }
    MMFreePid(pid);
#else
    if (addr == NULL || len == 0) {
        return;
    }

    // Align length to page size
    if (len % PAGE_SIZE != 0) {
        len = (len / PAGE_SIZE + 1) * PAGE_SIZE;
    }

    uint64_t address = VOID_TO_INT(addr);
    FreeBlock* newBlock = (FreeBlock*)MMAllocate(0, sizeof(FreeBlock));
    if (newBlock == NULL) {
        printf("Error: Unable to allocate memory for free block\n");
        return;
    }

    newBlock->address = address;
    newBlock->size = len;
    newBlock->next = NULL;

    // Insert the new block into the free list, sorted by address
    if (!freeList || freeList->address > newBlock->address) {
        newBlock->next = freeList;
        freeList = newBlock;
    } else {
        FreeBlock* current = freeList;
        while (current->next && current->next->address < newBlock->address) {
            current = current->next;
        }
        newBlock->next = current->next;
        current->next = newBlock;
    }

    // Coalesce adjacent free blocks
    FreeBlock* current = freeList;
    while (current && current->next) {
        if (current->address + current->size == current->next->address) {
            current->size += current->next->size;
            FreeBlock* temp = current->next;
            current->next = current->next->next;
            // Free the temporary block metadata
            MMFree(INT_TO_VOID(temp), sizeof(FreeBlock));
        } else {
            current = current->next;
        }
    }
#endif
}

// Free all memory regions associated with the specified PID
void MMFreePid(pid_t pid) {
#ifdef DEBUG
    for(int i = 0; i < MAX_USE_MEMORY; ++i){
        if(memUsed[i].type == 1 && memUsed[i].pid == pid){
            memUsed[i].type = 0;
        }
    }
#endif
    FreeBlock* current = freeList;
    FreeBlock* prev = NULL;

    while (current) {
        if (current->pid == pid) {
            // Free the memory block
            MMFree(INT_TO_VOID(current->address), current->size);

            // Remove the block from the free list
            if (prev) {
                prev->next = current->next;
            } else {
                freeList = current->next;
            }

            // Move to the next block
            FreeBlock* temp = current;
            current = current->next;
            MMFree(INT_TO_VOID(temp), sizeof(FreeBlock));
        } else {
            prev = current;
            current = current->next;
        }
    }
}

#ifdef DEBUG
void MMPrintNotUsedMemory(){
    for(int i = 0; i < MAX_USE_MEMORY; ++i){
        if(memUsed[i].type == 1){
            log_info("Memory", "Used memory using pid %d location = %d len = %d", memUsed[i].pid, memUsed[i].addr, memUsed[i].len);
        }
    }
}
#endif