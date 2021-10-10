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
from collections import namedtuple


# --------------------------------------------------------------------------- #
# Argument
# --------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force',
    action='store_true',
    help='Execute commands without confirmation.')

parser.add_argument('-n', '--name',
    type=str,
    help='Specify the configuration file name.')

parser.add_argument('-r', '--remove',
    action='store_true',
    help='Execute mkdr in the remove mode.')

parser.add_argument('-o', '--reorg',
    action='store_true',
    help="Execute mkdr in the reorg mode.")

parser.add_argument('-s', '--save',
    action='store_true',
    help="Execute mkdr in the save mode.")

arg = parser.parse_args()


# --------------------------------------------------------------------------- #
# Constant
# --------------------------------------------------------------------------- #
INDENT = 2
SIGD = 'd'
SIGF = 'f'


# --------------------------------------------------------------------------- #
# Color Text
# --------------------------------------------------------------------------- #
red = lambda str: print('\033[31m'+str+'\033[0m')
green =  lambda str: print('\033[32m'+str+'\033[0m')


# --------------------------------------------------------------------------- #
# Type
# --------------------------------------------------------------------------- #
Ob = namedtuple('Ob', ['type','path'])


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
    numOfModes = arg.remove + arg.reorg + arg.save
    if numOfModes > 1:
        red('ModeError: Only one mode can be specified.')
        sys.exit()


def checkOptionCombination():
    if arg.force:
        if arg.reorg:
            red('Reorg mode does not suppourt --force option.')
            sys.exit()


# --------------------------------------------------------------------------- #
# Module
# --------------------------------------------------------------------------- #
def getObsFromYml(filename):
    try:
        with open(filename) as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError as err:
        red('FileNotFoundError: No such file: \'{}\''.format(filename))
        sys.exit()

    isDir = lambda ob: isinstance(ob,dict)
    getDirName = lambda d: list(d.keys())[0]
    getDirContents = lambda d: d[getDirName(d)]

    def getObsRcsvly(yml, basePath):
        obs = []
        for ob in yml:
            if isDir(ob):
                dirName = getDirName(ob)
                obs.append(Ob(SIGD, os.path.join(*basePath,dirName)))
                obs += getObsRcsvly(getDirContents(ob), basePath+[dirName])
            elif ob is not None:
                obs.append(Ob(SIGF, os.path.join(*basePath,ob)))
        return obs
    return getObsRcsvly(yml, ['.'])


def checkNotExist(obs):
    obsExist = [ob.path for ob in obs if os.path.exists(ob.path)]
    if obsExist:
        red('CannotOverwriteError: The object(s) already exist(s). '\
            'If you overwrite, please specify `--force` option.')
        for ob in obsExist:
            red('  '+ob)
        sys.exit()


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


delObs = lambda obs: [shutil.rmtree(ob.path) for ob in obs \
    if os.path.exists(ob.path)]


# --------------------------------------------------------------------------- #
# Mode
# --------------------------------------------------------------------------- #
def make(filename):
    obs = getObsFromYml(filename)
    if arg.force:
        delObs(obs)
    else:
        checkNotExist(obs)

    green('Success: %d directories/files have been created!' % len(obs))
    makeOb = lambda ob: os.makedirs(ob.path) if ob.type == SIGD else \
        pathlib.Path(ob.path).touch()
    for ob in obs:
        green((' '*2)+ob.path)
        makeOb(ob)


def save(filename):
    def dirsToYaml(path):

        def getObsInCD(basePath,dirName):
            nbp = basePath + [dirName] # nextBasePath
            join = os.path.join
            isf = os.path.isfile
            ld = os.listdir
            obsInCD = [obn if isf(join(*nbp,obn)) else \
                {obn:getObsInCD(nbp,obn)} for obn in ld(join(*nbp))]
            return obsInCD if len(obsInCD) > 0 else [None]

        return getObsInCD([],path)

    if os.path.exists(filename) and not arg.force:
        print('The file \'{}\' already exists. '\
            'Do you overwrite with this saving file? [Y/n]:'.format(filename))
        if getInput() != 'Y':
            sys.exit()


    with open(filename, 'w') as file:
        yaml.dump(dirsToYaml('.'), file)
    green('Successfully Saved!')


def remove(filename):
    if not arg.force:
        print('Do you remove the objects? [Y/n]:'.format(filename))
        if getInput() != 'Y':
            sys.exit()
    delObs(getObsFromYml(filename))
    green('Success: the objects have been removed!')


def reorg(filename):
    print('Future feature: The reorganizing will be implemented in the '\
        'future release.')


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
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


