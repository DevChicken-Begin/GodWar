#!/usr/bin/env python3
"""Check the experimental cleanup changes only its specified isolated pixels."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
assets = root / 'Asset/Character'
folder = assets / 'fire_orphan_candidates/fireknight'
metadata = json.loads((folder / 'candidate.json').read_text())
assert hashlib.sha256((root / metadata['source']).read_bytes()).hexdigest() == metadata['source_sha256']
total = 0
page_number = -1
for i, frame in enumerate(metadata['frames']):
    if page_number != frame['atlas']:
        page_number = frame['atlas']
        with Image.open(assets / f'detailed_candidates/fireknight/atlas_{page_number:03}.png') as image:
            before_page = np.array(image.convert('RGBA'))
        with Image.open(folder / f'atlas_{page_number:03}.png') as image:
            after_page = np.array(image.convert('RGBA'))
    x, y, w, h = frame['region']
    before = before_page[y:y+h, x:x+w]
    after = after_page[y:y+h, x:x+w]
    visible = before[:, :, 3] > 0
    rgb = before[:, :, :3]
    target = visible & np.all(rgb == [0, 52, 115], axis=2)
    _, labels, stats, _ = cv2.connectedComponentsWithStats(target.astype('uint8'), 8)
    mask = target & (stats[labels, cv2.CC_STAT_AREA] == 1)
    _, labels, stats, _ = cv2.connectedComponentsWithStats(visible.astype('uint8'), 8)
    gray = np.all(rgb == [49, 56, 57], axis=2) | np.all(rgb == [74, 73, 74], axis=2)
    mask |= visible & gray & (stats[labels, cv2.CC_STAT_AREA] <= 3)
    expected = before.copy()
    expected[mask] = 0
    assert np.array_equal(expected, after)
    assert int(mask.sum()) == metadata['removed_per_frame'][i]
    total += int(mask.sum())
print(f'PASS: {len(metadata["frames"])} frames, {total} removed pixels; every other pixel unchanged')
