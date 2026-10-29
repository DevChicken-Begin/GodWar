#!/usr/bin/env python3
"""Check preserved frames and reconstructed beam on the installed Moxie atlas."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';dest=A/'measured_atlas_pilots/moxie_repaired';m=json.loads((dest/'candidate.json').read_text());proof=m['beam_reconstruction_oct29'];src=ROOT/proof['input'];old=json.loads((src/'candidate.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/m['source'])==m['source_sha256']==old['source_sha256'];assert proof['input_atlas_sha256']=={p.name:sha(p) for p in sorted(src.glob('atlas_*.png'))};assert len(m['frames'])==len(old['frames'])==97;assert [x['duration_ms'] for x in m['frames']]==[x['duration_ms'] for x in old['frames']];assert m['anchor_px']==old['anchor_px'] and m['display_scale']==old['display_scale'];pages=[{},{}]
def frame(folder,f,cache):
 p=f['atlas'];x,y,w,h=f['region']
 if p not in cache:cache[p]=Image.open(folder/f'atlas_{p:03d}.png').convert('RGBA')
 return np.array(cache[p].crop((x,y,x+w,y+h)))
template=Image.fromarray(frame(src,old['frames'][38],pages[0])).crop((204,110,237,140))
for i,(a,b) in enumerate(zip(old['frames'],m['frames'])):
 original=frame(src,a,pages[0]);actual=frame(dest,b,pages[1]);assert actual.shape==(250,660,4);expected=np.zeros_like(actual);expected[:,:340]=original
 if i in proof['frame_indices_zero_based']:
  column=expected[:,299,:].copy();ys=np.where(column[:,3]>0)[0];tip=proof['tip_x'][i-39];height=round(30*len(ys)/17);hx=tip-33;hy=round((float(ys.min())+float(ys.max()))/2-height/2);expected[:,300:hx+8]=column[:,None,:];im=Image.fromarray(expected);im.alpha_composite(template.resize((33,height),Image.Resampling.NEAREST),(hx,hy));expected=np.array(im);assert np.any(actual[:,tip-5:tip,3])
 assert np.array_equal(expected,actual),i
print('PASS: 97 frames, source and timing preserved, 8 reconstructed beam tips; unchanged pixels verified')
