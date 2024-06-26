// elf32.h
#ifndef ELF32_H
#define ELF32_H

#include <stdint.h>
#include "process.h"

#define EI_NIDENT 16

typedef struct {
    unsigned char e_ident[EI_NIDENT];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint32_t e_entry;
    uint32_t e_phoff;
    uint32_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
} Elf32_Ehdr;

typedef struct {
    uint32_t p_type;
    uint32_t p_offset;
    uint32_t p_vaddr;
    uint32_t p_paddr;
    uint32_t p_filesz;
    uint32_t p_memsz;
    uint32_t p_flags;
    uint32_t p_align;
} Elf32_Phdr;

typedef struct{
    uint32_t sh_name;
    uint32_t sh_type;
    uint32_t sh_flags;
    uint32_t sh_addr;
    uint32_t sh_offset;
    uint32_t sh_link;
    uint32_t sh_info;
    uint32_t sh_allign;
    uint32_t sh_entsize;
} Elf32_Shdr;

typedef struct{
    Elf32_Ehdr header;
    Elf32_Phdr *pHeaders;
    Elf32_Shdr *sHeaders;
} ElfFile;

#define PT_LOAD 1

ElfFile* loadElfFile(Process_t *proc);

#endif // ELF32_H
