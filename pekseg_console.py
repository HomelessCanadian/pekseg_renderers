import tkinter as tk
from tkinter import filedialog, colorchooser
from pekseg_display import launch_display
from pekseg_parser import glyph_buffer


segment_color_mode = "static"
user_selected_color = (255, 255, 255)

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

    def set_rainbow():
        global segment_color_mode
        segment_color_mode = "rainbow"

    def set_trans():
        global segment_color_mode
        segment_color_mode = "trans"

    tk.Button(console, text="Rainbow Mode", command=set_rainbow).grid(row=2, column=1, pady=5)
    tk.Button(console, text="Trans Mode", command=set_trans).grid(row=3, column=0, columnspan=2, pady=5)

# Launcher
if __name__ == "__main__":
    dispatch, root = launch_display()
    launch_console(dispatch, root)
    glyph_buffer[0].add(33)  # Activate segment 33 in slot 0
    dispatch(3)  # Trigger render
    render_display()

    root.mainloop()
