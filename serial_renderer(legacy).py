import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageOps
import threading, time, colorsys

# Config
GRID_COLS = 12
GRID_ROWS = 9
GLYPH_WIDTH = 80
GLYPH_HEIGHT = 99
SEGMENT_COUNT = 39
BAUD_DELAY = 1 / 60

# State
glyph_buffer = [set() for _ in range(GRID_COLS * GRID_ROWS)]
current_index = 0
frame_count = 0
segment_color_mode = "static"
user_selected_color = (255, 255, 255)

# Load segment images
segment_images = {}
for i in range(SEGMENT_COUNT):
    img = Image.open(f"segments/{i}.png").resize((GLYPH_WIDTH, GLYPH_HEIGHT), Image.Resampling.LANCZOS)
    segment_images[i] = img.convert("RGBA")

# Color logic
def get_segment_color(i):
    global frame_count
    if segment_color_mode == "static":
        return user_selected_color
    elif segment_color_mode == "rainbow":
        hue = ((i * 10 + frame_count * 5) % 360) / 360
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        return int(r * 255), int(g * 255), int(b * 255)
    elif segment_color_mode == "trans":
        palette = [(173,216,230), (255,182,193), (255,255,255)]
        return palette[(i + frame_count) % len(palette)]

def colorize_segment(img, rgb):
    gray = ImageOps.grayscale(img)
    colored = ImageOps.colorize(gray, black="black", white=rgb)
    return colored.convert("RGBA")

# Display window
def launch_display():
    display = tk.Toplevel()
    display.title("PEKSEG Display")
    canvas = tk.Canvas(display, width=GRID_COLS * GLYPH_WIDTH, height=GRID_ROWS * GLYPH_HEIGHT, bg="black")
    canvas.pack()
    slot_images = [None] * (GRID_COLS * GRID_ROWS)

    def render_display():
        canvas.delete("all")
        for idx, segments in enumerate(glyph_buffer):
            x = (idx % GRID_COLS) * GLYPH_WIDTH
            y = (idx // GRID_COLS) * GLYPH_HEIGHT
            base = Image.new("RGBA", (GLYPH_WIDTH, GLYPH_HEIGHT), (0, 0, 0, 255))

            # Background pass
            for i in range(SEGMENT_COUNT):
                faded = segment_images[i].copy()
                faded.putalpha(30)
                base.alpha_composite(faded)

            # Foreground pass
            for i in segments:
                rgb = get_segment_color(i)
                colored = colorize_segment(segment_images[i], rgb)
                base.alpha_composite(colored)

            slot_images[idx] = ImageTk.PhotoImage(base)
            canvas.create_image(x, y, anchor="nw", image=slot_images[idx])

        display.update()

    def handle_byte(b):
        global current_index, frame_count
        if b == 0x09:  # TAB → pacing
            pass  # Already fixed at 60Hz
        elif b == 0x03:  # ETX → frame sync
            frame_count += 1
            render_display()
            current_index = 0
            time.sleep(BAUD_DELAY)
        elif 0 <= b < SEGMENT_COUNT:
            glyph_buffer[current_index].add(b)
            current_index = (current_index + 1) % len(glyph_buffer)

    return handle_byte

# Console window
def launch_console(handle_byte):
    console = tk.Toplevel()
    console.title("PEKSEG Console")

    entry = tk.Entry(console, width=60)
    entry.grid(row=0, column=0, padx=5, pady=5)

    def send_command():
        cmd = entry.get()
        for char in cmd:
            handle_byte(ord(char))
        entry.delete(0, tk.END)

    tk.Button(console, text="Send", command=send_command).grid(row=0, column=1, padx=5)

    def load_bin():
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path:
            with open(path, "rb") as f:
                data = f.read()
                for byte in data:
                    handle_byte(byte)

    tk.Button(console, text="Load .bin", command=load_bin).grid(row=1, column=0, columnspan=2, pady=5)

    def pick_color():
        color = colorchooser.askcolor(title="Pick Segment Color")
        if color:
            global user_selected_color, segment_color_mode
            user_selected_color = tuple(map(int, color[0]))
            segment_color_mode = "static"

    tk.Button(console, text="Pick Color", command=pick_color).grid(row=2, column=0, pady=5)

    def set_rainbow():
        global segment_color_mode
        segment_color_mode = "rainbow"

    def set_trans():
        global segment_color_mode
        segment_color_mode = "trans"

    tk.Button(console, text="Rainbow Mode", command=set_rainbow).grid(row=2, column=1, pady=5)
    tk.Button(console, text="Trans Mode", command=set_trans).grid(row=3, column=0, columnspan=2, pady=5)

# Main launcher
root = tk.Tk()
root.withdraw()
handle_byte = launch_display()
launch_console(handle_byte)
root.mainloop()
