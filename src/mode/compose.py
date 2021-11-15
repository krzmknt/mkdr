import sys
from util import red
from util import green


# --------------------------------------------------------------------------- #
# Check
# --------------------------------------------------------------------------- #
def checkNotExist(mkdr):
    existingBeaks = Herd([beak for beak in mkdr.beaks if beak.exists()])
    if existingBeaks.exist():
        print(red('FileExistError: The object(s) already exist(s).'))
        for beak in existingBeaks:
            print(red(' - %s' % beak))
        print('Hint: If you overwrite, please specify `-f|--force` option.')
        sys.exit()


def checkFileSemantics(mkdr):
    paths = [beak.path for beak in beaks]
    if len(paths) > len(set(paths)):
        dups = len(paths) - len(set(paths))
        print(red('ObjectDuplicationError: {} duplications have been found in \'{}\'.'.format(dups, mkdr.beakfile)))
        sys.exit()


# --------------------------------------------------------------------------- #
# Mode
# --------------------------------------------------------------------------- #
def main(arg, mkdr):
    # Get
    mkdr.loadBeakfile()
    obs = mkdr.setBeaks()

    # Check
    checkFileSemantics(obs)
    if arg.force:
        mkdr.delete()
    checkNotExist(obs)

    # Compose
    mkdr.make(indexed=False)
    if not arg.nut:
        mkdr.copyTemplate()

    # Log
    print(green('Success: %d directories/files have been created!' % mkdr.beaks.n))
    for beak in mkdr.beaks:
        print(green(' - {}'.format(beak)))


if __name__ == '__main__':
    pass
