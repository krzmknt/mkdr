# coding: utf-8

import os
import sys
import argparse
from mkdr import Mkdr
from util import red
from util import loadMetadata


def getArg():
    parser = argparse.ArgumentParser()

    # mkdr
    parser = argparse.ArgumentParser(
        description='Organize your directory construction according to a specifiacation.',
        prog = 'mkdr',
        usage = "%(prog)s",
        epilog = None
    )
    # parser.add_argument('-v', '--version', action='store_true',help='display the current version')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s version '+str(loadMetadata('version')))
    subparsers = parser.add_subparsers(
        dest = 'mode',
        help = "sub-command help"
    )

    # compose
    parser_c = subparsers.add_parser('compose', aliases=['c'], help='Compose objects according to a beakfile.')
    parser_c.add_argument('beakfile', type=str, nargs='?', default='mkdrcompose.yml', help='Specify a path of an arbitrary beakfile.')
    parser_c.add_argument('-f', '--force', action='store_true', help='If any composing objecst already exists, mkdr overwrites that.')
    parser_c.add_argument('-n', '--not-use-template', action='store_true', help='Make zero byte files, even if its templates exist.')
    parser_c.set_defaults(beakfile = 'mkdrcompose.yml')

    # export
    parser_e = subparsers.add_parser('export', aliases=['e'], help='Export the current objects organization to a beakfile.')
    parser_c.add_argument('beakfile', type=str, nargs='?', default='mkdrcompose.yml', help='Specify a path of an arbitrary beakfile.')
    parser_e.add_argument('-f', '--force', action='store_true', help='If the beakfile already exists, mkdr overwrites that.')

    # delete
    parser_d = subparsers.add_parser('delete', aliases=['d'], help='Delete objects according to a beakfile.')
    parser_c.add_argument('beakfile', type=str, nargs='?', default='mkdrcompose.yml', help='Specify a path of an arbitrary beakfile.')
    parser_d.add_argument('-f', '--force', action='store_true', help='Delete the objecsts without confirmation')

    # reorg
    parser_r = subparsers.add_parser('reorg', aliases=['r'], help='Reorganize objects according to a beakfile.')
    parser_c.add_argument('beakfile', type=str, nargs='?', default='mkdrcompose.yml', help='Specify a path of an arbitrary beakfile.')
    parser_r.add_argument('passphrase', help='login with this passphrase')

    arg = parser.parse_args()

    return arg



def main():
    # Check if not a superuser
    if os.getuid() == 0:
        print(red('UserError: mkdr cannot be executed by superuser.'))
        sys.exit()

    arg = getArg()
    if arg.mode is None:
        arg.mode = loadMetadata('defaultMode')
        arg.beakfile = None

    mkdr = Mkdr()
    mode = [mode.rstrip('.py') for mode in os.listdir(os.path.join(os.path.dirname(__file__), 'mode')) if arg.mode[0] == mode[0]][0]

    from importlib import import_module
    print(mode)
    import_module('mode.'+mode).main(arg, mkdr)



if __name__ == '__main__':
    main()

