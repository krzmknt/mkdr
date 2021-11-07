# --------------------------------------------------------------------------- #
# mkdr.py
# --------------------------------------------------------------------------- #
# Author: @krzmknt
# Notability: [mkdr](https://notability.com/n/24FejozMK6WPk3qPDUNfXv)


# --------------------------------------------------------------------------- #
# Package
# --------------------------------------------------------------------------- #
import argparse
import os
import pathlib
import re
import shutil
import sys
import tempfile
import termios
import yaml

from Ob import Ob
from color import green, red


# --------------------------------------------------------------------------- #
# Argument
# --------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()

# Mode
parser.add_argument('-c','--compose', action='store_true',
    help="Comose objects according to a config file.")
parser.add_argument('-d', '--delete', action='store_true',
    help='Execute mkdr in the delete mode.')
parser.add_argument('-r', '--reorg', action='store_true',
    help="Execute mkdr in the reorg mode.")
parser.add_argument('-e', '--export', action='store_true',
    help="Export the current objects organization to mkdr config file.")
parser.add_argument('--configure', action='store_true',
    help="Show the mkdr configuration file path.")

# Option
parser.add_argument('-f', '--force', action='store_true',
    help='Execute commands without confirmation.')
parser.add_argument('-n', '--name', type=str,
    help='Specify the configuration file name.')
parser.add_argument('--nut', '--not-use-template', action='store_true',
    help="Compose objects with zero byte files.")

arg = parser.parse_args()


# --------------------------------------------------------------------------- #
# Constant
# --------------------------------------------------------------------------- #
MKDR_CONFIG_DIRNAME = os.environ.get('MKDR_CONFIG_DIRNAE', '.mkdr')

MKDR_CONFIG_PATH = os.environ.get('MKDR_CONFIG_PATH', '~/.config/mkdr/')
if os.path.exists(MKDR_CONFIG_DIRNAME):
    MKDR_CONFIG_PATH = MKDR_CONFIG_DIRNAME

MKDR_COMPOSE_FILENAME = os.environ.get('MKDR_COMPOSE_FILENAME', 'mkdrcompose.yml')

MKDR_IGNORE_FILENAME = os.environ.get('MKDR_IGNORE_FILENAME', '.mkdrignore')


# --------------------------------------------------------------------------- #
# Global Variables
# --------------------------------------------------------------------------- #
ignorePatterns = None


# --------------------------------------------------------------------------- #
# Check
# --------------------------------------------------------------------------- #
def check():
    checkUser()
    checkMode()
    checkOptionCombination()


def checkUser():
    if os.getuid() == 0:
        print(red('UserError: mkdr cannot be executed by superuser.'))
        sys.exit()


def checkMode():
    numOfModes = arg.compose + arg.export + arg.delete + arg.reorg + arg.configure
    if numOfModes > 1:
        print(red('ModeError: Only one mode can be specified.'))
        sys.exit()


def checkOptionCombination():
    if arg.export or arg.delete or arg.reorg:
        if arg.nut:
            print(red('Only compose mode suppourts --not-use-template option.'))
            sys.exit()

    if arg.force:
        if arg.reorg:
            print(red('Reorg mode does not suppourt --force option.'))
            sys.exit()

    if arg.configure:
        if arg.nut or arg.force or arg.name:
            print(red('Configure mode does not suppourt any other option.'))
            sys.exit()


def checkNotExist(obs):
    existingObs = [ob for ob in obs if ob.exists()]
    if existingObs:
        print(red('FileExistError: The object(s) already exist(s).'))
        for ob in existingObs:
            print(red(' - '+str(ob)))
        print('Hint: If you overwrite, please specify `-f|--force` option.')
        sys.exit()


def checkExist(obs):
    notExistingObs = [ob for ob in obs if not ob.exists()]
    if notExistingObs:
        print(red('FileNotExistError: The objects are not exists.'))
        for ob in notExistingObs:
            print(red('  '+str(ob)))
        sys.exit()


def checkComposeFileSemantics(obs):
    paths = [str(ob) for ob in obs]
    if len(paths) > len(set(paths)):
        print(red('ObjectDuplicationError: {} duplications have been found in \'{}\'.'.format(dups,MKDR_COMPOSE_FILENAME)))
        sys.exit()


# --------------------------------------------------------------------------- #
# Load ignorefile
# --------------------------------------------------------------------------- #
def loadIgnorePatterns():
    """
    Load ignore file placed current directory.
    If not exists, load from MKDR_CONFIG_PATH
    """
    # Get filepath
    global ignorePatterns
    ignoreFilePath = MKDR_IGNORE_FILENAME
    if not os.path.exists(ignoreFilePath):
        ignoreFilePath = os.path.join(MKDR_CONFIG_PATH, MKDR_IGNORE_FILENAME)

    # Load
    if ignorePatterns is None and os.path.exists(ignoreFilePath):
        with open(ignoreFilePath, 'r') as ignoreFile:
            ignoreData = ignoreFile.read()
            ignorePatterns = [ip for ip in ignoreData.split('\n') if not ip=='']


# --------------------------------------------------------------------------- #
# Module
# --------------------------------------------------------------------------- #
def loadYml():
    try:
        with open(MKDR_COMPOSE_FILENAME) as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
            if not isinstance(yml,list):
                print(red('InvalidFormatError: \'{}\''.format(MKDR_COMPOSE_FILENAME)))
                sys.exit()
    except FileNotFoundError as err:
        print(red('FileNotFoundError: No such file: \'{}\''.format(MKDR_COMPOSE_FILENAME)))
        sys.exit()
    except yaml.scanner.ScannerError as err:
        print(red('InvalidFormatError: \'{}\'\n{}'.format(MKDR_COMPOSE_FILENAME, err)))
        sys.exit()
    return yml


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
                ob = Ob(Ob.DIR, os.path.join(*basePath,dirName))
                if not ob.isMatched(ignorePatterns):
                    obs.append(ob)
                    obs += getObsRcsvly(getDirContents(path), basePath+[dirName])
            elif path is not None: # isFile(path)
                path = str(path)
                m = re.match('(.*){}([0-9]+)'.format(Ob.SEPARATOR), path)
                if m:
                    path = m[1]
                    index = m[2]
                    ob = Ob(Ob.FILE, os.path.join(*basePath,path), index)
                    if not ob.isMatched(ignorePatterns):
                        obs.append(ob)
                else:
                    ob = Ob(Ob.FILE, os.path.join(*basePath,path), None)
                    if not ob.isMatched(ignorePatterns):
                        obs.append(ob)
        return obs

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

    obs = getObsRcsvly(yml, ['.'])
    indexedObs = getIndexedObs(obs)
    return indexedObs


def composeDirs(obs, basePath='.', indexed=False):
    for ob in obs:
        ob.make(basePath=basePath, indexed=indexed)
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


def getYmlFromDirs(path='.'):
    def getYmlRcsvly(path):
        gp = lambda obn: os.path.join(path, obn)
        ld = os.listdir(path) # .mkdrignore
        obsInCD = [obn if os.path.isfile(gp(obn)) else {obn: getYmlRcsvly(gp(obn))} for obn in ld]
        return obsInCD if len(obsInCD) > 0 else [None]

    yml = getYmlRcsvly(path)
    return yml


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
def compose():
    # Get
    yml = loadYml()
    obs = getObsFromYml(yml)

    # Check
    checkComposeFileSemantics(obs)
    if arg.force:
        deleteDirs(obs)
    checkNotExist(obs)

    # Compose
    composedObs = composeDirs(obs, indexed=False)
    if not arg.nut:
        copyTemplate(obs)

    # Log
    print(green('Success: %d directories/files have been created!' % len(composedObs)))
    for ob in composedObs:
        print(green(' - {}'.format(ob)))


def export():
    # Confirm
    if os.path.exists(MKDR_COMPOSE_FILENAME) and not arg.force:
        print('The file \'{}\' already exists. '\
            'Do you overwrite with this saving file? [Y/n]:'.format(MKDR_COMPOSE_FILENAME))
        if getInput() != 'Y':
            sys.exit()

    # Get
    yml = getYmlFromDirs('.')
    obs = getObsFromYml(yml)
    with tempfile.TemporaryDirectory(dir='.') as tmpDirPath:
        composeDirs(obs, basePath=tmpDirPath, indexed=True)

        # Export
        yml = getYmlFromDirs(tmpDirPath)
        with open(MKDR_COMPOSE_FILENAME, 'w') as f:
            yaml.dump(yml, f)

    # Log
    print(green('Success: Exported!'))


def delete():
    # Comfirm
    if not arg.force:
        print('Comfirmation: Do you delete the objects? [Y/n]:'.format(MKDR_COMPOSE_FILENAME))
        if getInput() != 'Y':
            sys.exit()

    # Get
    yml = loadYml()
    obs = getObsFromYml(yml)

    # Delete
    deletedObs = deleteDirs(obs)

    # Log
    if len(deletedObs) > 0:
        print(green('Success: The objects have been deleted!'))
        for ob in deletedObs:
            print(green(' - {}'.format(ob)))
    else:
        print('No object.')


def reorg():
    with tempfile.TemporaryDirectory(dir='.') as tmpDirPath:
    # Step 1/2. Link Dir to TmpDir
        # Get
        ymlFromDir = getYmlFromDirs('.')
        obsFromDir = getObsFromYml(ymlFromDir)

        # Link
        try:
            [ob.linkTo(ob.under(tmpDirPath).indexed()) for ob in obsFromDir if ob.isFile()]
        except:
            print(red('CopyFileErrror: The specified file is not exists or another unknown error occured.'))
            sys.exit()

    # Step 2/2. Link back TmpDir to Dir (acc. mkdrcompose.yml)
        # Get
        yml = loadYml()
        obs = getObsFromYml(yml)

        # Check
        if all([ob.under(tmpDirPath).exists() for ob in obs if ob.isFile()]):
            pass
        else:
            print(red('FileNotExistsError: Specified objects must exist.'))
            sys.exit()

        # Link back
        deleteDirs(obs)
        composeDirs(obs)
        try:
            [ob.linkFrom(ob.under(tmpDirPath).indexed()) for ob in obs if ob.isFile()]
        except:
            print(red('CopyFileErrror: The object cannot be copied for some reason.'))
            sys.exit()

    # Log
    print(green('Success: The objects have been reorganized!'))


def configure():
    # TODO: どうやって設定変えるのか。アプリで変えさせたい。
    print('configpath [{}]:'.format(MKDR_CONFIG_PATH))
    print('composefile [{}]:'.format(MKDR_COMPOSE_FILENAME))
    print('ignorefile [{}]:'.format(MKDR_IGNORE_FILENAME))


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def main():
    """
    1. Check arguments
    2. Configure (if it is the case)
    3. Set global variables
    4. Execute the main procedure
    """
    check()

    if arg.configure:
        configure()
        sys.exit()

    if arg.name:
        global MKDR_COMPOSE_FILENAME
        MKDR_COMPOSE_FILENAME = arg.name
    loadIgnorePatterns()

    if arg.export:
        export()
    elif arg.delete:
        delete()
    elif arg.reorg:
        reorg()
    else:
        compose()


if __name__ == '__main__':
    main()

