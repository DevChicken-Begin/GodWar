#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageFilter
R=Path(__file__).resolve().parents[1];A=R/'Asset/Character';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cat={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
def read_frame(folder,f):
 x,y,w,h=f['region']
 with Image.open(folder/f'atlas_{f["atlas"]:03}.png') as page:return page.convert('RGBA').crop((x,y,x+w,y+h))
for name in ('momo','shellhost'):
 out=A/'revision_candidates'/name;m=json.loads((out/'candidate.json').read_text());e=cat[name];base=A/m['base_candidate']/name;old=json.loads((base/'candidate.json').read_text());assert sha(R/e['source'])==m['source_sha256']==e['source_sha256'];assert sha(base/'candidate.json')==m['base_metadata_sha256'];assert m['frame_count']==len(m['frames'])==e['frame_count'];assert m['loop']==old['loop']
 for f,d in m['base_atlas_sha256'].items():assert sha(base/f)==d
 for f,d in m['base_detail_sha256'].items():assert sha(base/f)==d
 if name=='momo':
  assert m['previous_display_size']==[440,440] and m['display_size']==[506,506] and m['previous_frame_detail_size']==[528,528] and m['frame_size']==[729,729] and m['edge_blend']==0.1
 else:
  box=m['speck_box'];template=np.array(read_frame(base,old['frames'][m['template_source_frame_zero_based']]).crop(tuple(box)));assert np.count_nonzero(template[:,:,3])==20
 for i,(f,oldf) in enumerate(zip(m['frames'],old['frames'])):
  assert f['duration_ms']==oldf['duration_ms'] and f['source_index']==oldf['source_index'];actual=read_frame(out,f)
  if name=='momo':
   with Image.open(base/f'frame_{i:03}.png') as image:
    res=image.convert('RGBa').resize(tuple(m['frame_size']),Image.Resampling.LANCZOS);expected=Image.blend(res,res.filter(ImageFilter.GaussianBlur(m['edge_blur_radius'])),m['edge_blend']).convert('RGBA')
  else:
   a=np.array(read_frame(base,oldf));x0,y0,x1,y1=box;match=np.array_equal(a[y0:y1,x0:x1],template);assert m['template_matches'][i]==match;mask=np.zeros(a.shape[:2],bool)
   if match:mask[y0:y1,x0:x1]=a[y0:y1,x0:x1,3]>0
   assert int(mask.sum())==m['removed_per_frame'][i];a[mask]=0;expected=Image.fromarray(a)
  assert ImageChops.difference(actual,expected).getbbox(alpha_only=False) is None
  preview=actual if name=='momo' else actual.convert('RGBa').resize((624,624),Image.Resampling.LANCZOS).convert('RGBA')
  with Image.open(out/f'frame_{i:03}.png') as im:assert ImageChops.difference(preview,im.convert('RGBA')).getbbox(alpha_only=False) is None
 if name=='shellhost':assert m['removed_per_frame'][35]==20
 print('PASS',name,len(m['frames']),'frames; display',m['display_size'],'raster',m['frame_size'],'pixels removed',sum(m['removed_per_frame']),flush=True)
