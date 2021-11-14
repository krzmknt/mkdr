import os
import re
import sys
import yaml
import shutil
import pathlib
import termios
import tempfile
import argparse

from beak import Beak
from util import red
from util import green
from util import loadMetadata


class Mkdr:
    def __init__(self):
        from os.path import exists, join
        from os import getenv

        # Config path (local > env > defualt)
        localConfigPath = loadMetadata('localConfigPath')
        envConfigPath = loadMetadata('envConfigPath')
        defaultConfigPath = loadMetadata('defaultConfigPath')
        if exists(localConfigPath):
            self.configPath = localConfigPath
        else:
            self.configPath = getenv(envConfigPath, defaultConfigPath)

        # Beakfile (env > default)
        envBeakfile = loadMetadata('envBeakfileName')
        defaultBeakfile = loadMetadata('defaultBeakfileName')
        self.beakfileName = getenv(envBeakfile, defaultBeakfile)
        self.beakfilePath = join(self.configPath, self.beakfileName)

        # Ignorefile (enc > defualt)
        envIgnorefile = loadMetadata('envIgnorefileName')
        defaultIgnorefile = loadMetadata('defaultIgnorefileName')
        self.ignorefileName = getenv(envIgnorefile, defaultIgnorefile)
        self.ignorefilePath = join(self.configPath, self.ignorefileName)

        # Mkdr
        self.beaks = None
        self.beakfile = None
        self.ignorePatterns = None

    def __iter(self):
        return self.beaks

    def loadBeakfile(self):
        # TODO: json compatibility
        try:
            with open(self.beakfilePath) as beakfile:
                self.beakfile = yaml.load(beakfile, Loader=yaml.SafeLoader)
                if not isinstance(self.beakfile, list):
                    print(red('BeakfileFormatError: \'{}\''.format(self.beakfileName)))
                    sys.exit()
        except FileNotFoundError as err:
            print(red('BeakfileNotFoundError: No such file: \'{}\''.format(self.beakfileName)))
            sys.exit()
        except yaml.scanner.ScannerError as err:
            print(red('BeakfileFormatError: \'{}\'\n{}'.format(self.beakfileName, err)))
            sys.exit()


    def loadIgnorePatterns(self):
        from os.path import exists
        if exists(self.ignorefilePath):
            with open(self.ignorefilePath, 'r') as ignorefile:
                self.ignorePatterns = [p for p in ignorefile.read().split('\n') if p!='']


    def setBeaks(self):
        isDir = lambda path: isinstance(path, dict)
        getDirName = lambda d: list(d.keys())[0]
        getDirContents = lambda d: d[getDirName(d)]

        def getBeaksRcsvly(beakfile, basePath=['.']):
            beaks = []
            if beakfile is None:
                return []
            for path in beakfile:
                if isDir(path):
                    dirName = str(getDirName(path))
                    beak = Beak(Beak.DIR, os.path.join(*basePath,dirName))
                    if not beak.isMatched(self.ignorePatterns):
                        beaks.append(beak)
                        beaks += getBeaksRcsvly(getDirContents(path), basePath+[dirName])
                elif path is not None: # isFile(path)
                    path = str(path)
                    match = re.match('(.*){}([0-9]+)'.format(Beak.SEPARATOR), path)
                    if match:
                        path = match[1]
                        index = match[2]
                        beak = Beak(Beak.FILE, os.path.join(*basePath,path), index)
                        if not beak.isMatched(self.ignorePatterns):
                            beaks.append(beak)
                    else:
                        beak = Beak(Beak.FILE, os.path.join(*basePath,path), None)
                        if not beak.isMatched(self.ignorePatterns):
                            beaks.append(beak)
            return beaks

        def index(beaks):
            counter = {}
            indexedBeaks = []
            for beak in beaks:
                if beak.isFile():
                    counter.setdefault(beak.name,0)
                    counter[beak.name] += 1
                    beak.index = counter[beak.name]
                indexedBeaks.append(beak)
            return indexedBeaks

        beaks = getIndexedBeaks(getBeaksRcsvly(beakfile))
        self.beaks = Herd(beaks)
        return self.beaks


    def make(self, base='.', indexed=False):
        for beak in self.beaks:
            beak.make(base=base, indexed=indexed)
        return self.beaks


    def copyTemplate(self):
        for beak in self.beaks:
            src = Beak(Beak.FILE, os.path.join(self.configPath, 'template%s'%(beak.ext()) ))
            if beak.isFile() and src.exists():
                beak.copyFrom(src)


    def delete(self):
        for beak in self.beaks:
            if beak.exists():
                beak.remove()
        deletedDirs = [beak for beak in self.beaks if beak.exists()]
        return Herd(deletedDirs)


    def genBeakfile(self, path='.'):
        def getBeaksRcsvly(path):
            def getBeaks(path, beak):
                if os.path.isfile(os.path.join(path, beak)):
                    return beak
                else:
                    return {beak: getBeaksRcsvly(os.path.join(path, beak))}
            beaksInCD = [getBeaks(path, beak) for beak in os.listdir(path)]
            return beaksInCD if len(beaksInCD) > 0 else [None]
        self.beakfile = getYmlRcsvly(path)
        return self.beakfile


def main():
    print(__file__)

if __name__ == '__main__':
    main()



class Herd:
    def __init__(self, beaks):
        self.beaks = beaks
        self.n = len(beaks)

    def __iter__(self):
        return self.beaks

    def exist(self):
        return len(self.beaks) > 0



# --------------------------------------------------------------------------- #
# Check
# --------------------------------------------------------------------------- #
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

