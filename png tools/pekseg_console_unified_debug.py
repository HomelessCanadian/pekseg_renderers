import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import colorsys
import threading
import sys

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
user_selected_color = (0, 255, 0)  # bright green

# ─────────────────────────────────────────────
# IMAGE LOADING
segment_images = {}
for i in range(SEGMENT_COUNT):
    try:
        img = Image.open(f"segments/{i}.png").resize((GLYPH_WIDTH, GLYPH_HEIGHT), Image.Resampling.LANCZOS)
        segment_images[i] = img.convert("RGBA")
    except Exception as e:
        print(f"[ERROR] Failed to load segment {i}: {e}")

# ─────────────────────────────────────────────
# COLOR LOGIC
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

# ─────────────────────────────────────────────
# BUFFER INIT
def init_buffer(cols, rows):
    global glyph_buffer
    glyph_buffer = [set() for _ in range(cols * rows)]

# ─────────────────────────────────────────────
# BYTE PARSER
def handle_byte(b, glyph_map=None):
    global current_index, mode, frame_count, segment_color_mode, user_selected_color

    if b == 0x01: current_index = 0
    elif b == 0x02: mode = "CHAR"
    elif b == 0x03: frame_count += 1; return "RENDER"
    elif b == 0x04: return "RENDER"
    elif b == 0x05: mode = "SEG"
    elif b == 0x08: glyph_buffer[current_index].clear()
    elif b == 0x09: return "BAUD"
    elif b == 0x0A: current_index = (current_index + 1) % len(glyph_buffer)
    elif b == 0x0D: current_index = 0
    elif b == 0x0F: segment_color_mode = "rainbow" if segment_color_mode == "static" else "static"
    elif b == 0x1B: mode = "SEG" if mode == "CHAR" else "CHAR"
    elif b == 0x7F: [slot.clear() for slot in glyph_buffer]
    else:
        if mode == "SEG" and 33 <= b <= 79:
            seg_id = b - 33
            glyph_buffer[current_index].add(seg_id)
        elif mode == "CHAR" and glyph_map:
            char = chr(b)
            segments = glyph_map.get(char)
            if segments:
                glyph_buffer[current_index] = set(segments)
                current_index = (current_index + 1) % len(glyph_buffer)
    return None

# ─────────────────────────────────────────────
# DISPLAY SETUP
canvas = None
slot_images = []

def render_display():
    global canvas, slot_images
    canvas.delete("all")

    for idx, segments in enumerate(glyph_buffer):
        x = (idx % GRID_COLS) * GLYPH_WIDTH
        y = (idx // GRID_COLS) * GLYPH_HEIGHT
        base = Image.new("RGBA", (GLYPH_WIDTH, GLYPH_HEIGHT), (0, 0, 0, 255))

        for i in range(39, 47):
            if i in segments:
                faded = segment_images[i].copy()
                faded.putalpha(30)
                base.alpha_composite(faded)

        for i in segments:
            if i < 39:
                rgb = get_segment_color(i)
                colored = colorize_segment(segment_images[i], rgb)
                base.alpha_composite(colored)

        try:
            slot_images[idx] = ImageTk.PhotoImage(base)
            canvas.create_image(x, y, anchor="nw", image=slot_images[idx])
        except RuntimeError as e:
            print(f"[RENDER ERROR] Skipped slot {idx}: {e}")

        slot_text = f"{idx}\n{sorted(list(segments))}"
        canvas.create_text(x + 5, y + 5, anchor="nw", text=slot_text, fill="white", font=("Courier", 8))

def launch_display():
    global canvas, slot_images
    init_buffer(GRID_COLS, GRID_ROWS)
    print(f"[DISPLAY INIT] glyph_buffer size: {len(glyph_buffer)}")

    root = tk.Tk()
    root.title("Segmented Display Simulator")
    canvas = tk.Canvas(root, width=GRID_COLS * GLYPH_WIDTH, height=GRID_ROWS * GLYPH_HEIGHT, bg="black")
    canvas.pack()
    slot_images = [None] * (GRID_COLS * GRID_ROWS)

    # Launch console window from inside the main GUI thread
    launch_console(root)

    def tick():
        global frame_count
        frame_count += 1
        render_display()
        root.after(int(BAUD_DELAY * 1000), tick)

    tick()
    root.mainloop()


# ─────────────────────────────────────────────
# CONSOLE GUI
def launch_console(root):
    console = tk.Toplevel(root)
    console.title("Segmented Console")

    input_var = tk.StringVar()
    input_entry = tk.Entry(console, textvariable=input_var, font=("Courier", 12), width=20)
    input_entry.grid(row=0, column=0, padx=10, pady=10)

    def send_char():
        text = input_var.get()
        if text:
            for char in text:
                b = ord(char)
                print(f"[CONSOLE] Sending: {char} ({b})")
                result = handle_byte(b)
                if result == "RENDER":
                    print(f"[DISPLAY] Rendering frame {frame_count}")
            input_var.set("")

    send_button = tk.Button(console, text="Send", command=send_char)
    send_button.grid(row=0, column=1, padx=5)

    control_codes = {
        "START (0x01)": 0x01,
        "RENDER (0x03)": 0x03,
        "NEXT SLOT (0x0A)": 0x0A,
        "CLEAR SLOT (0x08)": 0x08,
        "TOGGLE COLOR MODE (0x0F)": 0x0F,
        "RESET SLOT (0x0D)": 0x0D,
        "CLEAR ALL (0x7F)": 0x7F
    }

    selected_code = tk.StringVar(value="RENDER (0x03)")
    code_menu = tk.OptionMenu(console, selected_code, *control_codes.keys())
    code_menu.grid(row=1, column=0, padx=10, pady=5)

    def send_control():
        label = selected_code.get()
        b = control_codes[label]
        print(f"[CONSOLE] Sending control: {label} ({b})")
        result = handle_byte(b)
        if result == "RENDER":
            print(f"[DISPLAY] Rendering frame {frame_count}")

    control_button = tk.Button(console, text="Send Control Code", command=send_control)
    control_button.grid(row=1, column=1, padx=5)

    color_button = tk.Button(console, text="Set Color (soon)", state="disabled")
    color_button.grid(row=2, column=0, columnspan=2, pady=10)

# ─────────────────────────────────────────────
# ENTRY POINT
if __name__ == "__main__":
    print("[BOOT] Segmented Display Simulator starting...")
    launch_display()  # this calls root.mainloop()




# ─────────────────────────────────────────────
#                   END OF FILE
# ─────────────────────────────────────────────
# Requirements:
# - Python 3.6+ (f-string support)
# - Pillow library: pip install Pillow
# - 'segments/' directory with images named 0.png to 46.png

# Notes:
# - This simulator is for educational and experimental use only.
# - It does not interface with actual hardware.
# - Adjust GRID_COLS and GRID_ROWS to match your layout.
# - Modify BAUD_DELAY to simulate different refresh rates.
# - The GUI may behave differently across systems; tweak as needed.
# - Error handling is minimal—expand for production use.
# - Console GUI is basic; enhance for better UX.
# - Open-source and modifiable—feel free to fork and riff.
# - Always test in a safe environment before deploying.
# ─────────────────────────────────────────────
#             LICENSE: MIT License
# ─────────────────────────────────────────────
# (Isabel here, I love this whole vibe coding thing lmao. I hate python tho)
# ─────────────────────────────────────────────
