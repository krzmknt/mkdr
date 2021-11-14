import os
import shutil
from pathlib import Path

from util import loadMetadata



class Beak():
    FILE = loadMetadata('filesign')
    DIR = loadMetadata('dirsign')
    SEPARATOR = loadMetadata('separator')

    def __init__(self, type:[str], path:[str], index=None):
        self.path = Path(path)
        self.type = type
        self.index = index
        self.isFile = (self.type == Beak.FILE)
        self.isDir = (self.type == Beak.DIR)
        self.name = self.path.name
        self.stem = self.path.stem
        self.ext = self.path.suffix
        self.base = self.path.parent

    def __str__(self):
        return str(self.path)

    def indexed(self):
        if self.index is not None and self.index > 1:
            return '%s%s%s' % (self, Beak.SEPARATOR, self.index)
        else:
            return str(self)

    def exists(self):
        return self.path.exists()

    def join(self, cp):
        return self.path.joinpath(cp)

    def under(self, base):
        return Beak(self.type, os.path.join(base, self.name), self.index)

    def make(self, base='.', indexed=False):
        path = Path(base).joinpath(self.indexed() if indexed else self.path)
        if self.isFile:
            try:
                path.parent.mkdir(mode=511, parents=True, exist_ok=True)
                path.touch(mode=438, exist_ok=True)
            except:
                print('ERROR: File format error.')
        else:
            try:
                path.mkdir(mode=511, parents=True, exist_ok=True)
            except FileExistsError:
                print('ERROR: the file is already exists.')
            except:
                print('ERROR: File format error.')

    def remove(self):
        if self.isFile:
            os.remove(str(self))
        else:
            shutil.rmtree(str(self))

    def copyFrom(self, src):
        self.make()
        shutil.copyfile(src, self)

    def copyTo(self, dst):
        dstBeak = Beak(Beak.FILE, dst)
        dstBeak.make()
        shutil.copyfile(self, dstBeak)

    def linkFrom(self, src):
        self.remove()
        os.link(src, self.path)

    def linkTo(self, dst):
        dstBeak = Beak(Beak.FILE, dst)
        dstBeak.remove()
        os.link(self.path, dst)

    def isMatched(self, patterns):
        if patterns is None:
            return False

        name = self.name
        if self.isDir:
            name = name + '/'

        for pattern in patterns:
            if re.fullmatch(r'{}'.format(pattern), name, flags=re.IGNORECASE):
                return True
        return False



def main():
    print(__file__)

if __name__ == '__main__':
    main()


