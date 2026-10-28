#!/usr/bin/env python3
"""Pack review-only high-detail frames without modifying source atlases."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
NAMES = 'artemis nox overight powerdame wuchen ziggist scorpit skyles snowpie tigerknight azza dracian dragonmout mortafi'.split()
MAX_PAGE = 2048


def main():
    catalog = {item['id']: item for item in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets']}
    for name in NAMES:
        entry = catalog[name]
        provenance = json.loads((ASSETS / 'detail_130_candidates' / name / 'candidate.json').read_text())
        dest = ASSETS / 'detail_130_atlases' / name
        if dest.exists():
            raise FileExistsError(dest)
        dest.mkdir(parents=True)
        images = ASSETS / 'review' / name / 'detail_130_frames'
        with Image.open(images / 'frame_000.png') as image:
            width, height = image.size
        columns, rows = MAX_PAGE // width, MAX_PAGE // height
        if not columns or not rows:
            raise ValueError(f'{name}: frame exceeds atlas limit')
        capacity = columns * rows
        frames = []
        page = None
        for index, original in enumerate(entry['frames']):
            if index % capacity == 0:
                if page is not None:
                    page.save(dest / f'atlas_{page_number:03}.png')
                page_number = index // capacity
                remaining = min(capacity, len(entry['frames']) - index)
                page = Image.new('RGBA', (min(columns, remaining) * width, ((remaining + columns - 1) // columns) * height))
            slot = index % capacity
            x, y = (slot % columns) * width, (slot // columns) * height
            with Image.open(images / f'frame_{index:03}.png') as image:
                if image.size != (width, height):
                    raise ValueError(f'{name}: inconsistent frame size')
                page.paste(image.convert('RGBA'), (x, y))
            frames.append({'atlas': page_number, 'region': [x, y, width, height], 'duration_ms': original['duration_ms']})
        page.save(dest / f'atlas_{page_number:03}.png')
        metadata = {'id': name, 'source': entry['source'], 'source_sha256': entry['source_sha256'],
                    'base_candidate': provenance['base_candidate'], 'frame_count': len(frames), 'frames': frames,
                    'display_size': entry['size'], 'frame_size': [width, height], 'loop': entry['loop'],
                    'status': 'candidate_unreviewed',
                    'method': 'Pack existing 130% interpolated review frames; display scale is display_size / frame_size.',
                    'limitations': provenance['limitations']}
        (dest / 'candidate.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        print(name, len(frames), f'{width}x{height}', flush=True)


if __name__ == '__main__':
    main()
