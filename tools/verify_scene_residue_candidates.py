#!/usr/bin/env python3
"""Verify source, timings, and pixel invariants of scene-residue candidates."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; total=0
for name in ('animent','overight','skypit'):
 folder=A/'scene_detail_v3_candidates'/name; m=json.loads((folder/'candidate.json').read_text()); source=ROOT/m['source']
 assert hashlib.sha256(source.read_bytes()).hexdigest()==m['source_sha256']
 for ref in m['reference_sources']: assert hashlib.sha256((ROOT/ref['source']).read_bytes()).hexdigest()==ref['sha256']
 assert hashlib.sha256((ROOT/m['user_sample']['path']).read_bytes()).hexdigest()==m['user_sample']['sha256']
 with Image.open(source) as gif:
  assert gif.n_frames==len(m['frames'])==len(m['removed_per_frame'])==m['frame_count']
  current=-1; before=after=None
  for i,f in enumerate(m['frames']):
   if current!=f['atlas']:
    if before is not None: before.close(); after.close()
    current=f['atlas']; filename=f'atlas_{current:03d}.png'
    before=Image.open(A/m['base_candidate']/name/filename).convert('RGBA'); after=Image.open(folder/filename).convert('RGBA')
    assert before.size==after.size
   gif.seek(i); assert gif.info.get('duration',0)==f['duration_ms'];x,y,w,h=f['region']; box=(x,y,x+w,y+h)
   b=np.array(before.crop(box));a=np.array(after.crop(box));s=np.array(gif.convert('RGBA')); changed=np.any(a!=b,axis=2)
   assert np.all(a[changed]==0) and np.all(b[changed,3]>0)
   assert int(changed.sum())==m['removed_per_frame'][i]
   assert np.array_equal(a[a[:,:,3]>0],s[a[:,:,3]>0]);total+=1
  if before is not None: before.close();after.close()
 print(name, m['frame_count'], 'frames OK',flush=True)
print('PASS',total,'frames; pixel invariants, not visual approval')
