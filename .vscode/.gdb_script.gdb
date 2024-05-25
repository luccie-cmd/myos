    symbol-file /home/luccie/programming/myos/build/i686_release/kernel/kernel.elf
    set disassembly-flavor intel
    target remote | qemu-system-i386 -S -gdb stdio -m 32 -hda /home/luccie/programming/myos/build/i686_release/image.img
