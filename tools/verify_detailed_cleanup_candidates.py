#!/usr/bin/env python3
"""Check cleanup candidates against the previous candidate and original GIF."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
NAMES = ('animent','artemis','fireknight','javis','mainthen','mortafi','overight','powerdame','scatra','scorpit','skypit','waven','wuchen','ziggist')
total = 0
for name in NAMES:
    folder = ASSETS / 'detailed_candidates' / name
    meta = json.loads((folder / 'candidate.json').read_text())
    path = ROOT / meta['source']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta['source_sha256'], name
    with Image.open(path) as gif:
        assert gif.n_frames == meta['frame_count'] == len(meta['frames']) == len(meta['removed_per_frame']), name
        page_number = -1
        base = result = None
        for i, f in enumerate(meta['frames']):
            if f['atlas'] != page_number:
                if base is not None:
                    base.close(); result.close()
                page_number = f['atlas']
                filename = f'atlas_{page_number:03d}.png'
                base = Image.open(ASSETS / meta['base_candidate'] / name / filename).convert('RGBA')
                result = Image.open(folder / filename).convert('RGBA')
                assert base.size == result.size
            gif.seek(i)
            assert gif.info.get('duration', 0) == f['duration_ms'], (name, i, 'duration')
            x, y, w, h = f['region']
            box = (x, y, x+w, y+h)
            prior, actual, source = (np.asarray(im) for im in (base.crop(box), result.crop(box), gif.convert('RGBA')))
            changed = np.any(prior != actual, axis=2)
            assert np.all(actual[changed] == 0), (name, i, 'changed pixels not transparent')
            assert np.all(prior[changed, 3] > 0), (name, i, 'not previously visible')
            assert np.array_equal(actual[actual[:,:,3] > 0], source[actual[:,:,3] > 0]), (name, i, 'visible differs from GIF')
            count = meta['removed_per_frame'][i]
            assert int(changed.sum()) == sum(count[k] for k in ('logo', 'blue', 'noise')), (name, i, 'count')
            total += 1
        if base is not None:
            base.close(); result.close()
    print(f'{name}: {meta["frame_count"]} frames OK', flush=True)
print(f'PASS: {total} frames across {len(NAMES)} candidates; pixel invariants only, not visual approval')
