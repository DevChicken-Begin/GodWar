#!/usr/bin/env python3
"""Small reversible unsharp-mask experiment on Dragonmout, alpha unchanged."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';n='dragonmout';e=next(x for x in json.loads((A/'extracted/catalog.json').read_text())['assets'] if x['id']==n);src=ROOT/e['source'];base=A/'batch_candidates'/n;out=A/'sharp_candidates'/n
if out.exists():raise FileExistsError(out)
old=json.loads((base/'candidate.json').read_text());assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256']==old['source_sha256'];out.mkdir(parents=True);page=-1;prior=atlas=None;counts=[]
for i,f in enumerate(e['frames']):
 if page!=f['atlas']:
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
 x,y,w,h=f['region'];p=np.array(prior.crop((x,y,x+w,y+h)).convert('RGBA'));rgb=p[:,:,:3].astype(np.float32);a=p[:,:,3].astype(np.float32)/255
 # Blur premultiplied channels and normalize by blurred alpha so that a
 # transparent backdrop does not become a dark RGB fringe.
 blur_a=np.asarray(Image.fromarray(p[:,:,3]).filter(ImageFilter.GaussianBlur(1)),dtype=np.float32)/255
 normalized=[]
 for c in range(3):
  premult=np.rint(rgb[:,:,c]*a).astype(np.uint8);blur=np.asarray(Image.fromarray(premult).filter(ImageFilter.GaussianBlur(1)),dtype=np.float32);normalized.append(blur/np.maximum(blur_a,1/255))
 soft=np.stack(normalized,axis=2);sharpened=np.clip(np.rint(rgb+.20*(rgb-soft)),0,255).astype(np.uint8);outpixels=p.copy();outpixels[:,:,:3]=sharpened;outpixels[a==0]=0
 counts.append(int(np.any(outpixels!=p,axis=2).sum()));atlas.paste(Image.fromarray(outpixels),(x,y))
if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
meta={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'batch_candidates','frame_count':e['frame_count'],'frames':e['frames'],'changed_per_frame':counts,'art_source':'existing','status':'candidate_unreviewed','method':'20% alpha-normalized unsharp strength, Gaussian radius 1 source pixel; alpha and canvas size unchanged.','limitations':'The 20% is a filter setting, not a measured increase in detail. Can shift colors or add halos/flicker, and cannot restore missing source detail; compare each frame.'}
(out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(n,len(counts),'frames, RGB changed',sum(counts),'alpha unchanged; review required')
