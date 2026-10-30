#!/usr/bin/env python3
"""Restore non-logo source colors under the fixed footprint for flagged animations."""
from pathlib import Path
from PIL import Image,ImageFilter
import json,numpy as np,shutil,subprocess,sys
A=Path('Asset/Character');group='charmia combra cornra hecpoirt ison isorat kikontai maxoi ompan onaon osiris samset thorn uopon'.split();flagged='combra hecpoirt ompan onaon osiris samset thorn'.split()
refs=[]
for n in group:
 with Image.open(A/'vfx'/f'{n}.gif') as g:refs.append(np.array(g.convert('RGB')))
ref=np.median(np.stack(refs),axis=0).astype(np.int16);yy,xx=np.indices((520,520));roi=(yy>=40)&(yy<145)&(xx>=95)&(xx<430);mask0=roi&(ref.max(axis=2)>90);mask0=np.asarray(Image.fromarray((mask0*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>0;mask0 &= roi
bg=np.asarray(Image.open(A/'review/six-import-20261030/scene-reference-v2.png').convert('RGB')).astype(np.int16);sample=np.asarray(Image.open('pixel_simple.png').convert('RGB'));colors=np.unique(sample.reshape(-1,3),axis=0);colors=colors[(colors[:,0]<20)&(colors[:,1]>40)&(colors[:,1]<85)&(colors[:,2]>90)&(colors[:,2]<140)].astype(np.int16)
for n in flagged:
 p=A/'measured_atlas_pilots'/n;backup=A/'archive/twenty_before_logo_overlap'/n;backup.parent.mkdir(parents=True,exist_ok=True)
 if backup.exists():raise FileExistsError(backup)
 shutil.copytree(p,backup);m=json.load(open(p/'candidate.json'));g=Image.open(A/'vfx'/f'{n}.gif');pages={};restored=[];forge=A/'forge_pilots/fourteen_20261030'/n;new=forge/'repaired_frames';new.mkdir(exist_ok=False)
 for i,f in enumerate(m['frames']):
  g.seek(i);raw=np.array(g.convert('RGBA'));rgb=raw[:,:,:3].astype(np.int16);scene=np.max(np.abs(rgb-bg),axis=2)>16;nonlogo=np.max(np.abs(rgb-ref),axis=2)>40;blue=np.zeros((520,520),dtype=bool)
  for c in colors:blue |= np.max(np.abs(rgb-c),axis=2)<=5
  idx=f['atlas'];x,y,w,h=f['region']
  if idx not in pages:pages[idx]=np.array(Image.open(backup/f'atlas_{idx:03d}.png').convert('RGBA'))
  a=pages[idx][y:y+h,x:x+w];selected=mask0&nonlogo&scene&~blue&(a[:,:,3]==0);a[selected]=raw[selected];restored.append(int(selected.sum()));Image.fromarray(a.copy()).save(new/f'frame_{i:03d}.png',compress_level=3)
 for idx,a in pages.items():Image.fromarray(a).save(p/f'atlas_{idx:03d}.png',compress_level=3)
 m['logo_overlap_repair']={'base':str(backup),'method':'Restore source pixels in logo footprint if RGB differs from logo reference by >40 and shared scene by >16 and does not match blue sample within 5.','restored_per_frame':restored,'limitations':'Similar colors or palette changes can leave holes or restore logo; visual review required.'};m['forge_current_clip']='repaired-clips/animation-clips.json';(p/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 manifest=json.load(open(forge/'manifest.json'));manifest['frames']=[f'repaired_frames/frame_{i:03d}.png' for i in range(len(m['frames']))];(forge/'repaired-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');r=subprocess.run([sys.executable,'/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py','--manifest',str(forge/'repaired-manifest.json'),'--output-dir',str(forge/'repaired-clips'),'--no-reviews'],capture_output=True,text=True);(forge/'repaired-build.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(r.stderr)
 print(n,'restored',sum(restored),flush=True)
