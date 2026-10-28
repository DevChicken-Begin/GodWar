#!/usr/bin/env python3
"""Experimental shared-scene model; never treats automated segmentation as final."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'Asset/Character';NAMES=('animent','overight','tigerknight')


def main():
    entries={e['id']:e for e in json.loads((ASSETS/'extracted/catalog.json').read_text())['assets']};samples=[]
    for name in NAMES:
        e=entries[name];path=ROOT/e['source']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=e['source_sha256']:raise ValueError('Source hash changed: '+name)
        with Image.open(path) as gif:
            if gif.size!=(520,520):raise ValueError('Unexpected source size: '+name)
            for i in (0,gif.n_frames//3,2*gif.n_frames//3,gif.n_frames-1):
                gif.seek(i);samples.append(np.array(gif.convert('RGB')))
    reference=np.median(np.stack(samples),axis=0).astype(np.int16)
    for name in NAMES:
        e=entries[name];out=ASSETS/'shared_scene_candidates'/name
        if out.exists():raise ValueError(f'Refusing to overwrite {out}')
        out.mkdir(parents=True);page=-1; atlas=None
        with Image.open(ROOT/e['source']) as gif:
            for i,frame in enumerate(e['frames']):
                gif.seek(i);pixels=np.array(gif.convert('RGBA'));difference=np.max(np.abs(pixels[:,:,:3].astype(np.int16)-reference),axis=2);pixels[difference<=16]=0
                if page!=frame['atlas']:
                    if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
                    page=frame['atlas']
                    with Image.open(ASSETS/'extracted'/name/f'atlas_{page:03d}.png') as img:atlas=Image.new('RGBA',img.size)
                x,y,_,_=frame['region'];atlas.paste(Image.fromarray(pixels),(x,y))
        if atlas is not None:atlas.save(out/f'atlas_{page:03d}.png',compress_level=1)
        metadata={'source':e['source'],'source_sha256':e['source_sha256'],'frame_count':e['frame_count'],'frames':e['frames'],
                  'method':'median of four samples from each surviving same-sized source; RGB max distance >16',
                  'model_sources':[{'id':n,'sha256':entries[n]['source_sha256']} for n in NAMES],
                  'status':'candidate_unreviewed','limitations':'Model may include characters or erase static/dark foreground; background/letter artifacts may remain.'}
        (out/'candidate.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(name,e['frame_count'],'frames; unreviewed',flush=True)
if __name__=='__main__':main()
