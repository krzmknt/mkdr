import os
import sys
import yaml
import tempfile
from color import green


def export(arg, mkdr):
    if os.path.exists(mkdr.beakfileName) and not arg.force:
        print('The file \'{}\' already exists. '\
            'Do you overwrite with this saving file? [Y/n]:'.format(mkdr.beakfileName))
        if not getInput() == 'Y':
            sys.exit()

    mkdr.genBeakfile()
    mkdr.setBeaks()

    with tempfile.TemporaryDirectory(dir='.') as tmpDirPath:
        mkdr.make(base=tmpDirPath, indexed=True)
        beakfile = getBeakfile(tmpDirPath)
        with open(mkdr.beakfileName, 'w') as yml:
            yaml.dump(beakfile, yml)

    print(green('Success: Exported!'))


def main():
    pass

if __name__ == '__main__':
    main()

