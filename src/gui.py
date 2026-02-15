
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from Board import Board
from QueenManager import QueenManager

try:
    from PIL import Image, ImageGrab
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
        self.configure(padx=20, pady=20)

        self.board = Board()
        self.qm = QueenManager(self.board)
        self.filePath = None
        self.queenPositions = []
        self.currentAnimIndex = 0
        self.isSolving = False
        self.baseDisplay = []

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
                self.board.loadFromFile(path)
                self.baseDisplay = [row[:] for row in self.board.display]
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

        source = self.baseDisplay if self.baseDisplay else self.board.display

        color_map = {}
        palette = ["#f2f2f2", "#d9ead3", "#c9daf8", "#f4cccc",
                   "#fff2cc", "#d0e0e3", "#ead1dc", "#cfe2f3"]
        palette_idx = 0

        for y in range(self.board.row):
            for x in range(self.board.col):
                ch = source[y][x]

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
            self.board.loadFromFile(path)
            # Validasi papan sebelum mulai exhaustive search
            if not self.board.checkBoard():
                raise ValueError("Board tidak valid: papan harus NxN dan memiliki N warna unik.")

            self.baseDisplay = [row[:] for row in self.board.display]
            self.qm = QueenManager(self.board)

            def progressCallback(positions, tried):
                self.after(0, lambda p=positions, t=tried: self.onExhaustiveProgress(p, t))

            start_time = time.time()
            ok, board_state = self.board.exhaustiveSearch(self.qm, path, progressCallback)
            elapsed = (time.time() - start_time)*1000

            if ok:
                print(f"Waktu pencarian (exhaustive): {elapsed:.4f} ms")
                try:
                    self.board.writeSolutionToFile(path, elapsed, board_state, "exhaustive")
                except Exception as e:
                    print(f"Gagal menyimpan solusi exhaustive: {e}")

            positions = self.collectQueenPositionsFromManager() if ok else []
        except Exception as e:
            # Ikat exception ke argumen default lambda agar aman di Python 3.11+
            self.after(0, lambda err=e: self.onExhaustiveDone(path, False, [], err))
            return

        self.after(0, lambda: self.onExhaustiveDone(path, ok, positions, None))

    def onExhaustiveProgress(self, positions, tried):
        self.queenPositions = positions
        self.drawBoard(queens=self.queenPositions)

    def onExhaustiveDone(self, path, ok, positions, error):
        self.isSolving = False

        if error is not None:
            messagebox.showerror("Invalid Board", "Board harus NxN dan memiliki N warna unik.")
            return

        if not ok:
            messagebox.showinfo("Info", "No solution found (exhaustive).")
            return

        self.queenPositions = positions

        try:
            self.board.loadFromFile(path)
            self.baseDisplay = [row[:] for row in self.board.display]
            self.resizeCanvas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload board:\n{e}")
            return
        self.drawBoard(queens=self.queenPositions)

    def solveBacktrack(self):
        path = self.fileEntry.get().strip()
        if not path:
            messagebox.showwarning("Warning", "Please select a board file first.")
            return

        try:
            self.board.loadFromFile(path)
            if not self.board.checkBoard():
                messagebox.showerror("Invalid Board", "Board harus NxN dan memiliki N warna unik.")
                return

            self.baseDisplay = [row[:] for row in self.board.display]
            self.resizeCanvas()
            self.qm = QueenManager(self.board)
            result = self.board.solveBacktrack(self.qm, path)

            # Jika tidak ada solusi, tampilkan pesan di GUI dan berhenti
            if result is None or not self.qm.queensX:
                messagebox.showinfo("Info", "No solution found (backtrack).")
                return

            self.queenPositions = self.collectQueenPositionsFromManager()

            self.board.loadFromFile(path)
            self.baseDisplay = [row[:] for row in self.board.display]
            self.startAnimation()
        except Exception as e:
            messagebox.showerror("Error", f"Backtrack solve failed:\n{e}")

    def clearBoard(self):
        if not self.board.display:
            return
        try:
            if self.filePath:
                self.board.loadFromFile(self.filePath)
                self.baseDisplay = [row[:] for row in self.board.display]
        except Exception:
            pass
        self.queenPositions = []
        self.qm = QueenManager(self.board)
        self.drawBoard(backgroundOnly=True)

    def saveImage(self):
        if not self.board.display or not self.queenPositions:
            messagebox.showwarning("Warning", "No solution to save yet.")
            return

        baseDir = os.path.dirname(os.path.abspath(__file__))
        outputDir = os.path.join(baseDir, "..", "output")
        os.makedirs(outputDir, exist_ok=True)
        
        if not PIL_AVAILABLE:
            psPath = os.path.join(outputDir, "solution.ps")
            self.canvas.postscript(file=psPath)
            messagebox.showinfo(
                "Saved",
                f"PostScript saved to {psPath}\n"
                f"Install Pillow to save PNG automatically."
            )
            return

        try:
            pngPath = os.path.join(outputDir, "solution.png")
            self.renderBoardToPNG(pngPath)
            messagebox.showinfo("Saved", f"Image saved to {pngPath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PNG:\n{e}")


    def renderBoardToPNG(self, filepath):
        """Render board directly to PNG using PIL"""
        from PIL import Image, ImageDraw, ImageFont
        
        width = self.board.col * CELL_SIZE + 2 * PADDING
        height = self.board.row * CELL_SIZE + 2 * PADDING
        
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)
            font_bold = ImageFont.truetype("arialbd.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_bold = font
        
        source = self.baseDisplay if self.baseDisplay else self.board.display
        color_map = {}
        palette = ["#f2f2f2", "#d9ead3", "#c9daf8", "#f4cccc",
                "#fff2cc", "#d0e0e3", "#ead1dc", "#cfe2f3"]
        palette_idx = 0
        
        for y in range(self.board.row):
            for x in range(self.board.col):
                ch = source[y][x]
                
                if ch not in color_map:
                    color_map[ch] = palette[palette_idx % len(palette)]
                    palette_idx += 1
                
                x1 = PADDING + x * CELL_SIZE
                y1 = PADDING + y * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                draw.rectangle([x1, y1, x2, y2], 
                            fill=color_map[ch], 
                            outline='black', 
                            width=1)
                
                bbox = draw.textbbox((0, 0), ch, font=font_bold)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = x1 + (CELL_SIZE - text_width) // 2
                text_y = y1 + (CELL_SIZE - text_height) // 2
                
                draw.text((text_x, text_y), ch, fill='black', font=font_bold)
        
        for qx, qy in self.queenPositions:
            x1 = PADDING + qx * CELL_SIZE + 4
            y1 = PADDING + qy * CELL_SIZE + 4
            x2 = x1 + CELL_SIZE - 8
            y2 = y1 + CELL_SIZE - 8
            
            draw.ellipse([x1, y1, x2, y2], fill='black', outline='black')
            
            bbox = draw.textbbox((0, 0), "Q", font=font_bold)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x1 + (CELL_SIZE - 8 - text_width) // 2
            text_y = y1 + (CELL_SIZE - 8 - text_height) // 2
            
            draw.text((text_x, text_y), "Q", fill='white', font=font_bold)
        
        img.save(filepath, 'PNG')