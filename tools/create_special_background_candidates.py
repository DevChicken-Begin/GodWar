#!/usr/bin/env python3
"""Make limited, source-specific cleanup candidates, preserving previous versions."""
import hashlib
import json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'Asset/Character'
# Rectangles are measured on source GIF canvases, not inferred gameplay regions.
LOGOS={'mortafi':(100,45,425,140),'omra':(25,20,405,90)}


def create(name):
    source=ROOT/'vfx'/f'{name}.gif';base=ROOT/'batch_candidates'/name;out=ROOT/'special_candidates'/name
    if out.exists():raise ValueError(f'Refusing to overwrite: {out}')
    m=json.loads((base/'candidate.json').read_text(encoding='utf-8'))
    if hashlib.sha256(source.read_bytes()).hexdigest()!=m['source_sha256']:raise ValueError('Source hash mismatch')
    with Image.open(source) as gif:
        gif.seek(0);reference=np.array(gif.convert('RGBA'))
        stable=None
        if name in LOGOS:
            same=np.zeros(reference.shape[:2],dtype=np.uint16)
            for i in range(gif.n_frames):
                gif.seek(i); frame=np.array(gif.convert('RGBA')); same+=np.max(np.abs(frame[:,:,:3].astype(np.int16)-reference[:,:,:3].astype(np.int16)),axis=2)<=8
            x1,y1,x2,y2=LOGOS[name];region=np.zeros(reference.shape[:2],dtype=bool);region[y1:y2,x1:x2]=True
            bg=np.array(m['background_rgba'][:3],dtype=np.int16);dist=np.max(np.abs(reference[:,:,:3].astype(np.int16)-bg),axis=2)
            stable=region & (same>=int(gif.n_frames*.8)) & (dist>5)
        out.mkdir(parents=True);pages={};number=-1;atlas=None;extra=0
        try:
            for i,info in enumerate(m['frames']):
                gif.seek(i);orig=np.array(gif.convert('RGBA'));num=info['atlas']
                if num!=number:
                    if atlas is not None:atlas.save(out/f'atlas_{number:03d}.png',compress_level=1)
                    number=num
                    with Image.open(base/f'atlas_{num:03d}.png') as old:atlas=Image.new('RGBA',old.size)
                if num not in pages:pages[num]=Image.open(base/f'atlas_{num:03d}.png')
                x,y,w,h=info['region'];result=np.array(pages[num].crop((x,y,x+w,y+h)))
                if name in LOGOS:
                    difference=np.max(np.abs(orig[:,:,:3].astype(np.int16)-reference[:,:,:3].astype(np.int16)),axis=2)
                    mask=stable & (difference<=8)
                else:
                    pattern=np.all(orig[:,:,:3]==np.array([57,65,99]),axis=2) | np.all(orig[:,:,:3]==np.array([0,52,115]),axis=2)
                    foreground=(result[:,:,3]>0)&~pattern
                    near_foreground=cv2.dilate(foreground.astype(np.uint8),np.ones((5,5),np.uint8))>0
                    mask=pattern & ~near_foreground
                mask &= result[:,:,3]>0;extra+=int(mask.sum());result[mask]=0
                atlas.paste(Image.fromarray(result),(x,y))
            if atlas is not None:atlas.save(out/f'atlas_{number:03d}.png',compress_level=1)
        finally:
            for page in pages.values():page.close()
    m.update({'method': 'chroma key plus temporally stable logo reference within 8 RGB levels' if name in LOGOS else 'chroma key plus patterned colors away from foreground',
              'additional_removed_pixels':extra,'status':'candidate_unreviewed',
              'limitations':'Pixels matching logo or patterned background may belong to foreground or VFX. Manually inspect every frame, especially overlap.'})
    (out/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,'additional pixels cleared',extra)

if __name__=='__main__':
    for name in ('mortafi','omra','fireknight'):create(name)
