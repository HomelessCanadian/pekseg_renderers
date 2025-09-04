import tkinter as tk
from PIL import Image, ImageTk
import json
import os

# Version: 1.2
# Credits:
# - Copilot — Lead Developer
# - Isabel (PANK) — Creative Director, Chaos Lead
# - Jenny — Co-Director, Treat Debugger

SEGMENT_FOLDER = "segments"
GLYPH_MAP_FILE = "glyph_map.json"
SEGMENT_COUNT = 39
CHAR_WIDTH = 400
CHAR_HEIGHT = 499
SCALE = 0.10  # Use 0.02 for ultra-compact

DISPLAY_WIDTH = int(CHAR_WIDTH * SCALE)
DISPLAY_HEIGHT = int(CHAR_HEIGHT * SCALE)

# Load segment images
segment_images = {
    i: Image.open(f"{SEGMENT_FOLDER}/{i}.png").convert("RGBA").resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), resample=Image.BICUBIC)
    for i in range(SEGMENT_COUNT)
}

# Load glyph map
with open(GLYPH_MAP_FILE, "r", encoding="utf-8") as f:
    glyph_map = json.load(f)

def render_character(char):
    segments = glyph_map.get(char)
    if segments is None:
        print(f"[WARN] Character '{char}' not found in glyph_map.json")
        return None
    print(f"[INFO] Rendering '{char}' → segments {segments}")
    return render_character_from_segments(segments)

def render_character_from_segments(segments):
    base = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0, 255))
    for i in segments:
        if i in segment_images:
            base.alpha_composite(segment_images[i])
        else:
            print(f"[ERROR] Segment {i} image missing")
    return ImageTk.PhotoImage(base)

def update_display():
    text = entry.get()
    print(f"[INPUT] Typed string: '{text}'")
    for widget in display_frame.winfo_children():
        widget.destroy()

    i = 0
    while i < len(text):
        char = text[i]

        if char == ".":
            if i > 0:
                prev_char = text[i - 1]
                segments = glyph_map.get(prev_char, [])
                if 38 not in segments:
                    print(f"[INFO] Attaching decimal to '{prev_char}'")
                    combined_segments = segments + [38]
                    img = render_character_from_segments(combined_segments)
                    lbl = tk.Label(display_frame, image=img, bg="black")
                    lbl.image = img
                    lbl.grid(row=0, column=i - 1, padx=1)
                    i += 1
                    continue
                else:
                    print(f"[INFO] Decimal already present in '{prev_char}', rendering '.' standalone")
            else:
                print(f"[INFO] No previous character for '.', rendering standalone")

            img = render_character(".")
            if img:
                lbl = tk.Label(display_frame, image=img, bg="black")
                lbl.image = img
                lbl.grid(row=0, column=i, padx=1)
            else:
                print(f"[SKIP] No image rendered for '.'")
        else:
            img = render_character(char)
            if img:
                lbl = tk.Label(display_frame, image=img, bg="black")
                lbl.image = img
                lbl.grid(row=0, column=i, padx=1)
            else:
                print(f"[SKIP] No image rendered for '{char}'")
        i += 1

# GUI setup
root = tk.Tk()
root.title("Pekseg Typing Bar v1.2")
root.configure(bg="black")

entry = tk.Entry(root, width=40, bg="black", fg="white", insertbackground="white", font=("Courier", 12))
entry.pack(pady=5)
entry.bind("<Return>", lambda event: update_display())

render_btn = tk.Button(root, text="Render", command=update_display)
render_btn.pack(pady=5)

display_frame = tk.Frame(root, bg="black")
display_frame.pack(pady=10)

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
