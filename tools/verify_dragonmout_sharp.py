#!/usr/bin/env python3
"""Verify the sharp candidate's geometry and alpha against its base."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='dragonmout';out=A/'sharp_candidates'/n;m=json.loads((out/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256'];base=A/m['base_candidate']/n
with Image.open(src) as gif:
 assert gif.n_frames==m['frame_count']==len(m['frames'])==len(m['changed_per_frame']);page=-1;before=after=None
 for i,f in enumerate(m['frames']):
  gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
  if f['atlas']!=page:
   if before is not None:before.close();after.close()
   page=f['atlas'];fn=f'atlas_{page:03d}.png';before=Image.open(base/fn).convert('RGBA');after=Image.open(out/fn).convert('RGBA');assert before.size==after.size
  x,y,w,h=f['region'];box=x,y,x+w,y+h;p=np.array(before.crop(box));q=np.array(after.crop(box));assert np.array_equal(p[:,:,3],q[:,:,3]);assert np.all(q[q[:,:,3]==0]==0);assert int(np.any(p!=q,axis=2).sum())==m['changed_per_frame'][i]
 if before is not None:before.close();after.close()
print('PASS: 21 frames, alpha, timing, canvas and change counts; visual sharpness not established')
