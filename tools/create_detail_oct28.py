#!/usr/bin/env python3
"""Non-destructive resolution candidates from the viewer's current defaults."""
import hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
NAMES = 'artemis aument bearen biden botem choptian conden corepion dracian dragonight dragonmout ethan guard jaik Kahn knight mainthen mortafi nox overight powerdame scorpit skyles tigerknight wuchen'.split()
PRIORITIES = 'detail_130_candidates fine_candidates pixel_220_candidates sharp_candidates scorpit_repair18_candidates logo_candidates scene_protected_candidates pixel_180_candidates scorpit_repair_candidates pixel_120_candidates native_candidates oct28_fix_candidates pixel_candidates spot_candidates remaining_scene_candidates scene_detail_v3_candidates foot_candidates detailed_candidates special_candidates cleanup_candidates shared_scene_candidates temporal_candidates batch_candidates refined_candidates candidates'.split()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 names = sys.argv[1:] or NAMES
 assert all(n in NAMES for n in names) and len(set(names)) == len(names)
 catalog = {e['id']: e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for name in names:
  out=A/'detail_oct28_candidates'/name
  if out.exists(): raise FileExistsError(out)
 for name in names:
  e=catalog[name]; source=ROOT/e['source']; assert sha(source)==e['source_sha256']
  base = 'repaired_v5_candidates' if name=='conden' else 'tiger_clean_all_130' if name=='tigerknight' else next((p for p in PRIORITIES if (A/p/name/'candidate.json').exists()),'extracted')
  metadata=e if base in ('extracted', 'tiger_clean_all_130') else json.loads((A/base/name/'candidate.json').read_text())
  assert metadata.get('source_sha256',e['source_sha256'])==e['source_sha256']
  frames=metadata['frames'] if name=='conden' else e['frames']
  factor=1.4 if name=='dragonmout' else 1.2
  out=A/'detail_oct28_candidates'/name; out.mkdir(parents=True)
  hashes={}; newframes=[]; currentpage=-1; page=None
  # Increase the previous flight baseline of 55 px/70ms progressively to 83 px/70ms.
  steps=[55,59,63,67,71,75,79,83]; positions=[455]
  for step in steps: positions.append(positions[-1]+step)
  flight=0
  if name=='conden':
   arrow=Image.open(A/base/name/'projectile_template.png').convert('RGBA'); hashes[str((A/base/name/'projectile_template.png').relative_to(ROOT))]=sha(A/base/name/'projectile_template.png')
   original=catalog[name]['frames']; frames=[]
   for i,f in enumerate(original):
    for _ in range(3 if i==47 else 2 if i in (44,45,46) else 1): frames.append({**f,'source_index':i,'synthetic':i in (44,45,46,47),'projectile_x':positions.pop(0) if i in (44,45,46,47) else None})
   assert not positions
   source_base=A/'batch_candidates'/name
  else: source_base=A/base/name
  for i,f in enumerate(frames):
   if name=='conden':
    srcf=original[f['source_index']]; p=source_base/f'atlas_{srcf["atlas"]:03d}.png'; box=srcf['region']; w,h=960,720
   elif base in ('detail_130_candidates','tiger_clean_all_130'):
    folder='clean_all_v2_130_frames' if base=='tiger_clean_all_130' else 'detail_130_frames'
    p=A/'review'/name/folder/f'frame_{i:03d}.png'; box=None; w,h=e['size']
   else:
    p=source_base/f'atlas_{f["atlas"]:03d}.png'; box=f['region']; w,h=e['size']
   key=str(p.relative_to(ROOT))
   if key not in hashes: hashes[key]=sha(p)
   with Image.open(p) as im:
    if box:
     x,y,bw,bh=box; im=im.crop((x,y,x+bw,y+bh))
    rgba=im.convert('RGBA')
   if name=='conden':
    canvas=Image.new('RGBA',(w,h)); canvas.paste(rgba,(0,0))
    if f['projectile_x'] is not None: canvas.alpha_composite(arrow,(f['projectile_x'],390))
    rgba=canvas
   original_size=rgba.size; target=tuple(round(v*factor) for v in original_size)
   # Premultiplied resize avoids colour fringes; no synthetic new source detail claimed.
   high=rgba.convert('RGBa').resize(target, Image.Resampling.LANCZOS).convert('RGBA')
   high.save(out/f'frame_{i:03d}.png',compress_level=3)
   nf=dict(f); nf['region']=[0,0,w,h]; nf['detail_size']=list(target); newframes.append(nf)
  m={'id':name,'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':base,'base_input_sha256':hashes,'art_source':'existing','scale_factor':factor,'frame_count':len(newframes),'frames':newframes,'display_size':[960,720] if name=='conden' else e['size'],'status':'candidate_unreviewed','method':'Premultiplied-alpha Lanczos resize of current viewer frame; preserve display dimensions and timing. No new source detail is created.', 'limitations':'Upsampling alone does not restore missing detail; edges and VFX need visual review.'}
  if name=='conden': m.update({'arrow_base':'repaired_v5_candidates/conden/projectile_template.png','reference_step_per_70ms':55,'steps_per_70ms':steps,'projectile_positions':[f['projectile_x'] for f in newframes if f['projectile_x'] is not None], 'arrow_note':'Synthetic reconstructed arrow; accelerate from 100% to approximately 151% of prior 55 px/70 ms reference; final left edge beyond canvas.'})
  (out/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n'); print(name,base,len(newframes),factor,flush=True)
if __name__=='__main__': main()
