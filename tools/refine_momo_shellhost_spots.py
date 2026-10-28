#!/usr/bin/env python3
"""Target isolated reported residue and enlarge momo on a fixed canvas."""
import hashlib,json
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES=('momo','shellhost');BASE='scene_mask_deeper_candidates'; TEMPLATES=[(190,327,195,333),(179,343,185,353),(248,323,256,330)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cat={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for n in NAMES:
  if (A/'scene_spot_candidates'/n).exists() or (A/'review'/n/'scene_spot_review').exists():raise FileExistsError(n)
 for n in NAMES:
  e=cat[n];source=ROOT/e['source'];base=A/BASE/n;old=json.loads((base/'candidate.json').read_text());assert sha(source)==e['source_sha256']==old['source_sha256'];w,h=e['size'];out=A/'scene_spot_candidates'/n;out.mkdir(parents=True);review=A/'review'/n/'scene_spot_review';review.mkdir();imgs=[]
  for i,f in enumerate(e['frames']):
   x,y,fw,fh=f['region']
   with Image.open(base/f'atlas_{f["atlas"]:03}.png') as image:imgs.append(np.array(image.convert('RGBA').crop((x,y,x+fw,y+fh))))
  template=[imgs[0][y1:y2,x1:x2].copy() for x1,y1,x2,y2 in TEMPLATES] if n=='momo' else []
  raw=[]
  if n=='shellhost':
   with Image.open(source) as gif:
    for i in range(gif.n_frames):gif.seek(i);raw.append(np.array(gif.convert('RGB'),dtype=np.int16))
   raw=np.stack(raw)
  scale=1.1 if n=='momo' else 1.0;ow,oh=round(w*scale),round(h*scale);cols=2048//ow;rows=2048//oh;cap=cols*rows;page=-1;atlas=None;frames=[];counts=[];decisions=[]
  for i,(f,original) in enumerate(zip(e['frames'],imgs)):
   px=original.copy();removed=np.zeros((h,w),bool);reason=[]
   if n=='momo':
    for k,(x1,y1,x2,y2) in enumerate(TEMPLATES):
     area=original[y1:y2,x1:x2];match=np.array_equal(area,template[k]);reason.append(match)
     if match:removed[y1:y2,x1:x2]=area[:,:,3]>0
   elif 30<=i<=38:
    rgb=original[:,:,:3].astype(np.int16);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];blue=(original[:,:,3]>0)&(r<=12)&(g>=35)&(g<=90)&(b>=70)&(b<=155)&(b-g>=25)&(b-g<=70)
    frequency=(np.max(np.abs(raw-rgb[None,:,:,:]),axis=3)<=4).sum(axis=0);other=(original[:,:,3]>0)&~blue;protected=cv2.dilate(other.astype(np.uint8),np.ones((3,3),np.uint8),iterations=1).astype(bool);removed=blue&(frequency>=5)&~protected
   counts.append(int(removed.sum()));decisions.append(reason);px[removed]=0;im=Image.fromarray(px)
   if n=='momo':im=im.resize((ow,oh),Image.Resampling.NEAREST)
   p,slot=divmod(i,cap)
   if p!=page:
    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
    page=p;count=min(cap,len(e['frames'])-page*cap);atlas=Image.new('RGBA',(min(cols,count)*ow,((count+cols-1)//cols)*oh))
   x=(slot%cols)*ow;y=(slot//cols)*oh;atlas.paste(im,(x,y));hi=im.convert('RGBa').resize((round(ow*1.2),round(oh*1.2)),Image.Resampling.LANCZOS).convert('RGBA');hi.save(out/f'frame_{i:03d}.png',compress_level=3);frames.append({'atlas':p,'region':[x,y,ow,oh],'duration_ms':f['duration_ms'],'source_index':i})
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
  meta={'id':n,'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':BASE,'base_atlas_sha256':{p.name:sha(p) for p in sorted(base.glob('atlas_*.png'))},'art_source':'existing','frame_count':len(frames),'frames':frames,'loop':e['loop'],'display_size':[ow,oh],'source_display_size':[w,h],'display_scale':scale,'anchor_source':[w/2,h],'anchor_display':[ow/2,oh],'removed_per_frame':counts,'template_boxes':TEMPLATES if n=='momo' else [],'template_matches':decisions,'shell_indices_zero_based':[30,31,32,33,34,35,36,37,38] if n=='shellhost' else [],'status':'candidate_unreviewed','method':'Momo: remove 3 fixed coordinate patches only if entire RGBA crop equals frame 0; resize entire fixed canvas by 1.1x using nearest, keeping normalized bottom-center anchor. Shellhost: only indices 30..38, remove dark blue if same color appears >=5 source frames, excluding 1px around any non-blue opaque pixels. Repack atlas; 120% preview.','limitations':'Color match and temporal agreement are not proof of background. Shellhost leaves a 1px safety margin next to non-blue content. Frame-zero patch can overlap intentional static content; inspect. Scaling includes effects, changes display size and may alter pixel widths. Retains any prior defects.'}
  (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(n,len(frames),'new size',(ow,oh),'removed',sum(counts),'frame37',counts[36],flush=True)
if __name__=='__main__':main()
