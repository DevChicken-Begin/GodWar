#!/usr/bin/env python3
"""Verify Agon refinement grid, source colors, timing, and atlas packaging."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='agon';out=A/'fine_candidates'/n;m=json.loads((out/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256'];base=A/m['base_candidate']/n;logical=A/'review/agon/fine_frames'
with Image.open(src) as gif:
 assert gif.n_frames==m['frame_count']==len(m['frames'])==len(m['changed_subpixels_per_frame']);page=-1;prev=atlas=None
 for i,f in enumerate(m['frames']):
  gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
  if f['atlas']!=page:
   if prev is not None:prev.close();atlas.close()
   page=f['atlas'];fn=f'atlas_{page:03d}.png';prev=Image.open(base/fn).convert('RGBA');atlas=Image.open(out/fn).convert('RGBA');assert prev.size==atlas.size
  x,y,w,h=f['region'];box=x,y,x+w,y+h;p=np.array(prev.crop(box));cells=p.reshape(h//5,5,w//5,5,4);small=cells[:,0,:,0,:];assert np.all(cells==small[:,None,:,None,:])
  with Image.open(logical/f'frame_{i:03d}.png') as q:
   q=q.convert('RGBA');assert q.size==(190,160);v=np.array(q);palette={tuple(c) for c in small.reshape(-1,4)};assert all(tuple(c) in palette for c in v.reshape(-1,4));plain=np.repeat(np.repeat(small,2,axis=0),2,axis=1);assert int(np.any(v!=plain,axis=2).sum())==m['changed_subpixels_per_frame'][i];expected=q.resize((w,h),Image.Resampling.NEAREST)
  actual=atlas.crop(box);assert ImageChops.difference(actual,expected).getbbox(alpha_only=False) is None
 if prev is not None:prev.close();atlas.close()
print('PASS: 50 frames, uniform 5x5 input, source RGBA palette, 190x160 edges, timing and atlas; visual quality unverified')
