#!/usr/bin/env python3
"""Remove recurring sampled dark-blue scene pixels beside Maxoi's face."""
from pathlib import Path
from PIL import Image
import numpy as np,json,shutil,subprocess,sys
A=Path('Asset/Character');name='maxoi';cur=A/'measured_atlas_pilots'/name;old=A/'archive/maxoi_before_face_cleanup';old.parent.mkdir(parents=True,exist_ok=True)
if old.exists():raise FileExistsError(old)
shutil.copytree(cur,old);m=json.load(open(cur/'candidate.json'));forge=A/'forge_pilots/fourteen_20261030'/name;frames=forge/'face_clean_frames';frames.mkdir(exist_ok=False);pages={};counts=[];yy,xx=np.indices((520,520));roi=(xx>=218)&(xx<252)&(yy>=260)&(yy<350);colors=np.array([[11,64,118],[3,62,116]],dtype=np.int16)
for i,f in enumerate(m['frames']):
 idx=f['atlas'];x,y,w,h=f['region']
 if idx not in pages:pages[idx]=np.array(Image.open(old/f'atlas_{idx:03d}.png').convert('RGBA'))
 a=pages[idx][y:y+h,x:x+w];rgb=a[:,:,:3].astype(np.int16);match=np.zeros((520,520),bool)
 for c in colors:match|=np.max(np.abs(rgb-c),axis=2)<=5
 selected=(i>=32)&(i<=50)&roi&match&(a[:,:,3]>0);counts.append(int(selected.sum()));a[selected,3]=0;Image.fromarray(a.copy()).save(frames/f'frame_{i:03d}.png',compress_level=3)
for idx,a in pages.items():Image.fromarray(a).save(cur/f'atlas_{idx:03d}.png',compress_level=3)
m['face_residue_cleanup']={'base':str(old),'viewer_frames':'33–51','roi_xyxy':[218,260,252,350],'sampled_scene_rgb':colors.tolist(),'rgb_max_distance':5,'removed_per_frame':counts,'limitations':'Dark-blue character or VFX may share the sampled colors; review face and attack frames on light/dark backgrounds.'};m['forge_current_clip']='face-clean-clips/animation-clips.json';(cur/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');manifest=json.load(open(forge/'manifest.json'));manifest['frames']=[f'face_clean_frames/frame_{i:03d}.png' for i in range(len(counts))];(forge/'face-clean-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');r=subprocess.run([sys.executable,'/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py','--manifest',str(forge/'face-clean-manifest.json'),'--output-dir',str(forge/'face-clean-clips'),'--no-reviews'],capture_output=True,text=True);(forge/'face-clean-build.log').write_text(r.stdout+r.stderr);print('removed',sum(counts),'frames',[(i+1,v) for i,v in enumerate(counts) if v],flush=True)
if r.returncode:raise RuntimeError(r.stderr)
