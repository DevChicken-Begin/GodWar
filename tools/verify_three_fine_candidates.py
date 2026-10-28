#!/usr/bin/env python3
"""Check original grid, source palette, timing and atlas for Scale2x candidates."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';total=0
for n in ('airpot','amore','aoda'):
 out=A/'fine_candidates'/n;m=json.loads((out/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256'];base=A/m['base_candidate']/n;logical=A/'review'/n/'fine_frames';period=m['grid_period']
 with Image.open(src) as gif:
  assert gif.n_frames==m['frame_count']==len(m['frames'])==len(m['changed_subpixels_per_frame']);page=-1;prev=atlas=None
  for i,f in enumerate(m['frames']):
   gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
   if f['atlas']!=page:
    if prev is not None:prev.close();atlas.close()
    page=f['atlas'];fn=f'atlas_{page:03d}.png';prev=Image.open(base/fn).convert('RGBA');atlas=Image.open(out/fn).convert('RGBA');assert prev.size==atlas.size
   x,y,w,h=f['region'];box=x,y,x+w,y+h;p=np.array(prev.crop(box));cells=p.reshape(h//period,period,w//period,period,4);small=cells[:,0,:,0,:];assert np.all(cells==small[:,None,:,None,:]);palette={tuple(c) for c in small.reshape(-1,4)}
   with Image.open(logical/f'frame_{i:03d}.png') as q:
    q=q.convert('RGBA');assert list(q.size)==m['refined_canvas'];v=np.array(q);assert all(tuple(c) in palette for c in v.reshape(-1,4));plain=np.repeat(np.repeat(small,2,axis=0),2,axis=1);assert int(np.any(v!=plain,axis=2).sum())==m['changed_subpixels_per_frame'][i];expected=q.resize((w,h),Image.Resampling.NEAREST)
   actual=atlas.crop(box);assert ImageChops.difference(actual,expected).getbbox(alpha_only=False) is None
   if n=='airpot':assert np.array(actual)[:, :, 3][h-45:,w-110:].max()==0
   total+=1
  if prev is not None:prev.close();atlas.close()
 print(n,m['frame_count'],'frames verified')
print('PASS:',total,'frames; source-grid, palette, timing, atlas; visual quality unverified')
