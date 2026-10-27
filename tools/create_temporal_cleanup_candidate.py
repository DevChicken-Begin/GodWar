#!/usr/bin/env python3
"""Generate an alternative temporal mask for visual comparison; not production-ready."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]/'Asset/Character'
SOURCE=ROOT/'refined_candidates/animent'
DEST=ROOT/'cleanup_candidates/animent'

def main():
    if DEST.exists(): raise ValueError(f'Refusing to overwrite: {DEST}')
    meta=json.loads((SOURCE/'candidate.json').read_text(encoding='utf-8'))
    frames=[]
    with Image.open(ROOT/'vfx/animent.gif') as gif:
        for i in range(gif.n_frames):
            gif.seek(i);frames.append(np.array(gif.convert('RGBA')))
    stack=np.stack(frames); baseline=np.min(stack[:,:,:,:3],axis=0).astype(np.int16)
    masks=np.max(np.abs(stack[:,:,:,:3].astype(np.int16)-baseline),axis=3)>32
    DEST.mkdir(parents=True)
    page_number=-1; atlas=None
    for i,info in enumerate(meta['frames']):
        if info['atlas']!=page_number:
            if atlas: atlas.save(DEST/f'atlas_{page_number:03d}.png',compress_level=1)
            page_number=info['atlas']
            with Image.open(SOURCE/f'atlas_{page_number:03d}.png') as old: atlas=Image.new('RGBA',old.size)
        img=stack[i].copy();img[~masks[i]]=0;x,y,_,_=info['region'];atlas.paste(Image.fromarray(img),(x,y))
    if atlas:atlas.save(DEST/f'atlas_{page_number:03d}.png',compress_level=1)
    meta.update({'method':'temporal RGB minimum; max channel difference > 32',
                 'limitations':'Aggressive background removal may also erase dark/static character details or VFX. Requires frame-by-frame review.',
                 'status':'candidate_unreviewed'})
    (DEST/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'animent: {len(frames)} frames; alternate threshold 32, visual review required')

if __name__=='__main__':main()
