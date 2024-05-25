#pragma once
#include <arch/i686/io.h>

void InitSyscall();
void SyscallHandle(Registers* regs);
pid_t fork();
void exit(pid_t pid, int status);