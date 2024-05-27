#pragma once
#include <stdint.h>
#include <arch/i686/io.h>

typedef struct {
    pid_t pid;
    const char* exe_path;
    uint64_t memory_size;
    uint8_t* memory;
} Process_t;

Process_t* NewProcess(const char* exePath);
int StartProcess(Process_t* process);
void DeleteProcess(Process_t* process);