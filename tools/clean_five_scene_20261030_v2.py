#!/usr/bin/env python3
"""Provisional residual cleanup against Moregorn's sparsely occupied source frames."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
A=Path('Asset/Character'); names=['Aquamen','Diorai','Evenl','Moregorn','Moresword'];src=A/'vfx/Moregorn.gif';g=Image.open(src);samples=[]
for i in [37,38,39,40]:g.seek(i);samples.append(np.asarray(g.convert('RGB')).copy())
bg=np.median(np.stack(samples),axis=0).astype(np.int16); review=A/'review/six-import-20261030';Image.fromarray(bg.astype(np.uint8)).save(review/'scene-reference-v2.png')
for name in names:
 current=A/'measured_atlas_pilots'/name;backup=A/'archive/six_20261030_before_scene_v2'/name
 if backup.exists():raise FileExistsError(backup)
 backup.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(current,backup); meta=json.loads((current/'candidate.json').read_text());gif=Image.open(A/'vfx'/f'{name}.gif');gif.seek(0);first=np.array(gif.convert('RGB')).astype(np.int16); yy,xx=np.indices((520,520));roi=(yy>=40)&(yy<145)&(xx>=95)&(xx<430)
 pages={};counts=[];sheets={k:Image.new('RGB',(1000,((gif.n_frames+7)//8)*140),v) for k,v in [('light','#eee'),('dark','#181818')]};draw={k:ImageDraw.Draw(v) for k,v in sheets.items()}
 for i,f in enumerate(meta['frames']):
  gif.seek(i);raw=np.asarray(gif.convert('RGB')).astype(np.int16);p=f['atlas'];x,y,w,h=f['region']
  if p not in pages:pages[p]=np.array(Image.open(backup/f'atlas_{p:03d}.png').convert('RGBA'))
  a=pages[p][y:y+h,x:x+w];visible=a[:,:,3]>0;scene=np.max(np.abs(raw-bg),axis=2)<=16;logo=roi&(np.max(np.abs(raw-first),axis=2)<=40);mask=(scene|logo)&visible;counts.append(int(mask.sum()));a[mask,3]=0
  img=Image.fromarray(a.copy()).resize((115,115),Image.Resampling.NEAREST)
  for shade,sheet in sheets.items():
   xp=i%8*125;yp=i//8*140;sheet.paste(img,(xp+5,yp+20),img);draw[shade].text((xp+2,yp+2),str(i),fill='black' if shade=='light' else 'white')
 for p,img in pages.items():Image.fromarray(img).save(current/f'atlas_{p:03d}.png',compress_level=3)
 for shade,sheet in sheets.items():sheet.save(review/name/f'scene-v2-{shade}.jpg',quality=95)
 meta['cleanup_scene_v2']={'reference_source':str(src),'reference_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'reference_frames_zero_based':[37,38,39,40],'base':str(backup),'method':'Median RGB of Moregorn frames 37-40; remove pixels within maximum channel difference 16; within logo ROI also remove pixels within 40 of frame 0.','removed_per_frame':counts,'limitations':'Scene colors and logo may overlap subject/VFX; sparse reference frames include effects and are not ground truth. Inspect both frame 39 and 40 and all frames; not approved.'};(current/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(name,sum(counts),flush=True)
