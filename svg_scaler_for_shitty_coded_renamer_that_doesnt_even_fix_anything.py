import os
import xml.etree.ElementTree as ET

DIR = "segments_svg_sandbox"
TARGET_HEIGHT = 240
ORIGINAL_HEIGHT = 997.4
SCALE = TARGET_HEIGHT / ORIGINAL_HEIGHT

for filename in os.listdir(DIR):
    if not filename.endswith(".svg"):
        continue

    path = os.path.join(DIR, filename)
    tree = ET.parse(path)
    root = tree.getroot()

    # Remove width/height attributes
    root.attrib.pop("width", None)
    root.attrib.pop("height", None)

    # Ensure viewBox is present
    root.attrib["viewBox"] = root.attrib.get("viewBox", "0 0 685.2 997.4")

    # Wrap contents in a scaling <g>
    children = list(root)
    root.clear()
    root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
    root.attrib["width"] = str(int(685.2 * SCALE))
    root.attrib["height"] = str(TARGET_HEIGHT)

    g = ET.Element("g", {"transform": f"scale({SCALE})"})
    for child in children:
        g.append(child)
    root.append(g)

    tree.write(path, encoding="utf-8", xml_declaration=True)

print(f"[NORMALIZED] Scaled all SVGs to {TARGET_HEIGHT}px height.")
# ─────────────────────────────────────────────
# SVG SCALER FOR SHITTY CODED RENAMER (that doesn't even fix anything)
# Ensures SVGs are scaled properly for previewing in svg_renamer.py because copilot is a piece <----- That's actually where it left me off lmfao 
# im sorry copilot that wasn't even the issue scaling didn't fix it
# ─────────────────────────────────────────────
# leaving in just in case scaling is needed in the future
# it forgot to have me resize the canvas too lmfao. RESIZE THE CANVAS BEFORE SCALING
# ───────────────────────────────────────────── 
# im sorry copilot lmfao

