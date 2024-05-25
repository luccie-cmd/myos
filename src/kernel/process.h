#pragma once
#include <stdint.h>
#include <arch/i686/io.h>

typedef struct {
    pid_t pid;
    const char* exe_path;
} Process_t;

Process_t* NewProcess(const char* exePath);
void StartProcess(Process_t* process);
void DeleteProcess(Process_t* process);