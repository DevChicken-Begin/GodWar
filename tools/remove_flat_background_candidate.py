#!/usr/bin/env python3
"""Generate an inspectable candidate by clearing edge-connected exact GIF background."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


def clear_background(frame, background, corners):
    """Clear only exact matching pixels connected to a canvas corner."""
    if cv2 is None:
        for point in corners:
            if frame.getpixel(point) == background:
                ImageDraw.floodfill(frame, point, (0, 0, 0, 0), thresh=0)
        return frame
    pixels = np.array(frame)
    matches = np.all(pixels == np.array(background, dtype=np.uint8), axis=2).astype(np.uint8)
    for x, y in corners:
        if matches[y, x] == 1:
            cv2.floodFill(matches, None, (x, y), 2)
    pixels[matches == 2] = (0, 0, 0, 0)
    return Image.fromarray(pixels)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'Asset/Character/extracted/catalog.json'
DEST = ROOT / 'Asset/Character/candidates'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('asset_id')
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    entry = next((item for item in catalog['assets'] if item['id'] == args.asset_id), None)
    if entry is None:
        raise SystemExit('Unknown asset ID')
    source = ROOT / entry['source']
    if hashlib.sha256(source.read_bytes()).hexdigest() != entry['source_sha256']:
        raise SystemExit('Source differs from catalog; regenerate and review before proceeding')
    dest = DEST / entry['id']
    if dest.exists():
        raise SystemExit(f'Candidate exists; refusing to overwrite: {dest}')
    gif = Image.open(source)
    w, h = gif.size
    corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
    gif.seek(0)
    background = gif.convert('RGBA').getpixel((0, 0))
    if background[3] != 255:
        raise SystemExit('Source already has a transparent corner; review manually')
    for i in range(gif.n_frames):
        gif.seek(i)
        frame = gif.convert('RGBA')
        if any(frame.getpixel(point) != background for point in corners):
            raise SystemExit(f'Background corners vary at frame {i}; review manually')
    dest.mkdir(parents=True)
    current_page = -1
    atlas = None
    removed = 0
    for i, info in enumerate(entry['frames']):
        if info['atlas'] != current_page:
            if atlas is not None:
                atlas.save(dest / f'atlas_{current_page:03d}.png', compress_level=1)
            current_page = info['atlas']
            with Image.open(ROOT / 'Asset/Character/extracted' / entry['id'] / f'atlas_{current_page:03d}.png') as page:
                atlas = Image.new('RGBA', page.size)
        gif.seek(i)
        frame = gif.convert('RGBA')
        frame = clear_background(frame, background, corners)
        removed += frame.getchannel('A').histogram()[0]
        x, y, _, _ = info['region']
        atlas.paste(frame, (x, y))
    if atlas is not None:
        atlas.save(dest / f'atlas_{current_page:03d}.png', compress_level=1)
    metadata = {'source': entry['source'], 'source_sha256': entry['source_sha256'],
                'method': 'exact edge-connected background flood fill', 'background_rgba': background,
                'frame_count': gif.n_frames, 'removed_pixels': removed,
                'status': 'candidate_unreviewed', 'frames': entry['frames'],
                'limitations': 'No claim that isolated foreground, character, or VFX is complete; manual review required.'}
    (dest / 'candidate.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{entry["id"]}: {gif.n_frames} frames; {removed} background pixels cleared; candidate requires review')

if __name__ == '__main__':
    main()
