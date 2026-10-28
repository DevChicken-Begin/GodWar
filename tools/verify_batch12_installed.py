#!/usr/bin/env python3
"""Verify GIF/atlas timing, cleaned RGBA, interpolated frames and provenance."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; S=A/'archive_batch12_20261028'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S/'manifest.json').read_text());removed=set(json.loads((A/'characters/removed.json').read_text())['ids']);total=0;checked=0
for row in m['rows']:
 n=row['id'];
 if n in removed: print(n,'removed from active roster; skipped');continue
 checked+=1;e=row['entry'];meta=json.loads((A/'batch12_detail_candidates'/n/'candidate.json').read_text());assert sha(ROOT/e['source'])==e['source_sha256']==meta['source_sha256'];assert e['frame_count']==len(meta['frames'])
 with Image.open(ROOT/e['source']) as gif:
  assert gif.n_frames==e['frame_count']; page=-1
  for i,f in enumerate(e['frames']):
   gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms'];raw=gif.convert('RGBA')
   if page!=f['atlas']:
    page=f['atlas'];original=Image.open(A/'extracted'/n/f'atlas_{page:03d}.png').convert('RGBA');clean=Image.open(A/'batch12_native_candidates'/n/f'atlas_{page:03d}.png').convert('RGBA')
   x,y,w,h=f['region'];box=(x,y,x+w,y+h);ex=original.crop(box);fg=clean.crop(box);assert ImageChops.difference(ex,raw).getbbox(alpha_only=False) is None
   a=np.array(ex);b=np.array(fg);kept=b[:,:,3]>0;assert np.array_equal(a[kept],b[kept]);assert np.all(b[~kept]==0)
   expected=fg.convert('RGBa').resize((round(w*1.2),round(h*1.2)),Image.Resampling.LANCZOS).convert('RGBA')
   with Image.open(A/'batch12_detail_candidates'/n/f'frame_{i:03d}.png') as im:assert ImageChops.difference(expected,im.convert('RGBA')).getbbox(alpha_only=False) is None
   total+=1
 print(n,e['frame_count'],'verified',flush=True)
print('PASS',checked,'active GIFs',total,'frames; segmentation and animation still require visual review')
