import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import cairosvg
from PIL import ImageDraw
import xml.etree.ElementTree as ET
import re

# ─────────────────────────────────────────────
# CONFIG
SVG_DIR = "segments_svg_sandbox"
TEMP_DIR = "temp_renders"
TARGET_HEIGHT = 720
VIEWBOX_HEIGHT = 997.4
SCALE = TARGET_HEIGHT / VIEWBOX_HEIGHT  # This variable is calculated but currently unused
selected_index = 0

os.makedirs(TEMP_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# LOAD SVGs AFTER GUI INIT

def sort_svg_files(file_list):
    def extract_number(filename):
        name, _ = os.path.splitext(filename)
        try:
            return int(name)
        except ValueError:
            return float('inf')  # Push non-numeric names to the end
    return sorted(file_list, key=extract_number)

def get_sorted_svg_files():
    return sorted(
        [f for f in os.listdir(SVG_DIR) if f.endswith(".svg")],
        key=natural_key
    )


def natural_key(s):
    # Split into chunks of digits and non-digits
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

svg_files = sort_svg_files([f for f in os.listdir(SVG_DIR) if f.endswith(".svg")])



segment_images = {}

def load_segment_image(index):
    if index not in segment_images:
        filename = svg_files[index]
        svg_path = os.path.join(SVG_DIR, filename)
        temp_png = os.path.join(TEMP_DIR, f"{index}.png")
        cairosvg.svg2png(
            url=svg_path,
            write_to=temp_png,
            output_width=int(700 * SCALE),
            output_height=int(720 * SCALE)
        )
        img = Image.open(temp_png).convert("RGBA")
        segment_images[index] = img
    return segment_images[index]

def rename_segment():
    global svg_files, selected_index

    new_name = entry_var.get().strip()
    if not new_name:
        status_label.config(text="Name cannot be empty.")
        return

    old_path = os.path.join(SVG_DIR, svg_files[selected_index])
    new_path = os.path.join(SVG_DIR, new_name + ".svg")

    try:
        os.rename(old_path, new_path)
    except Exception as e:
        status_label.config(text=f"Rename failed: {e}")
        return

    # Refresh file list
    svg_files = sort_svg_files([f for f in os.listdir(SVG_DIR) if f.endswith(".svg")])
    # Find new index of renamed file

    # Advance to next segment
    selected_index = (selected_index + 1) % len(svg_files)

    segment_images.clear()
    status_label.config(text=f"Renamed to: {new_name}")
    render_composite()




#  # ───────────────────────────────────────────── This expanded the window endlessly for some reason. Keeping for funny prank purposes
#  # GUI SETUP
#  root = tk.Tk()
#  root.title("Composite Segment Viewer")
#  
#  # Allow grid cells to expand
#  root.grid_rowconfigure(0, weight=1)  # Canvas row
#  root.grid_rowconfigure(1, weight=0)  # Controls row
#  root.grid_columnconfigure(0, weight=1)
#  root.grid_columnconfigure(1, weight=1)
#  root.grid_columnconfigure(2, weight=1)
#  
#  canvas = tk.Canvas(root, bg="white")
#  canvas.grid(row=0, column=0, columnspan=3, sticky="nsew")
#  
#  entry_var = tk.StringVar()
#  entry = tk.Entry(root, textvariable=entry_var, font=("Courier", 14))
#  entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
#  entry.bind("<Return>", lambda e: rename_segment())
#  
#  status_label = tk.Label(root, text="", font=("Courier", 10))
#  status_label.grid(row=1, column=1, sticky="ew")
#  
#  rename_button = tk.Button(root, text="Rename", command=lambda: rename_segment())
#  rename_button.grid(row=1, column=2, sticky="ew")
#  
#  # Optional: Resize canvas when window resizes
#  def on_resize(event):
#      canvas.config(width=event.width, height=event.height)
#      # Optional: render_composite() if you want to re-render
#  
#  canvas.bind("<Configure>", on_resize)
#  
# ───────────────────────────────────────────── real one
# GUI SETUP
root = tk.Tk()
root.title("Composite Segment Viewer")

# Allow grid cells to expand
root.grid_rowconfigure(0, weight=1)  # Canvas row
root.grid_rowconfigure(1, weight=0)  # Controls row
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

canvas = tk.Canvas(root, bg="white")
canvas.grid(row=0, column=0, columnspan=3, sticky="nsew")

entry_var = tk.StringVar()
entry = tk.Entry(root, textvariable=entry_var, font=("Courier", 14))
entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
entry.bind("<Return>", lambda _: rename_segment())

status_label = tk.Label(root, text="", font=("Courier", 10))
status_label.grid(row=1, column=1, sticky="ew")

rename_button = tk.Button(root, text="Rename", command=lambda: rename_segment())
rename_button.grid(row=1, column=2, sticky="ew")

# Debounced resize handler
resize_pending = False

def on_resize(event):
    global resize_pending
    if not resize_pending:
        resize_pending = True
        root.after(100, redraw_after_resize)

def redraw_after_resize():
    global resize_pending
    resize_pending = False
    render_composite()  # Re-render canvas after resize

canvas.bind("<Configure>", on_resize)
# ─────────────────────────────────────────────

def get_svg_geometry_bounds(svg_path):
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        ns = {'svg': 'http://www.w3.org/2000/svg'}

        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

        for elem in root.iter():
            tag = elem.tag.split('}')[-1]
            if tag in ['rect', 'circle', 'ellipse', 'line']:
                x = float(elem.attrib.get('x', elem.attrib.get('cx', '0')))
                y = float(elem.attrib.get('y', elem.attrib.get('cy', '0')))
                w = float(elem.attrib.get('width', elem.attrib.get('r', '0')))
                h = float(elem.attrib.get('height', elem.attrib.get('r', '0')))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + w)
                max_y = max(max_y, y + h)

            elif tag == 'path':
                d = elem.attrib.get('d', '')
                # Optional: parse 'd' to extract path bounds (complex, can skip for now)

        if min_x < float('inf'):
            return (min_x, min_y, max_x, max_y)
    except Exception as e:
        print("Geometry parse error:", e)
    return None


def render_composite():
    composite = Image.new("RGBA", load_segment_image(0).size, (255, 255, 255, 0))
    global selected_index
    for i in range(len(svg_files)):
        img = load_segment_image(i)
        composite = Image.alpha_composite(composite, img)

    # Isolate selected segment and draw bounding box
    if 0 <= selected_index < len(svg_files):
        highlight = load_segment_image(selected_index)  # ← this was missing
        mask = highlight.getchannel("A")                # alpha channel
        bbox = mask.getbbox()                           # bounding box of visible pixels

        if bbox:
            draw = ImageDraw.Draw(composite)
            draw.rectangle(bbox, outline=(255, 0, 0), width=3)

    photo = ImageTk.PhotoImage(composite)
    canvas.image = photo
    canvas.create_image(0, 0, anchor="nw", image=photo)
    entry_var.set(os.path.splitext(svg_files[selected_index])[0])
    status_label.config(text=f"{selected_index + 1}/{len(svg_files)}")


def jump_to_segment(event=None):
    val = entry_var.get().strip()
    idx = None
    if val.isdigit():
        idx = int(val)
    elif val.isalpha() and len(val) == 1:
        idx = ord(val.lower()) - ord('a')
    
    if idx is not None and 0 <= idx < len(svg_files):
        global selected_index
        selected_index = idx
        render_composite()
    else:
        status_label.config(text="Invalid input. Enter a valid index or letter.")

def move_selection(delta):
    global selected_index
    selected_index = (selected_index + delta) % len(svg_files)
    render_composite()

root.bind("<Left>", lambda e: move_selection(-1))
root.bind("<Right>", lambda e: move_selection(1))
# root.bind("<Return>", lambda e: rename_segment())
#load_segment_image(i)
for i in range(len(svg_files)):
    load_segment_image(i)
#load_segment_image(i)
render_composite() # <-- keep? Keep
root.mainloop()
