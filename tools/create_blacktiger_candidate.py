#!/usr/bin/env python3
"""Experimental fixed-floor cleanup for the observed blacktiger reflection."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'Asset/Character';SRC=ROOT/'batch_candidates/blacktiger';OUT=ROOT/'special_candidates/blacktiger'

def main():
 if OUT.exists():raise ValueError('Candidate exists; will not overwrite')
 m=json.loads((SRC/'candidate.json').read_text());OUT.mkdir(parents=True);atlas=None;num=-1;pages={}
 try:
  for f in m['frames']:
   n=f['atlas']
   if n!=num:
    if atlas is not None:atlas.save(OUT/f'atlas_{num:03d}.png',compress_level=1)
    num=n
    with Image.open(SRC/f'atlas_{n:03d}.png') as old:atlas=Image.new('RGBA',old.size)
   if n not in pages:pages[n]=Image.open(SRC/f'atlas_{n:03d}.png')
   x,y,w,h=f['region'];img=np.array(pages[n].crop((x,y,x+w,y+h)));img[520:,:,:]=0
   rows=img[500:520];dark=np.all(rows[:,:,:3]==[113,108,102],axis=2);rows[dark]=0
   atlas.paste(Image.fromarray(img),(x,y))
  if atlas is not None:atlas.save(OUT/f'atlas_{num:03d}.png',compress_level=1)
 finally:
  for p in pages.values():p.close()
 m.update({'method':'chroma key plus fixed reflection cut at y=520 and floor-line color in rows 500–519','status':'candidate_unreviewed', 'limitations':'Any character or VFX below the cut will be erased; requires frame-by-frame verification.'})
 (OUT/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('blacktiger',m['frame_count'],'frames; review required')
if __name__=='__main__':main()
