#!/usr/bin/env python3
"""Build measured test atlases without downsampling or discarding frames."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
OUT = A / 'measured_atlas_pilots'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pack(name, images, durations, target, reference_height, anchor, provenance):
    dest = OUT / name
    if dest.exists():
        raise FileExistsError(dest)
    dest.mkdir(parents=True)
    width, height = images[0].size
    cols, rows = 2048 // width, 2048 // height
    assert cols and rows and all(im.size == (width, height) for im in images)
    capacity = cols * rows
    refs = []
    for start in range(0, len(images), capacity):
        count = min(capacity, len(images)-start)
        page = Image.new('RGBA', (min(cols, count)*width, ((count+cols-1)//cols)*height))
        for slot in range(count):
            x, y = (slot % cols)*width, (slot // cols)*height
            page.paste(images[start+slot], (x, y))
            refs.append({'atlas': start // capacity, 'region': [x, y, width, height], 'duration_ms': durations[start+slot]})
        page.save(dest / f'atlas_{start // capacity:03d}.png', compress_level=3)
    for original, frame in zip(images, refs):
        x, y, w, h = frame['region']
        with Image.open(dest / f'atlas_{frame["atlas"]:03d}.png') as page:
            assert ImageChops.difference(original, page.crop((x, y, x+w, y+h))).getbbox(alpha_only=False) is None
    meta = {'id': name, **provenance, 'art_source': 'existing', 'frame_count': len(refs), 'frames': refs,
            'frame_size': [width, height], 'target_height_px': target,
            'reference_frame': 0, 'reference_height_px': reference_height,
            'anchor_px': anchor, 'display_scale': target / reference_height,
            'status': 'candidate_unreviewed', 'method': 'Lossless unscaled RGBA frame packing; apply one display_scale to the entire frame and shared anchor.',
            'limitations': 'Reference alpha bounds can include effects; anchor and body height require visual review. Scene and device playback not verified.'}
    (dest / 'candidate.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(name, len(refs), 'frames', target, '/', reference_height, flush=True)


def main():
    cat = {x['id']: x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
    e = cat['amore']
    atlas_path = A/'fine_candidates/amore/atlas_000.png'
    images = []
    with Image.open(atlas_path) as atlas:
        for f in e['frames']:
            assert f['atlas'] == 0
            x, y, w, h = f['region']
            images.append(atlas.crop((x,y,x+w,y+h)).convert('RGBA'))
    pack('amore', images, [f['duration_ms'] for f in e['frames']], 80, 94, [126,208],
         {'source': e['source'], 'source_sha256': e['source_sha256'], 'input': str(atlas_path.relative_to(ROOT)), 'input_sha256': sha(atlas_path)})
    pilot = A/'scale_pilots/crapit_v1'
    meta = json.loads((pilot/'candidate.json').read_text())
    for key, name, anchor in [('main','crapit_main',[148,332]), ('secondary','crapit_secondary',[128,332])]:
        part = meta['parts'][key]
        paths = [pilot/key/f'frame_{i:03d}.png' for i in range(meta['frame_count'])]
        images = []
        for p in paths:
            with Image.open(p) as image:
                images.append(image.convert('RGBA'))
        pack(name, images, meta['duration_ms'], part['target_height_px'], part['reference_visible_height'], anchor,
             {'source': meta['source'], 'source_sha256': meta['source_sha256'], 'input': str((pilot/'candidate.json').relative_to(ROOT)),
              'input_sha256': sha(pilot/'candidate.json'), 'input_frame_sha256': {p.name:sha(p) for p in paths}})


if __name__ == '__main__':
    main()
