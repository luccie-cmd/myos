#include "process.h"
#include "syscall.h"
#include <stddef.h>
#include <debug.h>

Process* newProcess(pid_t pid){
    Process* p = (Process*)syscall_mmap(sizeof(Process), pid);
    p->pid = pid;
    p->freeMem = 0;
    p->active = 1;
    p->eip = 0;
    return p;
}