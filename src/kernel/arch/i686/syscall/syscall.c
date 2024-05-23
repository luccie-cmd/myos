#include "syscall.h"
#include <stdio.h>
#include <debug.h>
#include <arch/i686/disk/elf.h>
#include "process.h"
#include "memory.h"

#define MODULE "[Syscall Handler]"
#define MAX_PROCESSES 256
Process *processes[MAX_PROCESSES];
uint32_t active_programs;

void init_process_table() {
    for (int i = 0; i < MAX_PROCESSES; i++) {
        processes[i]->pid = -1;  // -1 indicates an unused slot
        processes[i]->active = 0;
        processes[i]->eip = 0;
    }
}

void i686_SYSCALL_Initialize(BootParams* params){
    active_programs = 0;
    init_process_table();
    i686_Memory_initMemory(params);
}

void SyscallHandler(Registers* regs){
    if(regs->interrupt != 0x80){
        printf("Syscall handler called via invalid interrupt\n");
        i686_kernel_panic(MODULE, regs);
    }
    log_debug("Syscall", "Handling syscall");
}

// FORK
// FIXME: Wayyyy to simple
pid_t find_available_pid() {
    for (int i = 0; i < MAX_PROCESSES; i++) {
        if (processes[i]->pid == -1) {
            return i;
        }
    }
    return -1;  // No available PIDs
}

pid_t syscall_fork(){
    pid_t pid = find_available_pid();
    if (pid == -1) {
        printf("KERNEL ERROR: No available PIDs!\n");
        return -1;
    }
    Process* process = newProcess(pid);
    processes[active_programs++] = process;
    return pid;
}

void syscall_exit(int code, pid_t pid){
    (void)code;
    if (pid >= 0 && pid < MAX_PROCESSES && processes[pid]->active) {
        processes[pid]->active = 0;
        processes[pid]->pid = -1;
        active_programs--;
    } else {
        printf("KERNEL ERROR: Invalid PID or inactive process!\n");
        for(;;);  // Infinite loop to halt the kernel in case of an error
    }
}

// Exec
void switch_to_user_mode(uint32_t entry_point) {
    __asm__(
        "cli\n"                      // Clear interrupts
        "mov $0x23, %%ax\n"           // Load user data segment selector
        "mov %%ax, %%ds\n"
        "mov %%ax, %%es\n"
        "mov %%ax, %%fs\n"
        "mov %%ax, %%gs\n"
        "mov %%esp, %%eax\n"           // Save current stack pointer
        "push $0x23\n"               // Push user data segment selector
        "push %%eax\n"                // Push stack pointer
        "pushf\n"                    // Push EFLAGS
        "pop %%eax\n"
        "or $0x200, %%eax\n"          // Enable interrupts
        "push %%eax\n"                // Push modified EFLAGS
        "push $0x1B\n"               // Push user code segment selector
        "push %0\n"                  // Push entry point
        "iret\n"                     // Interrupt return
        :
        : "r" (entry_point)
    );
}

void free_process_memory(pid_t pid){
    if (pid >= 0 && pid < MAX_PROCESSES && processes[pid]->active) {
        // Free any memory resources associated with the process
        // For example, you can release allocated memory regions or any other resources

        // Mark the process as inactive and release its PID
        processes[pid]->active = 0;
        processes[pid]->pid = -1;
        active_programs--;
    } else {
        printf("KERNEL ERROR: Invalid PID or inactive process!\n");
        for(;;);  // Infinite loop to halt the kernel in case of an error
    }
}

bool load_executable(const char* path, uint32_t* entry, pid_t pid){
    printf("Loading elf exe\n");
    ElfFile *file = elf_load_file(path, pid);
    if (file == NULL) {
        return false;
    }
    *entry = file->Header.header.ProgramEntryPosition;
    elf_free(file);
    return true;
}

void syscall_exec(const char* path, pid_t pid){
    uint32_t entry_point;

    // Load the executable into memory and get the entry point and new page directory
    printf("Loading exetuable\n");
    if (!load_executable(path, &entry_point, pid)) {
        return; // Failed to load executable
    }
    // Transfer control to the new process (enter user mode at the new entry point)
    switch_to_user_mode(entry_point);

    // We should never reach here
    printf("ERROR: Exec didn't do it's job correct\n");
    return;
}