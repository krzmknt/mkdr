# --------------------------------------------------------------------------- #
# mkdr.py
# --------------------------------------------------------------------------- #
# Author: @krzmknt
# Notability: [mkdr](https://notability.com/n/24FejozMK6WPk3qPDUNfXv)



# --------------------------------------------------------------------------- #
# Package
# --------------------------------------------------------------------------- #
import yaml
import pathlib
import os
import argparse
import shutil
import sys
import termios
import tempfile
import re
from collections import namedtuple
from Ob import Ob



# --------------------------------------------------------------------------- #
# Argument
# --------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()


# MODE
parser.add_argument('-c','--compose',
    action='store_true',
    help="Comose objects according to a config file.")

parser.add_argument('-d', '--delete',
    action='store_true',
    help='Execute mkdr in the delete mode.')

parser.add_argument('-r', '--reorg',
    action='store_true',
    help="Execute mkdr in the reorg mode.")

parser.add_argument('-e', '--export',
    action='store_true',
    help="Export the current objects organization to mkdr config file.")


# OPTION
parser.add_argument('--config',
    action='store_true',
    help="Show the mkdr configuration file path.")

parser.add_argument('-f', '--force',
    action='store_true',
    help='Execute commands without confirmation.')

parser.add_argument('-n', '--name',
    type=str,
    help='Specify the configuration file name.')

parser.add_argument('--nut', '--not-use-template',
    action='store_true',
    help="Compose objects with zero byte files.")

arg = parser.parse_args()


# --------------------------------------------------------------------------- #
# Constant
# --------------------------------------------------------------------------- #
INDENT = 2

MKDR_CONFIG_PATH = os.environ.get('MKDR_CONFIG_PATH', '~/.config/mkdr/')
MKDR_CONFIG_DIRNAME = os.environ.get('MKDR_CONFIG_DIRNAE', './mkdr')
if os.path.exists(MKDR_CONFIG_DIRNAME):
    MKDR_CONFIG_PATH = os.path.join('.', MKDR_CONFIG_DIRNAME)
MKDR_COMPOSE_FILENAME = os.environ.get('MKDR_COMPOSE_FILENAME', 'mkdrcompose.yml')
MKDR_IGNORE_FILENAME = os.environ.get('MKDR_IGNORE_FILENAME', '.mkdrignore')


# --------------------------------------------------------------------------- #
# Color Text
# --------------------------------------------------------------------------- #
red = lambda str: print('\033[31m'+str+'\033[0m')
green =  lambda str: print('\033[32m'+str+'\033[0m')



# --------------------------------------------------------------------------- #
# Check
# --------------------------------------------------------------------------- #
def check():
    checkUser()
    checkMode()
    checkOptionCombination()


def checkUser():
    if os.getuid() == 0:
        red('UserError: Running mkdr as root is not supported.')
        sys.exit()


def checkMode():
    numOfModes = arg.compose + arg.export + arg.delete + arg.reorg
    if numOfModes > 1:
        red('ModeError: Only one mode can be specified.')
        sys.exit()


def checkOptionCombination():
    if arg.export or arg.delete or arg.reorg:
        if arg.nut:
            red('Only compose mode suppourts --not-use-template option.')
            sys.exit()

    if arg.force:
        if arg.reorg:
            red('Reorg mode does not suppourt --force option.')
            sys.exit()

    if arg.config:
        if arg.reorg:
            red('Reorg mode does not suppourt --force option.')
            sys.exit()


def checkNotExist(obs):
    existingObs = [ob for ob in obs if ob.exists()]
    if existingObs:
        red('FileExistError: The object(s) already exist(s).')
        for ob in existingObs:
            red(' - '+str(ob))
        print('Hint: If you overwrite, please specify `-f|--force` option.')
        sys.exit()


def checkExist(obs):
    notExistingObs = [ob for ob in obs if not ob.exists()]
    if notExistingObs:
        red('FileNotExistError: The objects are not exists.')
        for ob in notExistingObs:
            red('  '+str(ob))
        sys.exit()


def checkComposeFileSemantics(obs):
    # Check duplication
    paths = [str(ob) for ob in obs]
    dups = len(paths) - len(set(paths))
    return dups




# --------------------------------------------------------------------------- #
# Load Ignore File
# --------------------------------------------------------------------------- #
def loadIgnoreFile():
    """
    Load ignore file placed current directory.
    If not exists, load from MKDR_CONFIG_PATH
    """
    ignore = []
    return ignore

# --------------------------------------------------------------------------- #
# Module
# --------------------------------------------------------------------------- #
def loadYml(filename):
    try:
        with open(filename) as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
            if not isinstance(yml,list):
                red('InvalidFormatError: \'{}\''.format(filename))
                sys.exit()

    except FileNotFoundError as err:
        red('FileNotFoundError: No such file: \'{}\''.format(filename))
        sys.exit()
    except yaml.scanner.ScannerError as err:
        red('InvalidFormatError: \'{}\'\n{}'.format(filename, err))
        sys.exit()

    return yml


def getIndexedObs(obs):
    counter = {}
    indexedObs = []
    for ob in obs:
        if ob.isFile():
            counter.setdefault(ob.name(),0)
            counter[ob.name()] += 1
            ob.index = counter[ob.name()]
        indexedObs.append(ob)
    return indexedObs


def getObsFromYml(yml):
    isDir = lambda path: isinstance(path, dict)
    getDirName = lambda d: list(d.keys())[0]
    getDirContents = lambda d: d[getDirName(d)]

    def getObsRcsvly(yml, basePath):
        obs = []
        if yml is None:
            return []
        for path in yml:
            if isDir(path):
                dirName = str(getDirName(path))
                obs.append(Ob(Ob.DIR, os.path.join(*basePath,dirName)))
                obs += getObsRcsvly(getDirContents(path), basePath+[dirName])
            elif path is not None: # isFile(path)
                path = str(path)
                m = re.match('^(.*){}([0-9]+)'.format(Ob.SEPARATOR), path)
                if m:
                    path = m[1]
                    index = m[2]
                    obs.append(Ob(Ob.FILE, os.path.join(*basePath,path), index))
                else:
                    obs.append(Ob(Ob.FILE, os.path.join(*basePath,path), None))
        return obs
    return getIndexedObs(getObsRcsvly(yml, ['.']))


def composeDirs(obs):
    for ob in obs:
        ob.make()
    return obs


def copyTemplate(obs):
    for ob in obs:
        src = Ob(Ob.FILE, os.path.join(MKDR_CONFIG_PATH, 'template{}'.format(ob.ext()) ))
        if ob.isFile() and src.exists():
            ob.copyFrom(src)


def deleteDirs(obs):
    deletedDirs = []
    for ob in obs:
        if ob.exists():
            ob.remove()
            deletedDirs.append(ob)
    return deletedDirs


def getYmlFromDirs(path):
    def getYmlRcsvly(path):
        gp = lambda obn: os.path.join(path, obn)
        ld = os.listdir(path) # .mkdrignore
        obsInCD = [obn if os.path.isfile(gp(obn)) else {obn: getYmlRcsvly(gp(obn))} for obn in ld]
        return obsInCD if len(obsInCD) > 0 else [None]

    yml = getYmlRcsvly(path)
#    obs = getObsFromYml(yml)
#    for ob in obs:
#        print(ob.indexed())

    return yml


def dumpYml(yml, filename):
    with open(filename, 'w') as f:
        yaml.dump(yml, f)


def getInput():
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


# --------------------------------------------------------------------------- #
# Mode
# --------------------------------------------------------------------------- #
def compose(filename):
    obs = getObsFromYml(loadYml(filename))
    dups = checkComposeFileSemantics(obs)
    if dups > 0:
        red('ObjectDuplicationError: {} duplication have been found in \'{}\'.'.format(dups,filename))
        sys.exit()

    if arg.force:
        deleteDirs(obs)
    else:
        checkNotExist(obs)

    composedObs = composeDirs(obs)
    if not arg.nut:
        copyTemplate(obs)
    green('Success: %d directories/files have been created!' % len(composedObs))
    for ob in composedObs:
        green(' - {}'.format(ob))


def export(filename):
    if os.path.exists(filename) and not arg.force:
        print('The file \'{}\' already exists. '\
            'Do you overwrite with this saving file? [Y/n]:'.format(filename))
        if getInput() != 'Y':
            sys.exit()

    dumpYml(getYmlFromDirs('.'), filename)
    green('Success: Exported!')


def delete(filename):
    if not arg.force:
        print('Comfirmation: Do you delete the objects? [Y/n]:'.format(filename))
        if getInput() != 'Y':
            print('')
            sys.exit()

    deletedObs = deleteDirs(getObsFromYml(loadYml(filename)))
    if len(deletedObs) > 0:
        green('Success: The objects have been deleted!')
        for ob in deletedObs:
            green(' - {}'.format(ob))
    else:
        print('No object.')


def reorg(filename):
    obsFromDir = getObsFromYml(getYmlFromDirs('.'))

    with tempfile.TemporaryDirectory(dir='.') as tmpDirPath:
        # Step 1. Dir to TmpDir
        try:
            [ob.copyTo(ob.under(tmpDirPath).indexed()) for ob in obsFromDir if ob.isFile()]
        except:
            red('CopyFileErrror: The specified file is not exists or another unknown error occured.')
            sys.exit()

        # Step 2. TmpDir to Dir (acc. mkdrcompose.yml)
        obs = getObsFromYml(loadYml(filename))

        if all([ob.under(tmpDirPath).exists() for ob in obs if ob.isFile()]):
            pass
        else:
            red('FileNotExistsError: Specified object must exist.')
            sys.exit()

        deleteDirs(obs)
        composeDirs(obs)
        try:
            [ob.copyFrom(ob.under(tmpDirPath).indexed()) for ob in obs if ob.isFile()]
        except:
            red('CopyFileErrror: The object cannot be copied for some reason.')
            sys.exit()
        green('Success: The objects have been reorganized!')


def config():
    print('Config path: {}'.format(MKDR_CONFIG_PATH))
    print('Config dirname: {}'.format(MKDR_CONFIG_DIRNAME))
    print('Compose filename: {}'.format(MKDR_COMPOSE_FILENAME))
    print('Ignore filename: {}'.format(MKDR_IGNORE_FILENAME))


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def main():
    check()
    filename = MKDR_COMPOSE_FILENAME if arg.name is None else arg.name
    ignore = loadIgnoreFile()
    if arg.delete:
        delete(filename)
    elif arg.reorg:
        reorg(filename)
    elif arg.export:
        export(filename)
    elif arg.config:
        config()
    else:
        compose(filename)


if __name__ == '__main__':
    main()


