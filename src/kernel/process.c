#include "process.h"
#include "memory.h"
#include "syscall.h"
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "elf.h"

Process_t* NewProcess(const char* exePath){
    pid_t pid = fork();
    Process_t* proc = MMAllocate(pid, sizeof(proc[0]));
    if(proc == NULL){
        printf("KERNEL ERROR: Failed allocate a new process!\n");
        i686_Panic();
    }
    
    proc->exe_path = exePath;
    proc->pid = pid;
    // Allocate memory for the process (e.g., 64 KB for simplicity)
    proc->memory_size = 64 * 1024;
    proc->memory = (uint8_t *)MMAllocate(pid, proc->memory_size);
    if (proc->memory == NULL) {
        return NULL; // Error: failed to allocate memory
    }

    // Initialize the memory to zero
    memset(proc->memory, 0, proc->memory_size);
    return proc;
}

int StartProcess(Process_t* process){
    if (process == NULL) {
        return -1; // Error: invalid arguments
    }

    

    // Executable loading successful
    return 0;
}

void DeleteProcess(Process_t* process){
    MMFreePid(process->pid);
    MMFree(process, sizeof(process[0]));
}