#include "syscall.h"
#include <stdio.h>
#include <string.h>
#include "debug.h"
#include "memory.h"
#include "process.h"

// Global process table
#define MAX_PROCESSES 10
static Process_t process_table[MAX_PROCESSES];
static Process_t* currentProcess = NULL;
static pid_t next_pid = 1;

void SyscallHandle(Registers* regs){
    printf("ERROR: Cannot handle user syscalls just yet!\n");
}

void InitSyscall(){
    memset(process_table, 0, sizeof(process_table));
    currentProcess = &process_table[0];
    currentProcess->pid = next_pid++;
}

// Helper function to find a free process slot
static Process_t* findFreeProcessSlot(){
    for (int i = 0; i < MAX_PROCESSES; i++) {
        if (process_table[i].pid == 0) {
            return &process_table[i];
        }
    }
    return NULL;
}

// Helper function to find a process by PID
static Process_t* findProcess(pid_t pid){
    for (int i = 0; i < MAX_PROCESSES; i++) {
        if (process_table[i].pid == pid) {
            return &process_table[i];
        }
    }
    return NULL;
}

// Helper function to remove a process from the table
static void removeProcess(Process_t *process){
    process->pid = 0;
}

// Helper function to create a new process
static Process_t* createProcess(){
    Process_t* new_process = findFreeProcessSlot();
    if (!new_process) {
        return NULL;
    }
    new_process->pid = next_pid++;
    new_process->exe_path = NULL;
    // Initialize other fields as necessary
    return new_process;
}

pid_t fork(){
    // Create a new process
    Process_t* child_process = createProcess();
    if (!child_process) {
        return -1; // Failed to create a new process
    }

    // Duplicate the parent's process structure to the child
    memcpy(child_process, currentProcess, sizeof(Process_t));

    // Update child's PID and allocate new memory for it
    child_process->pid = next_pid++;

    // Parent process returns child's PID
    log_info("Syscall", "New process created with PID %d", child_process->pid);
    return child_process->pid;
}

void exit(pid_t pid, int status){
    log_info("Syscall", "Exiting process with PID %d...", pid);

    // Find the process with the given PID
    Process_t* process = findProcess(pid);
    if (!process) {
        log_err("Syscall", "Process with PID %d not found!", pid);
        return;
    }

    // Remove the process from the process table
    removeProcess(process);

    // Update the current process if it is the exiting process
    if (currentProcess == process) {
        currentProcess = NULL;
    }
}