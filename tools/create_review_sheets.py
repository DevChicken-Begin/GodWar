#!/usr/bin/env python3
"""Create numbered, non-destructive frame sheets for manual source review."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Asset/Character/vfx'
OUTPUT = ROOT / 'Asset/Character/review'
CELL_W, CELL_H, COLUMNS, ROWS = 112, 130, 8, 8


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((ROOT / 'Asset/Character/extracted/catalog.json').read_text(encoding='utf-8'))
    inventory_path = OUTPUT / 'inventory.json'
    previous = {}
    if inventory_path.exists():
        old_inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
        previous = {item['source']: item for item in old_inventory['sources']}
    # Validate every source before writing sheets, so stale annotations remain untouched.
    catalog_paths = {entry['source'] for entry in catalog['assets']}
    if set(previous) - catalog_paths:
        raise ValueError('Previously inventoried sources are missing; preserving inventory')
    for entry in catalog['assets']:
        digest = hashlib.sha256((ROOT / entry['source']).read_bytes()).hexdigest()
        if digest != entry['source_sha256']:
            raise ValueError(f'Source differs from extraction catalog: {entry["source"]}')
        old = previous.get(entry['source'])
        if old and old['sha256'] != digest:
            raise ValueError(f'Source differs from review inventory: {entry["source"]}')
    inventory = []
    for entry in catalog['assets']:
        path = ROOT / entry['source']
        gif = Image.open(path)
        folder = OUTPUT / entry['id']
        folder.mkdir(parents=True, exist_ok=True)
        sheets = []
        for start in range(0, gif.n_frames, COLUMNS * ROWS):
            count = min(COLUMNS * ROWS, gif.n_frames - start)
            sheet = Image.new('RGB', (COLUMNS * CELL_W, ((count + COLUMNS - 1) // COLUMNS) * CELL_H), '#3a3a3a')
            draw = ImageDraw.Draw(sheet)
            for offset in range(count):
                index = start + offset
                gif.seek(index)
                frame = gif.convert('RGBA')
                frame.thumbnail((CELL_W - 8, CELL_H - 28), Image.Resampling.LANCZOS)
                x, y = (offset % COLUMNS) * CELL_W, (offset // COLUMNS) * CELL_H
                sheet.paste(frame, (x + (CELL_W - frame.width) // 2, y + 20 + (CELL_H - 24 - frame.height) // 2), frame)
                draw.text((x + 4, y + 3), f'#{index:03d}  {gif.info.get("duration", 0)}ms', fill='white')
            name = f'frames_{start:04d}_{start + count - 1:04d}.jpg'
            sheet.save(folder / name, quality=90)
            sheets.append(name)
        old = previous.pop(entry['source'], None)
        if old and old['sha256'] != entry['source_sha256']:
            raise ValueError(f'Source changed; preserve and review existing inventory: {entry["source"]}')
        item = old or {'source': entry['source'], 'sha256': entry['source_sha256'],
                       'status': 'unreviewed', 'observations': [], 'characters': []}
        item.update({'frames': entry['frame_count'], 'review_sheets': sheets})
        inventory.append(item)
        print(f'{entry["id"]}: {gif.n_frames} frames', flush=True)
        gif.close()
    if previous:
        raise ValueError(f'Previously inventoried sources are missing; preserving inventory: {list(previous)}')
    inventory_path.write_text(json.dumps({'version': 1, 'sources': inventory}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
