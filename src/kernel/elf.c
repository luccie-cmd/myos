#include "elf.h"
#include "memory.h"
#include <string.h>
#include <stdio.h>

ElfFile* loadElfFile(Process_t *proc){
    pid_t pid = proc->pid;
    ElfFile* Elffile = MMAllocate(pid, sizeof(Elffile[0]));
    // Open the executable file
    FILE *file = fopen(proc->exe_path, "rb");
    if (file == NULL) {
        return NULL; // Error: failed to open file
    }

    // Read the ELF header
    if (fread(&Elffile->header, 1, sizeof(Elffile->header), file) != sizeof(Elffile->header)) {
        fclose(file);
        return NULL; // Error: failed to read ELF header
    }

    // Verify the ELF magic number
    if (memcmp(Elffile->header.e_ident, "\x7f""ELF", 4) != 0) {
        fclose(file);
        return NULL; // Error: not a valid ELF file
    }

    // Read the program headers
    Elf32_Phdr *phdr = MMAllocate(proc->pid, sizeof(phdr[0]));
    for (int i = 0; i < Elffile->header.e_phnum; i++) {
        fseek(file, Elffile->header.e_phoff + i * sizeof(phdr[0]), SEEK_SET);
        if (fread(phdr, 1, sizeof(phdr[0]), file) != sizeof(phdr[0])) {
            fclose(file);
            return NULL; // Error: failed to read program header
        }

        if (phdr->p_type == PT_LOAD) {
            // Loadable segment
            fseek(file, phdr->p_offset, SEEK_SET);
            if (phdr->p_vaddr + phdr->p_memsz > proc->memory_size) {
                fclose(file);
                return NULL; // Error: segment too large for proc memory
            }

            // Read the segment into the proc's memory
            if (fread(proc->memory + phdr->p_vaddr, 1, phdr->p_filesz, file) != phdr->p_filesz) {
                fclose(file);
                return NULL; // Error: failed to read segment
            }

            // Zero out the BSS section (uninitialized data)
            memset(proc->memory + phdr->p_vaddr + phdr->p_filesz, 0, phdr->p_memsz - phdr->p_filesz);
        }
    }

    // Close the file
    fclose(file);

    // Set the entry point for the proc

    return Elffile;
}