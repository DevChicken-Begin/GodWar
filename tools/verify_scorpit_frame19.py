#!/usr/bin/env python3
"""Check reconstruction changes only declared watermark pixels and uses local donors."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';out=A/'scorpit_repair_candidates/scorpit';m=json.loads((out/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
base=A/m['base_candidate']/'scorpit';donor=A/m['donor_candidate']/'scorpit'
for folder,key in ((base,'base_atlas_sha256'),(donor,'donor_atlas_sha256')):
 for fn,digest in m[key].items():assert hashlib.sha256((folder/fn).read_bytes()).hexdigest()==digest
with Image.open(src) as gif:
 assert gif.n_frames==m['frame_count']==len(m['frames'])==len(m['changed_per_frame']);gif.seek(0);ref=np.array(gif.convert('RGB'),np.int16);h,w=ref.shape[:2];bg=ref[0,0];yy,xx=np.indices((h,w));roi=(xx>=195)&(yy>=270)&(yy<295);mask=roi&(np.max(np.abs(ref-bg),axis=2)>10);page=-1;before=after=donor_page=None
 for i,f in enumerate(m['frames']):
  gif.seek(i);assert gif.info.get('duration',0)==f['duration_ms']
  if f['atlas']!=page:
   if before is not None:before.close();after.close();donor_page.close()
   page=f['atlas'];fn=f'atlas_{page:03d}.png';before=Image.open(base/fn).convert('RGBA');after=Image.open(out/fn).convert('RGBA');donor_page=Image.open(donor/fn).convert('RGBA')
  x,y,fw,fh=f['region'];box=(x,y,x+fw,y+fh);p=np.array(before.crop(box));q=np.array(after.crop(box));changed=np.any(p!=q,axis=2);assert int(changed.sum())==m['changed_per_frame'][i]
  if i in m['repaired_indices']:
   assert not np.any(changed & ~mask)
   d=np.array(donor_page.crop(box));rr,gg,bb=d[:,:,0],d[:,:,1],d[:,:,2];suspect=roi&(d[:,:,3]>0)&(rr<90)&(gg<125)&(bb<160);_,nearest=distance_transform_edt(mask|suspect,return_indices=True);expected=d[nearest[0],nearest[1]];assert np.array_equal(q[mask],expected[mask])
  else:assert not changed.any()
 if before is not None:before.close();after.close();donor_page.close()
print('PASS: 40 frames; only indices 18/19 changed within text mask using nearest same-frame pixels; reconstructed effect remains an estimate')
