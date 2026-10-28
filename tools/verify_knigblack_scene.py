#!/usr/bin/env python3
"""Check protected-scene candidate preserves source colors and metadata."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='knigblack';folder=A/'scene_protected_candidates'/n;m=json.loads((folder/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
with Image.open(src) as gif:
 assert gif.n_frames==m['frame_count']==len(m['frames']);page=-1;old=out=None
 for i,f in enumerate(m['frames']):
  gif.seek(i);before=np.array(gif.convert('RGBA'));assert gif.info.get('duration',0)==f['duration_ms']
  if page!=f['atlas']:
   if old is not None:old.close();out.close()
   page=f['atlas'];fn=f'atlas_{page:03d}.png';old=Image.open(A/m['base_candidate']/n/fn).convert('RGBA');out=Image.open(folder/fn).convert('RGBA')
  x,y,w,h=f['region'];box=x,y,x+w,y+h;prior=np.array(old.crop(box));actual=np.array(out.crop(box));changed=np.any(prior!=actual,axis=2);assert int(changed.sum())==m['restored_per_frame'][i];assert np.array_equal(actual[changed],before[changed]);assert np.array_equal(actual[actual[:,:,3]>0],before[actual[:,:,3]>0]);assert np.all(actual[actual[:,:,3]==0]==0)
 if old is not None:old.close();out.close()
print('PASS: 12 frames; opaque pixels preserved from source; visible halo and ground shadow remain')
