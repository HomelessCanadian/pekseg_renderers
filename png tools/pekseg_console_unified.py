import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageOps
import time, colorsys

# ─────────────────────────────────────────────
# CONFIG
GRID_COLS = 12
GRID_ROWS = 9
GLYPH_WIDTH = 80
GLYPH_HEIGHT = 99
SEGMENT_COUNT = 47
BAUD_DELAY = 1 / 60

# ─────────────────────────────────────────────
# STATE
glyph_buffer = []
current_index = 0
mode = "SEG"
frame_count = 0
segment_color_mode = "static"
user_selected_color = (255, 255, 255)

# ─────────────────────────────────────────────
# INIT BUFFER
def init_buffer(cols, rows):
    global glyph_buffer
    glyph_buffer = [set() for _ in range(cols * rows)]

# ─────────────────────────────────────────────
def handle_byte(b, glyph_map=None):
    global current_index, mode, frame_count
    print(f"[PARSER] Handling byte: {b}")

    if b == 0x01:  # START
        current_index = 0
    elif b == 0x02:  # CHAR MODE
        mode = "CHAR"
    elif b == 0x03:  # RENDER
        frame_count += 1
        return "RENDER"
    elif b == 0x04:  # FLUSH
        return "RENDER"
    elif b == 0x05:  # FORCE SEG MODE
        mode = "SEG"
    elif b == 0x08:  # CLEAR SLOT
        glyph_buffer[current_index].clear()
    elif b == 0x09:  # BAUD RATE
        return "BAUD"
    elif b == 0x0A:  # NEXT SLOT
        current_index = (current_index + 1) % len(glyph_buffer)
    elif b == 0x0D:  # RESET SLOT
        current_index = 0
    elif b == 0x1B:  # TOGGLE MODE
        mode = "SEG" if mode == "CHAR" else "CHAR"
    elif b == 0x7F:  # CLEAR ALL
        for slot in glyph_buffer:
            slot.clear()
    else:
        if mode == "SEG" and 33 <= b <= 79:
            seg_id = b - 33  # remap printable byte to segment ID
            glyph_buffer[current_index].add(seg_id)
            print(f"[PARSER] Added segment {seg_id} to slot {current_index}")
            # ✅ No auto-advance here
        elif mode == "CHAR" and glyph_map:
            char = chr(b)
            segments = glyph_map.get(char)
            if segments:
                glyph_buffer[current_index] = set(segments)
                print(f"[PARSER] Mapped '{char}' to segments {segments} in slot {current_index}")
                current_index = (current_index + 1) % len(glyph_buffer)

    return None


# ─────────────────────────────────────────────
# SEGMENT IMAGE LOADING
segment_images = {}
for i in range(SEGMENT_COUNT):
    img = Image.open(f"segments/{i}.png").resize((GLYPH_WIDTH, GLYPH_HEIGHT), Image.Resampling.LANCZOS)
    segment_images[i] = img.convert("RGBA")

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
    # Ensure RGB is in 0–255 range
    if isinstance(rgb, tuple) and all(isinstance(c, float) for c in rgb):
        rgb = tuple(int(c * 255) for c in rgb)

    # Convert grayscale to color, then add alpha
    gray = ImageOps.grayscale(img)
    colored = ImageOps.colorize(gray, black="black", white=rgb)
    return colored.convert("RGBA")


# ─────────────────────────────────────────────
# DISPLAY SETUP
canvas = None
slot_images = []

def launch_display():
    global canvas, slot_images
    init_buffer(GRID_COLS, GRID_ROWS)
    print(f"[DISPLAY INIT] glyph_buffer size: {len(glyph_buffer)}")

    root = tk.Tk()
    root.title("Segmented Display Simulator")
    canvas = tk.Canvas(root, width=GRID_COLS * GLYPH_WIDTH, height=GRID_ROWS * GLYPH_HEIGHT, bg="black")
    canvas.pack()
    slot_images = [None] * (GRID_COLS * GRID_ROWS)

    def tick():
        render_display()
        root.after(int(BAUD_DELAY * 1000), tick)

    tick()
    root.mainloop()

def render_display():
    global canvas, slot_images
    canvas.delete("all")

    for idx, segments in enumerate(glyph_buffer):
        x = (idx % GRID_COLS) * GLYPH_WIDTH
        y = (idx // GRID_COLS) * GLYPH_HEIGHT

        base = Image.new("RGBA", (GLYPH_WIDTH, GLYPH_HEIGHT), (0, 0, 0, 255))

        # Optional: debug overlay if slot has segments
        if segments:
            debug_overlay = Image.new("RGBA", (GLYPH_WIDTH, GLYPH_HEIGHT), (255, 0, 0, 32))
            base.alpha_composite(debug_overlay)

        # Background segments (39–46) with low alpha
        for i in range(39, 47):
            if i in segments:
                faded = segment_images[i].copy()
                faded.putalpha(30)
                base.alpha_composite(faded)

        # Foreground segments (0–38) with dynamic color
        for i in segments:
            if i < 39:
                rgb = get_segment_color(i)
                colored = colorize_segment(segment_images[i], rgb)
                base.alpha_composite(colored)

        slot_images[idx] = ImageTk.PhotoImage(base)
        canvas.create_image(x, y, anchor="nw", image=slot_images[idx])

        # Slot index and segment list
        slot_text = f"{idx}\n{sorted(list(segments))}"
        canvas.create_text(x + 5, y + 5, anchor="nw", text=slot_text, fill="white", font=("Courier", 8))


    def dispatch(b):
        global frame_count
        print(f"[DISPATCH] Byte received: {b}")
        result = handle_byte(b)
        print(f"[DISPATCH] Parser returned: {result}")
        if result == "RENDER":
            frame_count += 1
            print(f"[DISPLAY] Rendering frame {frame_count}")
            render_display()
        elif result == "BAUD":
            print("[DISPLAY] Baud pacing triggered")
            time.sleep(BAUD_DELAY)

    return dispatch, root

# ─────────────────────────────────────────────
# CONSOLE SETUP
def launch_console(dispatch, root):
    console = tk.Toplevel(root)
    console.title("PEKSEG Console")

    entry = tk.Entry(console, width=60)
    entry.grid(row=0, column=0, padx=5, pady=5)

    def send_command():
        cmd = entry.get()
        print(f"[CONSOLE] Sending: {cmd}")
        for char in cmd:
            dispatch(ord(char))
        entry.delete(0, tk.END)

    tk.Button(console, text="Send", command=send_command).grid(row=0, column=1, padx=5)

    def load_bin():
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path:
            with open(path, "rb") as f:
                data = f.read()
                for byte in data:
                    dispatch(byte)

    tk.Button(console, text="Load .bin", command=load_bin).grid(row=1, column=0, columnspan=2, pady=5)

    def pick_color():
        color = colorchooser.askcolor(title="Pick Segment Color")
        if color:
            global user_selected_color, segment_color_mode
            user_selected_color = tuple(map(int, color[0]))
            segment_color_mode = "static"

    tk.Button(console, text="Pick Color", command=pick_color).grid(row=2, column=0, pady=5)

    def set_rainbow(): global segment_color_mode; segment_color_mode = "rainbow"
    def set_trans(): global segment_color_mode; segment_color_mode = "trans"

    tk.Button(console, text="Rainbow Mode", command=set_rainbow).grid(row=2, column=1, pady=5)
    tk.Button(console, text="Trans Mode", command=set_trans).grid(row=3, column=0, columnspan=2, pady=5)

# ─────────────────────────────────────────────
# LAUNCHER
if __name__ == "__main__":
    dispatch, root = launch_display()
    launch_console(dispatch, root)

    glyph_buffer[0].add(33)
    dispatch(3)

    root.mainloop()
