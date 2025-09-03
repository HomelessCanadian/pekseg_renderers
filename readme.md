# pekseg_renderer

Virtual display renderers based on Pekero's custom PEKSEG 38-segment display.  
Inspired by [38 SEGMENT DISPLAY – Pekero](https://www.youtube.com/watch?v=Th-u84OkpeQ)
## 📦 Overview

**pekseg_renderer** is a Python toolkit for designing and rendering characters on segmented virtual displays.  
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
python segment_mapper.py       # Define hitboxes for each segment
python character_mapper.py     # Map characters to segment combinations
python typing_bar.py           # Render typed strings in virtual display
python glyph_viewer.py         # Preview all mapped glyphs
python pekseg_console.py       # Launch console + display for live segment injection
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
