import tkinter as tk
from PIL import Image, ImageTk
import os
import shutil

# Version: 1.2
# Changelog:
# - Added version-aware sorting
# - Enter key triggers rename
# - Highlighted red overlay for current segment

SEGMENT_FOLDER = "segments"
TEMP_FOLDER = "segments_temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Version-aware sorting
def numeric_key(filename):
    return int(os.path.splitext(filename)[0])

segment_files = sorted(
    [f for f in os.listdir(SEGMENT_FOLDER) if f.endswith(".png")],
    key=numeric_key
)

segment_images = [Image.open(os.path.join(SEGMENT_FOLDER, f)).convert("RGBA") for f in segment_files]
DISPLAY_SIZE = (200, 250)
segment_images = [img.resize(DISPLAY_SIZE, resample=Image.BICUBIC) for img in segment_images]
current_index = 0

def highlight_segment(base, highlight_img):
    red_overlay = Image.new("RGBA", DISPLAY_SIZE, (255, 0, 0, 0))
    mask = highlight_img.split()[3]
    red_overlay.putalpha(mask)
    return Image.alpha_composite(base, red_overlay)

def update_display():
    base = Image.new("RGBA", DISPLAY_SIZE, (0, 0, 0, 255))
    for i, img in enumerate(segment_images):
        if i != current_index:
            base.alpha_composite(img)
    highlighted = highlight_segment(base, segment_images[current_index])
    tk_img = ImageTk.PhotoImage(highlighted)
    canvas.image = tk_img
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    status.config(text=f"Renaming segment {segment_files[current_index]} ({current_index + 1} of {len(segment_images)})")

def rename_segment():
    global current_index
    segment_id = entry.get()
    if not segment_id.isdigit():
        status.config(text="Enter a valid number")
        return
    new_name = f"{segment_id}.png"
    old_path = os.path.join(SEGMENT_FOLDER, segment_files[current_index])
    new_path = os.path.join(TEMP_FOLDER, new_name)
    shutil.copy(old_path, new_path)
    entry.delete(0, tk.END)
    current_index += 1
    if current_index < len(segment_images):
        update_display()
    else:
        status.config(text="All segments renamed!")
        entry.config(state="disabled")
        canvas.delete("all")

# GUI setup
root = tk.Tk()
root.title("Segment Renamer Overlay v1.2")
root.configure(bg="black")

canvas = tk.Canvas(root, width=DISPLAY_SIZE[0], height=DISPLAY_SIZE[1], bg="black", highlightthickness=0)
canvas.pack(pady=10)

entry = tk.Entry(root, width=10, bg="black", fg="white", insertbackground="white")
entry.pack()
entry.bind("<Return>", lambda event: rename_segment())  # Enter to continue

btn = tk.Button(root, text="Rename", command=rename_segment)
btn.pack(pady=5)

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
