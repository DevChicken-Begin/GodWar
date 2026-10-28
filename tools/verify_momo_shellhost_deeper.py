#!/usr/bin/env python3
"""Check evidence, matching rule, alpha edits and resized frames for both passes."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];A=R/'Asset/Character';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cat={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
for variant in ('scene_mask_deep_candidates','scene_mask_deeper_candidates'):
 for name in ('momo','shellhost'):
  out=A/variant/name;m=json.loads((out/'candidate.json').read_text());e=cat[name];base=A/m['base_candidate']/name;assert sha(R/m['source'])==m['source_sha256']==e['source_sha256'];assert m['frames']==e['frames'];w,h=e['size'];refs=[]
  for fn,digest in m['base_atlas_sha256'].items():assert sha(base/fn)==digest
  for ref in m['model_sources']:
   p=R/ref['source'];assert sha(p)==ref['sha256'];arr=[]
   with Image.open(p) as gif:
    for i in ref['sample_indices']:gif.seek(i);arr.append(np.asarray(gif.convert('RGB').resize((w,h),Image.Resampling.BILINEAR)))
   refs.append(np.stack(arr))
  for evidence in m['evidence']:assert sha(R/evidence['path'])==evidence['sha256']
  count=0;page=-1
  with Image.open(R/m['source']) as gif:
   for i,f in enumerate(e['frames']):
    gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
    if page!=f['atlas']:
     page=f['atlas'];before=Image.open(base/f'atlas_{page:03}.png').convert('RGBA');after=Image.open(out/f'atlas_{page:03}.png').convert('RGBA')
    x,y,fw,fh=f['region'];box=(x,y,x+fw,y+fh);a=np.array(before.crop(box));b=np.array(after.crop(box));kept=b[:,:,3]>0;removed=(a[:,:,3]>0)&~kept;assert np.array_equal(a[kept],b[kept]) and np.all(b[~kept]==0);assert int(removed.sum())==m['removed_per_frame'][i];count+=int(removed.sum())
    rgb=a[:,:,:3].astype(np.int16);rr,gg,bb=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];potential=(a[:,:,3]>0)&(rr<=12)&(gg>=35)&(gg<=90)&(bb>=70)&(bb<=155)&(bb-gg>=25)&(bb-gg<=70);yy,xx=np.where(potential);points=rgb[yy,xx];votes=np.zeros(len(yy),np.uint8);exact=np.zeros(len(yy),bool)
    for stack in refs:
     matched=np.zeros(len(yy),bool)
     for im in stack:
      diff=np.max(abs(im[yy,xx].astype(np.int16)-points),axis=1);matched|=diff<=8;exact|=diff<=3
     votes+=matched
    expected=np.zeros((h,w),bool);expected[yy,xx]=(votes>=2) | (exact if variant=='scene_mask_deeper_candidates' else False);assert np.array_equal(expected,removed)
    high=Image.fromarray(b).convert('RGBa').resize((round(w*1.2),round(h*1.2)),Image.Resampling.LANCZOS).convert('RGBA')
    with Image.open(out/f'frame_{i:03}.png') as image:assert ImageChops.difference(high,image.convert('RGBA')).getbbox(alpha_only=False) is None
  print('PASS',variant,name,len(e['frames']),'frames',count,'cleared pixels; visual review pending',flush=True)
