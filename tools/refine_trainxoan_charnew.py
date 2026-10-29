#!/usr/bin/env python3
"""Remove the observed near-background GIF palette speckles from Trainxoan."""
import json, os
from pathlib import Path
import numpy as np
from PIL import Image
from import_oct29_gifs import background
from import_charnew import A, ROOT, digest, write
p=A/'measured_atlas_pilots/Trainxoan'; m=json.loads((p/'candidate.json').read_text()); source=ROOT/m['source']; assert digest(source)==m['source_sha256']
page=None; atlas=None; removed=[]; first=None
with Image.open(source) as gif:
 for i,f in enumerate(m['frames']):
  gif.seek(i); raw=np.array(gif.convert('RGBA')); bg=background(gif.convert('RGBA')); mask=np.max(np.abs(raw[:,:,:3].astype(np.int16)-bg.astype(np.int16)),axis=2)<=8; removed.append(int(mask.sum()));raw[mask]=0; frame=Image.fromarray(raw)
  if i==0: first=frame.copy()
  if page!=f['atlas']:
   if atlas is not None: atlas.save(p/f'atlas_{page:03d}.png',compress_level=3)
   page=f['atlas']; path=p/f'atlas_{page:03d}.png'; atlas=Image.new('RGBA',Image.open(path).size)
  x,y,_,_=f['region']; atlas.paste(frame,(x,y))
 atlas.save(p/f'atlas_{page:03d}.png',compress_level=3)
bbox=first.getbbox(); ref=bbox[3]-bbox[1]; m.update(reference_height_px=ref,reference_alpha_bounds=list(bbox),anchor_px=[(bbox[0]+bbox[2])/2,bbox[3]],display_scale=85/ref,removed_per_frame=removed,method='Modal border RGB per frame; remove RGB distance <= 8 to clear observed dark background palette noise; retain all frames and timing.')
write(p/'candidate.json',m)
t=A/'characters/height-targets.json'; data=json.loads(t.read_text()); item=next(x for x in data['assets'] if x['id']=='Trainxoan');item['scale']=85/ref;write(t,data)
print('Trainxoan',len(m['frames']),'bbox',bbox,'ref',ref,'scale',85/ref,'removed',sum(removed))
