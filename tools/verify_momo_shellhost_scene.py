#!/usr/bin/env python3
"""Check provenance and ensure new candidates only remove pixels and preserve timing."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];A=R/'Asset/Character';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
for name in ('momo','shellhost'):
 out=A/'scene_mask_candidates'/name;m=json.loads((out/'candidate.json').read_text());e=cat[name];assert sha(R/m['source'])==m['source_sha256']==e['source_sha256'];base=A/m['base_candidate']/name
 for filename,digest in m['base_atlas_sha256'].items():assert sha(base/filename)==digest
 for ref in m['model_sources']:assert sha(R/ref['source'])==ref['sha256']
 for ref in m['evidence']:assert sha(R/ref['path'])==ref['sha256']
 assert m['frames']==e['frames'] and len(m['removed_per_frame'])==e['frame_count'];page=-1;count=0
 with Image.open(R/m['source']) as gif:
  assert gif.n_frames==e['frame_count']
  for i,f in enumerate(e['frames']):
   gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
   if page!=f['atlas']:
    page=f['atlas'];before=Image.open(base/f'atlas_{page:03d}.png').convert('RGBA');after=Image.open(out/f'atlas_{page:03d}.png').convert('RGBA')
   x,y,w,h=f['region'];box=(x,y,x+w,y+h);a=np.asarray(before.crop(box));b=np.asarray(after.crop(box));keep=b[:,:,3]>0;removed=(a[:,:,3]>0)&~keep;assert np.array_equal(a[keep],b[keep]) and np.all(b[~keep]==0);assert int(removed.sum())==m['removed_per_frame'][i];count+=int(removed.sum())
   expected=Image.fromarray(b).convert('RGBa').resize((round(w*1.2),round(h*1.2)),Image.Resampling.LANCZOS).convert('RGBA')
   with Image.open(out/f'frame_{i:03d}.png') as image:assert ImageChops.difference(expected,image.convert('RGBA')).getbbox(alpha_only=False) is None
 print('PASS',name,e['frame_count'],'frames',count,'removed pixels; visual review pending',flush=True)
