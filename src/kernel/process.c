#include "process.h"
#include "memory.h"
#include "syscall.h"
#include <stddef.h>
#include <stdio.h>

Process_t* NewProcess(const char* exePath){
    pid_t pid = fork();
    Process_t* proc = MMAllocate(pid, sizeof(proc[0]));
    if(proc == NULL){
        printf("KERNEL ERROR: Failed allocate a new process!\n");
        i686_Panic();
    }
    
    proc->exe_path = exePath;
    proc->pid = pid;
    return proc;
}

// @param regs is primaraly used for argc, argv, envp, ... but also for reseting the registers after they return from the process 
// since at execution time all the registers are saved into process->old_regs, process->regs is given to switchUserMode and
// after it's done executing it'll return to it's old registers
void StartProcess(Process_t* process){
    printf("TODO: Start a process!\n");
}

void DeleteProcess(Process_t* process){
    MMFreePid(process->pid);
    MMFree(process, sizeof(process[0]));
}