#!/usr/bin/env python3
"""Verify persisted fine candidates, source hashes, frame timings and palette."""
import hashlib,json,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
from build_fine_batch import scale2
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';BUILD=ROOT/'docs/fine-batch/build.json';REPORT=ROOT/'docs/fine-batch/verification.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 build=json.loads(BUILD.read_text());report={'version':1,'method':'Validate input hashes, exact per-frame grid, RGBA palette, timings, logical frames and reconstructed preview atlas; does not approve aesthetics or VFX.','results':[]};total=0
 for item in build['results']:
  if item['status']!='created_unreviewed':continue
  n=item['id'];out=A/'fine_candidates'/n;m=json.loads((out/'candidate.json').read_text());src=ROOT/m['source'];base=A/m['base_candidate']/n;logical=A/'review'/n/'fine_frames';assert sha(src)==m['source_sha256'],n
  for fn,digest in m['base_atlas_sha256'].items():assert sha(base/fn)==digest,(n,fn)
  count=0
  with Image.open(src) as gif:
   assert len(m['frames'])==m['frame_count']==len(m['changed_subpixels_per_frame']);page=-1;prior=atlas=None
   for i,f in enumerate(m['frames']):
    gif.seek(i+m['source_start']);assert gif.info.get('duration',0)==f['duration_ms'],(n,i,'duration')
    if f['atlas']!=page:
     if prior is not None:prior.close();atlas.close()
     page=f['atlas'];fn=f'atlas_{page:03d}.png';prior=Image.open(base/fn).convert('RGBA');atlas=Image.open(out/fn).convert('RGBA');assert prior.size==atlas.size
    x,y,w,h=f['region'];box=x,y,x+w,y+h;p=np.array(prior.crop(box));k=m['grid_period'];cells=p.reshape(h//k,k,w//k,k,4);small=cells[:,0,:,0,:];assert np.all(cells==small[:,None,:,None,:]),(n,i,'grid')
    with Image.open(logical/f'frame_{i:03d}.png') as q:
     q=q.convert('RGBA');assert list(q.size)==m['refined_canvas'];v=np.array(q);_,computed=scale2(p,k);assert np.array_equal(v,computed),(n,i,'scale2x');colors=np.unique(np.ascontiguousarray(small).view(np.uint32));used=np.unique(np.ascontiguousarray(v).view(np.uint32));assert np.all(np.isin(used,colors)),(n,i,'palette');plain=np.repeat(np.repeat(small,2,axis=0),2,axis=1);assert int(np.any(v!=plain,axis=2).sum())==m['changed_subpixels_per_frame'][i];expected=q.resize((w,h),Image.Resampling.NEAREST)
    assert ImageChops.difference(atlas.crop(box),expected).getbbox(alpha_only=False) is None,(n,i,'atlas');count+=1
   if prior is not None:prior.close();atlas.close()
  total+=count;report['results'].append({'id':n,'frames':count,'pixel_check':'passed','visual_review':'pending'});print(n,count,'frames OK',flush=True)
  tmp=REPORT.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,REPORT)
 print('PASS',len(report['results']),'candidates',total,'frames; aesthetic review remains pending',flush=True)
if __name__=='__main__':main()
