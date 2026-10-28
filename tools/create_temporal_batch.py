#!/usr/bin/env python3
"""Experimental scene subtraction; static foreground cannot be distinguished reliably."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; ASSETS=ROOT/'Asset/Character'
NAMES=('overight','skypit','tigerknight')


def create(entry):
    name=entry['id']; source=ROOT/entry['source']; out=ASSETS/'temporal_candidates'/name
    if out.exists(): raise ValueError(f'Refusing to overwrite: {out}')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['source_sha256']:raise ValueError('Source hash mismatch')
    # Estimate RGB scene minimum per pixel in a single pass, then render from source.
    with Image.open(source) as gif:
        baseline=None
        for i in range(gif.n_frames):
            gif.seek(i); frame=np.array(gif.convert('RGB'))
            baseline=frame if baseline is None else np.minimum(baseline,frame)
        baseline=baseline.astype(np.int16)
        out.mkdir(parents=True);page=-1; atlas=None
        for i,item in enumerate(entry['frames']):
            gif.seek(i); image=np.array(gif.convert('RGBA'))
            diff=np.max(np.abs(image[:,:,:3].astype(np.int16)-baseline),axis=2)
            image[diff<=16]=0
            if item['atlas']!=page:
                if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
                page=item['atlas']
                with Image.open(ASSETS/'extracted'/name/f'atlas_{page:03d}.png') as old:atlas=Image.new('RGBA',old.size)
            x,y,_,_=item['region'];atlas.paste(Image.fromarray(image),(x,y))
        if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
    meta={'source':entry['source'],'source_sha256':entry['source_sha256'],'frame_count':entry['frame_count'],'frames':entry['frames'],
          'method':'temporal RGB minimum, max channel distance > 16','status':'candidate_unreviewed',
          'limitations':'Static/dark character pixels or effects may be erased; residual scene may persist. Requires every-frame visual review.'}
    (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,entry['frame_count'],'frames; unreviewed',flush=True)


def main():
    catalog={x['id']:x for x in json.loads((ASSETS/'extracted/catalog.json').read_text())['assets']}
    for name in NAMES:create(catalog[name])
if __name__=='__main__':main()
