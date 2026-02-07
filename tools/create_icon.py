"""Create a proper multi-size .ico from the PNG for Windows taskbar/explorer."""
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG_PATH = os.path.join(PROJECT_DIR, "assets", "certiv-icon.png")
ICO_PATH = os.path.join(PROJECT_DIR, "assets", "certiv-icon.ico")

if not os.path.isfile(PNG_PATH):
    print(f"PNG not found: {PNG_PATH}")
    sys.exit(1)

img = Image.open(PNG_PATH).convert("RGBA")
# Windows expects multiple sizes for proper display
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(ICO_PATH, format="ICO", sizes=sizes)
print(f"Created {ICO_PATH}")
