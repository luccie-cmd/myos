#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef uint32_t pid_t;

typedef struct{
    pid_t pid;
    bool active;
    uint32_t eip;
    uint32_t freeMem;
} Process;

Process* newProcess(pid_t pid);