#!/usr/bin/env python3
"""Remove selected scene-blue residue using independent scene matching and temporal evidence."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'; NAMES=('momo','shellhost'); BASE='batch12_native_candidates'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 for n in NAMES:
  if (A/'scene_mask_candidates'/n).exists() or (A/'review'/n/'scene_mask_review').exists():raise FileExistsError(n)
 refs=[]; entries=[]
 for name in ('skypit','animent','overight','tigerknight'):
  e=cat[name];p=ROOT/e['source'];assert sha(p)==e['source_sha256'];entries.append({'source':e['source'],'sha256':e['source_sha256']})
  with Image.open(p) as g:
   for i in sorted(set(np.linspace(0,g.n_frames-1,9,dtype=int))):g.seek(int(i));refs.append((name,np.asarray(g.convert('RGB'))))
 for name in NAMES:
  e=cat[name];src=ROOT/e['source'];base=A/BASE/name;meta=json.loads((base/'candidate.json').read_text());assert sha(src)==e['source_sha256']==meta['source_sha256']
  with Image.open(src) as g:
   w,h=g.size;arr=[]
   for i in range(g.n_frames):g.seek(i);arr.append(np.asarray(g.convert('RGB')))
  raw=np.stack(arr).astype(np.int16);median=np.median(raw,axis=0).astype(np.int16); stable=(np.max(np.abs(raw-median),axis=3)<=9).sum(axis=0)>=int(e['frame_count']*.8)
  refs_scaled=[]
  for id,ref in refs:
   if name=='momo' and id!='skypit':continue
   if name=='shellhost' and id=='skypit':continue
   refs_scaled.append(np.asarray(Image.fromarray(ref).resize((w,h),Image.Resampling.BILINEAR),dtype=np.int16))
  model=np.median(np.stack(refs_scaled),axis=0).astype(np.int16)
  out=A/'scene_mask_candidates'/name;out.mkdir(parents=True); rev=A/'review'/name/'scene_mask_review';rev.mkdir();samples=['image copy.png','image copy 2.png'] if name=='momo' else ['image copy 3.png'];evidence=[]
  for sn in samples:
   sp=ROOT/sn;target=rev/sn;shutil.copy2(sp,target);evidence.append({'path':str(target.relative_to(ROOT)),'sha256':sha(target)})
  page=-1;atlas=None;prior=None;counts=[]
  for i,f in enumerate(e['frames']):
   rgb=raw[i];r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
   # Scene-blue bands from supplied crops, excluding bright cyan and purple.
   blue=(r<=18)&(g>=38)&(g<=82)&(b>=75)&(b<=145)&((b-g)>=30)&((b-g)<=64)
   reference=np.max(np.abs(rgb-model),axis=2)<=28
   temporal=stable&(np.max(np.abs(rgb-median),axis=2)<=9)
   mask=blue&(reference|temporal)
   if page!=f['atlas']:
    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
    page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png').convert('RGBA');atlas=Image.new('RGBA',prior.size)
   x,y,fw,fh=f['region'];px=np.array(prior.crop((x,y,x+fw,y+fh)));mask &= px[:,:,3]>0;counts.append(int(mask.sum()));px[mask]=0;im=Image.fromarray(px);atlas.paste(im,(x,y));hi=im.convert('RGBa').resize((round(w*1.2),round(h*1.2)),Image.Resampling.LANCZOS).convert('RGBA');hi.save(out/f'frame_{i:03d}.png',compress_level=3)
   if i%20==0:
    sheet=Image.new('RGB',(1000,((min(20,e['frame_count']-i)+4)//5)*195),'#444');draw=ImageDraw.Draw(sheet)
   thumbnail=im.copy();thumbnail.thumbnail((185,165));k=i%20;xy=(k%5*200,k//5*195);sheet.paste(thumbnail,(xy[0]+(200-thumbnail.width)//2,xy[1]+22),thumbnail);draw.text((xy[0]+4,xy[1]+4),f'{i}: -{counts[-1]} px',fill='white')
   if i%20==19 or i==e['frame_count']-1:sheet.save(rev/f'frames_{i//20*20:03d}_{i:03d}.jpg',quality=94)
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  result={'id':name,'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':BASE,'base_atlas_sha256':{p.name:sha(p) for p in sorted(base.glob('atlas_*.png'))},'model_sources':entries,'evidence':evidence,'frame_count':e['frame_count'],'frames':e['frames'],'display_size':e['size'],'scale_factor':1.2,'removed_per_frame':counts,'art_source':'existing','status':'candidate_unreviewed','method':'Remove remaining dark blue in sample-derived channel band, when within RGB max 28 of independent scene median or within 9 of own 80%-stable temporal median. Resize premultiplied 120% for display, retaining canvas size.','limitations':'Blue foreground and VFX can share background colors, including stationary shapes; may be removed. Scene-colored remnants may persist. Verify motion and all frames over light and dark backgrounds.'}
  (out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(name,len(counts),'frames removed',sum(counts),'range',min(counts),max(counts),flush=True)
if __name__=='__main__':main()
