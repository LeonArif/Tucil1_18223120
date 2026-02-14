class QueenManager:
    def __init__(self, board):
        self.board = board
        self.queensX = []
        self.queensY = []
        self.occupied_colors = []
        self.total = 0

    def place(self, x, y):
        b = self.board
        self.queensX.append(x)
        self.queensY.append(y)
        self.occupied_colors.append(b.display[y][x])
        self.total += 1
        b.display[y][x] = '#'

    def removeLatest(self):
        b = self.board
        x = self.queensX.pop()
        y = self.queensY.pop()
        color = self.occupied_colors.pop()
        self.total -= 1
        b.display[y][x] = color
        return x, y
        