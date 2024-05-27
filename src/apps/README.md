# APPS

Every app has it's own folder and is implementend in assembly

The reason for it being implemented in assembly is so that we can interract with the kernel without needing to implement our own libc and instead we can just call
interrupt `0x80`.