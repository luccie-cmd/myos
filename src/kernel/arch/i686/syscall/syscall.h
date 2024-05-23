#pragma once
#include <arch/i686/io.h>
#include <boot/bootparams.h>

typedef uint32_t pid_t;

#define PROT_NONE  0x00
#define PROT_READ  0x01
#define PROT_WRITE 0x02
#define PROT_EXEC  0x04

#define O_RDONLY   0x01

void i686_SYSCALL_Initialize(BootParams* params);
void SyscallHandler(Registers* regs);
pid_t syscall_fork();
void syscall_exit(int code, pid_t pid);
void* syscall_mmap(uint32_t length, pid_t pid);
void syscall_exec(const char* path, pid_t pid);
void syscall_munmap(void* addr, uint32_t length, pid_t pid);