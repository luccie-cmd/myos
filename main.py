#!/bin/python3

import os, glob, subprocess, re, parted, time, sys
from decimal import Decimal
from pathlib import Path
from io import SEEK_CUR, SEEK_SET
from shutil import copy2

if os.name != "nt":

    def check_file_extension(file_path, valid_extensions):
        try:
            file_name = file_path.split('/')[-1]  # Extract the file name from the file path
            if '.' in file_name:
                file_extension = file_name.split('.')[-1]  # Extract the file extension
                if file_extension in valid_extensions:
                    return True
                else:
                    return False
        except IndexError:
            print(f"Invalid file path: '{file_path}'")

    def file_in_directory(directory: str, file: str) -> bool:
        # Get the full path of the file inside the directory
        file_in_directory = os.path.join(directory, file)

        # Check if the file exists
        return os.path.isfile(file_in_directory)

    def getFileExtension(file_path: str) -> str:
        try:
            file_name = file_path.split('/')[-1]  # Extract the file name from the file path
            if '.' in file_name:
                file_extension = file_name.split('.')[-1]  # Extract the file extension
                return file_extension
        except IndexError:
            print(f"Invalid file path: '{file_path}'")

    def build_c(comp_path: str, path: str, out_dir: str, args: list[str]=[]):
        command: str = f"{comp_path}/i686-elf-gcc -c"
        for arg in args:
            command += ' ' + arg
        command += ' '
        command += path
        command += ' '
        command += f'-o {out_dir}/objects/{path}.o'
        if os.system(command) != 0:
            print(f"Failed to compile {path}")
            os.system(f"rm -f {out_dir}/Cache/{path}")
            exit(1)
    def build_cxx(comp_path: str, path: str, out_dir: str, args: list[str]=[]):
        command: str = f"{comp_path}/i686-elf-g++ -c"
        for arg in args:
            command += ' ' + arg
        command += ' '
        command += path
        command += ' '
        command += f'-o {out_dir}/objects/{path}.o'
        if os.system(command) != 0:
            print(f"Failed to compile {path}")
            os.system(f"rm -f {out_dir}/Cache/{path}")
            exit(1)
    def build_asm(path: str, out_dir: str, args: list[str]=[]):
        command: str = f"nasm"
        for arg in args:
            command += ' ' + arg
        command += ' '
        command += path
        command += ' '
        command += f'-o {out_dir}/objects/{path}.o'
        if os.system(command) != 0:
            print(f"Failed to compile {path}")
            os.system(f"rm -f {out_dir}/Cache/{path}")
            exit(1)

    # Function to parse the assignment string
    def parse_assignment(assignment):
        # Split the string at the first occurrence of '='
        parts = assignment.split('=', 1)
        # Strip whitespace and quotes
        name = parts[0].strip()
        value = parts[1].strip().strip("'")
        return name, value

    def parseConfig(path: str):
        config: dict[str, str] = {}
        with open(path) as f:
            for line in f.readlines():
                line = line.strip()
                name, value = parse_assignment(line)
                config[name] = value.strip("'")
        return config
    
    CONFIG = parseConfig("./build_scripts/config.py")

    def build_files(directory_path: str, out_dir: str, c_args: list[str]=[], asm_args: list[str]=[], cxx_args: list[str]=[]):
        print(f"Compiling all the files in {directory_path}")
        os.system(f"mkdir -p {out_dir}")
        os.system(f"mkdir -p {out_dir}/Cache")
        os.system(f"mkdir -p {out_dir}/objects")
        files = glob.glob(directory_path + '/**', recursive=True)
        # Loop through each file
        for file_path in files:
            if not check_file_extension(file_path, ['cpp', 'c', 'asm']):
                continue
            if file_in_directory(f"{out_dir}/Cache/", file_path):
                current = open(file_path)
                cache = open(f"{out_dir}/Cache/{file_path}")
                if current.read() == cache.read():
                    cache.close()
                    current.close()
                    continue
                cache.close()
                current.close()
            # Get the file name with the full path
            os.system(f"mkdir -p {out_dir}/objects/"+os.path.dirname(file_path))
            os.system(f"mkdir -p {out_dir}/Cache/"+os.path.dirname(file_path))
            os.system(f"cp {file_path} {out_dir}/Cache/{file_path}")
            extension: str = getFileExtension(file_path)
            match extension:
                case 'c':
                    print(f"Compiling C   {file_path}")
                    build_c(f"{CONFIG['toolchain']}/i686-elf/bin", file_path, out_dir, c_args)
                case 'asm':
                    print(f"Compiling Asm {file_path}")
                    build_asm(file_path, out_dir, asm_args)
                case 'cpp':
                    print(f"Compiling CXX {file_path}")
                    build_cxx(f"{CONFIG['toolchain']}/i686-elf/bin", file_path, out_dir, cxx_args)

    def RemoveSuffix(str, suffix):
        if str.endswith(suffix):
            return str[:-len(suffix)]
        return str
    
    def link_files(files_path: str, out_path: str, linker_file: str=""):
        print(f"Linking all the files in {files_path}")
        files = glob.glob(files_path + '/**', recursive=True)
        os.system(f"mkdir -p {os.path.dirname(out_path)}")
        # Loop through each file
        command: str = f"{CONFIG['toolchain']}/i686-elf/bin/i686-elf-gcc -nostdlib"
        for file_path in files:
            if not check_file_extension(file_path, ['o']):
                continue
            command += ' ' + file_path
        command += f" -Wl,-Map={out_path[:-4]}.map"
        command += f" -Wl,-T {linker_file}"
        command += f" -o {out_path}"
        command += " -lgcc"
        if os.system(command) != 0:
            print(f"Failed to link {files_path}!")
            exit(1)

    SECTOR_SIZE = 512

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

    def install_stage1(target: str, stage1: str, stage2_offset, stage2_size, offset=0):
        map_file = Path(stage1).with_suffix('.map')
        if not map_file.exists():
            raise ValueError("Can't find " + str(map_file))

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

    def build_floppy(image, stage1, stage2, kernel, files, env):
        size_sectors = 2880
        stage2_size = os.stat(stage2).st_size
        stage2_sectors = (stage2_size + SECTOR_SIZE - 1) // SECTOR_SIZE

        generate_image_file(image, size_sectors)

        print(f"> formatting file using fat12...")
        create_filesystem(image, 'fat12', stage2_sectors)

        print(f"> installing stage1...")
        install_stage1(image, stage1, stage2_offset=1, stage2_size=stage2_sectors)

        print(f"> installing stage2...")
        install_stage2(image, stage2, offset=1)

        print(f"> copying files...")
        print('    ... copying', kernel)
        subprocess.run(['mmd', '-i', image, '::boot'], check=True)
        subprocess.run(['mcopy', '-i', image, kernel, '::boot/'], check=True)

        # copy rest of files
        src_root = env['BASEDIR']
        for file in files:
            file_src = file.srcnode().path
            file_rel = os.path.relpath(file_src, src_root)
            file_dst = '::' + file_rel

            if os.path.isdir(file_src):
                print('    ... creating directory', file_rel)
                subprocess.run(['mmd', '-i', image, file_dst], check=True)
            else:
                print('    ... copying', file_rel)
                subprocess.run(['mcopy', '-i', image, file_src, file_dst], check=True)

    def create_partition_table(target: str, align_start: int):
        device = parted.getDevice(target)
        disk = parted.freshDisk(device, 'msdos')
        freeSpace = disk.getFreeSpaceRegions()
        partitionGeometry = parted.Geometry(device, align_start, end=freeSpace[-1].end)
        partition = parted.Partition(disk=disk, type=parted.PARTITION_NORMAL, geometry=partitionGeometry)
        partition.setFlag(parted.PARTITION_BOOT)
        disk.addPartition(partition, constraint=device.optimalAlignedConstraint)
        disk.commit()

    def mount_fs(image: str, mount_dir: str):
        subprocess.run(['guestmount', '-a', image, '-m', '/dev/sda1', mount_dir], check=True)

    def unmount_fs(mount_dir: str):
        time.sleep(3)
        subprocess.run(['fusermount', '-u', mount_dir], check=True)

    def ParseSize(size: str):
        size_match = re.match(r'([0-9\.]+)([kmg]?)', size, re.IGNORECASE)
        if size_match is None:
            raise ValueError(f'Error: Invalid size {size}')

        result = Decimal(size_match.group(1))
        multiplier = size_match.group(2).lower()

        if multiplier == 'k':
            result *= 1024
        if multiplier == 'm':
            result *= 1024 ** 2
        if multiplier == 'g':
            result *= 1024 ** 3

        return int(result)

    def build_disk(image, stage1, stage2, kernel, files, env):
        size_sectors = (ParseSize(env['imageSize']) + SECTOR_SIZE - 1) // SECTOR_SIZE
        file_system = env['imageFS']
        partition_offset = 2048

        stage1_size = os.stat(stage1).st_size
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
            os.makedirs(os.path.join(tempdir, "bin/kernel_apps"))
            print(f"> Copying applications")
            app_files = glob.glob("./out/apps/**", recursive=True)
            for file in app_files:
                if not check_file_extension(file, 'elf'):
                    continue
                print(f"Copying {os.path.basename(file)}")
                copy2(file, os.path.join(tempdir, f"bin/kernel_apps/{os.path.basename(file)}"))

            # copy rest of files
            src_root = env['BASEDIR']
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

    def build_image(source, env):
        print("Building image")
        stage1 = str(source[0])
        stage2 = str(source[1])
        kernel = str(source[2])
        files = source[3:]
        print("Building disk")
        build_disk("./out/image.img", stage1, stage2, kernel, files, env)

    def runShFile(file: str, options=[]):
        command = file
        for op in options:
            command += f" {op}"
        os.system(f"{command}")

    if __name__ == '__main__':
        if len(sys.argv) > 1:
            if sys.argv[1] == 'toolchain':
                runShFile("./scripts/setup_toolchain.sh")
        CONFIG['BASEDIR'] = 'image'
        build_files("src/bootloader/stage1", "out", asm_args=["-DFILESYSTEM=fat32", '-felf32', '-g'])
        build_files("src/bootloader/stage2", "out", ['-ffreestanding', '-nostdlib', '-O3', '-std=c11', '-Werror', '-Isrc/bootloader/stage2', '-Isrc/libs', '-Isrc/libs/core'], ['-felf32', '-g'])
        build_files("src/kernel", "out", ['-ffreestanding', '-nostdlib', '-O3', '-std=c11', '-Werror', '-Isrc/kernel', '-Isrc/libs', '-Isrc/libs/core'], ['-felf32', '-g', '-Isrc/kernel'])
        build_files("src/libs", "out", ['-ffreestanding', '-nostdlib', '-O3', '-std=c11', '-Werror', '-Isrc/kernel', '-Isrc/libs', '-Isrc/libs/core'], ['-felf32', '-g', '-Isrc/kernel'], ['-ffreestanding', '-nostdlib', '-fno-exceptions', '-fno-rtti', '-O3', '-std=c++20', '-Werror', '-Isrc/libs', '-Isrc/libs/core'])
        build_files("src/apps/terminal", "out", asm_args=['-felf32', '-g', '-Isrc/apps/terminal'])
        link_files("out/objects/src/bootloader/stage1", "out/stage1.bin", "./src/bootloader/stage1/linker.ld")
        link_files("out/objects/src/bootloader/stage2", "out/stage2.bin", "./src/bootloader/stage2/linker.ld")
        link_files("out/objects/src/kernel", "out/kernel.elf", "./src/kernel/linker.ld")
        link_files("out/objects/src/apps/terminal", "out/apps/terminal.elf", "./src/apps/terminal/linker.ld")
        build_image(["out/stage1.bin", "out/stage2.bin", "out/kernel.elf"], CONFIG)
        if len(sys.argv) > 1:
            if sys.argv[1] == 'run':
                runShFile("./scripts/run.sh", ["disk", "out/image.img"])