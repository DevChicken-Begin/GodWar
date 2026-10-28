#!/usr/bin/env python3
"""Prepare fixed-grid, non-destructive PNG frames from the supplied aonoma GIF."""
import hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; SOURCE=ROOT/'aonoma.gif'; COPY=A/'vfx/aonoma.gif'; OUT=A/'review/aonoma/pixel_input'; GRID=3
sys.path.insert(0,str(ROOT/'tools'))
from extract_gif_assets import extract

def main():
 if COPY.exists() or OUT.exists() or (A/'extracted/aonoma').exists():raise FileExistsError('aonoma output exists; refusing to overwrite')
 if not SOURCE.is_file():raise FileNotFoundError(SOURCE)
 with open(SOURCE,'rb') as src,open(COPY,'xb') as dst:shutil.copyfileobj(src,dst)
 entry=extract(COPY,A/'extracted')
 if entry['source_sha256']!=hashlib.sha256(SOURCE.read_bytes()).hexdigest():raise ValueError('copy hash differs')
 out=OUT;out.mkdir(parents=True)
 with Image.open(COPY) as gif:
  w,h=gif.size; pw=((w+GRID-1)//GRID)*GRID;ph=((h+GRID-1)//GRID)*GRID
  for i in range(gif.n_frames):
   gif.seek(i);rgba=np.array(gif.convert('RGBA'),dtype=np.float32);rgb=rgba[:,:,:3]; bg=242.0
   # White-matte estimate: maximum channel deficit gives a conservative alpha.
   # This cannot reconstruct pale foreground accurately; review is mandatory.
   a=np.clip((bg-np.min(rgb,axis=2))/bg,0,1)
   a=np.where(a < .025,0,a); safe=np.maximum(a,1e-5)
   unmatte=np.clip((rgb-bg*(1-a[:,:,None]))/safe[:,:,None],0,255)
   image=np.zeros((h,w,4),np.uint8);image[:,:,:3]=np.rint(unmatte).astype(np.uint8);image[:,:,3]=np.rint(a*255).astype(np.uint8);image[a==0]=0
   padded=Image.new('RGBA',(pw,ph));padded.paste(Image.fromarray(image),(0,0));small=padded.resize((pw//GRID,ph//GRID),Image.Resampling.BOX)
   small.save(out/f'frame_{i:03d}.png')
 (A/'review/aonoma/extraction-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
 print('prepared',gif.n_frames,'frames','source',w,h,'logical canvas',pw//GRID,ph//GRID,'sha256',entry['source_sha256'])
if __name__=='__main__':main()
