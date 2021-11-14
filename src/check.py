class Check:
    """
    exit: 何もしない/異常終了
    raise: 何もしない/例外
    bool: True/False を返す
    """
    def __init__(dscr, msg, cond, mode='exit'):
        self.msg = msg
        self.cond = cond

    def check(self, *args):
        if self.cond(*args):
            if mode == 'bool':
                return True
        else:
            if mode == 'exit':
                sys.exit()
            else if mode == 'raise':
                raise exception
            else:
                return False



def checkUser():
    if os.getuid() == 0:
        print(red('UserError: mkdr cannot be executed by superuser.'))
        sys.exit()

def checkMode():
    def hello():
        numOfModes = arg.compose + arg.export + arg.delete + arg.reorg

    if numOfModes > 1:
        print(red('ModeError: Only one mode can be specified.'))
        sys.exit()



def checkOptionCombination():
    if arg.export or arg.delete or arg.reorg:
        if arg.nut:
            print(red('Only compose mode suppourts --not-use-template option.'))
            sys.exit()

    if arg.force:
        if arg.reorg:
            print(red('Reorg mode does not suppourt --force option.'))
            sys.exit()

lambda modes=



