#!/usr/bin/env python3
"""Compare every extracted frame and delay against the original GIFs."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
ATLAS_ROOT = ROOT / 'Asset/Character/extracted'


def main():
    catalog = json.loads((ATLAS_ROOT / 'catalog.json').read_text(encoding='utf-8'))
    total = 0
    for entry in catalog['assets']:
        source = ROOT / entry['source']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256'], source
        with Image.open(source) as gif:
            assert gif.n_frames == len(entry['frames']) == entry['frame_count'], source
            page_number, page = None, None
            try:
                for index, frame in enumerate(entry['frames']):
                    gif.seek(index)
                    assert gif.info.get('duration', 0) == frame['duration_ms'], (source, index, 'duration')
                    if frame['atlas'] != page_number:
                        if page is not None:
                            page.close()
                        page_number = frame['atlas']
                        page = Image.open(ATLAS_ROOT / entry['id'] / f'atlas_{page_number:03d}.png').convert('RGBA')
                    x, y, w, h = frame['region']
                    assert w == gif.width and h == gif.height and x >= 0 and y >= 0 and x+w <= page.width and y+h <= page.height, (source,index,'region')
                    expected = gif.convert('RGBA')
                    actual = page.crop((x, y, x+w, y+h))
                    assert ImageChops.difference(expected, actual).getbbox(alpha_only=False) is None, (source,index,'pixels')
                    total += 1
            finally:
                if page is not None:
                    page.close()
        print(f'{entry["id"]}: {entry["frame_count"]} frames OK', flush=True)
    print(f'PASS: {total} frames across {len(catalog["assets"])} GIFs', flush=True)

if __name__ == '__main__':
    main()
