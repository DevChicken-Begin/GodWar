#!/usr/bin/env python3
"""Create selected non-destructive candidates; visual validation still required."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'Asset/Character/refined_candidates'
CATALOG = ROOT / 'Asset/Character/extracted/catalog.json'


def create(entry):
    asset_id = entry['id']
    source = ROOT / entry['source']
    if hashlib.sha256(source.read_bytes()).hexdigest() != entry['source_sha256']:
        raise ValueError(f'Source hash mismatch: {source}')
    target = OUTPUT / asset_id
    if target.exists():
        raise ValueError(f'Refusing to overwrite: {target}')
    with Image.open(source) as gif:
        frames = []
        for i in range(gif.n_frames):
            gif.seek(i)
            frames.append(np.asarray(gif.convert('RGBA')).copy())
    stack = np.stack(frames)
    if asset_id == 'animent':
        # A temporal minimum is only a rough background estimate; static foreground
        # or foreground as dark as the backdrop can disappear. Never mark approved.
        baseline = np.min(stack[:,:,:,:3], axis=0).astype(np.int16)
        distances = np.max(np.abs(stack[:,:,:,:3].astype(np.int16) - baseline), axis=3)
        masks = distances > 16
        method = 'temporal RGB minimum; max channel difference > 16'
        limitation = 'Dark or static foreground may be lost; colored background may remain. Requires detailed frame-by-frame visual review.'
    else:
        background = stack[0,0,0].copy()
        w, h = entry['size']
        if not all(np.array_equal(frame[y, x], background) for frame in stack for x,y in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))):
            raise ValueError(f'Corners vary: {source}')
        # Also clears enclosed pockets. Matching foreground-colored pixels can be lost.
        masks = ~np.all(stack == background, axis=3)
        method = f'exact RGBA color key including enclosed regions: {background.tolist()}'
        limitation = 'Foreground with exactly the background color will also be removed; edge colors may remain. Requires detailed visual review.'
    target.mkdir(parents=True)
    current_page = -1
    atlas = None
    for i, frame in enumerate(entry['frames']):
        if frame['atlas'] != current_page:
            if atlas is not None: atlas.save(target / f'atlas_{current_page:03d}.png', compress_level=1)
            current_page = frame['atlas']
            with Image.open(ROOT / 'Asset/Character/extracted' / asset_id / f'atlas_{current_page:03d}.png') as original:
                atlas = Image.new('RGBA', original.size)
        rgba = stack[i].copy()
        rgba[~masks[i]] = (0, 0, 0, 0)
        x,y,_,_ = frame['region']
        atlas.paste(Image.fromarray(rgba), (x,y))
    if atlas is not None: atlas.save(target / f'atlas_{current_page:03d}.png', compress_level=1)
    metadata = {'source':entry['source'], 'source_sha256':entry['source_sha256'],
                'frame_count':entry['frame_count'], 'frames':entry['frames'], 'method':method,
                'status':'candidate_unreviewed', 'limitations':limitation}
    (target/'candidate.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{asset_id}: {entry["frame_count"]} candidate frames; {method}')


def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('ids',nargs='+'); args=parser.parse_args()
    entries={e['id']:e for e in json.loads(CATALOG.read_text(encoding='utf-8'))['assets']}
    for asset_id in args.ids:
        if asset_id not in entries: raise ValueError(f'Unknown asset: {asset_id}')
        create(entries[asset_id])

if __name__ == '__main__': main()
