#!/usr/bin/env python3
"""Separate the two non-overlapping figures in the supplied crapit sequence."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
BASE = A / 'fine_candidates/crapit'
OUT = A / 'scale_pilots/crapit_v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    catalog = json.loads((A / 'extracted/catalog.json').read_text())
    entry = next(x for x in catalog['assets'] if x['id'] == 'crapit')
    base = json.loads((BASE / 'candidate.json').read_text())
    assert digest(ROOT / entry['source']) == entry['source_sha256'] == base['source_sha256']
    assert entry['size'] == [512, 512] and len(entry['frames']) == 24
    # The vertical corridor is transparent across every source frame.
    frames = []
    for frame in entry['frames']:
        x, y, w, h = frame['region']
        with Image.open(BASE / f'atlas_{frame["atlas"]:03d}.png') as atlas:
            image = atlas.crop((x, y, x + w, y + h)).convert('RGBA')
        assert image.getchannel('A').crop((172, 0, 252, 512)).getbbox() is None
        frames.append(image)
    OUT.mkdir(parents=True)
    parts = [('main', (230, 0, 512, 512), 100), ('secondary', (0, 0, 230, 512), 40)]
    result = {'source': entry['source'], 'source_sha256': entry['source_sha256'],
              'base_candidate': 'fine_candidates/crapit', 'base_metadata_sha256': digest(BASE / 'candidate.json'),
              'frame_count': len(frames), 'duration_ms': [f['duration_ms'] for f in entry['frames']],
              'art_source': 'existing', 'split_x': 230, 'parts': {}, 'status': 'candidate_unreviewed'}
    for name, box, height in parts:
        folder = OUT / name
        folder.mkdir()
        for i, frame in enumerate(frames):
            frame.crop(box).save(folder / f'frame_{i:03d}.png')
        bbox = frames[0].crop(box).getbbox()
        assert bbox is not None
        ref_height = bbox[3] - bbox[1]
        result['parts'][name] = {'crop_source': list(box), 'frame_size': [box[2]-box[0], box[3]-box[1]],
                                 'reference_frame': 0, 'visible_bbox': list(bbox),
                                 'reference_visible_height': ref_height, 'target_height_px': height,
                                 'display_scale_candidate': height / ref_height,
                                 'note': 'Frame 0 alpha bounds may include effects; verify the actual body and ground anchor before use.'}
    (OUT / 'candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('crapit:', len(frames), 'frames, transparent corridor verified; main and secondary separated')


if __name__ == '__main__':
    main()
