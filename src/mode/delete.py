import sys
from color import green


def delete(arg, mkdr):
    if not arg.force:
        beaksWillBeDeleted = Herd([beak for beak in self.beaks if beak.exists()])
        if not beaksWillBeDeleted.exist():
            print('No object.')
            sys.exit()

        for beak in beaksWillBeDeleted:
            print('- %s'%beak)
        print('Comfirmation: Do you delete the above objects? [Y/n]:')

        from util import getInput
        if not getInput() == 'Y':
            print('Cancelled.')
            sys.exit()

    mkdr.setBeaks()
    deletedDirs = mkdr.deleteDirs()

    if deletedDirs.exist:
        print(green('Success: The objects have been deleted!'))
    else:
        print('No object.')



def main():
    pass

if __name__ == '__main__':
    main()

