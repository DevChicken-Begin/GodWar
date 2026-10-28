#!/usr/bin/env python3
"""Compare skypit against a resized shared scene, with a conservative logo mask."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES=('animent','overight','tigerknight')

def main():
 entries={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']};samples=[]
 for name in NAMES:
  e=entries[name];path=ROOT/e['source']
  if hashlib.sha256(path.read_bytes()).hexdigest()!=e['source_sha256']:raise ValueError('Source hash changed: '+name)
  with Image.open(path) as gif:
   for i in (0,gif.n_frames//3,2*gif.n_frames//3,gif.n_frames-1):gif.seek(i);samples.append(np.array(gif.convert('RGB')))
 base=np.median(np.stack(samples),axis=0).astype(np.uint8);base=np.array(Image.fromarray(base).resize((400,400),Image.Resampling.BILINEAR)).astype(np.int16)
 e=entries['skypit'];out=A/'shared_scene_candidates/skypit'
 if out.exists():raise ValueError(f'Refusing to overwrite {out}')
 if hashlib.sha256((ROOT/e['source']).read_bytes()).hexdigest()!=e['source_sha256']:raise ValueError('Source hash changed')
 with Image.open(ROOT/e['source']) as gif:
  gif.seek(0); ref=np.array(gif.convert('RGB'));same=np.zeros(ref.shape[:2],dtype=np.uint16)
  for i in range(gif.n_frames):gif.seek(i);same+=np.max(np.abs(np.array(gif.convert('RGB')).astype(np.int16)-ref.astype(np.int16)),axis=2)<=8
  roi=np.zeros(ref.shape[:2],dtype=bool);roi[35:94,75:325]=True;logo=roi & (same>=int(gif.n_frames*.8))
  out.mkdir(parents=True);page=-1;atlas=None
  for i,f in enumerate(e['frames']):
   gif.seek(i);p=np.array(gif.convert('RGBA'));diff=np.max(np.abs(p[:,:,:3].astype(np.int16)-base),axis=2);refdiff=np.max(np.abs(p[:,:,:3].astype(np.int16)-ref.astype(np.int16)),axis=2);p[(diff<=16)|(logo&(refdiff<=8))]=0
   if f['atlas']!=page:
    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
    page=f['atlas']
    with Image.open(A/'extracted/skypit'/f'atlas_{page:03d}.png') as old:atlas=Image.new('RGBA',old.size)
   x,y,_,_=f['region'];atlas.paste(Image.fromarray(p),(x,y))
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
 meta={'source':e['source'],'source_sha256':e['source_sha256'],'frame_count':e['frame_count'],'frames':e['frames'],'method':'resized median of surviving shared-scene sources plus stable logo region mask','model_sources':[{'id':n,'sha256':entries[n]['source_sha256']} for n in NAMES], 'status':'candidate_unreviewed','limitations':'Logo-region character/effect pixels or dark details may be removed; residual logos/background may remain.'}
 (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('skypit:',e['frame_count'],'frames; visual review required')
if __name__=='__main__':main()
