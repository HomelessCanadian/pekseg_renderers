import os
import xml.etree.ElementTree as ET
import json

SOURCE_SVG = "PEKSEG-2.svg"
OUTPUT_DIR = "segments_svg"
MANIFEST_FILE = "segments.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
tree = ET.parse(SOURCE_SVG)
root = tree.getroot()

viewBox = root.attrib.get("viewBox", "0 0 1000 1000")
manifest = {}

for elem in root.iter():
    seg_id = elem.attrib.get("id")
    if not seg_id or not seg_id.startswith("svg_"):
        continue

    tag = elem.tag.split("}")[-1]  # strip namespace
    transform = elem.attrib.get("transform")

    # Wrap in <svg>
    svg_root = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": viewBox,
        "width": "100%",
        "height": "100%"
    })

    # Wrap in <g> if transform exists
    if transform:
        g = ET.Element("g", {"transform": transform})
        g.append(elem)
        svg_root.append(g)
    else:
        svg_root.append(elem)

    # Save individual SVG
    filename = f"{seg_id}.svg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    ET.ElementTree(svg_root).write(filepath, encoding="utf-8", xml_declaration=True)

    # Add to manifest
    manifest[seg_id] = {
        "filename": filename,
        "tag": tag,
        "transform": transform,
        "viewBox": viewBox
    }

# Save manifest
with open(os.path.join(OUTPUT_DIR, MANIFEST_FILE), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"[DONE] Extracted {len(manifest)} segments to '{OUTPUT_DIR}'")
