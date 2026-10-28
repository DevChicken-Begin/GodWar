#!/usr/bin/env python3
"""Create review-only, source-specific cleanup variants without changing source pixels."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
OUT = ASSETS / 'detailed_candidates'
BOTTOM = ('artemis', 'javis', 'mainthen', 'powerdame', 'scatra', 'scorpit', 'waven', 'wuchen', 'ziggist')
BLUE = ('animent', 'overight', 'skypit')
NAMES = (*BOTTOM, *BLUE, 'fireknight', 'mortafi')
BASE = {**{n: 'batch_candidates' for n in BOTTOM}, **{n: 'shared_scene_candidates' for n in BLUE}, 'fireknight': 'special_candidates', 'mortafi': 'special_candidates'}
KERNEL = np.ones((3, 3), np.uint8)


def create(entry):
    name = entry['id']
    source = ROOT / entry['source']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != entry['source_sha256']:
        raise ValueError(f'Source hash mismatch: {name}')
    base = ASSETS / BASE[name] / name
    meta = json.loads((base / 'candidate.json').read_text(encoding='utf8'))
    if meta['source_sha256'] != digest:
        raise ValueError(f'Candidate hash mismatch: {name}')
    out = OUT / name
    if out.exists():
        raise FileExistsError(f'Refusing to overwrite {out}')
    with Image.open(source) as gif:
        w, h = gif.size
        gif.seek(0)
        reference = np.array(gif.convert('RGB'), dtype=np.int16)
        stable = np.zeros((h, w), np.uint16)
        for i in range(gif.n_frames):
            gif.seek(i)
            rgb = np.array(gif.convert('RGB'), dtype=np.int16)
            stable += np.max(np.abs(rgb - reference), axis=2) <= 12
        # Only the observed fixed logo areas; matching source pixels are removed,
        # not the whole rectangle, so changed foreground remains.
        region = np.zeros((h, w), bool)
        if name in BOTTOM:
            region[int(h*.87):, int(w*.55):] = True
        if name in ('morexem', 'mortafi'):
            region[int(h*.06):int(h*.29), int(w*.12):int(w*.88)] = True
        logo = region & (stable >= int(gif.n_frames * .70))
        out.mkdir(parents=True)
        page_num = -1
        page = None
        original_page = None
        counts = []
        for i, frame in enumerate(entry['frames']):
            gif.seek(i)
            rgb = np.array(gif.convert('RGB'), dtype=np.int16)
            if frame['atlas'] != page_num:
                if page is not None:
                    page.save(out / f'atlas_{page_num:03d}.png', compress_level=1)
                    original_page.close()
                page_num = frame['atlas']
                original_page = Image.open(base / f'atlas_{page_num:03d}.png')
                page = Image.new('RGBA', original_page.size)
            x, y, fw, fh = frame['region']
            result = np.array(original_page.crop((x, y, x + fw, y + fh)))
            present = result[:, :, 3] > 0
            mask = logo & (np.max(np.abs(rgb - reference), axis=2) <= 12) & present
            logo_count = int(mask.sum())
            blue_count = 0
            if name in BLUE:
                # Color from the user-provided sample, limited to areas touching
                # already transparent pixels; this may still affect blue outlines.
                close = np.max(np.abs(rgb - np.array([2, 64, 116])), axis=2) <= 8
                transparent = (~present | mask).astype(np.uint8)
                seeds = close & present & (cv2.dilate(transparent, KERNEL) > 0)
                num, labels = cv2.connectedComponents(close.astype(np.uint8), connectivity=8)
                touching = np.zeros(num, dtype=bool)
                touching[labels[seeds]] = True
                touching[0] = False
                blue = touching[labels] & present & ~mask
                blue_count = int(blue.sum())
                mask |= blue
            noise_count = 0
            if name == 'fireknight':
                # Remove detached dark residual specks far from bright foreground;
                # preserve close particles and bright effects for manual review.
                dark = (rgb[:, :, 0] < 80) & (rgb[:, :, 1] < 100) & (rgb[:, :, 2] < 150) & present
                bright = present & ~dark
                near = cv2.dilate(bright.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
                noise = dark & ~near & ~mask
                noise_count = int(noise.sum())
                mask |= noise
            result[mask] = 0
            page.paste(Image.fromarray(result), (x, y))
            counts.append({'frame': i, 'logo': logo_count, 'blue': blue_count, 'noise': noise_count})
        if page is not None:
            page.save(out / f'atlas_{page_num:03d}.png', compress_level=1)
            original_page.close()
    metadata = {'source': entry['source'], 'source_sha256': digest, 'base_candidate': BASE[name],
                'sample': {'path': 'image.png', 'sha256': hashlib.sha256((ROOT / 'image.png').read_bytes()).hexdigest(), 'rgb': [2,64,116], 'tolerance': 8} if name in BLUE else None,
                'frames': entry['frames'], 'frame_count': entry['frame_count'], 'removed_per_frame': counts,
                'method': 'Stable source pixels in observed logo region; sample-blue components touching transparency; fireknight detached dark specks far from bright pixels, as applicable.',
                'status': 'candidate_unreviewed', 'limitations': 'Possible loss of similarly colored outlines, text-overlapping foreground, dark details or particles. Base candidate may already have removed details. Inspect every frame against the source.'}
    (out / 'candidate.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(name, 'frames', len(counts), 'removed', sum(sum(v[k] for k in ('logo','blue','noise')) for v in counts), flush=True)


def main():
    entries = {e['id']: e for e in json.loads((ASSETS / 'extracted/catalog.json').read_text(encoding='utf8'))['assets']}
    if any((OUT / name).exists() for name in NAMES):
        raise FileExistsError('A destination exists; refusing to overwrite any candidate')
    for name in NAMES:
        create(entries[name])

if __name__ == '__main__':
    main()
