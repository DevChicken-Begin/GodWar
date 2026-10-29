#!/usr/bin/env python3
"""Remove sample-like blue components touching transparency in two measured atlases."""
import hashlib,json,shutil
from collections import Counter
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'; sample=ROOT/'image copy 4.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
colors=[c for c in Counter(Image.open(sample).convert('RGB').getdata()) if c not in {(200,205,210),(174,181,188)}];assert len(colors)==8
archive=A/'archive/blue_fringe_oct29'
if archive.exists():raise FileExistsError(archive)
archive.mkdir(parents=True)
for name in ['buffao']:
 dest=A/'measured_atlas_pilots'/name;shutil.copytree(dest,archive/name)
 # Buffao's pre-exact-clean version lets the whole threshold apply in one pass.
 src=(A/'archive/cleanup_buffao_moxie_oct29/buffao') if name=='buffao' else archive/name
 meta=load(src/'candidate.json');assert sha(ROOT/meta['source'])==meta['source_sha256'];pages={};counts=[]
 for f in meta['frames']:
  page=f['atlas']
  if page not in pages:pages[page]=np.array(Image.open(src/f'atlas_{page:03d}.png').convert('RGBA'))
  x,y,w,h=f['region'];a=pages[page][y:y+h,x:x+w];rgb=a[:,:,:3].astype(np.int16);mask=np.zeros((h,w),bool)
  for c in colors:mask|=np.max(np.abs(rgb-np.array(c)),axis=2)<=6
  mask &= a[:,:,3]>0
  _,labels,_,_=cv2.connectedComponentsWithStats(mask.astype('uint8'),8);edge=cv2.dilate((a[:,:,3]==0).astype('uint8'),np.ones((3,3),np.uint8))>0;touching=np.unique(labels[mask&edge]);mask &= np.isin(labels,touching)
  counts.append(int(mask.sum()));a[mask]=0
 for page,a in pages.items():Image.fromarray(a).save(dest/f'atlas_{page:03d}.png',compress_level=3)
 meta['cleanup_oct29']={'input':str(src.relative_to(ROOT)),'input_atlas_sha256':{p.name:sha(p) for p in sorted(src.glob('atlas_*.png'))},'sample':str(sample.relative_to(ROOT)),'sample_sha256':sha(sample),'sample_rgb':colors,'tolerance_per_channel':6,'method':'Remove sample-like RGB components touching transparency, preserving other pixels.','removed_per_frame':counts,'status':'visual_review_pending','limitations':'Background and blue outlines or VFX can share colors; removal may damage details, and other colors can remain. Check all frames.'};save(dest/'candidate.json',meta);print(name,len(counts),sum(counts),min(counts),max(counts),flush=True)
