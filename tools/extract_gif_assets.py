#!/usr/bin/env python3
"""Losslessly decode source GIFs into bounded PNG atlases and an honest catalog."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import html
import os
from urllib.parse import quote
import json
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Asset/Character/vfx'
OUTPUT = ROOT / 'Asset/Character/extracted'
MAX_SIZE = 2048


def extract(source: Path, output: Path):
    gif = Image.open(source)
    width, height = gif.size
    if max(width, height) > MAX_SIZE:
        raise ValueError(f'{source}: dimensions exceed atlas limit')
    columns, rows = MAX_SIZE // width, MAX_SIZE // height
    capacity = columns * rows
    frame_count = gif.n_frames
    folder = output / source.stem
    folder.mkdir(parents=True, exist_ok=True)
    frames = []
    for start in range(0, frame_count, capacity):
        count = min(capacity, frame_count - start)
        used_columns = min(columns, count)
        used_rows = math.ceil(count / columns)
        atlas = Image.new('RGBA', (used_columns * width, used_rows * height))
        page = start // capacity
        for index in range(start, start + count):
            gif.seek(index)
            # Pillow composites disposal and transparency before converting to RGBA.
            frame = gif.convert('RGBA')
            local = index - start
            x, y = (local % columns) * width, (local // columns) * height
            atlas.paste(frame, (x, y))
            frames.append({'atlas': page, 'region': [x, y, width, height],
                           'duration_ms': gif.info.get('duration', 0)})
        atlas.save(folder / f'atlas_{page:03d}.png', compress_level=1)
    result = {'id': source.stem, 'source': str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'size': [width, height], 'frame_count': frame_count,
            'loop': gif.info.get('loop'), 'atlas_count': math.ceil(frame_count / capacity),
            'frames': frames, 'classification': 'unreviewed',
            'animations': {}, 'notes': 'GIF gốc có thể gộp nhân vật, hiệu ứng và nền; cần kiểm duyệt trước khi phân loại.'}
    gif.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    sources = sorted(args.source.glob('*.gif'), key=lambda p: p.name.lower())
    if not sources:
        raise SystemExit('No GIF files found')
    args.output.mkdir(parents=True, exist_ok=True)
    entries = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i, (source, entry) in enumerate(zip(sources, pool.map(extract, sources, [args.output] * len(sources))), 1):
            entries.append(entry)
            print(f'[{i}/{len(sources)}] {source.name}: {entry["frame_count"]} frames', flush=True)
    catalog = {'version': 1, 'atlas_max_size': MAX_SIZE, 'assets': entries}
    (args.output / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    cards = []
    for source, entry in zip(sources, entries):
        url = quote(os.path.relpath(source, args.output), safe='/')
        name = html.escape(entry['id'])
        cards.append(f'<article><h2>{name}</h2><img loading="lazy" src="{url}" alt="{name}"><p>{entry["frame_count"]} frames · {entry["size"][0]} × {entry["size"][1]} · chưa kiểm duyệt</p></article>')
    page = '''<!doctype html><html lang="vi"><meta charset="utf-8"><title>GodWar GIF catalog</title><style>body{font:16px sans-serif;background:#181e29;color:#eef;padding:24px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}article{background:#293343;padding:12px;border-radius:8px}h2{font-size:16px;overflow-wrap:anywhere}img{width:100%;height:200px;object-fit:contain;background:#111}p{font-size:13px}</style><h1>GIF nguồn nhân vật và VFX</h1><p>GIF gốc, chưa phân loại động tác; hình có thể gồm nền, VFX hoặc nhiều nhân vật.</p><main>''' + '\n'.join(cards) + '</main></html>'
    (args.output / 'index.html').write_text(page, encoding='utf-8')

if __name__ == '__main__':
    main()
