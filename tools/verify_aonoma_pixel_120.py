#!/usr/bin/env python3
"""Check Aonoma provenance, frame timing, pixel palette and preview atlas layout."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';d=json.loads((A/'pixel_120_candidates/aonoma/candidate.json').read_text());q=A/'review/aonoma/forge_quantized_120';qa=json.loads((q/'quantize-qa.json').read_text()); source=ROOT/d['source']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
entry=next(e for e in json.loads((A/'extracted/catalog.json').read_text())['assets'] if e['id']=='aonoma');assert d['source']==entry['source'] and sha(source)==d['source_sha256']==entry['source_sha256'];assert qa['status']=='pass'
for row in qa['inputs']:
 assert sha((q/row['path']).resolve())==row['sha256'],row['path']
for row in qa['outputs']:
 assert sha(q/row['path'])==row['sha256'],row['path']
colors=set()
with Image.open(source) as gif:
 assert gif.n_frames==d['frame_count']==len(d['frames'])==14
 for i,f in enumerate(d['frames']):
  gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
  with Image.open(q/f'frame_{i:03d}.png') as im:
   im=im.convert('RGBA');assert im.size==(108,86);pixels=np.array(im);assert set(np.unique(pixels[:,:,3]))<={0,255};colors.update(map(tuple,pixels[pixels[:,:,3]>0][:,:3]));expected=im.resize((268,214),Image.Resampling.NEAREST)
  x,y,w,h=f['region']
  with Image.open(A/'pixel_120_candidates/aonoma'/f'atlas_{f["atlas"]:03d}.png') as atlas:
   actual=atlas.convert('RGBA').crop((x,y,x+w,y+h));assert ImageChops.difference(expected,actual).getbbox(alpha_only=False) is None
assert len(colors)<=64
print('PASS: 14 frames, source hashes, duration, fixed 108x86 grid, binary alpha,',len(colors),'visible colors, and atlas layout; visual quality unverified')
