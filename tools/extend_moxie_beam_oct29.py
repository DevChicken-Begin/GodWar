#!/usr/bin/env python3
"""Reconstruct the clipped beam tip in Moxie's repaired measured preview."""
import hashlib,json,math,shutil
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';dest=A/'measured_atlas_pilots/moxie_repaired';backup=A/'archive/moxie_repaired_before_beam_oct29'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if backup.exists():raise FileExistsError(backup)
m=json.loads((dest/'candidate.json').read_text());assert sha(ROOT/m['source'])==m['source_sha256'];shutil.copytree(dest,backup)
pages={};images=[]
for f in m['frames']:
 p=f['atlas']
 if p not in pages:pages[p]=Image.open(backup/f'atlas_{p:03d}.png').convert('RGBA')
 x,y,w,h=f['region'];images.append(pages[p].crop((x,y,x+w,y+h)))
assert len(images)==97 and images[0].size==(340,250)
template=images[38].crop((204,110,237,140)); width,height=660,250; cols=2048//width; rows=2048//height; capacity=cols*rows;out={};refs=[]
for i,im in enumerate(images):
 frame=Image.new('RGBA',(width,height));frame.paste(im,(0,0))
 if 39<=i<=46:
  arr=np.array(frame); column=arr[:,299,:].copy();ys=np.where(column[:,3]>0)[0]; assert len(ys)>0 and ys.min()>=110 and ys.max()<=140
  tip=340+(i-39)*40; scale=len(ys)/17;head_h=max(1,round(30*scale));head=template.resize((33,head_h),Image.Resampling.NEAREST);hx=tip-33;hy=round((float(ys.min())+float(ys.max()))/2-head_h/2)
  arr[:,300:hx+8,:]=column[:,None,:];frame=Image.fromarray(arr);frame.alpha_composite(head,(hx,hy))
 page,slot=divmod(i,capacity)
 if page not in out:
  count=min(capacity,len(images)-page*capacity);out[page]=Image.new('RGBA',(min(cols,count)*width,math.ceil(count/cols)*height))
 x,y=slot%cols*width,slot//cols*height;out[page].paste(frame,(x,y));refs.append({'atlas':page,'region':[x,y,width,height],'duration_ms':m['frames'][i]['duration_ms']})
for p in dest.glob('atlas_*.png'):p.unlink()
for p,im in out.items():im.save(dest/f'atlas_{p:03d}.png',compress_level=3)
m['frames']=refs;m['frame_size']=[width,height];m['beam_reconstruction_oct29']={'input':str(backup.relative_to(ROOT)),'input_atlas_sha256':{p.name:sha(p) for p in sorted(backup.glob('atlas_*.png'))},'frame_indices_zero_based':list(range(39,47)),'template_frame_index':38,'template_region':[204,110,33,30],'tip_x':[340+(i-39)*40 for i in range(39,47)],'method':'Extend each clipped beam with its rightmost source column; attach the frame 39 tip, vertically scaled as the beam narrows; advance the tip 40 pixels per frame.','limitations':'Trajectory, new beam length and tip after the original canvas are reconstructed, not recovered; playback requires visual review.'}
(dest/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('Moxie: 97 frames, 660×250, reconstructed display frames 40–47')
