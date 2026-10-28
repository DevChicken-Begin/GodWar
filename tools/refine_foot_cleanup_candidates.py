#!/usr/bin/env python3
"""Conservative second cleanup pass; retains every previous candidate."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
NAMES = ('mainthen', 'animent', 'overight', 'skypit')
REFERENCES = {'animent': 'overight', 'overight': 'animent', 'skypit': 'animent'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(entry, entries):
    name = entry['id']; source = ROOT / entry['source']; out = A / 'foot_candidates' / name
    if digest(source) != entry['source_sha256']: raise ValueError('source hash mismatch')
    if out.exists(): raise FileExistsError(out)
    base = A / 'detailed_candidates' / name
    base_meta = json.loads((base / 'candidate.json').read_text())
    if base_meta['source_sha256'] != entry['source_sha256']: raise ValueError('base hash mismatch')
    with Image.open(source) as gif:
        w, h = gif.size
        gif.seek(0); ref = np.array(gif.convert('RGB'), dtype=np.int16)
        stable = np.zeros((h, w), dtype=np.uint16)
        for i in range(gif.n_frames):
            gif.seek(i); rgb = np.array(gif.convert('RGB'), dtype=np.int16)
            stable += (np.max(np.abs(rgb-ref), axis=2) <= 8)
        if name == 'mainthen':
            region = np.zeros((h,w), bool); region[200:204, 120:121] = True
            mask = region & (stable >= int(gif.n_frames*.8))
            provenance = []
        else:
            other = entries[REFERENCES[name]]; other_path = ROOT / other['source']
            if digest(other_path) != other['source_sha256']: raise ValueError('reference hash mismatch')
            similarity = np.full((h,w), 255, dtype=np.int16)
            with Image.open(other_path) as bg:
                for i in sorted(set((0,bg.n_frames//3,2*bg.n_frames//3,bg.n_frames-1))):
                    bg.seek(i); sample=bg.convert('RGB').resize((w,h),Image.Resampling.BILINEAR)
                    similarity=np.minimum(similarity,np.max(np.abs(np.array(sample,dtype=np.int16)-ref),axis=2))
            dark_blue = (ref[:,:,0] <= 18) & (ref[:,:,1] <= 90) & (ref[:,:,2] <= 150) & (ref[:,:,2] > ref[:,:,1])
            region = np.zeros((h,w), bool); region[int(h*.70):,:] = True
            mask = region & dark_blue & (stable >= int(gif.n_frames*.8)) & (similarity <= 10)
            provenance = [{'source': other['source'], 'sha256': other['source_sha256']}]
        out.mkdir(parents=True); page_no = -1; page = prior_page = None; counts=[]
        for i, info in enumerate(entry['frames']):
            gif.seek(i); rgb=np.array(gif.convert('RGB'),dtype=np.int16)
            if info['atlas'] != page_no:
                if page is not None: page.save(out/f'atlas_{page_no:03d}.png',compress_level=1); prior_page.close()
                page_no=info['atlas']; prior_page=Image.open(base/f'atlas_{page_no:03d}.png'); page=Image.new('RGBA',prior_page.size)
            x,y,fw,fh=info['region']; pixels=np.array(prior_page.crop((x,y,x+fw,y+fh)))
            remove=mask & (np.max(np.abs(rgb-ref),axis=2)<=8) & (pixels[:,:,3]>0)
            counts.append(int(remove.sum())); pixels[remove]=0
            page.paste(Image.fromarray(pixels),(x,y))
        if page is not None: page.save(out/f'atlas_{page_no:03d}.png',compress_level=1);prior_page.close()
    meta={'source':entry['source'],'source_sha256':entry['source_sha256'],'base_candidate':'detailed_candidates',
          'reference_sources':provenance,'frame_count':entry['frame_count'],'frames':entry['frames'],
          'removed_per_frame':counts,'status':'candidate_unreviewed',
          'method':'mainthen: exact four-pixel static spot at (120,200..203); others: stable dark-blue pixels below 70% canvas, matching a surviving independent scene source within RGB max 10, only where current source matches its first frame within 8.',
          'limitations':'Previous candidate already removed pixels; matching background can also remove stationary foreground or VFX. Visually review all frames, especially feet and blue outlines.'}
    (out/'candidate.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(name, 'frames',len(counts),'removed',sum(counts),'frame31',counts[31] if len(counts)>31 else 'n/a',flush=True)


def main():
    entries={e['id']:e for e in json.loads((A/'extracted/catalog.json').read_text())['assets']}
    if any((A/'foot_candidates'/n).exists() for n in NAMES): raise FileExistsError('destination already exists')
    for n in NAMES: create(entries[n],entries)
if __name__ == '__main__': main()
