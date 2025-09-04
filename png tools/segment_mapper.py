import tkinter as tk
from PIL import Image, ImageTk
import json
import os

# Version: 1.0.1
# Credits:
# - Copilot — Lead Developer
# - Isabel (PANK) — Creative Director, Chaos Lead
# - Jenny — Co-Director, Treat Debugger

SEGMENT_FOLDER = "segments"
HITBOX_FILE = "segment_hitboxes.json"
SEGMENT_COUNT = 39  # Segments 0–38
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 499

# Load segment files in numeric order
segment_files = sorted(
    [f for f in os.listdir(SEGMENT_FOLDER) if f.endswith(".png")],
    key=lambda x: int(os.path.splitext(x)[0])
)

# Load and resize segment images
segment_images = [
    Image.open(os.path.join(SEGMENT_FOLDER, f)).convert("RGBA").resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), resample=Image.BICUBIC)
    for f in segment_files[:SEGMENT_COUNT]
]

current_index = 0
hitboxes = {}

def update_display():
    base = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0, 255))
    for i, img in enumerate(segment_images):
        if i != current_index:
            base.alpha_composite(img)
    # Highlight current segment
    highlight_img = segment_images[current_index]
    red_overlay = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (255, 0, 0, 0))
    mask = highlight_img.split()[3]  # Use alpha channel
    red_overlay.putalpha(mask)
    base.alpha_composite(red_overlay)

    tk_img = ImageTk.PhotoImage(base)
    canvas.image = tk_img
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.delete("highlight")
    if str(current_index) in hitboxes:
        canvas.create_polygon(
            hitboxes[str(current_index)],
            outline="red", fill="", width=2, tags="highlight"
        )
    status.config(text=f"Defining hitbox for segment {current_index} of {SEGMENT_COUNT - 1}")


def on_click(event):
    x, y = event.x, event.y
    hitboxes.setdefault(str(current_index), []).append([x, y])
    update_display()

def next_segment():
    global current_index
    current_index += 1
    if current_index >= SEGMENT_COUNT:
        current_index = SEGMENT_COUNT - 1
        status.config(text="All segments mapped!")
    update_display()

def clear_segment():
    hitboxes[str(current_index)] = []
    update_display()

def save_hitboxes():
    with open(HITBOX_FILE, "w") as f:
        json.dump(hitboxes, f, indent=2)
    status.config(text="Hitboxes saved to segment_hitboxes.json")

# GUI setup
root = tk.Tk()
root.title("Segment Mapper v1.0.1")
root.configure(bg="black")

title = tk.Label(root, text="Segment Mapper — v1.0.1", bg="black", fg="white", font=("Courier", 12, "bold"))
title.pack(pady=(5, 0))

canvas = tk.Canvas(root, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg="black", highlightthickness=0)
canvas.pack(pady=10)
canvas.bind("<Button-1>", on_click)

btn_frame = tk.Frame(root, bg="black")
btn_frame.pack()

next_btn = tk.Button(btn_frame, text="Next Segment", command=next_segment)
next_btn.grid(row=0, column=0, padx=5)

clear_btn = tk.Button(btn_frame, text="Clear Points", command=clear_segment)
clear_btn.grid(row=0, column=1, padx=5)

save_btn = tk.Button(btn_frame, text="Save Hitboxes", command=save_hitboxes)
save_btn.grid(row=0, column=2, padx=5)

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
