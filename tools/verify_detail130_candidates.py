#!/usr/bin/env python3
"""Verify source hashes, 130% dimensions and exact generated preview pixels."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
from build_fine_batch import scale2
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';report=json.loads((ROOT/'docs/fine-batch/detail130.json').read_text());total=0
for item in report['results']:
 n=item['id'];folder=A/'detail_130_candidates'/n;m=json.loads((folder/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256'];base=A/m['base_candidate']/n
 for fn,h in m['base_atlas_sha256'].items():assert hashlib.sha256((base/fn).read_bytes()).hexdigest()==h
 with Image.open(src) as gif:
  assert gif.n_frames==m['frame_count']==len(m['frames'])==len(m['detail_sizes']);page=-1;before=after=None
  for i,f in enumerate(m['frames']):
   gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
   if page!=f['atlas']:
    if before is not None:before.close();after.close()
    page=f['atlas'];fn=f'atlas_{page:03d}.png';before=Image.open(base/fn).convert('RGBA');after=Image.open(folder/fn).convert('RGBA');assert before.size==after.size
   x,y,w,h=f['region'];box=x,y,x+w,y+h;view=np.array(before.crop(box))
   if m['base_candidate']=='fine_candidates':
    with Image.open(A/'review'/n/'fine_frames'/f'frame_{i:03d}.png') as im:p=np.array(im.convert('RGBA'))
   else:p=view
   _,q=scale2(p,1);old=[p.shape[1],p.shape[0]];new=[round(v*1.3) for v in old];assert m['detail_sizes'][i]=={'old':old,'new':new};expected=Image.fromarray(q).resize(tuple(new),Image.Resampling.NEAREST)
   with Image.open(A/'review'/n/'detail_130_frames'/f'frame_{i:03d}.png') as saved:
    saved=saved.convert('RGBA');assert ImageChops.difference(saved,expected).getbbox(alpha_only=False) is None;preview=saved.resize((w,h),Image.Resampling.NEAREST)
   actual=after.crop(box);assert ImageChops.difference(actual,preview).getbbox(alpha_only=False) is None;assert int(np.any(np.array(actual)!=view,axis=2).sum())==m['changed_pixels_per_frame'][i];total+=1
  if before is not None:before.close();after.close()
 print(n,m['frame_count'],'frames verified',flush=True)
print('PASS',len(report['results']),'assets',total,'frames; visual quality and VFX consistency require review')
