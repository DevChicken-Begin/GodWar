#!/usr/bin/env python3
"""Validate local fixes are transparent-only relative to prior candidates."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';total=0
for n in ('animent','scorpit'):
 out=A/'oct28_fix_candidates'/n;m=json.loads((out/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
 with Image.open(src) as gif:
  assert gif.n_frames==len(m['frames'])==len(m['removed_per_frame']);page=-1;a=b=None
  for i,f in enumerate(m['frames']):
   if page!=f['atlas']:
    if a is not None:a.close();b.close()
    page=f['atlas'];fn=f'atlas_{page:03d}.png';a=Image.open(A/m['base_candidate']/n/fn).convert('RGBA');b=Image.open(out/fn).convert('RGBA')
   gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms'];x,y,w,h=f['region'];box=(x,y,x+w,y+h);p=np.array(a.crop(box));q=np.array(b.crop(box));orig=np.array(gif.convert('RGBA'));changed=np.any(p!=q,axis=2);assert np.all(q[changed]==0) and int(changed.sum())==m['removed_per_frame'][i];assert np.array_equal(q[q[:,:,3]>0],orig[q[:,:,3]>0]);total+=1
  if a is not None:a.close();b.close()
 print(n,m['frame_count'],'frames OK')
print('PASS',total,'frames; visual quality and effect preservation remain unverified')
