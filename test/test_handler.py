import sys
sys.path.append('../')

from color import green
from color import red
import yaml
import os
import subprocess
from subprocess import PIPE

TESTSH = 'test.sh'
CHECKLIST = 'checklist.yml'

# keys
DSCR = 'description'
TESTID = 'testid'


def heading(title):
    w = 80 # The width for heading
    bar = '-'*w
    return '{}\n{}\n{}'.format(bar,title,bar)


def test(showLog=False):
    results = {}

    tests = [ob for ob in os.listdir() if os.path.isdir(ob) and not ob.startswith('.')]
    for testid in sorted(tests):
        result = None
        testShPath = os.path.join(testid,TESTSH)
        if os.path.exists(testShPath):
            result = subprocess.run(
                'sh {}'.format(testShPath),
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                text=True)
            results[testid] = True if result.stdout.strip()=='1' else False

        if showLog:
            print(heading('TEST ID: {}'.format(testid)))
            if testid in results.keys():
                with open(os.path.join(testid,'log'), 'r') as log:
                    for line in log.readlines():
                        print(line, end='')
            else:
                print('No test script exist.')
            # print()

    return results


def resultMsg(dscr, result):
    if result is None:
        return   'Untested: '+dscr
    if result:
        return green('PASS: '+dscr)
    else:
        return red('FAIL: '+dscr)


def main():
    results = test(showLog=True)

    try:
        with open(CHECKLIST) as f:
            checklist = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print(red('ERROR: \'{}\' is not found.'.format(CHECKLIST)))
        sys.exit()
    except:
        print(red('ERROR: \'{}\' format is invalid.'.format(CHECKLIST)))
        sys.exit()

    print()
    print(heading('CHECKLIST'))

    testid = lambda item: str(item[TESTID])
    for item in checklist:
        key = testid(item)
        if not key in results.keys():
            results[key] = None
        print(resultMsg(item[DSCR], results[key]))

    passed   = [item for item in checklist if results[str(item[TESTID])] == True]
    failed   = [item for item in checklist if results[str(item[TESTID])] == False]
    untested = [item for item in checklist if results[str(item[TESTID])] is None]

    print()
    print(heading('SUMMARY'))
    print('{} passed, {} failed, {} untested'.format(len(passed), len(failed), len(untested)))
    print()

    if len(passed) == len(checklist):
        return 1
    return 0


if __name__ == '__main__':
    main()
