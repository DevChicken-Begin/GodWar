#!/usr/bin/env python3
"""Check imported sources, source timing, uncut pixels and current height profiles."""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from import_charnew import A, ROOT, SOURCE, HEIGHTS, digest
from import_oct29_gifs import background, key
cat={x['id']:x for x in json.loads((A/'extracted/catalog.json').read_text())['assets']}
targets={x['id']:x for x in json.loads((A/'characters/height-targets.json').read_text())['assets']}
total=0
for name,height in HEIGHTS.items():
 entry=cat[name]; target=targets[name]; folder=A/'measured_atlas_pilots'/name; meta=json.loads((folder/'candidate.json').read_text()); source=SOURCE/(name+'.gif')
 assert digest(source)==digest(ROOT/entry['source'])==entry['source_sha256']==target['source_sha256']==meta['source_sha256']
 assert target['target_height_px']==meta['target_height_px']==height and math.isclose(meta['display_scale']*meta['reference_height_px'],height,rel_tol=1e-10)
 assert meta['size_target_approval']=='user_updated_round4'; assert len(meta['frames'])==entry['frame_count']
 rawpage=cleanpage=None; rawindex=cleanindex=None
 with Image.open(source) as gif:
  assert gif.n_frames==len(meta['frames'])
  for i,(r,f) in enumerate(zip(entry['frames'],meta['frames'])):
   gif.seek(i); original=gif.convert('RGBA'); assert r['duration_ms']==f['duration_ms']==gif.info.get('duration',0)
   if rawindex!=r['atlas']:
    if rawpage: rawpage.close()
    rawindex=r['atlas']; rawpage=Image.open(A/'extracted'/name/f'atlas_{rawindex:03d}.png')
   x,y,w,h=r['region']; decoded=rawpage.crop((x,y,x+w,y+h)).convert('RGBA'); assert decoded.tobytes()==original.tobytes(),(name,i,'raw')
   if cleanindex!=f['atlas']:
    if cleanpage: cleanpage.close()
    cleanindex=f['atlas']; cleanpage=Image.open(folder/f'atlas_{cleanindex:03d}.png')
   x,y,w,h=f['region']; actual=cleanpage.crop((x,y,x+w,y+h)).convert('RGBA')
   if name=='Trainxoan':
    arr=np.array(original); bg=background(original); mask=np.max(np.abs(arr[:,:,:3].astype(np.int16)-bg.astype(np.int16)),axis=2)<=8; arr[mask]=0; expected=Image.fromarray(arr)
   else: expected,_=key(original,background(original))
   if name=='Hatomin':
    expected=expected.convert('RGBa').resize((576,576),Image.Resampling.LANCZOS).convert('RGBA'); alpha=expected.getchannel('A'); expected=expected.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1,percent=18,threshold=3)); expected.putalpha(alpha)
   assert actual.tobytes()==expected.tobytes(),(name,i,'processed')
  rawpage.close(); cleanpage.close()
 total+=len(meta['frames']);print('PASS',name,len(meta['frames']),'frames',height,'px',flush=True)
assert digest(A/'vfx/scorpit.gif')==json.loads((A/'archive/scorpit_before_charnew/original-catalog-entry.json').read_text())['source_sha256']
print('PASS',len(HEIGHTS),'sources',total,'frames; Scorpit old source retained')
