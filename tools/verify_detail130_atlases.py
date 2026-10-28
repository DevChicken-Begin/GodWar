#!/usr/bin/env python3
"""Verify packed pixels, frame timings and display scale against review data."""
import hashlib
import json
from pathlib import Path
from PIL import Image
import numpy as np
from pack_detail130_atlases import ASSETS, ROOT, NAMES

catalog = {x['id']: x for x in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets']}
total = 0
for name in NAMES:
    original = catalog[name]
    folder = ASSETS / 'detail_130_atlases' / name
    info = json.loads((folder / 'candidate.json').read_text())
    assert info['frame_count'] == len(original['frames']) == len(info['frames'])
    assert info['display_size'] == original['size']
    assert hashlib.sha256((ROOT / info['source']).read_bytes()).hexdigest() == info['source_sha256']
    current_page = -1
    image = None
    for i, frame in enumerate(info['frames']):
        assert frame['duration_ms'] == original['frames'][i]['duration_ms']
        if current_page != frame['atlas']:
            if image is not None:
                image.close()
            current_page = frame['atlas']
            image = Image.open(folder / f'atlas_{current_page:03}.png').convert('RGBA')
            assert max(image.size) <= 2048
        x, y, width, height = frame['region']
        assert [width, height] == info['frame_size']
        assert x >= 0 and y >= 0 and x + width <= image.width and y + height <= image.height
        with Image.open(ASSETS / 'review' / name / 'detail_130_frames' / f'frame_{i:03}.png') as expected:
            assert np.array_equal(np.asarray(image.crop((x, y, x + width, y + height))), np.asarray(expected.convert('RGBA')))
        total += 1
    if image is not None:
        image.close()
    print(name, len(info['frames']), 'verified', flush=True)
print('PASS:', len(NAMES), 'assets,', total, 'frames')
