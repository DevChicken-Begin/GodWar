#!/usr/bin/env python3
"""Experimental local nearest-pixel reconstruction beneath Scorpit text."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='scorpit';cat=json.loads((A/'extracted/catalog.json').read_text());e=next(x for x in cat['assets'] if x['id']==n);src=ROOT/e['source'];base=A/'oct28_fix_candidates'/n;donor=A/'batch_candidates'/n;out=A/'scorpit_repair_candidates'/n
if out.exists():raise FileExistsError(out)
assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256']; old=json.loads((base/'candidate.json').read_text());assert old['source_sha256']==e['source_sha256'];counts=[]
with Image.open(src) as gif:
 gif.seek(0);reference=np.array(gif.convert('RGB'),dtype=np.int16);h,w=reference.shape[:2];bg=reference[0,0];yy,xx=np.indices((h,w));mask=(xx>=195)&(yy>=270)&(yy<295)&(np.max(np.abs(reference-bg),axis=2)>10)
 out.mkdir(parents=True);page=-1;source_page=donor_page=atlas=None
 for i,f in enumerate(e['frames']):
  gif.seek(i)
  if f['atlas']!=page:
   if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);source_page.close();donor_page.close()
   page=f['atlas'];source_page=Image.open(base/f'atlas_{page:03d}.png');donor_page=Image.open(donor/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',source_page.size)
  x,y,fw,fh=f['region'];box=(x,y,x+fw,y+fh);p=np.array(source_page.crop(box));orig=p.copy()
  if i in (18,19):
   d=np.array(donor_page.crop(box));rr,gg,bb=d[:,:,0],d[:,:,1],d[:,:,2];roi=(xx>=195)&(yy>=270)&(yy<295); suspect=roi&(d[:,:,3]>0)&(rr<90)&(gg<125)&(bb<160); invalid=mask|suspect
   _,nearest=distance_transform_edt(invalid,return_indices=True);replacement=d[nearest[0],nearest[1]];p[mask]=replacement[mask]
  counts.append(int(np.any(p!=orig,axis=2).sum()));atlas.paste(Image.fromarray(p),(x,y))
 if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);source_page.close();donor_page.close()
meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'oct28_fix_candidates','donor_candidate':'batch_candidates','base_atlas_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(base.glob('atlas_*.png'))},'donor_atlas_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(donor.glob('atlas_*.png'))},'frame_count':e['frame_count'],'frames':e['frames'],'repaired_indices':[18,19],'changed_per_frame':counts,'method':'Nearest pixel outside watermark template and dark watermark-like colors from same source frame, including its alpha; restore only at template locations for indices 18 and 19. Original underlying VFX is not known.','status':'candidate_unreviewed','limitations':'This estimates missing VFX and may introduce shapes/colors, leave text or cause temporal discontinuity; compare both frames and adjacent frames. It is not a recovery of original pixels.'}
(out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('scorpit repaired indices 18,19:',counts[18],counts[19],'pixels')
