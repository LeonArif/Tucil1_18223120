import time
import os


class Board:
    def __init__(self):
        self.row = 0
        self.col = 0
        self.colors = {}
        self.display = []

    
    def loadFromFile(self, fileName):
        self.row = 0
        self.col = 0
        self.colors = {}
        self.display = []

        with open(fileName, 'r') as file:
            lines = file.readlines()

        expected_len = None

        for y, line in enumerate(lines):
            row = list(line.strip('\n'))

            if expected_len is None:
                expected_len = len(row)
            elif len(row) != expected_len:
                raise ValueError("Setiap baris pada papan harus memiliki panjang yang sama.")

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

    def exhaustiveSearch(self, queenManager, fileName, progressCallback=None):
        colorsList = list(self.colors.values())
        k = len(colorsList)
        if k == 0:
            return False
        indexPerColor = [0] * k
    
        originalDisplay = [row[:] for row in self.display]
        tried = 0
        lastUpdate = time.time()

        while True:
            self.display = [row[:] for row in originalDisplay]
            queenManager.__init__(self)

            self.placeQueens(queenManager, indexPerColor)

            tried += 1
            if tried % 1000 == 0:
                print("tried", tried, "combinations:", indexPerColor)

            if progressCallback is not None:
                now = time.time()
                if now - lastUpdate >= 1.0:
                    positions = list(zip(queenManager.queensX, queenManager.queensY))
                    try:
                        progressCallback(positions, tried)
                    except Exception:
                        pass
                    lastUpdate = now

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
    
    def checkBoard(self):
        if self.row != self.col:
            return False
        if len(self.colors) != self.row or len(self.colors) != self.col:
            return False
        return True

    def solveExhaustive(self, queenManager, fileName):
        self.loadFromFile(fileName)

        if not self.checkBoard():
            print("Board tidak valid: papan harus NxN dan memiliki N warna unik.")
            return

        queenManager.__init__(self)

        start_time = time.time()
        ok, results = self.exhaustiveSearch(queenManager, fileName)
        end_time = time.time()
        elapsed = (end_time - start_time)*1000

        print(f"Waktu pencarian (exhaustive): {elapsed:.4f} ms")
        
        if not ok:
            print("Tidak ada solusi yang ditemukan (exhaustive).")
            return None

        for row in results:
            print("".join(row))

        self.writeSolutionToFile(fileName, elapsed, results, "exhaustive")

        return self.display
    
    def solveBacktrack(self, queenManager, fileName):
        self.loadFromFile(fileName)

        if not self.checkBoard():
            print("Board tidak valid: papan harus NxN dan memiliki N warna unik.")
            return

        queenManager.__init__(self)

        start_time = time.time()
        found = self.backtrack(0,queenManager)
        end_time = time.time()
        elapsed = (end_time - start_time)*1000

        print(f"Waktu pencarian (backtrack): {elapsed:.4f} ms")
        
        if not found:
            print("Tidak ada solusi yang ditemukan (backtrack).")
            return None

        for row in self.display:
            print("".join(row))

        self.writeSolutionToFile(fileName, elapsed, self.display, "backtrack")

        return self.display

    def writeSolutionToFile(self, fileName, elapsed, board_state, method_name):
        base = os.path.basename(fileName)
        name_no_ext, _ = os.path.splitext(base)

        dir_name = os.path.dirname(fileName)
        if not dir_name:
            dir_name = "test"

        os.makedirs(dir_name, exist_ok=True)

        output_path = os.path.join(dir_name, f"{name_no_ext}_solution.txt")

        try:
            with open(output_path, 'w') as f:
                f.write(f"Metode: {method_name}\n")
                f.write(f"Waktu pencarian: {elapsed:.4f} ms\n")
                for row in board_state:
                    f.write("".join(row) + "\n")
            print(f"Solusi disimpan di: {output_path}")
        except Exception as e:
            print(f"Gagal menulis file solusi: {e}")


