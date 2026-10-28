#!/usr/bin/env python3
"""Review-only dark-blue cleanup at the requested Tigerknight frame neighborhood."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
assets = root / 'Asset/Character'
name = 'tigerknight'
catalog = json.loads((assets / 'extracted/catalog.json').read_text())
entry = next(item for item in catalog['assets'] if item['id'] == name)
source = root / entry['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
out = assets / 'review' / name / 'clean_all_v2_130_frames'
if out.exists():
    raise FileExistsError(out)
out.mkdir(parents=True)
counts = []
for index, frame in enumerate(entry['frames']):
    detail_path = assets / 'review' / name / 'detail_130_frames' / f'frame_{index:03}.png'
    with Image.open(detail_path) as img:
        detail = np.array(img.convert('RGBA'))
    changed = 0
    if True:
        x, y, w, h = frame['region']
        with Image.open(assets / 'shared_scene_candidates' / name / f'atlas_{frame["atlas"]:03}.png') as img:
            base = np.array(img.convert('RGBA').crop((x, y, x+w, y+h)))
        r, g, b = (base[:, :, c].astype(np.int16) for c in range(3))
        mask = (base[:, :, 3] > 0) & (r < 20) & (g < 85) & (b > g * 1.3) & (b > r * 2) & (b < 160)
        # Match the original canvas to the detail grid; keep the rest untouched.
        scaled = np.asarray(Image.fromarray(mask.astype('uint8') * 255).resize((detail.shape[1], detail.shape[0]), Image.Resampling.NEAREST)) > 0
        dr, dg, db = (detail[:, :, c].astype(np.int16) for c in range(3))
        scaled |= (detail[:, :, 3] > 0) & (dr < 20) & (dg < 85) & (db > dg * 1.3) & (db > dr * 2) & (db < 160)
        changed = int(np.count_nonzero(scaled & (detail[:, :, 3] > 0)))
        detail[scaled] = 0
    Image.fromarray(detail).save(out / f'frame_{index:03}.png')
    counts.append(changed)
metadata = {'id': name, 'source': entry['source'], 'source_sha256': entry['source_sha256'],
            'base_detail': 'review/tigerknight/detail_130_frames', 'mask_base': 'shared_scene_candidates/tigerknight',
            'frames_modified_zero_based': list(range(len(entry['frames']))), 'removed_pixels_per_frame': counts,
            'method': 'Remove dark blue pixels across the full animation on existing 130% detail frames using a mask sampled from the shared-scene candidate plus matching blue left after resampling.',
            'status': 'candidate_unreviewed',
            'limitations': 'Similar dark blue may be legitimate character or VFX detail; this color rule must be reviewed against the GIF on all frames and effects.'}
(out / 'candidate.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(name, 'removed', sum(counts), 'detail pixels:', counts)
