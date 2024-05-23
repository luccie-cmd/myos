#include "elf.h"
#include "fat.h"
#include <stddef.h>
#include <stdio.h>
#include <debug.h>

ElfFile* elf_load_file(const char* path, pid_t pid){
    uint32_t filePos = 0;
    printf("Allocating memory for elffile\n");
    ElfFile* elf = syscall_mmap(sizeof(elf[0]), pid);
    if(elf == NULL){
        return NULL;
    }
    elf->pid = pid;
    printf("Opening file %s\n", path);
    FAT_File* file = FAT_Open(path);
    if(file == NULL){
        printf("Failed to open file %s\n", path);
        elf_free(elf);
        return NULL;
    }
    printf("Reading %s's header\n", path);
    elf->Header.bytes = syscall_mmap(sizeof(elf->Header.header), pid);
    if(elf->Header.bytes == NULL){
        printf("Failed to allocate memory for elf header\n");
        FAT_Close(file);
        elf_free(elf);
        return NULL;
    }
    // load program header
    ELFHeader header = elf->Header.header;
    uint32_t programHeaderOffset = header.ProgramHeaderTablePosition;
    uint32_t programHeaderSize = header.ProgramHeaderTableEntrySize * header.ProgramHeaderTableEntryCount;
    uint32_t programHeaderTableEntrySize = header.ProgramHeaderTableEntrySize;
    uint32_t programHeaderTableEntryCount = header.ProgramHeaderTableEntryCount;
    filePos += FAT_Read(file, sizeof(elf->Header.header), elf->Header.bytes);
    filePos += FAT_Read(file, programHeaderOffset - filePos, elf->Header.bytes);
    uint32_t read = 0;
    if ((read = FAT_Read(file, programHeaderSize, elf->Header.bytes)) != programHeaderSize)
    {
        printf("ELF Load error!\n");
        return NULL;
    }
    filePos += read;
    FAT_Close(file);
    log_warn("Elf", "TODO: Parse program header table");
    return elf;
}

void elf_free(ElfFile* file){
    syscall_munmap(file, sizeof(file[0]), file->pid);
}