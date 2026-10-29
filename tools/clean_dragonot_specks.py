#!/usr/bin/env python3
"""Remove detached dark GIF background specks from dragonot alpha frames."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
SOURCE = A / 'native_candidates/dragonot'
OUTPUT = A / 'revision_candidates/dragonot'


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    meta = json.loads((SOURCE / 'candidate.json').read_text())
    frames = meta['frames']
    OUTPUT.mkdir(parents=True)
    samples = sorted({round((len(frames) - 1) * k / 11) for k in range(12)})
    sheet = Image.new('RGB', (800, 615), '#aaaaaa')
    draw = ImageDraw.Draw(sheet)
    removed = []
    for i, region in enumerate(frames):
        x, y, w, h = region['region']
        path = SOURCE / f'atlas_{region["atlas"]:03d}.png'
        with Image.open(path) as atlas:
            rgba = np.array(atlas.crop((x, y, x + w, y + h)).convert('RGBA'))
        labels, _ = ndi.label(rgba[:, :, 3] > 0, structure=np.ones((3, 3)))
        sizes = np.bincount(labels.ravel())
        detached = (labels > 0) & (sizes[labels] <= 16)
        dark = (rgba[:, :, 0] <= 40) & (rgba[:, :, 1] <= 80) & (rgba[:, :, 2] <= 100)
        mask = detached & dark
        rgba[mask] = 0
        removed.append(int(mask.sum()))
        frame = Image.fromarray(rgba, 'RGBA')
        frame.save(OUTPUT / f'frame_{i:03d}.png', compress_level=1)
        if i in samples:
            slot = samples.index(i)
            thumb = frame.copy()
            thumb.thumbnail((188, 174), Image.Resampling.LANCZOS)
            sx, sy = slot % 4 * 200, slot // 4 * 205
            sheet.paste(thumb, (sx + (200 - thumb.width) // 2, sy + 22), thumb)
            draw.text((sx + 4, sy + 3), f'#{i}  -{removed[-1]} px', fill='white')
    sheet.save(OUTPUT / 'sample-light.jpg', quality=92)
    result = {
        'id': 'dragonot', 'source': meta['source'], 'source_sha256': meta['source_sha256'],
        'base_candidate': 'native_candidates',
        'base_metadata_sha256': hashlib.sha256((SOURCE / 'candidate.json').read_bytes()).hexdigest(),
        'art_source': 'existing', 'display_size': meta['frames'][0]['region'][2:],
        'frame_count': len(frames), 'frames': frames, 'removed_per_frame': removed,
        'method': '8-connected alpha components; remove detached components of at most 16 pixels only where every removed pixel is dark background-like RGB (R<=40,G<=80,B<=100). All other pixels and frame timing are unchanged.',
        'status': 'candidate_unreviewed',
        'limitations': 'Detached dark intentional detail may be removed. Inspect all frames over light and dark backgrounds.'
    }
    (OUTPUT / 'candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('dragonot:', len(frames), 'frames,', sum(removed), 'pixels removed; max', max(removed))


if __name__ == '__main__':
    main()
