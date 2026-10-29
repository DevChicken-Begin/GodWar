#!/usr/bin/env python3
"""Remove user-sampled Buffao blue and Moxie's pure-black floor shadow.

Back up measured atlases before writing. Sources and original candidate variants stay intact.
"""
import hashlib,json,shutil
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
sample=ROOT/'image copy 4.png'; counts=Counter(Image.open(sample).convert('RGB').getdata()); colors=[c for c in counts if c not in {(200,205,210),(174,181,188)}]; assert len(colors)==8
archive=A/'archive/cleanup_buffao_moxie_oct29'
if archive.exists():raise FileExistsError(archive)
archive.mkdir(parents=True)
for name in ['buffao','moxie','moxie_repaired']:
 folder=A/'measured_atlas_pilots'/name;old=archive/name;shutil.copytree(folder,old);meta=load(old/'candidate.json');assert sha(ROOT/meta['source'])==meta['source_sha256']; pages={}; counts=[]
 for f in meta['frames']:
  page=f['atlas']
  if page not in pages:pages[page]=np.array(Image.open(old/f'atlas_{page:03d}.png').convert('RGBA'))
  x,y,w,h=f['region'];a=pages[page][y:y+h,x:x+w];rgb=a[:,:,:3];visible=a[:,:,3]>0
  if name=='buffao':
   mask=np.zeros((h,w),bool)
   for color in colors:mask|=np.all(rgb==color,axis=2)
   mask &= visible
  else:
   yy=np.arange(h)[:,None];mask=visible & np.all(rgb==0,axis=2) & (yy>=162)
  counts.append(int(mask.sum()));a[mask]=0
 for page,a in pages.items():Image.fromarray(a).save(folder/f'atlas_{page:03d}.png',compress_level=3)
 meta['cleanup_oct29']={'input':str(old.relative_to(ROOT)),'input_atlas_sha256':{p.name:sha(p) for p in sorted(old.glob('atlas_*.png'))},'sample':str(sample.relative_to(ROOT)) if name=='buffao' else 'image copy 7.png','sample_sha256':sha(sample if name=='buffao' else ROOT/'image copy 7.png'),'colors':colors if name=='buffao' else [[0,0,0]],'method':'Clear exactly the eight non-checkerboard RGB colors in the supplied sample.' if name=='buffao' else 'Clear opaque exact black pixels in source canvas rows y >= 162; preserve other colors and projectile reconstruction.','removed_per_frame':counts,'status':'visual_review_pending','limitations':'Sample colors may also occur in outlines or effects; check animation on multiple backgrounds.' if name=='buffao' else 'Shadow pixels overlapping the feet cannot be separated perfectly; reference height and anchor remain as before.'};save(folder/'candidate.json',meta); print(name, len(counts),sum(counts),min(counts),max(counts))
