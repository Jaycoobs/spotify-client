import shutil

def sequence(char, args=None):
    if (args == None):
        print("\033[" + char, end="")
    else:
        print("\033[" + ";".join([str(a) for a in args]) + char, end="")

def moveCursor(r, c):
    sequence("H", (r, c))

def cursorBackward(n):
    sequence("D", (n,))

def clearLine():
    sequence("K")
    cursorBackward(999)

def clearScreen():
    sequence("s")
    sequence("J")
    sequence("u")

def printAt(r, c, text):
    moveCursor(r, c)
    print(text, end="")

def hideCursor():
    sequence("?25l", ())

def showCursor():
    sequence("?25h", ())

def setBold():
    sequence("m", (1,))

def setInverted():
    sequence("m", (7,))

def clearAttributes():
    sequence("m", (0,))

def getTerminalSize():
    size = shutil.get_terminal_size()
    return (size[1], size[0])
