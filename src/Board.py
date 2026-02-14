class Board:
    def __init__(self):
        self.row = 0
        self.col = 0
        self.colors = {}
        self.display = []

    
    def load_from_file(self, fileName):
        self.row = 0
        self.col = 0
        self.colors = {}
        self.display = []

        with open(fileName, 'r') as file:
            lines = file.readlines()

        for y, line in enumerate(lines):
            row = list(line.strip('\n'))
            self.display.append(row)
            for x, ch in enumerate(row):
                if ch not in self.colors:
                    self.colors[ch] = []
                self.colors[ch].append((x,y))

        self.row = len(self.display)
        self.col = len(self.display[0])

    def checkDiagonal(self, x,y):
        max_x = self.col
        max_y = self.row
        directions = [(-1, 1), (-1, -1), (1, 1), (1, -1)]

        for dy, dx in directions:
            ny = y + dy
            nx = x + dx

            if 0 <= nx < max_x and 0 <= ny < max_y:
                if self.display[ny][nx] == '#':
                    return False

        return True
    
    def placeQueens(self, queenManager, indexPerColor):
        i = 0
        for position in self.colors.values():
            x, y = position[indexPerColor[i]]
            queenManager.place(x,y)
            i += 1

    def validChecker(self):
        queenX = set()
        queenY = set()
        for i in range(self.row):
            for j in range(self.col):
                if self.display[i][j] == '#':
                    if i in queenY:
                        return False
                    
                    if j in queenX:
                        return False
                    
                    if not self.checkDiagonal(j,i):
                        return False
                    
                    queenX.add(j)
                    queenY.add(i)

        return True

    def moveQueen(self, arr):
        colorsList = list(self.colors.values())
        maxIndexPerColor = [len(colorsList[i]) for i in range(len(colorsList))]

        i = len(arr) -1
        while i >= 0:
            arr[i] += 1
            if arr[i] < maxIndexPerColor[i]:
                return True
            
            else:
                arr[i] = 0
                i -= 1

        return False


    # def exhaustiveSearch(self, queenManager, fileName):
    #     colorsList = list(self.colors.values())
    #     k = len(colorsList)
    #     if k == 0:
    #         return False
    #     indexPerColor = [0] * k
    #     originalDisplay = [row[:] for row in self.display]

    #     while True:
    #         self.display = [row[:] for row in originalDisplay]
    #         queenManager.__init__(self)
    #         self.placeQueens(queenManager, indexPerColor)
    #         if self.validChecker():
    #             return True, self.display
            
    #         if not self.moveQueen(indexPerColor):
    #             return False, originalDisplay

    def exhaustiveSearch(self, queenManager, fileName):
        colorsList = list(self.colors.values())
        k = len(colorsList)
        if k == 0:
            return False
        indexPerColor = [0] * k
        originalDisplay = [row[:] for row in self.display]

        tried = 0

        while True:
            self.display = [row[:] for row in originalDisplay]
            queenManager.__init__(self)
            self.placeQueens(queenManager, indexPerColor)

            tried += 1
            if tried % 1000 == 0:
                print("tried", tried, "combinations:", indexPerColor)

            if self.validChecker():
                print("found after", tried, "combinations")
                return True, self.display
            
            if not self.moveQueen(indexPerColor):
                print("no solution after", tried, "combinations")
                return False, originalDisplay

    def backtrack(self, row, queenManager):
        if row == self.row or len(queenManager.occupied_colors) == len(self.colors):
            return True

        for col in range(self.col):
            if (self.display[row][col] not in queenManager.occupied_colors and
                col not in queenManager.queensX and
                row not in queenManager.queensY and
                self.checkDiagonal(col,row)):

                queenManager.place(col, row)

                if self.backtrack(row + 1, queenManager):
                    return True

                queenManager.removeLatest()

        return False

    def solveExhaustive(self, queenManager, fileName):
        self.load_from_file(fileName)
        queenManager.__init__(self)
        _ , results = self.exhaustiveSearch(queenManager, fileName)
        for row in results:
            print("".join(row))

        return self.display
    
    def solveBacktrack(self, queenManager, fileName):
        self.load_from_file(fileName)
        queenManager.__init__(self)
        self.backtrack(0,queenManager)

        for row in self.display:
            print("".join(row))

        return self.display


