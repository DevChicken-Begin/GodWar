#!/usr/bin/env python3
"""Make a higher-detail Aonoma experiment, finer source sampling with the same preview size."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character';src=A/'vfx/aonoma.gif';out=A/'review/aonoma/pixel_input_220';entry=json.loads((A/'review/aonoma/extraction-entry.json').read_text())
if hashlib.sha256(src.read_bytes()).hexdigest()!=entry['source_sha256']:raise ValueError('source hash differs')
if out.exists():raise FileExistsError(out)
out.mkdir(parents=True)
with Image.open(src) as gif:
 for i in range(gif.n_frames):
  gif.seek(i);rgba=np.array(gif.convert('RGBA'),dtype=np.float32);rgb=rgba[:,:,:3]; bg=242.0
  alpha=np.clip((bg-np.min(rgb,axis=2))/bg,0,1);alpha=np.where(alpha<.025,0,alpha);safe=np.maximum(alpha,1e-5)
  unmatted=np.clip((rgb-bg*(1-alpha[:,:,None]))/safe[:,:,None],0,255);p=np.zeros((*alpha.shape,4),np.uint8)
  p[:,:,:3]=np.rint(unmatted).astype(np.uint8);p[:,:,3]=np.rint(alpha*255).astype(np.uint8);p[alpha==0]=0
  Image.fromarray(p).resize((198,158),Image.Resampling.BOX).save(out/f'frame_{i:03d}.png')
print('prepared',gif.n_frames,'frames, 198x158 logical frames, same display size')
