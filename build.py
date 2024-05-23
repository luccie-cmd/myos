#!/usr/bin/python3

import os

if os.name == "nt":
    print("ERROR: Cannot build for windows!!!")
    exit(1)

def build_asm(in_path: str, out_path: str) -> None:
    pass
def build_c(in_path: str, out_path: str) -> None:
    pass
def build_cpp(in_path: str, out_path: str) -> None:
    pass
def link_files(files: list[str], out_path: str) -> None:
    pass
def build_stage1(out_dir: str) -> None:
    pass
def build_stage2(out_dir: str) -> None:
    pass
def build_kernel(out_dir: str) -> None:
    pass