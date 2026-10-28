#!/usr/bin/env python3
"""Build reversible, explicitly synthetic optical-flow midpoint experiments."""
import argparse
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
BASES = {'blacktiger': 'special_candidates', 'firer': 'batch_candidates'}


def midpoint(a, b):
    h, w = a.shape[:2]
    small = (max(16, w // 3), max(16, h // 3))
    # Alpha is used as a silhouette feature alongside luminance, so motion of
    # transparent sprites can be estimated without inventing a background.
    def feature(rgba):
        color = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
        return cv2.resize(np.maximum(color * (rgba[:, :, 3] / 255.0), rgba[:, :, 3] * .45).astype('uint8'), small)
    fa, fb = feature(a), feature(b)
    alg = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    def flow(x, y):
        f = alg.calc(x, y, None)
        f = cv2.resize(f, (w, h), interpolation=cv2.INTER_LINEAR)
        f[:, :, 0] *= w / small[0]
        f[:, :, 1] *= h / small[1]
        return f
    fwd, rev = flow(fa, fb), flow(fb, fa)
    yy, xx = np.indices((h, w), dtype=np.float32)
    left = cv2.remap(a, xx - fwd[:, :, 0] * .5, yy - fwd[:, :, 1] * .5, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
    right = cv2.remap(b, xx - rev[:, :, 0] * .5, yy - rev[:, :, 1] * .5, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
    # Use one original pixel at each location, never translucent crossfades.
    # In overlap use the earlier pose; new visible areas come from the later pose.
    result = left.copy()
    use_right = (left[:, :, 3] == 0) & (right[:, :, 3] > 0)
    result[use_right] = right[use_right]
    return result


def main(name):
    catalog = json.loads((ASSETS / 'extracted/catalog.json').read_text())
    entry = next(x for x in catalog['assets'] if x['id'] == name)
    source = ROOT / entry['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
    base = ASSETS / BASES[name] / name
    meta = json.loads((base / 'candidate.json').read_text())
    assert meta['source_sha256'] == entry['source_sha256']
    folder = ASSETS / 'motion_candidates' / name
    if folder.exists():
        raise FileExistsError(folder)
    folder.mkdir(parents=True)
    images = []
    for f in entry['frames']:
        x, y, w, h = f['region']
        with Image.open(base / f'atlas_{f["atlas"]:03}.png') as im:
            images.append(np.array(im.convert('RGBA').crop((x, y, x+w, y+h))))
    h, w = images[0].shape[:2]
    columns, rows = 2048 // w, 2048 // h
    if columns == 0 or rows == 0:
        raise ValueError('Frame exceeds atlas page size')
    capacity = columns * rows
    n = len(images) * 2
    pages, frames = {}, []
    for i, image in enumerate(images):
        duration = entry['frames'][i]['duration_ms']
        assert duration >= 2
        for extra, pixels in enumerate((image, midpoint(image, images[(i+1) % len(images)]))):
            j = 2*i + extra
            page, slot = divmod(j, capacity)
            if page not in pages:
                count = min(capacity, n - page * capacity)
                pages[page] = Image.new('RGBA', (min(columns, count)*w, ((count+columns-1)//columns)*h))
            x, y = (slot % columns)*w, (slot // columns)*h
            pages[page].paste(Image.fromarray(pixels), (x, y))
            frames.append({'atlas': page, 'region': [x, y, w, h], 'duration_ms': duration // 2 if extra == 0 else duration - duration // 2, 'source_index': i, 'synthetic': bool(extra)})
        print(name, i+1, '/', len(images), flush=True)
    for page, image in pages.items():
        image.save(folder / f'atlas_{page:03}.png')
    output = {'id': name, 'source': entry['source'], 'source_sha256': entry['source_sha256'], 'base_candidate': BASES[name],
              'frame_count': n, 'frames': frames, 'loop': entry['loop'],
              'method': 'DIS optical flow at one-third canvas resolution; nearest-neighbor midpoint warps without crossfade; preserve every source frame and total duration.',
              'status': 'candidate_unreviewed', 'limitations': 'Optical flow can bend or duplicate body parts and VFX, especially during rapid changes, cuts and loop boundaries; each midpoint needs visual review.'}
    (folder / 'candidate.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', choices=BASES)
    main(parser.parse_args().name)
