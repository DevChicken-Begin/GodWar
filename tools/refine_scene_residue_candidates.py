#!/usr/bin/env python3
"""Third review-only pass for user-identified shared-scene residue."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'
NAMES=('animent','overight','skypit')
REFS={'animent':'overight','overight':'animent','skypit':'animent'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def create(e, entries):
 name=e['id']; src=ROOT/e['source']; ref_entry=entries[REFS[name]]; ref_src=ROOT/ref_entry['source']; out=A/'scene_detail_v3_candidates'/name; base=A/'foot_candidates'/name
 if out.exists(): raise FileExistsError(out)
 if sha(src)!=e['source_sha256'] or sha(ref_src)!=ref_entry['source_sha256']: raise ValueError('source hash mismatch')
 old=json.loads((base/'candidate.json').read_text()); assert old['source_sha256']==e['source_sha256']
 with Image.open(src) as gif:
  w,h=gif.size; samples=[]
  for i in sorted(set(np.linspace(0,gif.n_frames-1,21,dtype=int).tolist())):
   gif.seek(i); samples.append(np.array(gif.convert('RGB')))
  first=np.median(np.stack(samples),axis=0).astype(np.int16); stable=np.zeros((h,w),np.uint16)
  for i in range(gif.n_frames):
   gif.seek(i);p=np.array(gif.convert('RGB'),dtype=np.int16); stable+=(np.max(np.abs(p-first),axis=2)<=8)
  # Compare to a second source across several poses. At each position, retain
  # the closest reference, because its foreground can cover the shared scene.
  diff=np.full((h,w),255,np.int16)
  with Image.open(ref_src) as bg:
   for i in sorted(set(np.linspace(0,bg.n_frames-1,12,dtype=int).tolist())):
    bg.seek(i); sample=bg.convert('RGB').resize((w,h),Image.Resampling.BILINEAR)
    diff=np.minimum(diff,np.max(np.abs(np.array(sample,dtype=np.int16)-first),axis=2))
  # User sample dark blue spans approximately R 0..5, G 32..70, B 71..125.
  blue=(first[:,:,0]<=12)&(first[:,:,1]>=27)&(first[:,:,1]<=78)&(first[:,:,2]>=60)&(first[:,:,2]<=145)&(first[:,:,2]>first[:,:,1])
  region=np.zeros((h,w),bool)
  if name=='skypit': region[int(h*.62):,:]=True
  else: region[int(h*.48):,:]=True
  # Skypit uses a differently scaled scene. Require 80% temporal stability;
  # for the equal-sized GIFs additionally match the independent reference.
  scene=region & blue & (stable>=int(gif.n_frames*.8))
  if name!='skypit': scene &= diff<=20
  line=np.zeros((h,w),bool)
  if name=='overight': line[59:102,220]=True
  line &= stable>=int(gif.n_frames*.8)
  out.mkdir(parents=True);number=-1;before=atlas=None; counts=[]
  for i,f in enumerate(e['frames']):
   gif.seek(i);rgb=np.array(gif.convert('RGB'),dtype=np.int16)
   if f['atlas']!=number:
    if atlas is not None:atlas.save(out/f'atlas_{number:03d}.png',compress_level=1);before.close()
    number=f['atlas'];before=Image.open(base/f'atlas_{number:03d}.png');atlas=Image.new('RGBA',before.size)
   x,y,fw,fh=f['region'];pixels=np.array(before.crop((x,y,x+fw,y+fh)));same=np.max(np.abs(rgb-first),axis=2)<=8
   remove=(scene|line)&same&(pixels[:,:,3]>0)
   if name=='skypit':
    # The sampled scene palette changes slightly with GIF quantization. Only
    # use this stronger color rule in the observed lower-foot region.
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    sample_blue=(r<=5)&(g>=32)&(g<=70)&(b>=70)&(b<=125)&(b>g+25)
    lower=np.zeros((h,w),bool);lower[int(h*.70):,:]=True
    remove |= lower & sample_blue & (pixels[:,:,3]>0)
   counts.append(int(remove.sum()));pixels[remove]=0;atlas.paste(Image.fromarray(pixels),(x,y))
  if atlas is not None:atlas.save(out/f'atlas_{number:03d}.png',compress_level=1);before.close()
 meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'foot_candidates',
 'reference_sources':[{'source':ref_entry['source'],'sha256':ref_entry['source_sha256']}],
 'user_sample':{'path':'Asset/Character/review/reference-samples/scene-dark-blue-2026-10-28.png','original_path':'image copy 3.png','sha256':sha(A/'review/reference-samples/scene-dark-blue-2026-10-28.png')},
 'frame_count':e['frame_count'],'frames':e['frames'],'removed_per_frame':counts,'status':'candidate_unreviewed',
 'method':'Dark-blue sample color band, restricted to stable coordinates and the lower scene; animent/overight also require a similar pixel in independent scene. Overight additionally clears stable column x=220, y=59..101. Skypit also clears near-sample dark-blue colors below 70% canvas even when not temporally stable. Each frame must match the temporal median source colors, except the skypit lower-foot color rule.',
 'limitations':'Similar blue character/FX pixels can match the background; static subject details can be erased. Previous candidate may already contain losses. Some scene residue may remain; inspect every frame on light/dark backgrounds.'}
 (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(name, 'frames',len(counts),'removed',sum(counts),'frame31',counts[31],flush=True)

def main():
 entries={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 if any((A/'scene_detail_v3_candidates'/n).exists() for n in NAMES):raise FileExistsError('candidate exists')
 for n in NAMES:create(entries[n],entries)
if __name__=='__main__':main()
