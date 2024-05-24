#!/usr/bin/python3

import time
import os
import subprocess
import re
import glob
import parted
from shutil import copy2
from io import SEEK_CUR, SEEK_SET
from pathlib import Path
from build_scripts.utility import ParseSize, RemoveSuffix

if os.name == "nt":
    print("ERROR: Cannot build for windows!!!")
    exit(1)

def identifier(line: str) -> str:
    idx: int = 0
    for i in range(len(line)):
        if line[i] == " ":
            idx = i
            break
    return line[:idx]

def parseConfig(config_path: str) -> map:
    config: map = {}
    with open(config_path, "r") as config_file:
        for line in config_file.readlines():
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            name = identifier(line)
            value = line.split("=")[1].strip()
            value = value.strip("'")
            config[name] = value
    return config

def create_partition_table(target: str, align_start: int):
    device = parted.getDevice(target)
    disk = parted.freshDisk(device, 'msdos')
    freeSpace = disk.getFreeSpaceRegions()
    partitionGeometry = parted.Geometry(device, align_start, end=freeSpace[-1].end)
    partition = parted.Partition(disk=disk, type=parted.PARTITION_NORMAL, geometry=partitionGeometry)
    partition.setFlag(parted.PARTITION_BOOT)
    disk.addPartition(partition, constraint=device.optimalAlignedConstraint)
    disk.commit()

SECTOR_SIZE = 512
CONFIG = parseConfig("./build_scripts/config.py")
platform_prefix = ''
if CONFIG['arch'] == 'i686':
    platform_prefix = 'i686-elf-'
else:
    print("TODO: Build for x86_64 and other build types")
    exit(1)
DEPS = {
    'binutils': '2.41',
    'gcc': '14.1.0'
}
toolchainDir = Path(CONFIG['toolchain'], RemoveSuffix(platform_prefix, '-')).resolve()
toolchainBin = Path(toolchainDir, 'bin')
toolchainGccLibs = Path(toolchainDir, 'lib', 'gcc', RemoveSuffix(platform_prefix, '-'), DEPS['gcc'])
FLAGS: map = {
    "AS": 'nasm',
    "LD": platform_prefix+"g++",
    "CC": platform_prefix+"gcc",
    "CXX": platform_prefix+"g++",
    "ASFLAGS": ["-felf"],
    "CFLAGS": ["-std=c11", "-ffreestanding", "-nostdlib", "-c"],
    "CXXFLAGS": ["-std=c++20", "-fno-exceptions", "-fno-rtti", "-c"],
    "LDFLAGS": ["-nostdlib"],
    "LIBS": ['gcc'],
    "LIBPATH": [ str(toolchainGccLibs) ],
}
BUILD_MESSAGES: map = {
    "ASM": "AS  ",
    "CC":   "CC  ",
    "CXX": "CXX ",
    "LD":  "LD  ",
}
if CONFIG["config"] == "debug":
    FLAGS["CFLAGS"].append("-g -O0")
else:
    FLAGS["CFLAGS"].append("-O3")

def generate_image_file(target: str, size_sectors: int):
    with open(target, 'wb') as fout:
        fout.write(bytes(size_sectors * SECTOR_SIZE))
        fout.close()

def create_filesystem(target: str, filesystem, reserved_sectors=0, offset=0):
    if filesystem in ['fat12', 'fat16', 'fat32']:
        reserved_sectors += 1
        if filesystem == 'fat32':
            reserved_sectors += 1

        mkfs_fat_cmd = [
            'mkfs.fat',
            '-F', filesystem[3:],  # fat size
            '-n', 'NBOS',          # label
            '-R', str(reserved_sectors),  # reserved sectors
            '--offset', str(offset),
            target
        ]

        subprocess.run(mkfs_fat_cmd, check=True)
    elif filesystem == 'ext2':
        mkfs_ext2_cmd = [
            'mkfs.ext2',
            '-L', 'NBOS',  # label
            '-E', f'offset={offset * SECTOR_SIZE}'
        ]
        subprocess.run(mkfs_ext2_cmd, check=True)
    else:
        raise ValueError('Unsupported filesystem ' + filesystem)

def find_symbol_in_map_file(map_file: str, symbol: str):
    with map_file.open('r') as fmap:
        for line in fmap:
            if symbol in line:
                match = re.search('0x([0-9a-fA-F]+)', line)
                if match is not None:
                    return int(match.group(1), base=16)
    return None

def get_first_directory(out_dir):
    # Normalize the path to remove any redundant separators and up-level references
    normalized_path = os.path.normpath(out_dir)
    
    # Split the normalized path
    parts = normalized_path.split(os.sep)
    
    # Return the first directory name
    if parts[0] == '':
        # This means the path started with a separator, so the first element is empty
        return parts[1] if len(parts) > 1 else None
    else:
        return parts[0]

def build_asm(in_path: str, out_path: str, out_dir: str) -> None:
    print(f"{BUILD_MESSAGES['ASM']} {in_path}")
    command = FLAGS['AS']
    for flag in FLAGS['ASFLAGS']:
        command += " " + flag
    command += " "
    command += in_path
    command += " -o "
    command += f"{out_dir}/{os.path.basename(out_path)}.o"
    os.system(f"mkdir -p {os.path.dirname(out_path)}")
    os.system(f"mkdir -p {out_dir}")
    subprocess.run(command, shell=True, check=True)

def build_c(in_path: str, out_path: str, out_dir: str) -> None:
    print(f"{BUILD_MESSAGES['CC']} {in_path} {out_dir}/{os.path.basename(out_path)}.o")
    command = FLAGS['CC']
    for flag in FLAGS['CFLAGS']:
        command += " " + flag
    command += ' '
    command += in_path
    command += ' -o '
    command += f"{out_dir}/{os.path.basename(out_path)}.o"
    os.system(f"mkdir -p {os.path.dirname(out_path)}")
    os.system(f"mkdir -p {out_dir}")
    subprocess.run(command, shell=True, check=True)

def build_cpp(in_path: str, out_path: str) -> None:
    pass

def link_files(files: list[str], linker_script: str, map_path, out_path: str) -> None:
    print(f"{BUILD_MESSAGES['LD']} {out_path}")
    command = FLAGS['LD']
    for flag in FLAGS['LDFLAGS']:
        command += " " + flag
    command += " -T "
    command += linker_script
    command += f" -Wl,-Map={map_path}"
    for file in files:
        if file_end_with(file, ".o"):
            command += " " + file
    command += " -o "
    command += out_path
    os.system(f"mkdir -p {os.path.dirname(out_path)}")
    subprocess.run(command, shell=True, check=True)



def file_end_with(file, end):
    return file.endswith(end)

# returns a string where of the output file
def build_stage1(out_dir: str) -> str:
    print("> Building Stage1...")

# returns a string where of the output file
def build_stage2(out_dir: str) -> str:
    print("> Building Stage2...")
    

# returns a string where of the output file
def build_kernel(out_dir: str) -> str:
    print("> Building kernel...")

def mount_fs(image: str, mount_dir: str):
    subprocess.run(['guestmount', '-a', image, '-m', '/dev/sda1', mount_dir], check=True)

def unmount_fs(mount_dir: str):
    time.sleep(3)
    subprocess.run(['fusermount', '-u', mount_dir], check=True)

def install_stage1(target: str, stage1: str, stage2_offset, stage2_size, offset=0):
    map_file = Path(stage1).with_suffix('.map')
    if not map_file.exists():
        raise ValueError("Can't find " + map_file)
    
    entry_offset = find_symbol_in_map_file(map_file, '__entry_start')
    if entry_offset is None:
        raise ValueError("Can't find __entry_start symbol in map file " + str(map_file))
    entry_offset -= 0x7c00

    stage2_start = find_symbol_in_map_file(map_file, 'stage2_location')
    if stage2_start is None:
        raise ValueError("Can't find stage2_location symbol in map file " + str(map_file))
    stage2_start -= 0x7c00

    with open(stage1, 'rb') as fstage1:
        with os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT), 'wb+') as ftarget:
            ftarget.seek(offset * SECTOR_SIZE, SEEK_SET)

            # write first 3 bytes jump instruction
            ftarget.write(fstage1.read(3))

            # write starting at entry_offset (end of header)
            fstage1.seek(entry_offset - 3, SEEK_CUR)
            ftarget.seek(entry_offset - 3, SEEK_CUR)
            ftarget.write(fstage1.read())

            # write location of stage2
            ftarget.seek(offset * SECTOR_SIZE + stage2_start, SEEK_SET)
            ftarget.write(stage2_offset.to_bytes(4, byteorder='little'))
            ftarget.write(stage2_size.to_bytes(1, byteorder='little'))

def install_stage2(target: str, stage2: str, offset=0, limit=None):
    with open(stage2, 'rb') as fstage2:
        with os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT), 'wb+') as ftarget:
            ftarget.seek(offset * SECTOR_SIZE, SEEK_SET)
            ftarget.write(fstage2.read())

def build_disk(out_dir: str) -> None:
    os.system(f"mkdir -p {get_first_directory(out_dir)}")
    image: str = out_dir+"/image.img"
    stage1: str = build_stage1(out_dir)
    stage2: str = build_stage2(out_dir)
    kernel: str = build_kernel(out_dir)
    print(f"image = {image}")
    print(f"stage1 = {stage1}")
    print(f"stage2 = {stage2}")
    print(f"kernel = {kernel}")

    size_sectors = (ParseSize(CONFIG['imageSize']) + SECTOR_SIZE - 1) // SECTOR_SIZE
    file_system = CONFIG['imageFS']
    partition_offset = 2048

    stage2_size = os.stat(stage2).st_size
    stage2_sectors = (stage2_size + SECTOR_SIZE - 1) // SECTOR_SIZE

    generate_image_file(image, size_sectors)

    # create partition table
    print(f"> creating partition table...")
    create_partition_table(image, partition_offset)

    # create file system
    print(f"> formatting file using {file_system}...")
    create_filesystem(image, file_system, offset=partition_offset)

    # install stage1
    print(f"> installing stage1...")
    install_stage1(image, stage1, offset=partition_offset, stage2_offset=1, stage2_size=stage2_sectors)
 
    # install stage2
    print(f"> installing stage2...")
    install_stage2(image, stage2, offset=1, limit=partition_offset)

    tempdir_name = 'tmp_mount_{0}'.format(int(time.time()))
    tempdir = os.path.join(os.path.dirname(image), tempdir_name)
    try:
        # mount
        os.mkdir(tempdir)

        print(f"> mounting image to {tempdir}...")
        mount_fs(image, tempdir)

        # copy kernel
        print(f"> copying kernel...")
        bootdir = os.path.join(tempdir, 'boot')
        os.makedirs(bootdir)
        copy2(kernel, bootdir)

        # make the default files and folders
        print(f"> making default files and folders...")
        os.makedirs(os.path.join(tempdir, "bin"))
        os.makedirs(os.path.join(tempdir, "usr"))
        os.makedirs(os.path.join(tempdir, "usr/bin"))

        # copy rest of files
        src_root = "image/root"
        files: list[str] = glob.glob(src_root+"/**", recursive=True)
        print(f"> copying files...")
        for file in files:
            file_src = file.srcnode().path
            file_rel = os.path.relpath(file_src, src_root)
            file_dst = os.path.join(tempdir, file_rel)

            if os.path.isdir(file_src):
                print('    ... creating directory', file_rel)
                os.makedirs(file_dst)
            else:
                print('    ... copying', file_rel)
                copy2(file_src, file_dst)

    finally:
        print("> cleaning up...")
        try:
            unmount_fs(tempdir)
        except:
            pass
        os.rmdir(tempdir)

def main():
    print(CONFIG)
    print(FLAGS)
    build_disk(f"{CONFIG['outDir']}/i686_{CONFIG['config']}")

if __name__ == '__main__':
    main()
