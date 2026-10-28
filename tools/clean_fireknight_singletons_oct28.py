#!/usr/bin/env python3
"""Conservative removal of observed dark-blue specks in Fireknight preview."""
import hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='fireknight';cat=json.loads((A/'extracted/catalog.json').read_text());e=next(x for x in cat['assets'] if x['id']==n);src=ROOT/e['source'];base=A/'detailed_candidates'/n;out=A/'fire_singleton_candidates'/n;sample=A/'review/request-20261028/fireknight.png'
if out.exists():raise FileExistsError(out)
assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256']==json.loads((base/'candidate.json').read_text())['source_sha256'];out.mkdir(parents=True);page=-1;prior=atlas=None;counts=[]
for i,f in enumerate(e['frames']):
 if page!=f['atlas']:
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
 x,y,w,h=f['region'];p=np.array(prior.crop((x,y,x+w,y+h)).convert('RGBA'));rgb=p[:,:,:3];r,g,b=(rgb[:,:,i].astype(np.int16) for i in range(3));visible=p[:,:,3]>0;target=visible&np.all(rgb==[0,52,115],axis=2)
 # Protect dark neutral material near the character's body; particles are still
 # ambiguous if effects use the same color, so this remains a candidate.
 body=visible&(np.maximum.reduce((r,g,b))<110)&(r>=15)&(np.abs(r-g)<45)&(~target)
 components,labels,stats,_=cv2.connectedComponentsWithStats(target.astype('uint8'),8); sizes=stats[:,cv2.CC_STAT_AREA]; mask=target&(sizes[labels]==1); counts.append(int(mask.sum()));p[mask]=0;atlas.paste(Image.fromarray(p),(x,y))
if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'detailed_candidates','frame_count':e['frame_count'],'frames':e['frames'],'removed_per_frame':counts,'sample':str(sample.relative_to(ROOT)),'sample_sha256':hashlib.sha256(sample.read_bytes()).hexdigest(),'method':'Clear single isolated exact RGB (0,52,115) pixels; retain connected clusters of that color. See source-colored samples and reference screenshot.','status':'candidate_unreviewed','limitations':'Isolated blue can also be legitimate detail; visually inspect all animation frames and VFX. Other colored background can remain.'}
(out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('fireknight',len(counts),'frames; removed',sum(counts),'frame 53',counts[53])
