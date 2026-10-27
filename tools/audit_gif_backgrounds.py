#!/usr/bin/env python3
"""Conservatively measure GIF edge colors; results are evidence, not masks."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'Asset/Character/extracted/catalog.json'
OUTPUT = ROOT / 'Asset/Character/review/background-audit.json'


def audit(entry):
    path = ROOT / entry['source']
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['source_sha256']:
        raise ValueError(f'Source hash mismatch: {path}')
    colors = set()
    transparent_frames = 0
    uniform_border_frames = 0
    with Image.open(path) as gif:
        w, h = gif.size
        for index in range(gif.n_frames):
            gif.seek(index)
            frame = gif.convert('RGBA')
            extrema = frame.getchannel('A').getextrema()
            if extrema[0] < 255:
                transparent_frames += 1
            corner = frame.getpixel((0, 0))
            colors.add(corner)
            # All border pixels must exactly match the top-left pixel.
            edges = (frame.crop((0,0,w,1)), frame.crop((0,h-1,w,h)),
                     frame.crop((0,0,1,h)), frame.crop((w-1,0,w,h)))
            if all(edge.getextrema() == tuple((v, v) for v in corner) for edge in edges):
                uniform_border_frames += 1
        if transparent_frames == gif.n_frames:
            category = 'transparent_all_frames'
        elif transparent_frames:
            category = 'mixed_transparency'
        elif len(colors) == 1 and uniform_border_frames == gif.n_frames:
            category = 'solid_border_candidate'
        else:
            category = 'complex_or_varying_border'
        return {'id': entry['id'], 'source': entry['source'], 'source_sha256': entry['source_sha256'],
                'frames': gif.n_frames, 'frames_with_transparency': transparent_frames,
                'frames_with_uniform_border': uniform_border_frames, 'corner_colors': [list(c) for c in sorted(colors)],
                'category': category, 'status': 'automatic_measurement_unreviewed'}


def main():
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    results = []
    for entry in catalog['assets']:
        result = audit(entry)
        results.append(result)
        print(f'{entry["id"]}: {result["category"]}', flush=True)
    OUTPUT.write_text(json.dumps({'version': 1, 'description': 'Edge measurements only; no guarantee about interior pixels or masks.', 'sources': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(results)} sources audited', flush=True)

if __name__ == '__main__':
    main()
