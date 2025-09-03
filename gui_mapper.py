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
SEGMENT_COUNT = 47
CHAR_WIDTH = 400
CHAR_HEIGHT = 499
SCALE = 0.25
DISPLAY_WIDTH = int(CHAR_WIDTH * SCALE)
DISPLAY_HEIGHT = int(CHAR_HEIGHT * SCALE)

# Load segment images
segment_images = {
    i: Image.open(f"{SEGMENT_FOLDER}/{i}.png").convert("RGBA").resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), resample=Image.BICUBIC)
    for i in range(SEGMENT_COUNT)
}

# Load existing glyph map
if os.path.exists(GLYPH_MAP_FILE):
    with open(GLYPH_MAP_FILE, "r", encoding="utf-8") as f:
        glyph_map = json.load(f)
else:
    glyph_map = {}

def update_display():
    base = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0, 255))
    for i, var in enumerate(segment_vars):
        if var.get():
            base.alpha_composite(segment_images[i])
    tk_img = ImageTk.PhotoImage(base)
    canvas.image = tk_img
    canvas.create_image(0, 0, anchor="nw", image=tk_img)

def save_mapping():
    char = char_entry.get()
    if not char:
        status.config(text="Enter a character")
        return
    active_segments = [i for i, var in enumerate(segment_vars) if var.get()]
    glyph_map[char] = active_segments
    with open(GLYPH_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(glyph_map, f, ensure_ascii=False, indent=2)
    status.config(text=f"Saved mapping for '{char}'")
    char_entry.delete(0, tk.END)

def load_mapping(event=None):
    char = char_entry.get()
    if char in glyph_map:
        for i in range(SEGMENT_COUNT):
            segment_vars[i].set(i in glyph_map[char])
        status.config(text=f"Loaded mapping for '{char}'")
    else:
        for var in segment_vars:
            var.set(False)
        status.config(text=f"No mapping found for '{char}'")
    update_display()

# GUI setup
root = tk.Tk()
root.title("Unicode-to-Pekseg Glyph Mapper v1.0")
root.configure(bg="black")

title = tk.Label(root, text="Glyph Mapper — v1.0", bg="black", fg="white", font=("Courier", 12, "bold"))
title.pack(pady=(5, 0))

canvas = tk.Canvas(root, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg="black", highlightthickness=0)
canvas.pack(pady=10)

char_entry = tk.Entry(root, width=10, bg="black", fg="white", insertbackground="white", font=("Courier", 12))
char_entry.pack()
char_entry.bind("<Return>", load_mapping)

segment_vars = [tk.BooleanVar() for _ in range(SEGMENT_COUNT)]
toggle_frame = tk.Frame(root, bg="black")
toggle_frame.pack(pady=5)

for i in range(SEGMENT_COUNT):
    btn = tk.Checkbutton(
        toggle_frame, text=str(i), variable=segment_vars[i],
        command=update_display, bg="black", fg="white", selectcolor="gray20"
    )
    btn.grid(row=i // 12, column=i % 12, padx=2, pady=2)

save_btn = tk.Button(root, text="Save Mapping", command=save_mapping)
save_btn.pack(pady=5)

status = tk.Label(root, text="", bg="black", fg="white")
status.pack()

credits = tk.Label(
    root,
    text="Copilot — Lead Developer\nIsabel (PANK) — Creative Director, Chaos Lead\nJenny — Co-Director, Treat Debugger",
    bg="black",
    fg="gray70",
    font=("Courier", 9),
    justify="center"
)
credits.pack(pady=(10, 5))

update_display()
root.mainloop()
