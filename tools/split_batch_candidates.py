#!/usr/bin/env python3
"""Repack the 3-char batch candidate into independent named character atlases."""
import json
import math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'Asset/Character'

def main():
    src=next(e for e in json.loads((ROOT/'extracted/catalog.json').read_text())['assets'] if e['id']=='3 char')
    entries=json.loads((ROOT/'extracted/split-catalog.json').read_text())['assets']; meta=json.loads((ROOT/'batch_candidates/3 char/candidate.json').read_text())
    for entry in entries:
        dest=ROOT/'batch_candidates'/entry['id']
        if dest.exists(): raise ValueError(f'Refusing to overwrite: {dest}')
        dest.mkdir(parents=True); pages={}; atlas=None; number=-1
        try:
            for i,item in enumerate(entry['frames']):
                if number!=item['atlas']:
                    if atlas is not None:atlas.save(dest/f'atlas_{number:03d}.png',compress_level=1)
                    number=item['atlas'];n=min(entry['frame_count']-i,36);w,h=entry['size'];atlas=Image.new('RGBA',(min(6,n)*w, math.ceil(n/6)*h))
                old=src['frames'][entry['sourceStart']+i];n=old['atlas']
                if n not in pages:pages[n]=Image.open(ROOT/'batch_candidates/3 char'/f'atlas_{n:03d}.png')
                x,y,w,h=old['region'];img=pages[n].crop((x,y,x+w,y+h));x,y,_,_=item['region'];atlas.paste(img,(x,y))
            if atlas is not None:atlas.save(dest/f'atlas_{number:03d}.png',compress_level=1)
        finally:
            for page in pages.values():page.close()
        derived={k:v for k,v in meta.items() if k!='removed_pixels'}
        derived.update({'id':entry['id'],'frame_count':entry['frame_count'],'frames':entry['frames'], 'derived_from':'3 char'})
        (dest/'candidate.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(entry['id'],entry['frame_count'])

if __name__=='__main__':main()
