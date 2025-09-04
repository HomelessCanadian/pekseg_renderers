import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import time, colorsys
from pekseg_parser import glyph_buffer, init_buffer, handle_byte

# Config
GRID_COLS = 12
GRID_ROWS = 9
GLYPH_WIDTH = 80
GLYPH_HEIGHT = 99
SEGMENT_COUNT = 47
BAUD_DELAY = 1 / 60

# State
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

# GUI setup
def launch_display():
    init_buffer(GRID_COLS, GRID_ROWS)
    print(f"[DISPLAY INIT] glyph_buffer size: {len(glyph_buffer)}")  # Should be 108
    root = tk.Tk()
    root.title("PEKSEG Display")
    canvas = tk.Canvas(root, width=GRID_COLS * GLYPH_WIDTH, height=GRID_ROWS * GLYPH_HEIGHT, bg="black")
    canvas.pack()
    slot_images = [None] * (GRID_COLS * GRID_ROWS)

    def render_display():
        canvas.delete("all")
        for idx, segments in enumerate(glyph_buffer):
            x = (idx % GRID_COLS) * GLYPH_WIDTH
            y = (idx // GRID_COLS) * GLYPH_HEIGHT
            base = Image.new("RGBA", (GLYPH_WIDTH, GLYPH_HEIGHT), (0, 0, 0, 255))

            # Background pass
            for i in range(39, 47):
                if i in segments:
                    faded = segment_images[i].copy()
                    faded.putalpha(30)
                    base.alpha_composite(faded)

            # Foreground pass
            for i in segments:
                if i < 39:
                    rgb = get_segment_color(i)
                    colored = colorize_segment(segment_images[i], rgb)
                    base.alpha_composite(colored)


            slot_images[idx] = ImageTk.PhotoImage(base)
            canvas.create_image(x, y, anchor="nw", image=slot_images[idx])
            # Overlay slot index and active segments
            slot_text = f"{idx}\n{sorted(list(segments))}"
            canvas.create_text(x + 5, y + 5, anchor="nw", text=slot_text, fill="white", font=("Courier", 8))


        root.update()

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
