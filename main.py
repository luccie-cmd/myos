#!/bin/python3

import os, glob

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

    def main(directory_path: str, out_dir: str, out_name: str, compile_args: list[str]=[], link_args: list[str]=[]):
        print("Compiling all the files")
        os.system(f"rm -f {out_dir}/{out_name}")
        os.system(f"mkdir -p {out_dir}")
        os.system(f"mkdir -p {out_dir}/Cache")
        os.system(f"mkdir -p {out_dir}/objects")
        files = glob.glob(directory_path + '/**', recursive=True)
        # Loop through each file
        for file_path in files:
            if not check_file_extension(file_path, ['cpp']):
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
            print("Compiling:", file_path)
            os.system(f"mkdir -p {out_dir}/objects/"+os.path.dirname(file_path))
            os.system(f"mkdir -p {out_dir}/Cache/"+os.path.dirname(file_path))
            os.system(f"cp {file_path} {out_dir}/Cache/{file_path}")
            command: str = f"g++ -c -std=c++20 -O3 -ggdb -Iinclude -o {out_dir}/objects/{file_path}.o {file_path}"
            for comp_arg in compile_args:
                command += " " + comp_arg
            if os.system(command) != 0:
                print(f"FAILED TO COMPILE DIRECTORY {directory_path}\nPath: {file_path}")
                os.system(f"rm -f {out_dir}/Cache/{file_path}")
                return
        files = glob.glob(f"{out_dir}/objects/**", recursive=True)
        command: str = f"g++ -std=c++20 -O3 -o ./{out_dir}/{out_name} -ggdb "
        for file_path in files:
            if file_path[-2] != '.':
                continue
            print(f"Adding {file_path} to the linker")
            command += file_path + " "
        # Add the remaining arguments
        command += " lib/liblinuxfmt.a"
        for link_arg in link_args:
            command += " " + link_arg
        os.system(command)

    if __name__ == '__main__':
        main("src", "out", "lunar", ["-DCOMPILE", "-fsanitize=address"], ["-fsanitize=address"]);
else:
    import os
    import glob

    def check_file_extension(file_path, valid_extensions):
        try:
            file_name = file_path.split('\\')[-1]  # Extract the file name from the file path
            if '.' in file_name:
                file_extension = file_name.split('.')[-1]  # Extract the file extension
                if file_extension in valid_extensions:
                    return True
                else:
                    return False
            else:
                print(f"No file extension found in '{file_name}'.")
        except IndexError:
            print(f"Invalid file path: '{file_path}'")

    def main(directory_path: str):
        print("Compiling all the files")
        os.system("del /Q .\\build\\main.exe")
        os.system("mkdir .\\build")
        os.system("mkdir .\\build\\objects")
        files = glob.glob(directory_path + '\\**', recursive=True)
        # Loop through each file
        for file_path in files:
            if not check_file_extension(file_path, ['cpp']):
                continue
            # Get the file name with the full path
            print("Compiling:", file_path)
            os.system("mkdir .\\build\\objects\\" + os.path.dirname(file_path))
            # Use the C++ compiler, set the include as the include directory, use compile mode, set the maximum optimization level, and also set some warnings (also enable Asan), enable std c++ 23, also define COMPILE
            command: str = f"g++ -O3 -c -std=c++20 -ggdb -DWINDOWS -DCOMPILE -Iinclude -Iinclude\\game -o .\\build\\objects\\{file_path}.o {file_path}"
            if os.system(command) != 0:
                print(f"FAILED TO COMPILE DIRECTORY {directory_path}")
                return
        files = glob.glob(".\\build\\objects\\**", recursive=True)
        command: str = "g++ -O3 -std=c++20 -o .\\build\\main.exe -ggdb "
        for file_path in files:
            if file_path[-2:] != '.o':
                continue
            print(f"Adding {file_path} to the command")
            command += file_path + " "
        # Add the remaining arguments
        command += " .\\lib\\libwindowsfmt.a .\\lib\\libSDL2.dll.a .\\lib\\libSDL2.a .\\lib\\libSDL2main.a .\\lib\\glad.a"
        print("Command: " + command)
        if os.system(command) != 0:
            print(f"FAILED TO COMPILE DIRECTORY {directory_path}")
            return
        print("Removing objects")
        # os.system("rmdir /s /Q .\\build\\objects\\")

    if __name__ == '__main__':
        main(".\\src")
