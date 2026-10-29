#!/usr/bin/env python3
"""Verify source timing, decoded and keyed atlases and Sprite Forge frame copies."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from import_five_oct29_specs import SPECS
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']};targets={e['id']:e for e in json.loads((A/'characters/height-targets.json').read_text())['assets']}
for n,(height,bounds) in SPECS.items():
 e=cat[n];m=json.loads((A/'measured_atlas_pilots'/n/'candidate.json').read_text());t=targets[n];src=ROOT/e['source'];forge=A/'forge_pilots/five_oct29'/n;assert sha(ROOT/(n+'.gif'))==sha(src)==m['source_sha256']==e['source_sha256']==t['source_sha256'];assert height==t['target_height_px']==m['target_height_px'] and bounds==m['reference_body_bounds'];assert math.isclose(m['display_scale']*m['reference_height_px'],height);assert len(e['frames'])==len(m['frames'])==120
 cache=[{},{}]
 with Image.open(src) as gif:
  for i,(rf,f) in enumerate(zip(e['frames'],m['frames'])):
   gif.seek(i);raw=np.array(gif.convert('RGBA'));assert gif.info['duration']==rf['duration_ms']==f['duration_ms'];mask=(raw[:,:,3]>0)&(np.max(np.abs(raw[:,:,:3].astype(np.int16)-np.array([4,50,71])),axis=2)<=5);assert int(mask.sum())==m['removed_per_frame'][i];clean=raw.copy();clean[mask]=0
   for idx,(folder,fr,expected) in enumerate([(A/'extracted'/n,rf,raw),(A/'measured_atlas_pilots'/n,f,clean)]):
    p=fr['atlas'];x,y,w,h=fr['region']
    if p not in cache[idx]:cache[idx][p]=np.array(Image.open(folder/f'atlas_{p:03d}.png').convert('RGBA'))
    assert np.array_equal(cache[idx][p][y:y+h,x:x+w],expected),(n,i,idx)
   assert np.array_equal(np.array(Image.open(forge/'input_frames'/f'frame_{i:03d}.png').convert('RGBA')),clean),(n,i,'forge')
 print('PASS',n,120,'frames',height,'px',flush=True)
