#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef struct{
    int x;
} DISK;

bool Disk_ReadSectors(DISK* disk, uint32_t lba, uint32_t sectors, void* dataOut);