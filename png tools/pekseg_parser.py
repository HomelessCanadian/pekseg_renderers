# pekseg_parser.py

glyph_buffer = []
current_index = 0
mode = "SEG"
frame_count = 0

def init_buffer(cols, rows):
    global glyph_buffer
    glyph_buffer = [set() for _ in range(cols * rows)]

def handle_byte(b, glyph_map=None):
    global current_index, mode, frame_count
    print(f"[PARSER] Handling byte: {b}")
    ...
    

    if b == 0x01:  # START
        current_index = 0
    elif b == 0x02:  # CHAR MODE
        mode = "CHAR"
    elif b == 0x03:  # END CHAR
        frame_count += 1
        return "RENDER"
    elif b == 0x04:  # FLUSH
        return "RENDER"
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
        if mode == "SEG":
            if 0 <= b <= 46:
                glyph_buffer[current_index].add(b)
                print(f"[PARSER] Added segment {b} to slot {current_index}")
                current_index = (current_index + 1) % len(glyph_buffer)
        elif mode == "CHAR" and glyph_map:
            char = chr(b)
            segments = glyph_map.get(char)
            if segments:
                glyph_buffer[current_index] = set(segments)
                print(f"[PARSER] Mapped '{char}' to segments {segments} in slot {current_index}")
                current_index = (current_index + 1) % len(glyph_buffer)


    return None
