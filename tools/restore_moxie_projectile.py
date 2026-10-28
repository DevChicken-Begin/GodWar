#!/usr/bin/env python3
"""Experiment: reconstruct three clipped projectiles from an earlier source frame."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
entry = next(x for x in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets'] if x['id'] == 'moxie')
source = ROOT / entry['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
base = ASSETS / 'batch_candidates/moxie'
out = ASSETS / 'repaired_candidates/moxie'
if out.exists():
    raise FileExistsError(out)
out.mkdir(parents=True)

def get_frame(index):
    f = entry['frames'][index]
    x, y, w, h = f['region']
    with Image.open(base / f'atlas_{f["atlas"]:03}.png') as img:
        return img.convert('RGBA').crop((x, y, x+w, y+h))

# The reference orb is visible in the prior source-derived frame. The missing
# portion outside the original GIF is reconstructed, not original image data.
template = get_frame(20).crop((137, 105, 166, 139))
template.save(out / 'projectile_template_frame020.png')
modified = [21, 25, 30]
width, height = 340, 250
columns, rows = 2048 // width, 2048 // height
capacity = columns * rows
pages, frames = {}, []
for i, original in enumerate(entry['frames']):
    page, slot = divmod(i, capacity)
    if page not in pages:
        count = min(capacity, len(entry['frames']) - page*capacity)
        pages[page] = Image.new('RGBA', (min(columns, count)*width, ((count+columns-1)//columns)*height))
    frame = Image.new('RGBA', (width, height))
    frame.paste(get_frame(i), (0, 0))
    if i in modified:
        # Remove only the cut fragment, then add an earlier complete orb at the
        # original edge. Adjacent flame trails and all other source pixels remain.
        pixels = np.array(frame)
        pixels[105:139, 295:300] = 0
        frame = Image.fromarray(pixels)
        frame.alpha_composite(template, (295, 105))
    x, y = (slot % columns)*width, (slot // columns)*height
    pages[page].paste(frame, (x, y))
    frames.append({'atlas': page, 'region': [x, y, width, height], 'duration_ms': original['duration_ms']})
for page, image in pages.items():
    image.save(out / f'atlas_{page:03}.png')
metadata = {'id': 'moxie', 'source': entry['source'], 'source_sha256': entry['source_sha256'], 'base_candidate': 'batch_candidates',
            'frame_count': len(frames), 'frames': frames, 'loop': entry['loop'], 'display_size': [width, height],
            'modified_indices_zero_based': modified, 'template_source_index': 20, 'template_region': [137, 105, 29, 34],
            'method': 'Expand right canvas by 40 pixels and reconstruct the clipped object with a crop of an earlier source-derived frame.',
            'status': 'candidate_unreviewed', 'limitations': 'The area outside the original GIF is reconstructed, not recovered; orb appearance and placement require review during playback.'}
(out / 'candidate.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print('moxie:', len(frames), 'frames; reconstructed:', modified)
