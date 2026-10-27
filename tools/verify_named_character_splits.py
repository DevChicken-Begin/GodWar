#!/usr/bin/env python3
"""Verify every pixel and duration in the three independently packed atlases."""
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]/'Asset/Character'


def main():
    source=next(e for e in json.loads((ROOT/'extracted/catalog.json').read_text())['assets'] if e['id']=='3 char')
    splits=json.loads((ROOT/'extracted/split-catalog.json').read_text())['assets']
    total=0
    for entry in splits:
        for kind in ('extracted','refined_candidates','batch_candidates'):
            originals={}; separate={}
            try:
                for index, item in enumerate(entry['frames']):
                    src=source['frames'][entry['sourceStart']+index]
                    if item['duration_ms']!=src['duration_ms']: raise ValueError('duration mismatch')
                    for pages, name, num in ((originals,'3 char',src['atlas']),(separate,entry['id'],item['atlas'])):
                        if num not in pages: pages[num]=Image.open(ROOT/kind/name/f'atlas_{num:03d}.png')
                    x,y,w,h=src['region']; old=originals[src['atlas']].crop((x,y,x+w,y+h))
                    x,y,w,h=item['region']; new=separate[item['atlas']].crop((x,y,x+w,y+h))
                    if ImageChops.difference(old,new).getbbox(alpha_only=False) is not None: raise ValueError(f'{entry["id"]} {kind} frame {index}')
                    total+=1
            finally:
                for image in list(originals.values())+list(separate.values()): image.close()
        print(f'{entry["id"]}: {entry["frame_count"]} source and candidate frames match')
    print(f'PASS: {total} frame comparisons')

if __name__=='__main__':main()
