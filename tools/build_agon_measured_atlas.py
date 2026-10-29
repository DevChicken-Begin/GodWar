#!/usr/bin/env python3
"""Pack Agon's visually inspected frame-0 reference and all source frames."""
import json
from pathlib import Path
from PIL import Image
from build_measured_atlas_pilots import pack, sha

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
entry = next(x for x in json.loads((A/'extracted/catalog.json').read_text())['assets'] if x['id'] == 'agon')
assert sha(ROOT / entry['source']) == entry['source_sha256']
base = A/'fine_candidates/agon'
images, hashes = [], {}
for frame in entry['frames']:
    path = base / f'atlas_{frame["atlas"]:03d}.png'
    hashes[str(path.relative_to(ROOT))] = sha(path)
    x, y, w, h = frame['region']
    with Image.open(path) as atlas:
        images.append(atlas.crop((x,y,x+w,y+h)).convert('RGBA'))
assert images[0].getbbox() == (125, 145, 295, 365)
pack('agon', images, [f['duration_ms'] for f in entry['frames']], 90, 220, [210,365],
     {'source': entry['source'], 'source_sha256': entry['source_sha256'], 'input_atlas_sha256': hashes})
