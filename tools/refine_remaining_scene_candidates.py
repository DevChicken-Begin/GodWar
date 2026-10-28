#!/usr/bin/env python3
"""Follow-up review candidates for reported scene-colored residue."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; NAMES=('skypit','overight','animent')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def create(e, entries):
 name=e['id'];src=ROOT/e['source'];base=A/'scene_detail_v3_candidates'/name;out=A/'remaining_scene_candidates'/name
 if out.exists():raise FileExistsError(out)
 if sha(src)!=e['source_sha256']:raise ValueError('source hash mismatch')
 base_meta=json.loads((base/'candidate.json').read_text());assert base_meta['source_sha256']==e['source_sha256']
 ref_entry=entries['overight']; refsrc=ROOT/ref_entry['source']; reference=[]
 if name=='animent':
  if sha(refsrc)!=ref_entry['source_sha256']:raise ValueError('reference hash mismatch')
  with Image.open(refsrc) as gif:
   for i in sorted(set(np.linspace(0,gif.n_frames-1,12,dtype=int).tolist())):
    gif.seek(i);reference.append(np.array(gif.convert('RGB'),dtype=np.int16))
 with Image.open(src) as gif:
  w,h=gif.size; yy=np.indices((h,w))[0]; out.mkdir(parents=True);page_no=-1;atlas=prev=None;counts=[]
  for i,f in enumerate(e['frames']):
   gif.seek(i);rgb=np.array(gif.convert('RGB'),dtype=np.int16)
   if f['atlas']!=page_no:
    if atlas is not None:atlas.save(out/f'atlas_{page_no:03d}.png',compress_level=1);prev.close()
    page_no=f['atlas'];prev=Image.open(base/f'atlas_{page_no:03d}.png');atlas=Image.new('RGBA',prev.size)
   x,y,fw,fh=f['region'];p=np.array(prev.crop((x,y,x+fw,y+fh)));r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
   # Color band sampled from the user's dark-blue examples; the restricted
   # lower-canvas pass can still affect identically colored body/FX details.
   color=(r<=20)&(g>=27)&(g<=90)&(b>=60)&(b<=155)&(b>g+22)
   if name=='animent':
    match=np.zeros((h,w),bool)
    for ref in reference:match|=np.max(np.abs(rgb-ref),axis=2)<=3
    remove=color & (yy>=int(h*.50)) & match
   else:remove=color & (yy>=int(h*.70 if name=='skypit' else h*.68))
   remove &= p[:,:,3]>0;counts.append(int(remove.sum()));p[remove]=0;atlas.paste(Image.fromarray(p),(x,y))
  if atlas is not None:atlas.save(out/f'atlas_{page_no:03d}.png',compress_level=1);prev.close()
 meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'scene_detail_v3_candidates',
 'reference_sources':[{'source':ref_entry['source'],'sha256':ref_entry['source_sha256']}] if name=='animent' else [],
 'sample':{'path':'Asset/Character/review/reference-samples/scene-dark-blue-2026-10-28.png','sha256':sha(A/'review/reference-samples/scene-dark-blue-2026-10-28.png')},
 'frames':e['frames'],'frame_count':e['frame_count'],'removed_per_frame':counts,'status':'candidate_unreviewed',
 'method':'dark-blue sample band below 70% canvas for skypit or 68% for overight; animent below 50% requires same-position RGB within 3 of one of 12 overight source frames.',
 'limitations':'Shared colors and coincident sprites can cause foreground or VFX loss. Reference is not a clean ground truth. Check all frames on multiple backgrounds; earlier candidate may already be damaged.'}
 (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(name,'frames',len(counts),'removed',sum(counts),'frame 31',counts[31],'frame 40',counts[40],flush=True)
def main():
 entries={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 if any((A/'remaining_scene_candidates'/n).exists() for n in NAMES):raise FileExistsError('candidate exists')
 for n in NAMES:create(entries[n],entries)
if __name__=='__main__':main()
