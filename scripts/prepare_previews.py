"""Create compact JPEG previews from Blender's PNG renders (Pillow required)."""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for path in (ROOT/'assets').rglob('*.png'):
 Image.open(path).convert('RGB').save(path.with_suffix('.jpg'),quality=90,optimize=True)
