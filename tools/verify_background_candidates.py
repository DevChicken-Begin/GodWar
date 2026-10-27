#!/usr/bin/env python3
"""Check candidate pixel changes against GIFs; cannot determine semantic damage."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / 'Asset/Character/candidates'
OUTPUT = ROOT / 'Asset/Character/review/background-candidate-verification.json'


def main():
    results = []
    for meta_path in sorted(CANDIDATES.glob('*/candidate.json')):
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        source = ROOT / meta['source']
        if hashlib.sha256(source.read_bytes()).hexdigest() != meta['source_sha256']:
            raise ValueError(f'Source changed: {source}')
        changed_pixels = 0
        with Image.open(source) as gif:
            if gif.n_frames != meta['frame_count'] or len(meta['frames']) != gif.n_frames:
                raise ValueError(f'Frame count mismatch: {source}')
            page_number, page = None, None
            try:
                for i, info in enumerate(meta['frames']):
                    gif.seek(i)
                    before = np.asarray(gif.convert('RGBA'))
                    if info['atlas'] != page_number:
                        if page is not None: page.close()
                        page_number = info['atlas']
                        with Image.open(meta_path.parent / f'atlas_{page_number:03d}.png') as source_page:
                            page = source_page.convert('RGBA')
                    x, y, w, h = info['region']
                    after = np.asarray(page.crop((x,y,x+w,y+h)))
                    if before.shape != after.shape: raise ValueError(f'Invalid region: {source}, frame {i}')
                    changed = np.any(before != after, axis=2)
                    allowed = np.all(before == meta['background_rgba'], axis=2) & np.all(after == (0,0,0,0), axis=2)
                    if np.any(changed & ~allowed): raise ValueError(f'Unexpected pixel change: {source}, frame {i}')
                    changed_pixels += int(changed.sum())
            finally:
                if page is not None: page.close()
        if changed_pixels != meta['removed_pixels']: raise ValueError(f'Removed pixel count mismatch: {source}')
        results.append({'id': meta_path.parent.name, 'source': meta['source'], 'frames': meta['frame_count'],
                        'removed_pixels': changed_pixels, 'pixel_check': 'passed', 'visual_status': 'unreviewed'})
        print(f'{meta_path.parent.name}: {meta["frame_count"]} frames pixel check OK', flush=True)
    OUTPUT.write_text(json.dumps({'version': 1, 'limitation': 'Checks exact changed pixel colors, not whether changed pixels belong to a character or VFX; visual review remains required.', 'candidates': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(results)} candidates, {sum(r["frames"] for r in results)} frames', flush=True)

if __name__ == '__main__': main()
