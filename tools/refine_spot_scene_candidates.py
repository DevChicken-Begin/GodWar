#!/usr/bin/env python3
"""Remove reported fixed-location scene specks without overwriting earlier variants."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; NAMES=('animent','skypit','overight')
# Rectangles are source-canvas coordinates [left, top, right, bottom), measured
# from the user's reported regions. The frame's actual colors must also match.
SPECS={'animent': {'box':(245,260,265,300),'colors':((5,69,125),(6,72,127),(2,68,125))},
       'skypit': {'box':(243,277,246,280),'colors':((1,56,105),(1,54,104))},
       'overight':{'box':(210,300,230,309),'colors':((5,70,125),)}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def create(e):
 n=e['id']; src=ROOT/e['source']; base=A/'remaining_scene_candidates'/n;out=A/'spot_candidates'/n;spec=SPECS[n]
 if out.exists():raise FileExistsError(out)
 if sha(src)!=e['source_sha256']:raise ValueError('source hash mismatch')
 old=json.loads((base/'candidate.json').read_text());assert old['source_sha256']==e['source_sha256']
 with Image.open(src) as gif:
  w,h=gif.size;x1,y1,x2,y2=spec['box'];assert 0<=x1<x2<=w and 0<=y1<y2<=h
  area=np.zeros((h,w),bool);area[y1:y2,x1:x2]=True;out.mkdir(parents=True);num=-1;page=prior=None;counts=[]
  for i,f in enumerate(e['frames']):
   gif.seek(i);rgb=np.array(gif.convert('RGB')); color=np.zeros((h,w),bool)
   for col in spec['colors']:color|=np.all(rgb==col,axis=2)
   if f['atlas']!=num:
    if page is not None:page.save(out/f'atlas_{num:03d}.png',compress_level=1);prior.close()
    num=f['atlas'];prior=Image.open(base/f'atlas_{num:03d}.png');page=Image.new('RGBA',prior.size)
   x,y,fw,fh=f['region'];p=np.array(prior.crop((x,y,x+fw,y+fh)));remove=area & color & (p[:,:,3]>0)
   counts.append(int(remove.sum()));p[remove]=0;page.paste(Image.fromarray(p),(x,y))
  if page is not None:page.save(out/f'atlas_{num:03d}.png',compress_level=1);prior.close()
 meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'remaining_scene_candidates','reference_sources':[],
       'sample':{'path':'Asset/Character/review/reference-samples/scene-dark-blue-2026-10-28.png','sha256':sha(A/'review/reference-samples/scene-dark-blue-2026-10-28.png')},
       'frame_count':e['frame_count'],'frames':e['frames'],'removed_per_frame':counts,'spot':spec,'status':'candidate_unreviewed',
       'method':'Observed source-canvas rectangle and exact observed RGB colors only; matching pixels in each frame become transparent.',
       'limitations':'An identically colored character or effect inside the rectangle can also be removed; earlier versions may have lost foreground. Inspect all frames and compare with source.'}
 (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(n,'frames',len(counts),'removed',sum(counts),'index 38',counts[38],'index 40',counts[40],flush=True)
def main():
 entries={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 if any((A/'spot_candidates'/n).exists() for n in NAMES):raise FileExistsError('candidate exists')
 for n in NAMES:create(entries[n])
if __name__=='__main__':main()
