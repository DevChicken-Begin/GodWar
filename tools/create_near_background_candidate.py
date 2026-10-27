#!/usr/bin/env python3
"""Optional more aggressive candidate: clear colors close to measured flat background."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Asset/Character/refined_candidates/aminao'
DEST=ROOT/'Asset/Character/cleanup_candidates/aminao'

def main():
    if DEST.exists(): raise ValueError(f'Refusing to overwrite: {DEST}')
    metadata=json.loads((SOURCE/'candidate.json').read_text(encoding='utf-8'))
    DEST.mkdir(parents=True)
    count=0
    for path in sorted(SOURCE.glob('atlas_*.png')):
        with Image.open(path) as image: pixels=np.array(image.convert('RGBA'))
        diff=np.max(np.abs(pixels[:,:,:3].astype(np.int16)-np.array([3,50,71])),axis=2)
        mask=(pixels[:,:,3]>0)&(diff<=5)
        count+=int(mask.sum()); pixels[mask]=(0,0,0,0)
        Image.fromarray(pixels).save(DEST/path.name,compress_level=1)
    metadata.update({'method':'remove RGB values within 5 per channel of (3,50,71), after exact-key candidate',
                     'status':'candidate_unreviewed','additional_removed_pixels':count,
                     'limitations':'Foreground or VFX close to background color may be erased. Requires detailed visual review.'})
    (DEST/'candidate.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'aminao: {count} additional pixels cleared; candidate requires detailed review')

if __name__=='__main__': main()
