#!/usr/bin/env python3
"""Review-only scene-residue pass using agreement from two independent GIFs."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; NAMES=('momo','shellhost'); REFS=('skypit','animent','overight','tigerknight')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for n in NAMES:
  if (A/'scene_mask_deep_candidates'/n).exists() or (A/'review'/n/'scene_mask_deep_review').exists():raise FileExistsError(n)
 for n in NAMES:
  e=cat[n];source=ROOT/e['source'];base=A/'scene_mask_candidates'/n;meta=json.loads((base/'candidate.json').read_text());assert sha(source)==meta['source_sha256']==e['source_sha256'];w,h=e['size'];refs=[];sources=[]
  for name in REFS:
   ref=cat[name];p=ROOT/ref['source'];assert sha(p)==ref['source_sha256'];samples=[]
   with Image.open(p) as gif:
    indices=sorted(set(int(i) for i in np.linspace(0,gif.n_frames-1,20,dtype=int)))
    for i in indices:
     gif.seek(i);samples.append(np.asarray(gif.convert('RGB').resize((w,h),Image.Resampling.BILINEAR)))
   refs.append(np.stack(samples));sources.append({'source':ref['source'],'sha256':ref['source_sha256'],'sample_indices':indices})
  out=A/'scene_mask_deep_candidates'/n;out.mkdir(parents=True);review=A/'review'/n/'scene_mask_deep_review';review.mkdir();page=-1;atlas=before=None;counts=[];analysis=[]
  for i,f in enumerate(e['frames']):
   if f['atlas']!=page:
    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);before.close()
    page=f['atlas'];before=Image.open(base/f'atlas_{page:03d}.png').convert('RGBA');atlas=Image.new('RGBA',before.size)
   x,y,fw,fh=f['region'];prior=np.array(before.crop((x,y,x+fw,y+fh)));rgb=prior[:,:,:3].astype(np.int16);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
   candidate=(prior[:,:,3]>0)&(r<=12)&(g>=35)&(g<=90)&(b>=70)&(b<=155)&(b-g>=25)&(b-g<=70);yy,xx=np.where(candidate);points=rgb[yy,xx];votes=np.zeros(len(yy),dtype=np.uint8)
   for stack in refs:
    matched=np.zeros(len(yy),bool)
    for image in stack:
     diff=np.max(np.abs(image[yy,xx].astype(np.int16)-points),axis=1);matched|=diff<=8
    votes+=matched
   removed=np.zeros((h,w),bool);selected=votes>=2;removed[yy[selected],xx[selected]]=True;counts.append(int(selected.sum()));analysis.append({'blue_tested':len(yy),'matched_at_least_two':int(selected.sum()),'retained_unconfirmed':int((~selected).sum())});clean=prior.copy();clean[removed]=0;im=Image.fromarray(clean);atlas.paste(im,(x,y));hi=im.convert('RGBa').resize((round(w*1.2),round(h*1.2)),Image.Resampling.LANCZOS).convert('RGBA');hi.save(out/f'frame_{i:03d}.png',compress_level=3)
   if i%20==0:sheet=Image.new('RGB',(1000,((min(20,e['frame_count']-i)+4)//5)*195),'#ddd');draw=ImageDraw.Draw(sheet)
   thumb=im.copy();thumb.thumbnail((185,165));k=i%20;xy=(k%5*200,k//5*195);sheet.paste(thumb,(xy[0]+(200-thumb.width)//2,xy[1]+22),thumb);draw.text((xy[0]+4,xy[1]+4),f'{i+1}: -{counts[-1]} px',fill='black')
   if i%20==19 or i==e['frame_count']-1:sheet.save(review/f'frames_{i//20*20:03d}_{i:03d}.jpg',quality=94)
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);before.close()
  result={'id':n,'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'scene_mask_candidates','base_atlas_sha256':{p.name:sha(p) for p in sorted(base.glob('atlas_*.png'))},'model_sources':sources,'evidence':meta['evidence'],'frame_count':e['frame_count'],'frames':e['frames'],'display_size':e['size'],'scale_factor':1.2,'removed_per_frame':counts,'analysis_per_frame':analysis,'art_source':'existing','status':'candidate_unreviewed','method':'For surviving dark blue pixels, require same-position RGB max difference <=8 against one sample each from at least two independent reference GIFs (20 sampled frames per GIF). Original-resolution atlas pixels either kept exactly or cleared; premultiplied Lanczos 120% frame preview.','limitations':'Background-colored character or effect can coincidentally match two references, especially at overlap. Unconfirmed residue remains intentionally. Alpha and interpolation may affect edges. Check all frames in motion on light/dark backgrounds; cannot guarantee zero foreground loss.'}
  (out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(n,len(counts),'frames removed',sum(counts),'index32',counts[32], 'retained',sum(v['retained_unconfirmed'] for v in analysis),flush=True)
if __name__=='__main__':main()
