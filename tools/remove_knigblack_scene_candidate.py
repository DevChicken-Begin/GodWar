#!/usr/bin/env python3
"""Experimental smooth background model; retains source pixels outside mask."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';name='knigblack';e=next(x for x in json.loads((A/'extracted/catalog.json').read_text())['assets'] if x['id']==name);src=ROOT/e['source'];out=A/'scene_model_candidates'/name
if out.exists():raise FileExistsError(out)
assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256'];
with Image.open(src) as gif:
 gif.seek(0);p=np.array(gif.convert('RGB'),np.float64);h,w=p.shape[:2];y,x=np.mgrid[0:h:4,0:w:4];X=x/240-1;Y=y/240-1;bg=(x<95)|(x>345)|(y<115)|(y>460);terms=[(i,j) for i in range(7) for j in range(7-i)];F=np.stack([X**i*Y**j for i,j in terms],axis=-1);coef=np.linalg.lstsq(F[bg],p[::4,::4][bg],rcond=None)[0];fit=F@coef;residual=np.max(np.abs(fit-p[::4,::4]),axis=2);fy,fx=np.mgrid[0:h,0:w];fx=fx/240-1;fy=fy/240-1;pred=np.zeros((h,w,3),np.float64)
 for k,(i,j) in enumerate(terms):pred+=(fx**i*fy**j)[:,:,None]*coef[k]
 out.mkdir(parents=True);num=-1;atlas=None;counts=[]
 for i,f in enumerate(e['frames']):
  gif.seek(i);pixels=np.array(gif.convert('RGBA'));mask=np.max(np.abs(pixels[:,:,:3].astype(np.float64)-pred),axis=2)<=4;counts.append(int(mask.sum()));pixels[mask]=0
  if num!=f['atlas']:
   if atlas is not None:atlas.save(out/f'atlas_{num:03d}.png',compress_level=1)
   num=f['atlas'];prior=Image.open(A/'extracted'/name/f'atlas_{num:03d}.png');atlas=Image.new('RGBA',prior.size);prior.close()
  x,y,w0,h0=f['region'];atlas.paste(Image.fromarray(pixels),(x,y))
 if atlas is not None:atlas.save(out/f'atlas_{num:03d}.png',compress_level=1)
meta={'source':e['source'],'source_sha256':e['source_sha256'],'art_source':'existing','frame_count':e['frame_count'],'frames':e['frames'],'removed_per_frame':counts,'method':'Polynomial degree 6 fitted on frame 0 peripheral scene (x<95, x>345, y<115 or y>460), RGB max distance <=4; transparent pixels, source canvas maintained.','model_coefficients':coef.tolist(),'terms':terms,'training_error_p99':float(np.quantile(residual[bg],.99)),'status':'candidate_unreviewed','limitations':'Background model may erase similarly colored armor, shadows or effects; background/shadow may remain. Compare each frame to source on multiple backgrounds.'}
(out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('knigblack',len(counts),'frames','fit p99',round(meta['training_error_p99'],3),'removed',sum(counts),flush=True)
