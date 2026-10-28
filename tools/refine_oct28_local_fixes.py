#!/usr/bin/env python3
"""Narrow review fixes for Aonoma task: animent back and scorpit watermark."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES=('animent','scorpit');BASE={'animent':'spot_candidates','scorpit':'detailed_candidates'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 entries={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 if any((A/'oct28_fix_candidates'/n).exists() for n in NAMES):raise FileExistsError('candidate exists')
 for n in NAMES:
  e=entries[n];source=ROOT/e['source'];base=A/BASE[n]/n;meta=json.loads((base/'candidate.json').read_text());assert sha(source)==e['source_sha256']==meta['source_sha256']
  out=A/'oct28_fix_candidates'/n;out.mkdir(parents=True);page=-1;prior=atlas=None;counts=[]
  with Image.open(source) as gif:
   w,h=gif.size;gif.seek(0);ref=np.array(gif.convert('RGB'),dtype=np.int16)
   if n=='scorpit':
    yy,xx=np.indices((h,w));bg=ref[0,0];roi=(xx>=195)&(yy>=270)&(yy<295);letter=roi&(np.max(np.abs(ref-bg),axis=2)>10)
   for i,f in enumerate(e['frames']):
    gif.seek(i);rgb=np.array(gif.convert('RGB'),dtype=np.int16)
    if page!=f['atlas']:
     if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
     page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
    x,y,fw,fh=f['region'];p=np.array(prior.crop((x,y,x+fw,y+fh)))
    if n=='animent':
     yy,xx=np.indices((h,w));area=(xx>=239)&(xx<245)&(yy>=323)&(yy<350);colors=np.zeros((h,w),bool)
     for color in ((5,69,125),(6,72,127),(2,68,125)):colors|=np.all(rgb==color,axis=2)
     mask=area & colors
    else:
     # A literal template removes remaining text even where VFX overlays it;
     # pixels underneath cannot be reconstructed and holes are possible.
     mask=letter
    mask &= p[:,:,3]>0;counts.append(int(mask.sum()));p[mask]=0;atlas.paste(Image.fromarray(p),(x,y))
   if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  method='exact sampled RGB within x=239..244,y=323..349' if n=='animent' else 'mask watermark pixels from source frame 0 in bottom-right region, including where VFX overlaps'
  result={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':BASE[n], 'frame_count':e['frame_count'],'frames':e['frames'],'removed_per_frame':counts,'status':'candidate_unreviewed','method':method,'limitations':'Overlapping same-colored character/FX may be erased; scorpit watermark template also removes any VFX under those letters, potentially leaving holes.'}
  (out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(n,'frames',len(counts),'removed',sum(counts),'frame index',58 if n=='animent' else 20,'count',counts[58 if n=='animent' else 20],flush=True)
if __name__=='__main__':main()
