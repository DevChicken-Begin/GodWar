#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
for name in ('firer','conden'):
 m=json.loads((A/'speed_oct28_candidates'/name/'candidate.json').read_text()); e=cat[name];base=A/m['base_candidate']/name
 assert sha(ROOT/m['source'])==m['source_sha256']==e['source_sha256']
 assert sha(base/'candidate.json')==m['base_metadata_sha256']
 for f,h in m.get('base_atlas_sha256',{}).items(): assert sha(base/f)==h
 for f,h in m.get('base_frames_sha256',{}).items(): assert sha(base/f)==h
 for f,h in m.get('reconstructed_pose_atlas_sha256',{}).items(): assert sha(A/'batch_candidates'/name/f)==h
 assert len(m['frames'])==m['frame_count']
 if name=='firer':
  assert m['image_variant']=='fine_candidates'
  for f,original in zip(m['frames'],e['frames']): assert f['region']==original['region'] and f['atlas']==original['atlas'] and f['duration_ms']*5==original['duration_ms']
 else:
  old=json.loads((base/'candidate.json').read_text()); oldarrows=[f for f in old['frames'] if f.get('projectile_x') is not None]; newarrows=[f for f in m['frames'] if f.get('speed_insert')]
  assert len(newarrows)==len(oldarrows)==9
  assert all(a['projectile_x']==b['projectile_x'] and a['duration_ms']*100==b['duration_ms'] for a,b in zip(newarrows,oldarrows))
  for i,src in enumerate(e['frames']): assert abs(sum(f['duration_ms'] for f in m['frames'] if f['source_index']==i)-src['duration_ms'])<1e-6
  for f in m['frames']:
   path=A/f['image_variant']/name/f'frame_{f["image_index"]:03}.png'
   with Image.open(path) as im: assert im.size==(1152,864)
 print('PASS',name,len(m['frames']),'frames',sum(f['duration_ms'] for f in m['frames']),'ms')
