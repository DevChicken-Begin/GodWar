#!/usr/bin/env python3
"""Make review sheets for every keyed frame on light and dark backgrounds."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from import_charnew import A, HEIGHTS
for name in HEIGHTS:
 folder=A/'measured_atlas_pilots'/name; meta=json.loads((folder/'candidate.json').read_text()); out=A/'review'/f'charnew_{name}'; out.mkdir(exist_ok=True); loaded={}
 for start in range(0,len(meta['frames']),24):
  for bg,shade in [('light','#dadada'),('dark','#202020')]:
   sheet=Image.new('RGB',(960,760),shade); draw=ImageDraw.Draw(sheet)
   for slot,f in enumerate(meta['frames'][start:start+24]):
    page=f['atlas']
    if page not in loaded: loaded[page]=Image.open(folder/f'atlas_{page:03d}.png').convert('RGBA')
    x,y,w,h=f['region']; frame=loaded[page].crop((x,y,x+w,y+h)); frame.thumbnail((152,166),Image.Resampling.LANCZOS); sx=slot%6*160;sy=slot//6*190; sheet.paste(frame,(sx+(160-frame.width)//2,sy+20),frame); draw.text((sx+4,sy+3),f'{name} #{start+slot} {f["duration_ms"]}ms',fill='black' if bg=='light' else 'white')
   sheet.save(out/f'{start:03d}_{bg}.jpg',quality=90)
 print(name, len(meta['frames']), 'frames reviewed in sheets',flush=True)
