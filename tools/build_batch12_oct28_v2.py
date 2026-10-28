#!/usr/bin/env python3
"""Stage GIF extraction and provisional separation; source and old assets untouched."""
import hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; STAGE=A/'batch12_stage_v2_20261028';NAMES='Trex butayaro comic ethan godi jaying kasai momo odin panfire shellhost warior'.split();SCENES={'godi','kasai','momo','shellhost'}
sys.path.insert(0,str(ROOT/'tools'));from extract_gif_assets import extract

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def input_gif(n):
 root=ROOT/f'{n}.gif'; return root if root.exists() else A/'vfx'/f'{n}.gif'
def main():
 for n in NAMES:
  if not input_gif(n).is_file():raise FileNotFoundError(n)
 STAGE.mkdir(exist_ok=True)
 for sub in ('vfx','extracted','native','detail','review'): (STAGE/sub).mkdir(exist_ok=True)
 # Independent subjects on the same Duelyst scene supply a reference; not ground truth.
 references=[];refs=[]
 for n in ['animent','overight','tigerknight']:
  p=A/'vfx'/f'{n}.gif';refs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
  with Image.open(p) as g:
   for i in [0,g.n_frames//3,2*g.n_frames//3,g.n_frames-1]:g.seek(i);references.append(np.array(g.convert('RGB')))
 reference=np.median(np.stack(references),axis=0).astype(np.uint8)
 samples400=[]; refs400=[]
 for r in ('godi','kasai','momo'):
  p=input_gif(r); refs400.append({'path':f'Asset/Character/vfx/{r}.gif','sha256':sha(p)})
  with Image.open(p) as g:
   for i in [0,g.n_frames//4,g.n_frames//2,3*g.n_frames//4,g.n_frames-1]: g.seek(i); samples400.append(np.array(g.convert('RGB')))
 reference400=np.median(np.stack(samples400),axis=0).astype(np.uint8)
 rows=[]
 for n in NAMES:
  ready=STAGE/'detail'/n/'candidate.json'
  if ready.exists():
   meta=json.loads(ready.read_text());entry=json.loads((STAGE/'review'/n/'entry.json').read_text());counts=meta['removed_per_frame'];sheets=sorted(x.name for x in (STAGE/'review'/n).glob('frames_*.jpg'));rows.append({'id':n,'entry':entry,'review_sheets':sheets,'removed_min':min(counts),'removed_max':max(counts),'scene':n in SCENES});continue
  for kind in ('vfx','extracted','native','detail','review'):
   q=(STAGE/kind/f'{n}.gif') if kind=='vfx' else STAGE/kind/n
   if q.exists():
    if q.is_dir(): shutil.rmtree(q)
    else: q.unlink()
  src=input_gif(n); dest=STAGE/'vfx'/src.name;shutil.copy2(src,dest);digest=sha(src);assert sha(dest)==digest
  entry=extract(dest,STAGE/'extracted');entry['source']=f'Asset/Character/vfx/{n}.gif';assert entry['source_sha256']==digest
  native=STAGE/'native'/n;native.mkdir();detail=STAGE/'detail'/n;detail.mkdir();review=STAGE/'review'/n;review.mkdir();counts=[];frames=[];sheets=[];page=-1;atlas=None
  with Image.open(dest) as g:
   w,h=g.size; bg=np.array(g.convert('RGB').getpixel((0,0)),np.int16); scene=np.array(reference400 if (w,h)==(400,400) else Image.fromarray(reference).resize((w,h),Image.Resampling.BILINEAR),np.int16) if n in SCENES else None
   # For Trex, only stable non-background pixels in the observed bottom-right logo area.
   logo=None; ref=None
   if n=='Trex' or n in SCENES:
    g.seek(0);ref=np.array(g.convert('RGB'),np.int16);stable=np.zeros((h,w),np.uint16)
    for i in range(g.n_frames):g.seek(i); stable+=(np.max(np.abs(np.array(g.convert('RGB'),np.int16)-ref),axis=2)<=8)
    yy,xx=np.indices((h,w));logo=((xx>=int(w*.58))&(yy>=int(h*.88)) if n=='Trex' else (yy<int(h*.27)))&(stable>=int(g.n_frames*.80))&(np.max(np.abs(ref-bg),axis=2)>5)
   for i,f in enumerate(entry['frames']):
    g.seek(i);rgba=np.array(g.convert('RGBA'));rgb=rgba[:,:,:3].astype(np.int16)
    if scene is not None: mask=np.max(np.abs(rgb-scene),axis=2)<=18
    else: mask=np.max(np.abs(rgb-bg),axis=2)<=5
    if logo is not None:mask|=logo&(np.max(np.abs(rgb-ref),axis=2)<=16)
    counts.append(int(np.count_nonzero(mask & (rgba[:,:,3]>0))));rgba[mask]=0; clean=Image.fromarray(rgba)
    if f['atlas']!=page:
     if atlas is not None:atlas.save(native/f'atlas_{page:03d}.png',compress_level=1)
     page=f['atlas'];
     with Image.open(STAGE/'extracted'/n/f'atlas_{page:03d}.png') as im:atlas=Image.new('RGBA',im.size)
    x,y,fw,fh=f['region'];atlas.paste(clean,(x,y))
    high=clean.convert('RGBa').resize((round(w*1.2),round(h*1.2)),Image.Resampling.LANCZOS).convert('RGBA');high.save(detail/f'frame_{i:03d}.png',compress_level=3);frames.append({**f,'detail_size':list(high.size)})
    if i%30==0:sheet=Image.new('RGB',(900,((min(30,entry['frame_count']-i)+5)//6)*170),'#444');d=ImageDraw.Draw(sheet)
    thumbnail=clean.copy();thumbnail.thumbnail((140,140));slot=i%30;xy=(slot%6*150,slot//6*170);sheet.paste(thumbnail,(xy[0]+(150-thumbnail.width)//2,xy[1]+22),thumbnail);d.text((xy[0]+4,xy[1]+3),str(i),fill='white')
    if i%30==29 or i==entry['frame_count']-1:
     filename=f'frames_{i//30*30:04d}_{i:04d}.jpg';sheet.save(review/filename,quality=90);sheets.append(filename)
   if atlas is not None:atlas.save(native/f'atlas_{page:03d}.png',compress_level=1)
  meta={'id':n,'source':entry['source'],'source_sha256':digest,'art_source':'existing','frame_count':entry['frame_count'],'frames':frames,'display_size':entry['size'],'scale_factor':1.2,'removed_per_frame':counts,'model_sources':(refs400 if (w,h)==(400,400) else refs) if n in SCENES else [],'status':'candidate_unreviewed','method':('Shared scene model from independent sources, RGB distance <=18' if n in SCENES else 'Flat corner color RGB distance <=5')+ ('; Trex static bottom-right logo mask' if n=='Trex' else '; static top logo mask' if n in SCENES else '')+'; premultiplied Lanczos resize 120% per axis for viewer','limitations':'Background or text may remain; similar foreground/FX can be removed; interpolation does not restore missing detail. Review every frame on light/dark backgrounds and in motion.'}
  (native/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');(detail/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');(review/'entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n');rows.append({'id':n,'entry':entry,'review_sheets':sheets,'removed_min':min(counts),'removed_max':max(counts),'scene':n in SCENES});print(n,entry['frame_count'],'frames',entry['size'],'removed range',min(counts),max(counts),flush=True)
 (STAGE/'manifest.json').write_text(json.dumps({'rows':rows,'model_sources':refs},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
