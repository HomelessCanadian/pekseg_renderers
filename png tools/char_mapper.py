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
HITBOX_FILE = "segment_hitboxes.json"
GLYPH_MAP_FILE = "glyph_map.json"
SEGMENT_COUNT = 39
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 499

# Load segment images
segment_images = {
    i: Image.open(f"{SEGMENT_FOLDER}/{i}.png").convert("RGBA").resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), resample=Image.BICUBIC)
    for i in range(SEGMENT_COUNT)
}

# Load hitboxes
with open(HITBOX_FILE, "r") as f:
    hitboxes = json.load(f)

# Load existing glyph map
if os.path.exists(GLYPH_MAP_FILE):
    with open(GLYPH_MAP_FILE, "r", encoding="utf-8") as f:
        glyph_map = json.load(f)
else:
    glyph_map = {}

selected_segments = set()

def point_in_polygon(x, y, polygon):
    # Ray casting algorithm
    inside = False
    n = len(polygon)
    px, py = x, y
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[(i + 1) % n]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-6) + xi):
            inside = not inside
    return inside

def on_click(event):
    x, y = event.x, event.y
    for seg_id, polygon in hitboxes.items():
        if point_in_polygon(x, y, polygon):
            seg = int(seg_id)
            if seg in selected_segments:
                selected_segments.remove(seg)
            else:
                selected_segments.add(seg)
            break
    update_display()

def update_display():
    base = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0, 255))
    for i in range(SEGMENT_COUNT):
        if i in selected_segments:
            # Red tint
            mask = segment_images[i].split()[3]
            red_overlay = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (255, 0, 0, 0))
            red_overlay.putalpha(mask)
            base.alpha_composite(red_overlay)
        else:
            base.alpha_composite(segment_images[i])
    tk_img = ImageTk.PhotoImage(base)
    canvas.image = tk_img
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    status.config(text=f"Selected segments: {sorted(selected_segments)}")

def save_mapping():
    char = char_entry.get()
    if not char:
        status.config(text="Enter a character")
        return
    glyph_map[char] = sorted(selected_segments)
    with open(GLYPH_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(glyph_map, f, ensure_ascii=False, indent=2)
    status.config(text=f"Saved mapping for '{char}'")
    char_entry.delete(0, tk.END)
    selected_segments.clear()
    update_display()

def load_mapping(event=None):
    char = char_entry.get()
    if char in glyph_map:
        selected_segments.clear()
        selected_segments.update(glyph_map[char])
        status.config(text=f"Loaded mapping for '{char}'")
    else:
        selected_segments.clear()
        status.config(text=f"No mapping found for '{char}'")
    update_display()

# GUI setup
root = tk.Tk()
root.title("Character Mapper v1.0")
root.configure(bg="black")

title = tk.Label(root, text="Character Mapper — v1.0", bg="black", fg="white", font=("Courier", 12, "bold"))
title.pack(pady=(5, 0))

canvas = tk.Canvas(root, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg="black", highlightthickness=0)
canvas.pack(pady=10)
canvas.bind("<Button-1>", on_click)

char_entry = tk.Entry(root, width=10, bg="black", fg="white", insertbackground="white", font=("Courier", 12))
char_entry.pack()
char_entry.bind("<Return>", load_mapping)

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
