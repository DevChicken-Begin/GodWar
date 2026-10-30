#!/usr/bin/env python3
"""Restore cons effect under static logo footprint using source pixels that differ from logo reference."""
import json,shutil,subprocess,sys
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
A=Path('Asset/Character');names='Kungteng cons isis omega oset pandung'.split();samples=[]
for n in names:
 with Image.open(A/'vfx'/f'{n}.gif') as g:samples.append(np.array(g.convert('RGB')))
ref=np.median(np.stack(samples),axis=0).astype(np.int16);yy,xx=np.indices((520,520));roi=(yy>=40)&(yy<145)&(xx>=95)&(xx<430);logo=roi&(ref.max(axis=2)>90);logo=np.array(Image.fromarray((logo*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>0;logo &= roi
bg=np.asarray(Image.open(A/'review/six-import-20261030/scene-reference-v2.png').convert('RGB')).astype(np.int16)
sample=np.asarray(Image.open('pixel_simple.png').convert('RGB'));colors=np.unique(sample.reshape(-1,3),axis=0);colors=colors[(colors[:,0]<20)&(colors[:,1]>40)&(colors[:,1]<85)&(colors[:,2]>90)&(colors[:,2]<140)].astype(np.int16)
p=A/'measured_atlas_pilots/cons';backup=A/'archive/twenty_cons_before_logo_repair';backup.parent.mkdir(exist_ok=True);assert not backup.exists();shutil.copytree(p,backup);m=json.load(open(p/'candidate.json'));g=Image.open(A/'vfx/cons.gif');pages={};restored=[]
forge=A/'forge_pilots/six_remaining_20261030/cons'; new=forge/'repaired_frames';new.mkdir(exist_ok=False)
for i,f in enumerate(m['frames']):
 g.seek(i);raw=np.asarray(g.convert('RGBA'));rgb=raw[:,:,:3].astype(np.int16);diff=np.max(np.abs(rgb-bg),axis=2);nonlogo=np.max(np.abs(rgb-ref),axis=2)>40;blue=np.zeros((520,520),dtype=bool)
 for c in colors:blue|=np.max(np.abs(rgb-c),axis=2)<=5
 idx=f['atlas'];x,y,w,h=f['region']
 if idx not in pages:pages[idx]=np.array(Image.open(backup/f'atlas_{idx:03d}.png').convert('RGBA'))
 a=pages[idx][y:y+h,x:x+w];mask=logo & nonlogo & (diff>16)&~blue & (a[:,:,3]==0);a[mask]=raw[mask];restored.append(int(mask.sum()));Image.fromarray(a.copy()).save(new/f'frame_{i:03d}.png',compress_level=3)
for idx,a in pages.items():Image.fromarray(a).save(p/f'atlas_{idx:03d}.png',compress_level=3)
m['logo_overlap_repair']={'base':str(backup),'method':'Restore source pixels inside fixed logo footprint only when RGB differs from independent logo reference by >40, differs from shared scene by >16 and does not match blue sample within 5.','restored_per_frame':restored,'limitations':'Logo reference may share effect colors or GIF palettes vary; other effect pixels and residual logo may still need review.'};(p/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
manifest=json.load(open(forge/'manifest.json'));manifest['frames']=[f'repaired_frames/frame_{i:03d}.png' for i in range(len(m['frames']))];(forge/'repaired-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');r=subprocess.run([sys.executable,'/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py','--manifest',str(forge/'repaired-manifest.json'),'--output-dir',str(forge/'repaired-clips'),'--no-reviews'],capture_output=True,text=True);(forge/'repaired-build.log').write_text(r.stdout+r.stderr);print('restored',sum(restored),'frame48',restored[48],'forge',r.returncode,flush=True)
if r.returncode:raise RuntimeError(r.stderr)
