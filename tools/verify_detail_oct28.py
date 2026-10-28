#!/usr/bin/env python3
"""Validate source provenance, frame geometry, timings, and projectile trajectory."""
import hashlib,json
from pathlib import Path
from PIL import Image
from create_detail_oct28 import A, ROOT, NAMES

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
total=0
for name in NAMES:
 p=A/'detail_oct28_candidates'/name; m=json.loads((p/'candidate.json').read_text()); e=cat[name]
 assert m['source_sha256']==sha(ROOT/m['source'])==e['source_sha256']
 for path, digest in m['base_input_sha256'].items(): assert sha(ROOT/path)==digest
 assert len(m['frames'])==m['frame_count']; factor=1.4 if name=='dragonmout' else 1.2; assert m['scale_factor']==factor
 if name!='conden': assert len(m['frames'])==e['frame_count']
 for i,f in enumerate(m['frames']):
  src=e['frames'][f.get('source_index',i)]; assert f['duration_ms']==src['duration_ms']; assert f['region'][2:]==m['display_size']
  if m['base_candidate'] in ('detail_130_candidates','tiger_clean_all_130'):
   folder='clean_all_v2_130_frames' if m['base_candidate']=='tiger_clean_all_130' else 'detail_130_frames'
   with Image.open(A/'review'/name/folder/f'frame_{i:03d}.png') as image: expected=[round(x*factor) for x in image.size]
  else: expected=[round(x*factor) for x in m['display_size']]
  with Image.open(p/f'frame_{i:03d}.png') as image: assert list(image.size)==f['detail_size']==expected
  total+=1
 if name=='conden':
  pos=m['projectile_positions']; steps=[b-a for a,b in zip(pos,pos[1:])]; assert steps==m['steps_per_70ms']==[55,59,63,67,71,75,79,83]; assert pos[-1]>=m['display_size'][0]; assert len(m['frames'])==53
 print(name, len(m['frames']), 'OK',flush=True)
print('PASS',len(NAMES),'assets',total,'frames; visual review pending')
