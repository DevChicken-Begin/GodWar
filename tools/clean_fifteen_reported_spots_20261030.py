#!/usr/bin/env python3
"""Remove reported fixed scene specks and per-source static logo remnants."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, json, shutil, hashlib, subprocess, sys
A=Path('Asset/Character'); foot='Kungteng charmia combra cornra isis omega ompan pandung samset thorn uopon maxoi'.split(); logos='cons ompan osiris oset samset thorn'.split(); names=list(dict.fromkeys(foot+logos)); bgpath=A/'review/twenty-import-20261030/static-reference.png';bg=np.asarray(Image.open(bgpath).convert('RGB')).astype(np.int16);yy,xx=np.indices((520,520));foot_roi=((xx>=307)&(xx<317)&(yy>=387)&(yy<393))|((xx>=323)&(xx<329)&(yy>=331)&(yy<337))|((xx>=327)&(xx<334)&(yy>=431)&(yy<437))|((xx>=240)&(xx<245)&(yy>=299)&(yy<303));logo_roi=(xx>=90)&(xx<435)&(yy>=35)&(yy<150);review=A/'review/twenty-import-20261030';report=[]
for name in names:
 cur=A/'measured_atlas_pilots'/name;old=A/'archive/twenty_before_reported_spots'/name
 if old.exists():raise FileExistsError(old)
 old.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(cur,old);m=json.load(open(cur/'candidate.json'));g=Image.open(A/'vfx'/f'{name}.gif');g.seek(0);logo_ref=np.asarray(g.convert('RGB')).astype(np.int16);pages={};counts=[];group='six_remaining_20261030' if name in ['Kungteng','cons','isis','omega','oset','pandung'] else 'fourteen_20261030';forge=A/'forge_pilots'/group/name;frames=forge/'reported_spots_frames';frames.mkdir(exist_ok=False);sheets={c:Image.new('RGB',(1000,((len(m['frames'])+7)//8)*140),v) for c,v in [('light','#eee'),('dark','#181818')]};draw={k:ImageDraw.Draw(v) for k,v in sheets.items()}
 for i,f in enumerate(m['frames']):
  g.seek(i);raw=np.asarray(g.convert('RGB')).astype(np.int16);idx=f['atlas'];x,y,w,h=f['region']
  if idx not in pages:pages[idx]=np.array(Image.open(old/f'atlas_{idx:03d}.png').convert('RGBA'))
  a=pages[idx][y:y+h,x:x+w];rgb=a[:,:,:3].astype(np.int16);visible=a[:,:,3]>0;flag=np.zeros((520,520),bool)
  if name in foot:flag |= foot_roi & (np.max(np.abs(rgb-bg),axis=2)<=25) & (rgb[:,:,0]<45)&(rgb[:,:,1]<115)&(rgb[:,:,2]<165)
  if name in logos:flag |= logo_roi & (np.max(np.abs(raw-logo_ref),axis=2)<=25)
  flag &= visible;counts.append(int(flag.sum()));a[flag,3]=0;im=Image.fromarray(a.copy());im.save(frames/f'frame_{i:03d}.png',compress_level=3);thumb=im.resize((115,115),Image.Resampling.NEAREST)
  for shade,sheet in sheets.items():
   xp=i%8*125;yp=i//8*140;sheet.paste(thumb,(xp+5,yp+20),thumb);draw[shade].text((xp+2,yp+2),str(i),fill='black' if shade=='light' else 'white')
 for idx,arr in pages.items():Image.fromarray(arr).save(cur/f'atlas_{idx:03d}.png',compress_level=3)
 for shade,sheet in sheets.items():sheet.save(review/name/f'reported-spots-{shade}.jpg',quality=95)
 m['reported_spot_cleanup']={'base':str(old),'method':'Fixed four reported scene-speck regions: compare to common scene RGB max <=25 and require dark-blue; logo region: compare current frame to own frame 0 RGB max <=25. Remove matching pixels only.','source_sha256':hashlib.sha256((A/'vfx'/f'{name}.gif').read_bytes()).hexdigest(),'scene_reference':str(bgpath),'scene_reference_sha256':hashlib.sha256(bgpath.read_bytes()).hexdigest(),'counts_per_frame':counts,'limitations':'Logo and scene colors can match VFX; artifacts outside fixed regions or tolerance may remain. Inspect every frame; candidate unapproved.'};m['forge_current_clip']='reported-spots-clips/animation-clips.json';(cur/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 manifest=json.load(open(forge/'manifest.json'));manifest['frames']=[f'reported_spots_frames/frame_{i:03d}.png' for i in range(len(counts))];(forge/'reported-spots-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');r=subprocess.run([sys.executable,'/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py','--manifest',str(forge/'reported-spots-manifest.json'),'--output-dir',str(forge/'reported-spots-clips'),'--no-reviews'],capture_output=True,text=True);(forge/'reported-spots-build.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(name+': '+r.stderr)
 report.append({'id':name,'pixels_removed':sum(counts),'frames_changed':sum(c>0 for c in counts)});print(name,sum(counts),flush=True)
(review/'reported-spots-summary.json').write_text(json.dumps({'results':report},ensure_ascii=False,indent=2)+'\n')
