#!/usr/bin/env python3
"""Ensure cleanup outputs only clear pixels and preserve all other RGBA data."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
folder = ASSETS / 'fire_deep_candidates/fireknight'
metadata = json.loads((folder / 'candidate.json').read_text())
assert hashlib.sha256((ROOT / metadata['source']).read_bytes()).hexdigest() == metadata['source_sha256']
counts = []
last_page = -1
for f in metadata['frames']:
    if f['atlas'] != last_page:
        last_page = f['atlas']
        with Image.open(ASSETS / f'fire_orphan_candidates/fireknight/atlas_{last_page:03}.png') as image:
            before_page = np.array(image.convert('RGBA'))
        with Image.open(folder / f'atlas_{last_page:03}.png') as image:
            after_page = np.array(image.convert('RGBA'))
    x, y, w, h = f['region']
    before, after = before_page[y:y+h, x:x+w], after_page[y:y+h, x:x+w]
    changed = np.any(before != after, axis=2)
    assert np.all(after[changed] == 0)
    allowed = np.array([[0,52,115], [49,56,57], [74,73,74], [57,65,99], [8,77,140]], dtype=np.uint8)
    assert np.all(np.any(np.all(before[changed, :3, None] == allowed.T[None, :, :], axis=1), axis=1))
    counts.append(int(changed.sum()))
assert counts == metadata['removed_per_frame']
print('PASS fireknight:', len(counts), 'frames;', sum(counts), 'additional pixels cleared')

folder = ASSETS / 'review/tigerknight/clean_all_v2_130_frames'
metadata = json.loads((folder / 'candidate.json').read_text())
assert hashlib.sha256((ROOT / metadata['source']).read_bytes()).hexdigest() == metadata['source_sha256']
counts = []
for i in range(len(metadata['removed_pixels_per_frame'])):
    with Image.open(ASSETS / f'review/tigerknight/detail_130_frames/frame_{i:03}.png') as image:
        before = np.array(image.convert('RGBA'))
    with Image.open(folder / f'frame_{i:03}.png') as image:
        after = np.array(image.convert('RGBA'))
    changed = np.any(before != after, axis=2)
    assert np.all(after[changed] == 0)
    counts.append(int(changed.sum()))
assert counts == metadata['removed_pixels_per_frame']
print('PASS tigerknight:', len(counts), 'frames;', sum(counts), 'pixels cleared')
