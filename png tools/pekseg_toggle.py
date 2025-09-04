import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import os

# Constants
CHAR_WIDTH = 400
CHAR_HEIGHT = 499
SCALE = 0.5
DISPLAY_WIDTH = int(CHAR_WIDTH * SCALE)
DISPLAY_HEIGHT = int(CHAR_HEIGHT * SCALE)
SEGMENT_FOLDER = "segments"
FOREGROUND_SEGMENTS = list(range(0, 39))
BACKGROUND_SEGMENTS = list(range(39, 47))  # Includes segment 46

class PeksegCharacter(tk.Frame):
    def __init__(self, master, index):
        super().__init__(master, bg="black")
        self.index = index
        self.foreground_on = False
        self.background_on = False

        # Load segment images
        self.segment_images = {
            i: Image.open(f"{SEGMENT_FOLDER}/segment_{i:02d}.png").convert("RGBA")
            for i in range(47)
        }

        # Canvas for rendering
        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=2)

        # Toggle buttons
        self.fg_btn = tk.Checkbutton(
            self, text="Foreground", command=self.toggle_foreground,
            bg="black", fg="white", selectcolor="gray20"
        )
        self.fg_btn.grid(row=1, column=0, pady=5)

        self.bg_btn = tk.Checkbutton(
            self, text="Background", command=self.toggle_background,
            bg="black", fg="white", selectcolor="gray20"
        )
        self.bg_btn.grid(row=1, column=1, pady=5)

        self.update_display()

    def toggle_foreground(self):
        self.foreground_on = not self.foreground_on
        self.update_display()

    def toggle_background(self):
        self.background_on = not self.background_on
        self.update_display()

    def update_display(self):
        base = Image.new("RGBA", (CHAR_WIDTH, CHAR_HEIGHT), (0, 0, 0, 255))
        if self.foreground_on:
            for i in FOREGROUND_SEGMENTS:
                base.alpha_composite(self.segment_images[i])
        if self.background_on:
            for i in BACKGROUND_SEGMENTS:
                base.alpha_composite(self.segment_images[i])
        scaled = base.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), resample=Image.BICUBIC)
        self.tk_image = ImageTk.PhotoImage(scaled)
        self.canvas.config(width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

def main():
    root = tk.Tk()
    root.title("Pekseg Grid Display")
    root.configure(bg="black")

    # Ask user for grid dimensions
    x_len = simpledialog.askinteger("Grid Width", "Enter number of characters per row (X):", minvalue=1)
    y_len = simpledialog.askinteger("Grid Height", "Enter number of rows (Y):", minvalue=1)

    for y in range(y_len):
        for x in range(x_len):
            index = y * x_len + x
            char = PeksegCharacter(root, index)
            char.grid(row=y, column=x, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
