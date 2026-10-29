#!/usr/bin/env python3
"""Verify all automatically prepared height atlas candidates against their inputs."""
import json
from pathlib import Path
from PIL import Image, ImageChops
from build_height_bulk_preview import A, ROOT, OUT, sha

def main():
    catalog = {e['id']: e for filename in ('catalog.json','split-catalog.json')
               for e in json.loads((A/'extracted'/filename).read_text())['assets']}
    count = frames_total = 0
    for folder in sorted(OUT.iterdir()):
        path = folder/'candidate.json'
        if not path.exists(): continue
        meta = json.loads(path.read_text())
        if meta.get('status') != 'automatic_candidate_unreviewed': continue
        name = meta['id']; source = catalog[name]
        assert sha(ROOT/meta['source']) == meta['source_sha256'] == source['source_sha256']
        frames = meta['frames']
        assert len(frames) == meta['frame_count'] == source['frame_count']
        assert [f['duration_ms'] for f in frames] == [f['duration_ms'] for f in source['frames']]
        assert abs(meta['display_scale'] * meta['reference_height_px'] - meta['target_height_px']) < 1e-8
        hashes = meta['input_sha256']
        for path_str, digest in hashes.items():
            assert sha(ROOT/path_str) == digest, path_str
        per_frame = all(Path(path_str).name.startswith('frame_') for path_str in hashes)
        if not per_frame:
            for path_str,digest in hashes.items():
                assert sha(folder/Path(path_str).name) == digest, path_str
        else:
            by_name = {Path(path_str).name: ROOT/path_str for path_str in hashes}
            page_number, atlas = None, None
            try:
                for i,f in enumerate(frames):
                    if f['atlas'] != page_number:
                        if atlas: atlas.close()
                        page_number = f['atlas']
                        atlas = Image.open(folder/f'atlas_{page_number:03d}.png').convert('RGBA')
                    x,y,w,h=f['region']
                    with Image.open(by_name[f'frame_{i:03d}.png']) as source_image:
                        difference=ImageChops.difference(atlas.crop((x,y,x+w,y+h)),source_image.convert('RGBA'))
                        assert difference.getbbox(alpha_only=False) is None, (name,i)
            finally:
                if atlas: atlas.close()
        count += 1; frames_total += len(frames)
        print(name, len(frames), 'OK', flush=True)
    print('PASS', count, 'automatic candidates', frames_total, 'frames')

if __name__ == '__main__': main()
