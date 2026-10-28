#!/usr/bin/env python3
"""Create continuous 60 Hz arrow frames, preserving source poses and canvas."""
import json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; tick=1000/60
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
e=next(x for x in json.loads((A/'extracted/catalog.json').read_text())['assets'] if x['id']=='conden')
base=A/'speed_60fps_candidates/conden'; m=json.loads((base/'candidate.json').read_text()); assert sha(ROOT/e['source'])==e['source_sha256']==m['source_sha256']
out=A/'tune_60fps_candidates/conden'
if out.exists(): raise FileExistsError(out)
out.mkdir(parents=True); frames=[f for f in m['frames'] if f['source_index']<44]; pos=455; positions=[]; paths={}
arrow_path=A/'repaired_v5_candidates/conden/projectile_template.png';paths[str(arrow_path.relative_to(ROOT))]=sha(arrow_path)
with Image.open(arrow_path) as im: arrow=im.convert('RGBA')
for source_index in range(44,48):
 source=e['frames'][source_index]; p=A/'batch_candidates/conden'/f'atlas_{source["atlas"]:03d}.png';paths[str(p.relative_to(ROOT))]=sha(p)
 x,y,w,h=source['region']
 with Image.open(p) as im: pose=im.convert('RGBA').crop((x,y,x+w,y+h))
 ticks=sum(f['duration_ticks'] for f in m['frames'] if f['source_index']==source_index)
 for j in range(ticks):
  i=len(positions); positions.append(pos)
  canvas=Image.new('RGBA',(960,720));canvas.paste(pose,(0,0));canvas.alpha_composite(arrow,(pos,390));high=canvas.convert('RGBa').resize((1152,864),Image.Resampling.LANCZOS).convert('RGBA');high.save(out/f'frame_{i:03d}.png',compress_level=3)
  frames.append({'atlas':source['atlas'],'region':[0,0,960,720],'duration_ms':tick,'duration_ticks':1,'source_index':source_index,'image_variant':'tune_60fps_candidates','image_index':i,'projectile_x':pos,'synthetic':True})
  if i<16: pos+=33
assert len(positions)==17 and positions[-1]>=960
result={'id':'conden','source':e['source'],'source_sha256':e['source_sha256'],'art_source':'existing','base_candidate':'speed_60fps_candidates','base_metadata_sha256':sha(base/'candidate.json'),'input_sha256':paths,'frame_files':True,'frame_count':len(frames),'frames':frames,'display_size':[960,720],'fps':60,'projectile_positions':positions,'status':'candidate_unreviewed','method':'Render a fresh arrow position in each 60Hz tick from source index 44 to 47; constant step of 33 px/tick. Preserve cumulative source pose ticks.','limitations':'Arrow and occluded shaft are reconstructed; source background defects remain. Real-time display and device performance require review.'}
(out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('frames',len(frames),'arrow positions',positions)
