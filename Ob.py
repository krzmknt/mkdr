import os
import shutil
from pathlib import Path


class Ob():
    FILE = 'f'
    DIR = 'd'
    SEPARATOR = '#'

    def __init__(self, type:[str], path:[str], index=None):
        self.path = Path(path)
        self.type = type
        self.index = index

    __str__ = lambda self: str(self.path)
    isFile  = lambda self: self.type == Ob.FILE
    isDir   = lambda self: self.type == Ob.DIR
    name    = lambda self: self.path.name
    stem    = lambda self: self.path.stem
    ext     = lambda self: self.path.suffix
    base    = lambda self: self.path.parent
    indexed = lambda self: str(self)+Ob.SEPARATOR+str(self.index) \
        if self.index is not None and self.index > 1 else str(self)
    exists  = lambda self: self.path.exists()
    join    = lambda self, cp: self.path.joinpath(cp)
    under   = lambda self, basePath: Ob(self.type, os.path.join(basePath,self.name()), self.index)

    match   = lambda self, pattern: self.path.match(pattern)
    glob    = lambda self, pattern: self.path.glob(pattern)

    def make(self, copyFrom:[str]=None):
        """
        1. Make the file or dir according to its type and path.
        2. Even if the objet already exists, it overwrites that.
        3.
        """
        if self.isFile():
            try:
                Path(self.base()).mkdir(mode=511, parents=True, exist_ok=True)
                self.path.touch(mode=438, exist_ok=True)
                # print('Created: {}'.format(self))
            except:
                print('ERROR: File format error.')
        else:
            try:
                self.path.mkdir(mode=511, parents=True, exist_ok=True)
                # print('Created: {}/'.format(self))
            except FileExistsError:
                print('ERROR: the file is already exists.')
            except:
                print('ERROR: File format error.')

    def copyFrom(self, src:[str]):
        if self.isDir():
            print('Error: `copyFrom` mehtod is available only for file type object.')
            raise
        self.make()
        shutil.copyfile(str(src), str(self))

    def copyTo(self, dst:[str]):
        if self.isDir():
            print('Error: `copyTo` mehtod is available only for file type object.')
            raise
        dstOb = Ob(Ob.FILE, dst)
        dstOb.make()
        shutil.copyfile(str(self), str(dstOb))

    def remove(self):
        if self.isFile():
            os.remove(str(self))
            # print('Removed: {}'.format(self))
        else:
            shutil.rmtree(str(self))
            # print('Removed: {}/'.format(self))




def main():
    obs = []
    obs.append(Ob(type=Ob.DIR, path='./1/2/3'))
    obs.append(Ob(type=Ob.FILE, path='./1/2-1/3/4'))

    for ob in obs:
        ob.make()

    for ob in obs:
        ob.remove()


if __name__ == '__main__':
    main()


