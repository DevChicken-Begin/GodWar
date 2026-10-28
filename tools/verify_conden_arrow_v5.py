#!/usr/bin/env python3
"""Check arrow provenance, acceleration, full shaft and all atlas regions."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
entry = next(e for e in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets'] if e['id'] == 'conden')
folder = ASSETS / 'repaired_v5_candidates/conden'
meta = json.loads((folder / 'candidate.json').read_text())
assert meta['source_sha256'] == hashlib.sha256((ROOT / entry['source']).read_bytes()).hexdigest()
for ref in meta['references']:
    assert ref['sha256'] == hashlib.sha256((ROOT / ref['path']).read_bytes()).hexdigest()
assert meta['frame_count'] == len(meta['frames']) == 56
positions = meta['projectile_positions']
steps = [b-a for a, b in zip(positions, positions[1:])]
assert steps == meta['steps_per_70ms'] and steps == sorted(steps)
assert 0.70 <= steps[0]/meta['reference_step_per_70ms'] < 0.72
assert steps[-1] == meta['reference_step_per_70ms']
assert positions[-1] >= meta['display_size'][0]
with Image.open(folder / 'projectile_template.png') as image:
    projectile = image.convert('RGBA')
shaft = np.array(projectile)[36:42, :145]
assert np.all(shaft[:, :, 3] == 255) and np.all(shaft[:, :, :3] >= 240)
modified = []
page_no = -1
for index, frame in enumerate(meta['frames']):
    source = entry['frames'][frame['source_index']]
    x, y, w, h = source['region']
    with Image.open(ASSETS / f'batch_candidates/conden/atlas_{source["atlas"]:03}.png') as image:
        original = image.convert('RGBA').crop((x, y, x+w, y+h))
    expected = Image.new('RGBA', tuple(meta['display_size']))
    expected.paste(original, (0, 0))
    if frame['synthetic']:
        modified.append(frame['projectile_x'])
        expected.alpha_composite(projectile, (frame['projectile_x'], 390))
    assert frame['duration_ms'] == source['duration_ms'] == 70
    if page_no != frame['atlas']:
        page_no = frame['atlas']
        with Image.open(folder / f'atlas_{page_no:03}.png') as image:
            page = image.convert('RGBA')
    x, y, w, h = frame['region']
    assert np.array_equal(np.asarray(page.crop((x, y, x+w, y+h))), np.asarray(expected))
assert modified == positions
print('PASS: 56 frames, source and screenshot hashes, shaft, 12 projectile positions, 70%-to-100% acceleration and full exit')
