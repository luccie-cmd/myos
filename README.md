# Aurora Os

An os inspired by [nanobyte](https://github.com/nanobyte-dev/nanobyte_os)

## Building

First, install the following dependencies:

```sh
# Ubuntu, Debian:
sudo apt install build-essential bison flex libgmp3-dev libmpc-dev libmpfr-dev texinfo wget \
                   nasm mtools python3 python3-pip python3-parted dosfstools libguestfs-tools qemu-system-x86

# Fedora:
sudo dnf install gcc gcc-c++ make bison flex gmp-devel libmpc-devel mpfr-devel texinfo wget \
                   nasm mtools python3 python3-pip python3-pyparted dosfstools guestfs-tools qemu-system-x86

# Arch & Arch-based:
sudo pacman -S gcc make bison flex libgmp-static libmpc mpfr texinfo nasm mtools qemu-system-x86 python3
```
NOTE: to install all the required packages on Arch, you need an [AUR helper](https://wiki.archlinux.org/title/AUR_helpers).

Then you must run `python3 -m pip install -r requirements.txt`  

Next, modify the configuration in `build_scripts/config.py`. The most important is the `toolchain='../.toolchains'` option which sets where the toolchain will be downloaded and built. The default option is in the directory above where the repo is cloned, in a .toolchains directory, but you will get an error if this directory doesn't exist.  

Before running `main.py` make sure it's executable  

After that, run `main.py toolchain`, this should download and build the required tools (binutils and GCC). If you encounter errors during this step, you might have to modify `scripts/setup_toolchain.sh` and try a different version of **binutils** and **gcc**. Using the same version as the one bundled with your distribution is your best bet.

Finally, you should be able to run `main.py`. Use `main.py run` to test your OS using qemu.

NOTE: When qemu complains about not being able to get a write lock just remove out and try it again. It should work after that

## TODO
syscall handling  
actually starting processes