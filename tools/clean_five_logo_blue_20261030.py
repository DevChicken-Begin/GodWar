#!/usr/bin/env python3
"""Conservative, reversible cleanup of sampled blue and persistent logo pixels."""
import json, shutil, hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
A=Path('Asset/Character');names=['Aquamen','Diorai','Evenl','Moregorn','Moresword'];review=A/'review/six-import-20261030'; sample=np.array(Image.open('pixel_simple.png').convert('RGB'));colors=np.unique(sample.reshape(-1,3),axis=0);colors=colors[(colors[:,0]<20)&(colors[:,1]>40)&(colors[:,1]<85)&(colors[:,2]>90)&(colors[:,2]<140)].astype(np.int16)
for name in names:
 current=A/'measured_atlas_pilots'/name;backup=A/'archive/six_20261030_before_blue_cleanup'/name
 if backup.exists(): raise RuntimeError(f'Backup exists: {backup}')
 backup.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(current,backup)
 meta=json.loads((current/'candidate.json').read_text());gif=Image.open(A/'vfx'/f'{name}.gif');gif.seek(0);first=np.asarray(gif.convert('RGB')).astype(np.int16);yy,xx=np.indices(first.shape[:2]);roi=(yy>=40)&(yy<145)&(xx>=95)&(xx<430);logo=roi & (first.max(axis=2)>135) & ((first.max(axis=2)-first.min(axis=2)>20)|(first.min(axis=2)>115));logo=np.asarray(Image.fromarray((logo*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0
 pages={};sheets={shade:Image.new('RGB',(1000,((gif.n_frames+7)//8)*140),color) for shade,color in [('light','#eee'),('dark','#181818')]};draw={k:ImageDraw.Draw(v) for k,v in sheets.items()};counts=[]
 for i,f in enumerate(meta['frames']):
  gif.seek(i);raw=np.asarray(gif.convert('RGB')).astype(np.int16);page=f['atlas'];x,y,w,h=f['region']
  if page not in pages: pages[page]=np.array(Image.open(backup/f'atlas_{page:03d}.png').convert('RGBA'))
  a=pages[page][y:y+h,x:x+w]; rgb=a[:,:,:3].astype(np.int16);blue=np.zeros((h,w),dtype=bool)
  for c in colors: blue|=np.max(np.abs(rgb-c),axis=2)<=5
  text=logo & (np.max(np.abs(raw-first),axis=2)<=35);mask=(blue|text)&(a[:,:,3]>0); counts.append({'blue':int((blue&(a[:,:,3]>0)).sum()),'logo':int((text&(a[:,:,3]>0)).sum())});a[mask,3]=0
  img=Image.fromarray(a.copy()).resize((115,115),Image.Resampling.NEAREST)
  for shade,sheet in sheets.items():
   px=i%8*125;py=i//8*140;sheet.paste(img,(px+5,py+20),img);draw[shade].text((px+2,py+2),str(i),fill='black' if shade=='light' else 'white')
 for page,img in pages.items():Image.fromarray(img).save(current/f'atlas_{page:03d}.png',compress_level=3)
 for shade,sheet in sheets.items():sheet.save(review/name/f'cleanup-{shade}.jpg',quality=95)
 meta['cleanup_20261030']={'sample':'pixel_simple.png','sample_sha256':hashlib.sha256(Path('pixel_simple.png').read_bytes()).hexdigest(),'base':str(backup),'method':'Remove RGBA pixels within max RGB distance 5 of blue sample colors; remove logo-mask pixels matching source frame 0 within max RGB distance 35, logo mask dilated 2px.','counts_per_frame':counts,'limitations':'Foreground and VFX colors may match sample; logo-overlapping FX may be erased; residue may remain. Unapproved.'};(current/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(name,'blue',sum(x['blue'] for x in counts),'logo',sum(x['logo'] for x in counts),flush=True)
