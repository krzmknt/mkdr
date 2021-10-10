import yaml
import pathlib
import os
import argparse
import shutil
import sys
from collections import namedtuple


# ---------------------------------------------------------------------------- #
# Argument
# ---------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force', action='store_true', help='Overwrite the existing objects')
parser.add_argument('-n', '--name', type=str, help='Specify the filename')
parser.add_argument('-r', '--remove', action='store_true', help='Remove mode')
parser.add_argument('-o', '--reorg', action='store_true', help="Not organize new objects, but rearrange the existing objects.")
parser.add_argument('-s', '--save', action='store_true', help="Save mode")
arg = parser.parse_args()


# ---------------------------------------------------------------------------- #
# Variables
# ---------------------------------------------------------------------------- #
INDENT = 2
Path = namedtuple('Path', ['type','path'])
sign_dir = 'd'
sign_file = 'f'
red = lambda str: print('\033[31m'+str+'\033[0m')
green =  lambda str: print('\033[32m'+str+'\033[0m')


# ---------------------------------------------------------------------------- #
# Check
# ---------------------------------------------------------------------------- #
def check():
    checkUser()
    checkMode()
    checkOptionCombination()

def checkUser():
    if os.getuid() == 0:
        red('UserError: Running mkdr as root is not supported.')
        sys.exit()


def checkMode():
    modes = arg.remove + arg.reorg + arg.save
    if modes > 1:
        red('ModeError: Only one mode can be specified.')
        sys.exit()


def checkOptionCombination():
    if arg.force:
        if arg.reorg:
            red('Reorg mode does not suppourt --force option.')
            sys.exit()


# ---------------------------------------------------------------------------- #
# Module
# ---------------------------------------------------------------------------- #
def getPathsFromOrgYaml(filename):
    try:
        with open(filename) as f:
            paths_yml = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError as err:
        red('FileNotFoundError: No such file: \'{}\''.format(filename))
        sys.exit()

    isDirectory = lambda d: isinstance(d,dict)
    getDirName = lambda d: list(d.keys())[0]
    getDirContents = lambda d: d[getDirName(d)]

    path = ['.']
    paths = []
    def recursiveMkdir(paths_yml, path):
        for d in paths_yml:
            if isDirectory(d):
                path.append(getDirName(d))
                paths.append(Path(sign_dir, '/'.join(path)))
                recursiveMkdir(getDirContents(d), path)
            elif d is not None:
                paths.append(Path(sign_file, '/'.join(path)+'/'+d))
        path.pop()

    recursiveMkdir(paths_yml, path)
    return paths


def checkNotExist(paths):
    paths_exist = [p.path for p in paths if os.path.exists(p.path)]
    if paths_exist:
        red('CannotOverwriteError: The object(s) already exist(s). If you overwrite, please specify `--force` option.')
        for p in paths_exist:
            red('  '+p)
        sys.exit()


def getInput():
    import sys
    import termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] &= ~termios.ICANON
    new[3] &= ~termios.ECHO
    try:
        termios.tcsetattr(fd, termios.TCSANOW, new)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)
    return ch


deleteObjects = lambda paths: [shutil.rmtree(p.path) for p in paths if os.path.exists(p.path)]


# ---------------------------------------------------------------------------- #
# Mode
# ---------------------------------------------------------------------------- #
def make(filename):
    paths = getPathsFromOrgYaml(filename)
    if arg.force:
        deleteObjects(paths)
    else:
        checkNotExist(paths)

    green('Success: %d directories/files have been created!'%len(paths))
    makeObject = lambda p: os.makedirs(p.path) if p.type==sign_dir else pathlib.Path(p.path).touch()
    for p in paths:
        green((' '*2)+p.path)
        makeObject(p)


def remove(filename):
    paths = getPathsFromOrgYaml(filename)
    if arg.force:
        red('OptionError: The option \'--force\' cannot be specified in the remove mode.')
        sys.exit()
    else:
        deleteObjects(paths)
    green('Success: the directories/files have been removed!')


def reorg(filename):
    print('Future feature: The reorganizing will be implemented in the future release.')


def save(filename):
    def dirsToYaml(path):
        from os import listdir as ld
        from os.path import join
        from os.path import isfile
        import yaml
        def getObsAtCurrentDir(basePath,dirName):
            nbp = basePath + [dirName]
            obsAtCurrentDir = [ob if isfile(join(*nbp,ob)) else {ob:getObsAtCurrentDir(nbp,ob)} for ob in ld(join(*nbp))]
            return obsAtCurrentDir if len(obsAtCurrentDir) > 0 else [None]
        return getObsAtCurrentDir([],path)

    if os.path.exists(filename) and not arg.force:
        print('The file \'{}\' already exists. Do you overwrite with this saving file? [Y/n]:'.format(filename))
        if getInput() != 'Y':
            sys.exit()

    with open(filename, 'w') as file:
        yaml.dump(dirsToYaml('.'), file)
    green('Successfully Saved!')


# ---------------------------------------------------------------------------- #
# Entrypoint
# ---------------------------------------------------------------------------- #
def main():
    check()
    filename = 'mkdr-config.yml' if arg.name is None else arg.name
    if arg.remove:
        remove(filename)
    elif arg.reorg:
        reorg(filename)
    elif arg.save:
        save(filename)
    else:
        make(filename)


if __name__ == '__main__':
    main()


