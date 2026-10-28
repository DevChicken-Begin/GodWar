#!/usr/bin/env python3
"""Remove a fixed logo at its measured source coordinates, as review candidates."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';NAMES=('airpot','wavinges');BASE={'airpot':'native_candidates','wavinges':'batch_candidates'}
def main():
 cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
 if any((A/'logo_candidates'/n).exists() for n in NAMES):raise FileExistsError('candidate exists')
 for n in NAMES:
  e=cat[n];src=ROOT/e['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256'];base=A/BASE[n]/n;meta=json.loads((base/'candidate.json').read_text());assert meta['source_sha256']==e['source_sha256'];out=A/'logo_candidates'/n
  with Image.open(src) as gif:
   gif.seek(0);ref=np.array(gif.convert('RGB'),np.int16);h,w=ref.shape[:2];yy,xx=np.indices((h,w));roi=(xx>=w-110)&(yy>=h-45);bg=ref[0,0];glyph=roi&(np.max(np.abs(ref-bg),axis=2)>5)
   # All frame source colors at the identified pixels must match the reference:
   # otherwise refuse rather than erase a possible overlapping subject or VFX.
   for i in range(gif.n_frames):
    gif.seek(i);rgb=np.array(gif.convert('RGB'),np.int16)
    if np.any(glyph & (np.max(np.abs(rgb-ref),axis=2)>12)):raise ValueError(f'{n}: logo region changed in frame {i}')
   out.mkdir(parents=True);page=-1;atlas=prior=None;counts=[]
   for i,f in enumerate(e['frames']):
    if page!=f['atlas']:
     if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
     page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
    x,y,w0,h0=f['region'];p=np.array(prior.crop((x,y,x+w0,y+h0)));mask=glyph&(p[:,:,3]>0);counts.append(int(mask.sum()));p[mask]=0;atlas.paste(Image.fromarray(p),(x,y))
   if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  result={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':BASE[n],'frame_count':e['frame_count'],'frames':e['frames'],'removed_per_frame':counts,'status':'candidate_unreviewed','method':'Observed fixed logo mask in bottom-right 110x45 canvas area, derived from frame 0 against corner background. Verify all source frames match it within RGB max 12 before clearing.','limitations':'Similar static foreground in the ROI could also be removed; inspect all frames on light/dark backgrounds.'}
  (out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(n,'frames',len(counts),'removed',sum(counts),'template',int(glyph.sum()),flush=True)
if __name__=='__main__':main()
