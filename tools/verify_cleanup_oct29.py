#!/usr/bin/env python3
"""Verify the installed cleanup against recorded inputs, without regenerating them."""
import hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['buffao','moxie','moxie_repaired']:
 dest=A/'measured_atlas_pilots'/name;m=json.loads((dest/'candidate.json').read_text());c=m['cleanup_oct29'];src=ROOT/c['input'];old=json.loads((src/'candidate.json').read_text());assert sha(ROOT/m['source'])==m['source_sha256'];assert len(m['frames'])==len(old['frames']);assert [f['duration_ms'] for f in m['frames']]==[f['duration_ms'] for f in old['frames']];assert c['input_atlas_sha256']=={p.name:sha(p) for p in sorted(src.glob('atlas_*.png'))}; originals={};outputs={};total=0
 for i,(f,g) in enumerate(zip(old['frames'],m['frames'])):
  p=f['atlas'];x,y,w,h=f['region'];newp=g['atlas'];nx,ny,nw,nh=g['region'];assert nw>=w and nh==h
  if p not in originals:originals[p]=np.array(Image.open(src/f'atlas_{p:03d}.png').convert('RGBA'))
  if newp not in outputs:outputs[newp]=np.array(Image.open(dest/f'atlas_{newp:03d}.png').convert('RGBA'))
  a=originals[p][y:y+h,x:x+w];b=outputs[newp][ny:ny+h,nx:nx+w];rgb=a[:,:,:3].astype(np.int16);visible=a[:,:,3]>0
  if name in ('buffao',):
   mask=np.zeros((h,w),bool)
   for color in c['sample_rgb']:mask|=np.max(np.abs(rgb-np.array(color)),axis=2)<=c['tolerance_per_channel']
   mask &= visible;_,labels,_,_=cv2.connectedComponentsWithStats(mask.astype('uint8'),8);edge=cv2.dilate((~visible).astype('uint8'),np.ones((3,3),np.uint8))>0;mask &= np.isin(labels,np.unique(labels[mask&edge]))
  else:mask=visible & np.all(rgb==0,axis=2) & (np.arange(h)[:,None]>=162)
  assert int(mask.sum())==c['removed_per_frame'][i];assert np.all(b[mask]==0)
  unchanged=~mask
  if i in m.get('beam_reconstruction_oct29',{}).get('frame_indices_zero_based',[]): unchanged[:,300:]=False
  assert np.array_equal(a[unchanged],b[unchanged]);total+=int(mask.sum())
 print(name,len(m['frames']),'frames checked, pixels removed',total)
