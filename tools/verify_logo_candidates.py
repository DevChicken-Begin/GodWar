#!/usr/bin/env python3
"""Validate fixed logo removal and preserve all other prior pixels."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';total=0
for n in ('airpot','wavinges'):
 folder=A/'logo_candidates'/n;m=json.loads((folder/'candidate.json').read_text());src=ROOT/m['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256'];
 with Image.open(src) as gif:
  gif.seek(0);ref=np.array(gif.convert('RGB'),np.int16);h,w=ref.shape[:2];yy,xx=np.indices((h,w));roi=(xx>=w-110)&(yy>=h-45);glyph=roi&(np.max(np.abs(ref-ref[0,0]),axis=2)>5);assert gif.n_frames==m['frame_count']==len(m['frames']);page=-1;base=out=None
  for i,f in enumerate(m['frames']):
   gif.seek(i);orig=np.array(gif.convert('RGBA'));assert gif.info.get('duration',0)==f['duration_ms'];assert not np.any(glyph&(np.max(np.abs(orig[:,:,:3].astype(np.int16)-ref),axis=2)>12))
   if page!=f['atlas']:
    if base is not None:base.close();out.close()
    page=f['atlas'];fn=f'atlas_{page:03d}.png';base=Image.open(A/m['base_candidate']/n/fn).convert('RGBA');out=Image.open(folder/fn).convert('RGBA')
   x,y,fw,fh=f['region'];box=x,y,x+fw,y+fh;before=np.array(base.crop(box));after=np.array(out.crop(box));removed=glyph&(before[:,:,3]>0);assert int(removed.sum())==m['removed_per_frame'][i];assert np.all(after[removed]==0) and np.array_equal(after[~removed],before[~removed]);assert not np.any(after[roi,3]);total+=1
  if base is not None:base.close();out.close()
 print(n,m['frame_count'],'frames; logo area alpha zero')
print('PASS',total,'frames; pixel and region checks, visual review remains required')
