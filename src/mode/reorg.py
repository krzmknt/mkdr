import sys
import tempfile
from util import red
from util import green


def main():
    # Step 1/2. Link Dir to TmpDir
    # Get
    mkdr.genBeakfile()
    beaksFromDir = mkdr.setBeaks()

    with tempfile.TemporaryDirectory(dir='.') as tmpDirPath:
        # Link
        try:
            [beak.linkTo(beak.under(tmpDirPath).indexed()) for beak in mkdr.beaks if beak.isFile]
        except:
            print(red('CopyFileErrror: The specified file is not exists or another unknown error occured.'))
            sys.exit()

    # Step 2/2. Link back TmpDir to Dir (acc. beakfile)
        # Get
        mkdr.loadBeakfile()
        beaks = mkdr.setBeaks()

        # Check
        if all([beak.under(tmpDirPath).exists() for beak in mkdr if beak.isFile]):
            pass
        else:
            print(red('FileNotExistsError: Specified objects must exist.'))
            sys.exit()

        mkdr.beaks = beaksFromDir
        mkdr.delete()
        mkdr.beaks = beaks

        # Link back
        mkdr.delete()
        mkdr.make()
        try:
            [beak.linkFrom(beak.under(tmpDirPath).indexed()) for beak in mkdr if beak.isFile]
        except:
            print(red('CopyFileErrror: The object cannot be copied for some reason.'))
            sys.exit()

    # Log
    print(green('Success: The objects have been reorganized!'))


if __name__ == '__main__':
    pass

