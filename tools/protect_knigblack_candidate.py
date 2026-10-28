#!/usr/bin/env python3
"""Protect nearby details after aggressive background fit, as an unreviewed candidate."""
import hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='knigblack';e=next(x for x in json.loads((A/'extracted/catalog.json').read_text())['assets'] if x['id']==n);src=ROOT/e['source'];strong=A/'scene_model_strong_candidates'/n;out=A/'scene_protected_candidates'/n
if out.exists():raise FileExistsError(out)
assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256'];out.mkdir(parents=True);atlas=prior=None;num=-1;counts=[]
with Image.open(src) as gif:
 for i,f in enumerate(e['frames']):
  gif.seek(i);orig=np.array(gif.convert('RGBA'));h,w=orig.shape[:2]
  if f['atlas']!=num:
   if atlas is not None:atlas.save(out/f'atlas_{num:03d}.png',compress_level=1);prior.close()
   num=f['atlas'];prior=Image.open(strong/f'atlas_{num:03d}.png');atlas=Image.new('RGBA',prior.size)
  x,y,fw,fh=f['region'];p=np.array(prior.crop((x,y,x+fw,y+fh)));present=p[:,:,3]>0;area=np.zeros((h,w),bool);area[:420,:]=True;near=cv2.dilate((present&area).astype('uint8'),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))>0;restore=(~present)&near&area;counts.append(int(restore.sum()));p[restore]=orig[restore];atlas.paste(Image.fromarray(p),(x,y))
 if atlas is not None:atlas.save(out/f'atlas_{num:03d}.png',compress_level=1);prior.close()
meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'scene_model_strong_candidates','frame_count':e['frame_count'],'frames':e['frames'],'restored_per_frame':counts,'status':'candidate_unreviewed','method':'Restore source pixels within 7 px of strong foreground above y=420 to preserve details, without recropping frames.','limitations':'Background halos remain around silhouette and shadows remain; some gray foreground can still be missing. Requires manual refinement of every frame.'}
(out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(n,'frames',len(counts),'restored',sum(counts),'unreviewed')
