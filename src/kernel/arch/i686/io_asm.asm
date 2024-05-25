
global i686_outb
i686_outb:
    [bits 32]
    mov dx, [esp + 4]
    mov al, [esp + 8]
    out dx, al
    ret

global i686_inb
i686_inb:
    [bits 32]
    mov dx, [esp + 4]
    xor eax, eax
    in al, dx
    ret

global i686_Panic
i686_Panic:
    cli
    hlt

global i686_EnableInterrupts
i686_EnableInterrupts:
    sti
    ret

global i686_DisableInterrupts
i686_DisableInterrupts:
    cli
    ret

global i686_GetCurrentRegisters
i686_GetCurrentRegisters:
    ; Set up stack frame
    push ebp
    mov ebp, esp
    
    ; Get the pointer to Registers struct from stack
    mov eax, [ebp + 8]
    
    ; Save registers into the struct
    mov [eax], ds        ; Save ds
    mov [eax + 4], edi   ; Save edi
    mov [eax + 8], esi   ; Save esi
    mov [eax + 12], ebp  ; Save ebp
    mov [eax + 16], dword 0 ; Placeholder for 'useless'
    mov [eax + 20], ebx  ; Save ebx
    mov [eax + 24], edx  ; Save edx
    mov [eax + 28], ecx  ; Save ecx
    mov [eax + 32], eax  ; Save eax (the address of struct itself here)
    
    ; Save interrupt number (dummy value for demonstration)
    mov dword [eax + 40], 0
    ; Save error code (dummy value for demonstration)
    mov dword [eax + 44], 0

    ; Save the rest of the registers
    pushfd
    pop ebx              ; Save eflags
    mov [eax + 36], ebx
    mov [eax + 40], cs   ; Save cs
    mov [eax + 52], ss   ; Save ss
    mov [eax + 48], esp  ; Save esp
    
    ; Capture the return address (EIP) from stack
    mov ecx, [ebp + 4]
    mov [eax + 44], ecx  ; Save eip

    ; Restore stack frame
    mov esp, ebp
    pop ebp
    ret