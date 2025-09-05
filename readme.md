# pekseg_renderer

Virtual display renderers based on Pekero's custom PEKSEG 38-segment display.  
Inspired by [38 SEGMENT DISPLAY – Pekero](https://www.youtube.com/watch?v=Th-u84OkpeQ)
## 📦 Overview

**pekseg_renderer** is a Python toolkit for designing and rendering characters on virtual segmented displays.
It includes tools for segment hitbox definition, character mapping, display simulation, and glyph previewing.
## 🧰 Included Tools

| Tool                | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `segment_mapper.py` | Define polygonal hitboxes for each segment (0–38)                           |
| `character_mapper.py` | Assign Unicode characters to segment combinations via direct interaction |
| `typing_bar.py`     | Render typed strings using mapped glyphs with decimal logic                |
| `glyph_viewer.py`   | Display all mapped characters and their segment data                        |
| `pekseg_console.py` | GUI console for sending serial commands and triggering display updates |
| `pekseg_display.py` | Tkinter-based renderer for segmented glyphs with overlay and frame control |
| `pekseg_parser.py` | Serial protocol interpreter for segment injection, slot control, and frame commits |
## 🔧 Requirements

- Python 3.x  
- Pillow (`pip install pillow`)  
- A folder named `segments/` containing PNG files named `0.png` through `38.png`  
- Character-to-segment mapping file: `glyph_map.json`  
- Segment hitbox definition file: `segment_hitboxes.json` (used by `character_mapper.py`)
## 🚀 Usage

Run each tool independently from the command line:

```bash
python segment_mapper.py       # Define hitboxes for each segment, generates segment_hitboxes.json
python character_mapper.py     # Map characters to segment combinations
python glyph_viewer.py         # Preview all mapped glyphs
python pekseg_console.py       # Launch console + display for live segment injection
```

## 🔢 Segment ID Map (SEG Mode: ASCII 33–79)
```
Segment 0   → Alt+0033 → !
Segment 1   → Alt+0034 → "
Segment 2   → Alt+0035 → #
Segment 3   → Alt+0036 → $
Segment 4   → Alt+0037 → %
Segment 5   → Alt+0038 → &
Segment 6   → Alt+0039 → '
Segment 7   → Alt+0040 → (
Segment 8   → Alt+0041 → )
Segment 9   → Alt+0042 → *
Segment 10  → Alt+0043 → +
Segment 11  → Alt+0044 → ,
Segment 12  → Alt+0045 → -
Segment 13  → Alt+0046 → .
Segment 14  → Alt+0047 → /
Segment 15  → Alt+0048 → 0
Segment 16  → Alt+0049 → 1
Segment 17  → Alt+0050 → 2
Segment 18  → Alt+0051 → 3
Segment 19  → Alt+0052 → 4
Segment 20  → Alt+0053 → 5
Segment 21  → Alt+0054 → 6
Segment 22  → Alt+0055 → 7
Segment 23  → Alt+0056 → 8
Segment 24  → Alt+0057 → 9
Segment 25  → Alt+0058 → :
Segment 26  → Alt+0059 → ;
Segment 27  → Alt+0060 → <
Segment 28  → Alt+0061 → =
Segment 29  → Alt+0062 → >
Segment 30  → Alt+0063 → ?
Segment 31  → Alt+0064 → @
Segment 32  → Alt+0065 → A
Segment 33  → Alt+0066 → B
Segment 34  → Alt+0067 → C
Segment 35  → Alt+0068 → D
Segment 36  → Alt+0069 → E
Segment 37  → Alt+0070 → F
Segment 38  → Alt+0071 → G
Segment 39  → Alt+0072 → H
Segment 40  → Alt+0073 → I
Segment 41  → Alt+0074 → J
Segment 42  → Alt+0075 → K
Segment 43  → Alt+0076 → L
Segment 44  → Alt+0077 → M
Segment 45  → Alt+0078 → N
Segment 46  → Alt+0079 → O
```
## 🧭 Control Bytes (Alt+Numpad)
```
Alt+0001 → START (reset slot index)
Alt+0002 → CHAR MODE
Alt+0003 → RENDER frame
Alt+0004 → FLUSH (render)
Alt+0005 → FORCE SEG MODE
Alt+0008 → CLEAR current slot
Alt+0009 → BAUD pacing
Alt+0010 → NEXT slot
Alt+0013 → RESET slot index
Alt+0027 → TOGGLE SEG/CHAR mode
Alt+0127 → CLEAR ALL slots
```
## ⚙️ Features

- Scalable rendering (adjustable via `SCALE` parameter)
- Decimal point logic: segment 38 can be conditionally attached to preceding characters
- JSON-based configuration for portability and extensibility
- Console logging for debugging character rendering and segment behavior
## 👥 Credits

- Isabel — Project Lead, Creative Director 
- Copilot — Lead Developer
- Jenny — Interface Testing  
- Pepper — Security Advisor
- Claire — Executive Napping Lead
- Pekero — Original PEKSEG Display Design
## 📄 License

This project is licensed under the MIT License.
