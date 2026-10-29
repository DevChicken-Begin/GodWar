#!/usr/bin/env python3
"""Preserve the previously selected Conden timeline in a height-scaled atlas."""
import json
from pathlib import Path
from PIL import Image
from build_measured_atlas_pilots import A, ROOT, pack, sha

def main():
    base = json.loads((A/'tune_60fps_candidates/conden/candidate.json').read_text())
    reference = json.loads((A/'measured_atlas_pilots/conden/candidate.json').read_text())
    assert base['source_sha256'] == reference['source_sha256'] == sha(ROOT/base['source'])
    # Existing detail frames are 1.2x the source canvas, including the shared anchor.
    image_scale = 1.2
    images, hashes = [], {}
    for frame in base['frames']:
        path = A/frame['image_variant']/'conden'/f'frame_{frame["image_index"]:03d}.png'
        key = str(path.relative_to(ROOT))
        if key not in hashes: hashes[key] = sha(path)
        with Image.open(path) as im: images.append(im.convert('RGBA'))
    assert all(im.size == (1152,864) for im in images)
    pack('conden_tuned', images, [f['duration_ms'] for f in base['frames']],
         reference['target_height_px'], reference['reference_height_px'] * image_scale,
         [round(v * image_scale, 4) for v in reference['anchor_px']],
         {'source':base['source'], 'source_sha256':base['source_sha256'],
          'input_candidate':'tune_60fps_candidates/conden', 'input_sha256':hashes,
          'measurement_kind':'automatic_alpha_bbox_unreviewed',
          'source_timeline_note':'Preserves the previously selected 61-frame timeline, including reconstructed projectile frames.'})

if __name__ == '__main__': main()
