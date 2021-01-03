import display

class Menu:

    def __init__(self, viewSize=0, options=[]):
        self.viewSize = viewSize
        self.options = options
        self.offset = 0
        self.selected = 0

    def setViewSize(self, viewSize):
        self.viewSize = viewSize

    def print(self, top=0):
        # Determine the index of the last item to print
        end = len(self.options)
        if (self.viewSize > 0):
            end = min(end, self.offset + self.viewSize)

        # Determine the size of the terminal
        termSize = display.getTerminalSize()

        # Move the cursor to the starting location
        display.moveCursor(top, 0)

        # Print the desired number of menu entries
        for i in range(self.offset, end):
            o = self.options[i]

            # If the object implements getMenuText, use that
            # to get the text that should be displayed.
            # Otherwise just use the repr.
            if ("getMenuText" in dir(o)):
                text = self.options[i].getMenuText(termSize[1])
            else:
                text = str(self.options[i])

            if (len(text) > termSize[1]):
                text = text[:termSize[1]]

            # When printing the selected option, we should invert
            # the text to highlight it.
            if (i == self.selected):
                display.setInverted()

            display.clearLine()
            print(text)

            # If we inverted the text, switch it back before printing
            # the next option
            if (i == self.selected):
                display.clearAttributes()

    def selectionDown(self, n=1):
        self.selected += n
        if (self.selected >= len(self.options)):
            self.selected = len(self.options) - 1
        if (self.selected >= self.offset + self.viewSize):
            self.offset = self.selected - self.viewSize + 1

    def selectionUp(self, n=1):
        self.selected -= n
        if (self.selected < 0):
            self.selected = 0
        if (self.selected < self.offset):
            self.offset = self.selected

    def getSelection(self):
        return self.options[self.selected]
