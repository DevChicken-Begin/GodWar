#!/usr/bin/env python3
"""Soften the two solid flash frames; preserve GIF and the previous atlas."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';dest=A/'measured_atlas_pilots/firemen';archive=A/'archive/firemen_before_soft_flash'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if archive.exists():raise FileExistsError(archive)
m=json.loads((dest/'candidate.json').read_text());assert sha(ROOT/m['source'])==m['source_sha256'];shutil.copytree(dest,archive);pages={}
for i,color in [(73,0),(74,255)]:
 f=m['frames'][i];p=f['atlas'];x,y,w,h=f['region']
 if p not in pages:pages[p]=np.array(Image.open(archive/f'atlas_{p:03d}.png').convert('RGBA'))
 a=pages[p][y:y+h,x:x+w];assert np.all(a[:,:,:3]==color) and np.all(a[:,:,3]==255)
 # Elliptical smoothstep: full-strength center, zero alpha before canvas edges.
 yy,xx=np.ogrid[:h,:w];r=np.sqrt(((xx-(w-1)/2)/(w/2))**2+((yy-(h-1)/2)/(h/2))**2);t=np.clip((r-0.12)/(0.96-0.12),0,1);alpha=np.rint(255*(1-t*t*(3-2*t))).astype(np.uint8);a[:,:,3]=alpha;a[alpha==0]=0
for p,a in pages.items():Image.fromarray(a).save(dest/f'atlas_{p:03d}.png',compress_level=3)
m['flash_softening']={'input':str(archive.relative_to(ROOT)),'input_atlas_sha256':{p.name:sha(p) for p in sorted(archive.glob('atlas_*.png'))},'frame_indices_zero_based':[73,74],'display_frame_numbers':[74,75],'method':'Solid source black and white preserved; elliptical smoothstep alpha from radius 0.12 to 0.96, zero before every canvas edge.','status':'visual_review_pending'}
(dest/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('Softened Firemen frames 74–75; duration unchanged')
