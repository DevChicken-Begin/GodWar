#!/usr/bin/env python3
"""Verify exact patch rules, source timing, scaling, atlas and previews."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np,cv2
R=Path(__file__).resolve().parents[1];A=R/'Asset/Character';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cat={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
for n in ('momo','shellhost'):
 e=cat[n];out=A/'scene_spot_candidates'/n;m=json.loads((out/'candidate.json').read_text());base=A/m['base_candidate']/n;assert sha(R/e['source'])==e['source_sha256']==m['source_sha256'];assert len(m['frames'])==e['frame_count'];w,h=e['size'];size=tuple(m['display_size']);assert size==((440,440) if n=='momo' else (520,520)); assert m['anchor_source']==[w/2,h] and m['anchor_display']==[size[0]/2,size[1]]
 for fn,d in m['base_atlas_sha256'].items():assert sha(base/fn)==d
 imgs=[]
 for f in e['frames']:
  x,y,fw,fh=f['region']
  with Image.open(base/f'atlas_{f["atlas"]:03}.png') as page:imgs.append(np.array(page.convert('RGBA').crop((x,y,x+fw,y+fh))))
 boxes=m['template_boxes'];templates=[imgs[0][y1:y2,x1:x2] for x1,y1,x2,y2 in boxes];raw=[]
 with Image.open(R/e['source']) as gif:
  for i in range(gif.n_frames):gif.seek(i);raw.append(np.array(gif.convert('RGB'),np.int16))
  raw=np.stack(raw)
  for i,(source,f,prior) in enumerate(zip(e['frames'],m['frames'],imgs)):
   gif.seek(i);assert gif.info.get('duration',0)==source['duration_ms']==f['duration_ms'];removed=np.zeros((h,w),bool)
   if n=='momo':
    matches=[]
    for k,(x1,y1,x2,y2) in enumerate(boxes):
     area=prior[y1:y2,x1:x2];same=np.array_equal(area,templates[k]);matches.append(same)
     if same:removed[y1:y2,x1:x2]=area[:,:,3]>0
    assert matches==m['template_matches'][i]
   elif i in m['shell_indices_zero_based']:
    rgb=prior[:,:,:3].astype(np.int16);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];blue=(prior[:,:,3]>0)&(r<=12)&(g>=35)&(g<=90)&(b>=70)&(b<=155)&(b-g>=25)&(b-g<=70);freq=(np.max(abs(raw-rgb[None,:,:,:]),axis=3)<=4).sum(axis=0);other=(prior[:,:,3]>0)&~blue;protect=cv2.dilate(other.astype(np.uint8),np.ones((3,3),np.uint8),iterations=1).astype(bool);removed=blue&(freq>=5)&~protect
   assert int(removed.sum())==m['removed_per_frame'][i];processed=prior.copy();processed[removed]=0;im=Image.fromarray(processed)
   if n=='momo':im=im.resize(size,Image.Resampling.NEAREST)
   x,y,fw,fh=f['region'];assert (fw,fh)==size
   with Image.open(out/f'atlas_{f["atlas"]:03}.png') as atlas: assert ImageChops.difference(im,atlas.convert('RGBA').crop((x,y,x+fw,y+fh))).getbbox(alpha_only=False) is None
   expect=im.convert('RGBa').resize((round(size[0]*1.2),round(size[1]*1.2)),Image.Resampling.LANCZOS).convert('RGBA')
   with Image.open(out/f'frame_{i:03}.png') as preview:assert ImageChops.difference(expect,preview.convert('RGBA')).getbbox(alpha_only=False) is None
 print('PASS',n,len(m['frames']),'frames, size',size,'removed',sum(m['removed_per_frame']),'frame 37',m['removed_per_frame'][36],flush=True)
