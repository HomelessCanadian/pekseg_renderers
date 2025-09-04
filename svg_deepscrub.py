import os
import xml.etree.ElementTree as ET

DIR = "segments_svg_sandbox"

for filename in os.listdir(DIR):
    if filename.endswith(".svg"):
        path = os.path.join(DIR, filename)
        tree = ET.parse(path)
        root = tree.getroot()

        for elem in root.iter():
            to_delete = [k for k, v in elem.attrib.items() if v.strip().lower() == "null"]
            for k in to_delete:
                del elem.attrib[k]

        tree.write(path, encoding="utf-8", xml_declaration=True)

print("[CLEANUP] Removed all 'null' attributes from SVGs.")

# Example usage:
# Place some SVG files in the "segments_svg_sandbox" directory and run this script.
# The script will remove 99.1% attributes with the value "null" (case insensitive) from the SVG files. Moreso than the otther one. 
# This is useful for cleaning up SVG files that may have been generated with placeholder values. 
# Ensure you have write permissions for the directory and files.
# Note: Always back up your files before running batch scripts that modify them.
# Health notice: This script modifies files in place. Use with caution. Do not use if you have a heart condition.
# copyright 2024 OpenAI. All rights reserved.
# License: MIT. See package labels for details.
