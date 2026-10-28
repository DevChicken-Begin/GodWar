#!/usr/bin/env python3
"""Verify new native-resolution candidates against source GIFs and the rule."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES=('biden','airpot','black','knigblack','pigpor','jaik');total=0
catalog={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
for n in NAMES:
 p=A/'native_candidates'/n;m=json.loads((p/'candidate.json').read_text());src=ROOT/m['source'];assert m['source']==catalog[n]['source'] and hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']==catalog[n]['source_sha256'];bg=np.array(m['background_rgb'],np.int16)
 with Image.open(src) as gif:
  assert gif.n_frames==m['frame_count']==len(m['frames'])==len(m['removed_per_frame']);page=-1;orig=out=None
  for i,f in enumerate(m['frames']):
   if f['atlas']!=page:
    if out is not None:out.close();orig.close()
    page=f['atlas'];filename=f'atlas_{page:03d}.png';out=Image.open(p/filename).convert('RGBA');orig=Image.open(A/'extracted'/n/filename).convert('RGBA');assert orig.size==out.size
   gif.seek(i);before=np.array(gif.convert('RGBA'));assert gif.info.get('duration',0)==f['duration_ms'];x,y,w,h=f['region'];box=x,y,x+w,y+h;actual=np.array(out.crop(box));saved=np.array(orig.crop(box));assert np.array_equal(saved,before)
   mask=(before[:,:,3]>0)&(np.max(np.abs(before[:,:,:3].astype(np.int16)-bg),axis=2)<=5);assert int(mask.sum())==m['removed_per_frame'][i];assert np.all(actual[mask]==0) and np.array_equal(actual[~mask],before[~mask]);total+=1
  if out is not None:out.close();orig.close()
 print(n,m['frame_count'],'frames OK',flush=True)
print('PASS',total,'native-size frames; pixel checks do not prove visual separation')
