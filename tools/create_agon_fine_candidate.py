#!/usr/bin/env python3
"""Create a non-destructive edge-refined Agon preview on its verified 5px grid."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';name='agon';e=next(x for x in json.loads((A/'extracted/catalog.json').read_text())['assets'] if x['id']==name);src=ROOT/e['source'];base=A/'batch_candidates'/name;out=A/'fine_candidates'/name;logical=A/'review/agon/fine_frames'
if out.exists() or logical.exists():raise FileExistsError('candidate exists')
assert hashlib.sha256(src.read_bytes()).hexdigest()==e['source_sha256'];meta=json.loads((base/'candidate.json').read_text());assert meta['source_sha256']==e['source_sha256'];out.mkdir(parents=True);logical.mkdir(parents=True);page=-1;prior=atlas=None;counts=[]
for i,f in enumerate(e['frames']):
 if f['atlas']!=page:
  if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
  page=f['atlas'];prior=Image.open(base/f'atlas_{page:03d}.png');atlas=Image.new('RGBA',prior.size)
 x,y,w,h=f['region'];p=np.array(prior.crop((x,y,x+w,y+h)).convert('RGBA'));assert w%5==0 and h%5==0
 cells=p.reshape(h//5,5,w//5,5,4);small=cells[:,0,:,0,:];assert np.all(cells==small[:,None,:,None,:]),f'nonuniform 5x5 block at frame {i}'
 pad=np.pad(small,((1,1),(1,1),(0,0)),mode='edge');b=pad[:-2,1:-1];d=pad[1:-1,:-2];fwd=pad[1:-1,2:];hdown=pad[2:,1:-1]
 eq=lambda a,b:np.all(a==b,axis=2)
 active=(~eq(b,hdown))&(~eq(d,fwd));q=np.repeat(np.repeat(small,2,axis=0),2,axis=1)
 for dx,dy,cond,repl in [(0,0,eq(d,b),d),(1,0,eq(b,fwd),fwd),(0,1,eq(d,hdown),d),(1,1,eq(hdown,fwd),fwd)]:
  tile=q[dy::2,dx::2];mask=active&cond;tile[mask]=repl[mask]
 counts.append(int(np.any(q!=np.repeat(np.repeat(small,2,axis=0),2,axis=1),axis=2).sum()));Image.fromarray(q).save(logical/f'frame_{i:03d}.png')
 scaled=Image.fromarray(q).resize((w,h),Image.Resampling.NEAREST);atlas.paste(scaled,(x,y))
if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1);prior.close()
result={'source':e['source'],'source_sha256':e['source_sha256'],'base_candidate':'batch_candidates','art_source':'existing','frame_count':e['frame_count'],'frames':e['frames'],'grid_period':5,'logical_canvas':[95,80],'refined_canvas':[190,160],'viewer_canvas':[475,400],'changed_subpixels_per_frame':counts,'status':'candidate_unreviewed','method':'Exact uniform 5x5 source cells; Scale2x edge rules with the same RGBA colors; nearest resize to fixed original canvas for viewer.','limitations':'Edge interpolation does not recover missing details; may alter silhouettes, hair, fine VFX, or cause flicker; nearest display resize is non-integer. Compare every frame to source.'}
(out/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('agon',len(counts),'frames, verified uniform grid; changed logical subpixels',sum(counts),'review required')
