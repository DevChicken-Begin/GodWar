#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; tick=1000/60
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
f=json.loads((A/'speed_60fps_candidates/firer/candidate.json').read_text()); e=cat['firer']; assert sha(ROOT/f['source'])==f['source_sha256']==e['source_sha256']; assert sha(A/'speed_oct28_candidates/firer/candidate.json')==f['base_metadata_sha256']; assert len(f['frames'])==len(e['frames'])
actual=ideal=0
for frame,original in zip(f['frames'],e['frames']):
 assert frame['region']==original['region'] and frame['atlas']==original['atlas'];assert frame['duration_ticks']>0 and abs(frame['duration_ms']-frame['duration_ticks']*tick)<1e-9
 actual+=frame['duration_ms'];ideal+=original['duration_ms']/3;assert abs(actual-ideal)<=tick/2+1e-6
assert abs(actual-ideal)<=tick/2
print('PASS firer:',len(f['frames']),'frames,',round(actual,3),'ms; target',round(ideal,3),'ms')
m=json.loads((A/'conden_60fps_candidates/conden/candidate.json').read_text()); e=cat['conden']; assert sha(ROOT/m['source'])==m['source_sha256']==e['source_sha256']; assert sha(A/'speed_60fps_candidates/conden/candidate.json')==m['base_metadata_sha256']
for path,digest in m['input_sha256'].items():assert sha(ROOT/path)==digest
assert len(m['frames'])==61; arrows=[x for x in m['frames'] if x.get('projectile_x') is not None]; pos=[x['projectile_x'] for x in arrows];assert pos==m['projectile_positions'] and len(pos)==17 and [b-a for a,b in zip(pos,pos[1:])]==list(range(25,41)); assert pos[-1]>=960 and m['frames'][49].get('projectile_x') is not None
with Image.open(A/'repaired_v5_candidates/conden/projectile_template.png') as im: arrow=im.convert('RGBA')
for frame in arrows:
 src=e['frames'][frame['source_index']];x,y,w,h=src['region']
 with Image.open(A/'batch_candidates/conden'/f'atlas_{src["atlas"]:03}.png') as image:pose=image.convert('RGBA').crop((x,y,x+w,y+h))
 canvas=Image.new('RGBA',(960,720));canvas.paste(pose,(0,0));canvas.alpha_composite(arrow,(frame['projectile_x'],390));expected=canvas.convert('RGBa').resize((1152,864),Image.Resampling.LANCZOS).convert('RGBA')
 with Image.open(A/frame['image_variant']/'conden'/f'frame_{frame["image_index"]:03d}.png') as image:assert ImageChops.difference(expected,image.convert('RGBA')).getbbox(alpha_only=False) is None
 assert frame['duration_ticks']==1 and abs(frame['duration_ms']-tick)<1e-9
for i,src in enumerate(e['frames']):
 group=[f for f in m['frames'] if f['source_index']==i];assert group and all(f['duration_ticks']>0 for f in group)
 assert abs(sum(f['duration_ms'] for f in m['frames'] if f['source_index']<=i)-sum(f['duration_ms'] for f in e['frames'][:i+1]))<=tick/2+1e-6
print('PASS conden: 17 continuous arrow positions, frame 50 includes projectile, final position outside canvas, 60Hz timings')
