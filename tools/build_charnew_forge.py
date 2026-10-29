#!/usr/bin/env python3
"""Build unclassified source-reference clip packages with Sprite Forge."""
import json, subprocess, sys
from PIL import Image
from import_charnew import A, HEIGHTS, write
FORGE='/home/codespace/.codex/skills/generate2dsprite/scripts/build_animation_clips.py'
base=A/'forge_pilots/charnew'; base.mkdir(parents=True,exist_ok=True)
for name in HEIGHTS:
 folder=base/name
 if folder.exists(): raise FileExistsError(folder)
 folder.mkdir(); framefolder=folder/'input_frames'; framefolder.mkdir(); src=A/'measured_atlas_pilots'/name; meta=json.loads((src/'candidate.json').read_text()); pages={}; files=[]
 for i,f in enumerate(meta['frames']):
  page=f['atlas']
  if page not in pages: pages[page]=Image.open(src/f'atlas_{page:03d}.png').convert('RGBA')
  x,y,w,h=f['region']; dest=framefolder/f'frame_{i:03d}.png'; pages[page].crop((x,y,x+w,y+h)).save(dest,compress_level=3);files.append('input_frames/'+dest.name)
 manifest={'schema':'generate2dsprite.animation_clips.v2','frames':files,'anchor_px':meta['anchor_px'],'art_source':'existing','sampling':'nearest','pixel_art':True,'clips':{'reference_unclassified':{'frames':list(range(len(files))),'duration_ms':[f['duration_ms'] for f in meta['frames']],'loop':True}}}
 write(folder/'manifest.json',manifest)
 r=subprocess.run([sys.executable,FORGE,'--manifest',str(folder/'manifest.json'),'--output-dir',str(folder/'clips'),'--no-reviews'],capture_output=True,text=True)
 (folder/'build.log').write_text(r.stdout+r.stderr)
 print(name,'PASS' if r.returncode==0 else 'FAIL',r.stdout[-500:],r.stderr[-500:],flush=True)
