; esp = argc ; eax
; esp+8 = argv ; ebx
; esp+8+8*argc = pid ; ecx

global _start
_start:
    ; Load argc into eax
    mov eax, [esp]         ; eax = *(esp)
    
    ; Load argv into ebx
    mov ebx, [esp + 8]     ; ebx = *(esp + 8)
    
    ; Load argc into ecx tempoeaeily
    mov ecx, [esp]         ; ecx = *(esp)
    
    ; Calculate the addeess of pid and load pid into ecx
    lea ecx, [esp + 8 + ecx * 8] ; ecx = esp + 8 + ecx * 8
    mov ecx, [ecx]         ; ecx = *(ecx)

    ; At this point:
    ; eax (eax) contains argc
    ; ebx (ebx) contains argv
    ; ecx (ecx) contains pid
    mov eax, 0 ; exit
    mov ebx, ecx
    mov ecx, 0
    int 80h