red = lambda str:'\033[31m'+str+'\033[0m'
green = lambda str:'\033[32m'+str+'\033[0m'


def loadMetadata(key):
    from os.path import join, dirname
    import yaml
    with open(join(dirname(__file__), '../metadata.yml')) as f:
        metadata = yaml.load(f, Loader=yaml.SafeLoader)
    return metadata[key]


def getInput():
    import sys
    import termios
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
