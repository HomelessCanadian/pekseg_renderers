import os
import re

DIR = "segments_svg_sandbox"

for filename in os.listdir(DIR):
    if filename.endswith(".svg"):
        path = os.path.join(DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove any attribute="null"
        cleaned = re.sub(r'\s+\w+="null"', '', content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)

print("[CLEANUP] Removed null attributes from all SVGs.")
# This script removes attributes with the value "null" from SVG files in the specified directory, which causes rendering issues in some applications. 👀
