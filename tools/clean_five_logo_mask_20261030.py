#!/usr/bin/env python3
"""Remove static shared logo footprint; can remove overlapping VFX."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,shutil
A=Path('Asset/Character');names=['Aquamen','Diorai','Evenl','Moregorn','Moresword']; samples=[]
for n in names:
 g=Image.open(A/'vfx'/f'{n}.gif');samples.append(np.array(g.convert('RGB')))
base=np.median(np.stack(samples),axis=0).astype(np.uint8);yy,xx=np.indices((520,520));roi=(yy>=40)&(yy<145)&(xx>=95)&(xx<430);logo=roi & (np.max(base,axis=2)>90);mask=np.array(Image.fromarray((logo*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>0;mask &= roi
for n in names:
 cur=A/'measured_atlas_pilots'/n;old=A/'archive/six_20261030_before_logo_mask'/n
 if old.exists():raise FileExistsError(old)
 old.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(cur,old);meta=json.loads((cur/'candidate.json').read_text());pages={};counts=[]
 for f in meta['frames']:
  idx=f['atlas'];x,y,w,h=f['region']
  if idx not in pages:pages[idx]=np.array(Image.open(old/f'atlas_{idx:03d}.png').convert('RGBA'))
  region=pages[idx][y:y+h,x:x+w];inside=mask & (region[:,:,3]>0);counts.append(int(inside.sum()));region[inside,3]=0
 for idx,a in pages.items():Image.fromarray(a).save(cur/f'atlas_{idx:03d}.png',compress_level=3)
 meta['cleanup_logo_v3']={'source':'median frame 0 of Aquamen, Diorai, Evenl, Moregorn, Moresword','base':str(old),'method':'Within logo ROI, mask pixels where shared reference RGB max >90, dilated 4px; remove all pixels under that footprint.','removed_per_frame':counts,'limitations':'The fixed logo footprint can erase character effects crossing it; inspect all frames, especially Aquamen late frames.'};(cur/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(n,sum(counts),flush=True)
