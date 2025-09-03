import tkinter as tk
from PIL import Image, ImageTk
import json
import os

# Version: 1.0
# Credits:
# - Copilot — Lead Developer
# - Isabel (PANK) — Creative Director, Chaos Lead
# - Jenny — Co-Director, Treat Debugger

SEGMENT_FOLDER = "segments"
GLYPH_MAP_FILE = "glyph_map.json"
SEGMENT_COUNT = 39
DISPLAY_WIDTH = 100
DISPLAY_HEIGHT = 125

# Load segment images
segment_images = {
    i: Image.open(f"{SEGMENT_FOLDER}/{i}.png").convert("RGBA").resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), resample=Image.BICUBIC)
    for i in range(SEGMENT_COUNT)
}

# Load glyph map
with open(GLYPH_MAP_FILE, "r", encoding="utf-8") as f:
    glyph_map = json.load(f)

# GUI setup
root = tk.Tk()
root.title("Glyph Viewer v1.0")
root.configure(bg="black")

canvas_frame = tk.Frame(root, bg="black")
canvas_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(canvas_frame)
scrollbar.pack(side="right", fill="y")

canvas = tk.Canvas(canvas_frame, bg="black", yscrollcommand=scrollbar.set, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.config(command=canvas.yview)

glyph_frame = tk.Frame(canvas, bg="black")
canvas.create_window((0, 0), window=glyph_frame, anchor="nw")

def render_glyph(char, segments):
    base = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0, 255))
    for i in segments:
        base.alpha_composite(segment_images[i])
    return ImageTk.PhotoImage(base)

row = 0
for char, segments in glyph_map.items():
    img = render_glyph(char, segments)
    img_label = tk.Label(glyph_frame, image=img, bg="black")
    img_label.image = img
    img_label.grid(row=row, column=0, padx=5, pady=5)

    char_label = tk.Label(glyph_frame, text=f"'{char}' → {segments}", bg="black", fg="white", font=("Courier", 10))
    char_label.grid(row=row, column=1, sticky="w", padx=5)
    row += 1

glyph_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

credits = tk.Label(
    root,
    text="Copilot — Lead Developer\nIsabel (PANK) — Creative Director, Chaos Lead\nJenny — Co-Director, Treat Debugger",
    bg="black",
    fg="gray70",
    font=("Courier", 9),
    justify="center"
)
credits.pack(pady=(10, 5))

root.mainloop()
