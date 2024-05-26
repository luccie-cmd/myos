from decimal import Decimal
import re
import os

from SCons.Node.FS import Dir, File, Entry
from SCons.Environment import Environment



def GlobRecursive(env: Environment, pattern, node='.'):
    src = str(env.Dir(node).srcnode())
    cwd = str(env.Dir('.').srcnode())

    dir_list = [src]
    for root, directories, _ in os.walk(src):
        for d in directories:
            dir_list.append(os.path.join(root, d))

    globs = []
    for d in dir_list:
        glob = env.Glob(os.path.join(os.path.relpath(d, cwd), pattern))
        globs.append(glob)

    return globs


def FindIndex(the_list, predicate):
    for i in range(len(the_list)):
        if predicate(the_list[i]):
            return i
    return None


def IsFileName(obj, name):
    if isinstance(obj, str):
        return name in obj
    elif isinstance(obj, File) or isinstance(obj, Dir) or isinstance(obj, Entry):
        return obj.name == name
    return False