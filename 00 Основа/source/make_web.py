"""Derigava: light WebP copies for the gallery, in previews/web.

Run after render_scenes.py. The gallery links to the SVG layouts, and the full PNGs stay in place.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'previews' / 'web'
DIRECTIONS = {'BIO': '01 Биология', 'TEXT': '02 Писательство', 'TECH': '03 Техника и AI', 'WORK': '04 Управление и продажи', 'LIFE': '05 Личное'}
TILE, SCENE, HERO = 640, 1400, 1600


def save(source, name, width):
    image = Image.open(source).convert('RGB')
    if image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(OUT / f'{name}.webp', quality=82, method=6)


OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('*.webp'):
    old.unlink()
for code, folder in DIRECTIONS.items():
    save(ROOT / folder / 'illustrations' / 'key-visual.png', f'{code}-hero', HERO)
    for template in (ROOT / folder / 'templates').glob('*.png'):
        save(template, f'{code}-{template.stem}', TILE)
for scene in (ROOT / 'previews' / 'in-use').glob('*.png'):
    save(scene, f'in-use-{scene.stem}', SCENE)
files = list(OUT.glob('*.webp'))
print(f'previews/web: {len(files)} files, {sum(f.stat().st_size for f in files) / 1e6:.1f} MB')
