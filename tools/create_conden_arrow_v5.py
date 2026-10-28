#!/usr/bin/env python3
"""Make a review candidate with a source-sampled shaft and accelerating flight."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
entry = next(e for e in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets'] if e['id'] == 'conden')
source = ROOT / entry['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
base = ASSETS / 'batch_candidates/conden'
assert json.loads((base / 'candidate.json').read_text())['source_sha256'] == entry['source_sha256']
out = ASSETS / 'repaired_v5_candidates/conden'
if out.exists():
    raise FileExistsError(out)
out.mkdir(parents=True)

def read_frame(index):
    frame = entry['frames'][index]
    x, y, w, h = frame['region']
    with Image.open(base / f'atlas_{frame["atlas"]:03}.png') as image:
        return image.convert('RGBA').crop((x, y, x+w, y+h))

# The source frame contains the shaft behind the bow and a separate bright tip.
# Repeat a white column sampled from the unobscured shaft to reconstruct the
# section hidden by the bow/hand. This is synthetic and recorded separately.
reference = read_frame(43)
tip = reference.crop((575, 390, 715, 465))
shaft_column = reference.crop((475, 420, 476, 426))
shaft = np.array(shaft_column)
assert np.all(shaft[:, 0, 3] == 255) and np.all(shaft[:, 0, :3] >= 240)
projectile = Image.new('RGBA', (285, 75))
projectile.paste(shaft_column.resize((145, 6), Image.Resampling.NEAREST), (0, 36))
projectile.alpha_composite(tip, (145, 0))
projectile.save(out / 'projectile_template.png')

# Baseline previous experiment: 55 pixels per 70 ms source frame. Distances below
# rise from 39/55 (~70%) to 55/55 (100%) over consecutive intervals.
steps = [39, 41, 43, 45, 48, 51, 55, 55, 55, 55, 55]
positions = [455]
for step in steps:
    positions.append(positions[-1] + step)
assert len(positions) == 12
width, height = 960, 720
columns, rows = 2048 // width, 2048 // height
capacity = columns * rows
total = len(entry['frames']) + 8
pages, frames = {}, []
flight_index = 0
for index, original in enumerate(entry['frames']):
    variants = 6 if index == 47 else 2 if index in (44, 45, 46) else 1
    for part in range(variants):
        frame = Image.new('RGBA', (width, height))
        frame.paste(read_frame(index), (0, 0))
        arrow_x = None
        if variants > 1:
            arrow_x = positions[flight_index]
            frame.alpha_composite(projectile, (arrow_x, 390))
            flight_index += 1
        index_out = len(frames)
        page, slot = divmod(index_out, capacity)
        if page not in pages:
            count = min(capacity, total - page * capacity)
            pages[page] = Image.new('RGBA', (min(columns, count)*width, ((count+columns-1)//columns)*height))
        x, y = (slot % columns)*width, (slot // columns)*height
        pages[page].paste(frame, (x, y))
        frames.append({'atlas': page, 'region': [x, y, width, height], 'duration_ms': original['duration_ms'],
                       'source_index': index, 'synthetic': variants > 1, 'projectile_x': arrow_x})
for page, image in pages.items():
    image.save(out / f'atlas_{page:03}.png')
references = []
for name in ('conden-before-shot.png', 'conden-missing-shaft.png'):
    path = ASSETS / 'review/request-20261028' / name
    references.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
meta = {'id': 'conden', 'source': entry['source'], 'source_sha256': entry['source_sha256'],
        'base_candidate': 'batch_candidates', 'frame_count': len(frames), 'frames': frames,
        'loop': entry['loop'], 'display_size': [width, height], 'references': references,
        'projectile_reference_frame': 43, 'tip_region_xyxy': [575, 390, 715, 465],
        'shaft_column_region_xyxy': [475, 420, 476, 426], 'shaft_length': 145,
        'projectile_positions': positions, 'steps_per_70ms': steps, 'reference_step_per_70ms': 55,
        'method': 'Reuse original tip and reconstruct the occluded shaft by repeating an unobscured source pixel column; move at 70%-to-100% of the prior candidate step.',
        'status': 'candidate_unreviewed',
        'limitations': 'The shaft under the bow is reconstructed; accelerating motion is synthetic and uses the 55 px per 70 ms source frame in the previous candidate as its speed reference. The wider canvas requires anchor adjustment.'}
(out / 'candidate.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
print('conden:', len(frames), 'frames; projectile positions', positions, '; step distances', steps)
