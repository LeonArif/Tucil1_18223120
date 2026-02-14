
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from Board import Board
from QueenManager import QueenManager

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


CELL_SIZE = 40
PADDING = 20
ANIMATION_DELAY_MS = 300


class BoardGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Colored Queens")

        self.board = Board()
        self.qm = QueenManager(self.board)
        self.filePath = None
        self.queenPositions = []
        self.currentAnimIndex = 0
        self.isSolving = False

        self.buildWidgets()

    def buildWidgets(self):
        topFrame = tk.Frame(self)
        topFrame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.fileEntry = tk.Entry(topFrame, width=40)
        self.fileEntry.pack(side=tk.LEFT, padx=5)

        browseButton = tk.Button(topFrame, text="Browse...", command=self.browseFile)
        browseButton.pack(side=tk.LEFT, padx=5)

        solveExhaustiveButton = tk.Button(topFrame, text="Solve Exhaustive",
                                          command=self.solveExhaustive)
        solveExhaustiveButton.pack(side=tk.LEFT, padx=5)

        solveBacktrackButton = tk.Button(topFrame, text="Solve Backtrack",
                                         command=self.solveBacktrack)
        solveBacktrackButton.pack(side=tk.LEFT, padx=5)

        clearButton = tk.Button(topFrame, text="Clear Board", command=self.clearBoard)
        clearButton.pack(side=tk.LEFT, padx=5)

        saveButton = tk.Button(topFrame, text="Save Image", command=self.saveImage)
        saveButton.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)

    def browseFile(self):
        path = filedialog.askopenfilename(
            initialdir=".",
            title="Select board file",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if path:
            self.filePath = path
            self.fileEntry.delete(0, tk.END)
            self.fileEntry.insert(0, path)
            try:
                self.board.load_from_file(path)
                self.resizeCanvas()
                self.drawBoard(backgroundOnly=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def resizeCanvas(self):
        w = self.board.col * CELL_SIZE + 2 * PADDING
        h = self.board.row * CELL_SIZE + 2 * PADDING
        self.canvas.config(width=w, height=h)

    def drawBoard(self, queens=None, backgroundOnly=False):
        self.canvas.delete("all")

        if not self.board.display:
            return

        color_map = {}
        palette = ["#f2f2f2", "#d9ead3", "#c9daf8", "#f4cccc",
                   "#fff2cc", "#d0e0e3", "#ead1dc", "#cfe2f3"]
        palette_idx = 0

        for y in range(self.board.row):
            for x in range(self.board.col):
                ch = self.board.display[y][x]

                if ch not in color_map:
                    color_map[ch] = palette[palette_idx % len(palette)]
                    palette_idx += 1

                x1 = PADDING + x * CELL_SIZE
                y1 = PADDING + y * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color_map[ch],
                    outline="black"
                )
                self.canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=ch,
                    font=("Arial", 14, "bold")
                )

        if not backgroundOnly and queens:
            for qx, qy in queens:
                self.drawQueen(qx, qy)

    def drawQueen(self, x, y):
        x1 = PADDING + x * CELL_SIZE + 4
        y1 = PADDING + y * CELL_SIZE + 4
        x2 = x1 + CELL_SIZE - 8
        y2 = y1 + CELL_SIZE - 8
        self.canvas.create_oval(x1, y1, x2, y2, fill="black")
        self.canvas.create_text(
            (x1 + x2) // 2,
            (y1 + y2) // 2,
            text="Q",
            fill="white",
            font=("Arial", 14, "bold")
        )

    def collectQueenPositionsFromManager(self):
        return list(zip(self.qm.queensX, self.qm.queensY))

    def startAnimation(self):
        self.drawBoard(backgroundOnly=True)
        self.currentAnimIndex = 0
        self.animateStep()

    def animateStep(self):
        if self.currentAnimIndex >= len(self.queenPositions):
            return
        qx, qy = self.queenPositions[self.currentAnimIndex]
        self.drawQueen(qx, qy)
        self.currentAnimIndex += 1
        self.after(ANIMATION_DELAY_MS, self.animateStep)

    def solveExhaustive(self):
        if self.isSolving:
            return

        path = self.fileEntry.get().strip()
        if not path:
            messagebox.showwarning("Warning", "Please select a board file first.")
            return

        self.isSolving = True

        t = threading.Thread(target=self.workerExhaustive, args=(path,), daemon=True)
        t.start()

    def workerExhaustive(self, path):
        try:
            self.board.load_from_file(path)
            self.qm = QueenManager(self.board)

            ok, _ = self.board.exhaustiveSearch(self.qm, path)
            positions = self.collectQueenPositionsFromManager() if ok else []
        except Exception as e:
            self.after(0, lambda: self.onExhaustiveDone(path, False, [], e))
            return

        self.after(0, lambda: self.onExhaustiveDone(path, ok, positions, None))

    def onExhaustiveDone(self, path, ok, positions, error):
        self.isSolving = False

        if error is not None:
            messagebox.showerror("Error", f"Exhaustive solve failed:\n{error}")
            return

        if not ok:
            messagebox.showinfo("Info", "No solution found (exhaustive).")
            return

        self.queenPositions = positions

        try:
            self.board.load_from_file(path)
            self.resizeCanvas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload board:\n{e}")
            return

        self.startAnimation()

    def solveBacktrack(self):
        path = self.fileEntry.get().strip()
        if not path:
            messagebox.showwarning("Warning", "Please select a board file first.")
            return

        try:
            self.board.load_from_file(path)
            self.resizeCanvas()
            self.qm = QueenManager(self.board)

            self.board.solveBacktrack(self.qm, path)

            self.queenPositions = self.collectQueenPositionsFromManager()

            self.board.load_from_file(path)
            self.startAnimation()
        except Exception as e:
            messagebox.showerror("Error", f"Backtrack solve failed:\n{e}")

    def clearBoard(self):
        if not self.board.display:
            return
        try:
            if self.filePath:
                self.board.load_from_file(self.filePath)
        except Exception:
            pass
        self.queenPositions = []
        self.qm = QueenManager(self.board)
        self.drawBoard(backgroundOnly=True)

    def saveImage(self):
        if not self.board.display or not self.queenPositions:
            messagebox.showwarning("Warning", "No solution to save yet.")
            return

        self.drawBoard(queens=self.queenPositions)

        os.makedirs("../output", exist_ok=True)
        ps_path = "../output/solution.ps"
        self.canvas.postscript(file=ps_path)

        if not PIL_AVAILABLE:
            messagebox.showinfo(
                "Saved",
                f"PostScript saved to {ps_path}\n"
                f"Install Pillow to auto-convert to PNG."
            )
            return

        try:
            img = Image.open(ps_path)
            png_path = "../output/solution.png"
            img.save(png_path)
            messagebox.showinfo("Saved", f"Image saved to {png_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert to PNG:\n{e}")


if __name__ == "__main__":
    app = BoardGUI()
    app.mainloop()