#!/usr/bin/env python3
"""Check timing, source linkage and unmodified frames of animation experiments."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
catalog = {x['id']: x for x in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets']}


def read(folder, frame):
    x, y, w, h = frame['region']
    with Image.open(folder / f'atlas_{frame["atlas"]:03}.png') as image:
        assert x >= 0 and y >= 0 and x+w <= image.width and y+h <= image.height
        return np.asarray(image.convert('RGBA').crop((x, y, x+w, y+h)))


for name in ('blacktiger', 'firer', 'conden', 'moxie'):
    entry = catalog[name]
    variant = 'motion_v2_candidates' if name in ('blacktiger', 'firer') else 'repaired_candidates'
    folder = ASSETS / variant / name
    meta = json.loads((folder / 'candidate.json').read_text())
    assert hashlib.sha256((ROOT / meta['source']).read_bytes()).hexdigest() == meta['source_sha256'] == entry['source_sha256']
    assert meta['frame_count'] == len(meta['frames'])
    assert sum(x['duration_ms'] for x in meta['frames']) == sum(x['duration_ms'] for x in entry['frames'])
    assert all(x['duration_ms'] > 0 for x in meta['frames'])
    base = ASSETS / meta['base_candidate'] / name
    counts = [0] * len(entry['frames'])
    durations = [0] * len(entry['frames'])
    for i, frame in enumerate(meta['frames']):
        source_index = frame.get('source_index', i)
        assert 0 <= source_index < len(entry['frames'])
        counts[source_index] += 1
        durations[source_index] += frame['duration_ms']
        candidate = read(folder, frame)
        original = read(base, entry['frames'][source_index])
        synthetic = frame.get('synthetic', False) or (name == 'moxie' and source_index in meta['modified_indices_zero_based'])
        if not synthetic:
            h, w = original.shape[:2]
            assert np.array_equal(candidate[:h, :w], original)
            assert not np.any(candidate[h:, :, 3]) and not np.any(candidate[:, w:, 3])
    assert all(durations[i] == f['duration_ms'] for i, f in enumerate(entry['frames']))
    assert all(n >= 1 for n in counts)
    print(f'PASS {name}: {len(entry["frames"])} -> {len(meta["frames"])} frames; source timing preserved', flush=True)
