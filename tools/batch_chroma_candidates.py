#!/usr/bin/env python3
"""Generate conservative, review-only chroma candidates for audited flat-edge GIFs."""
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'Asset/Character'
TOLERANCE=5


def run(entry, audited):
    dest=ASSETS/'batch_candidates'/entry['id']
    if dest.exists():
        meta=dest/'candidate.json'
        if not meta.is_file(): return {'id':entry['id'],'result':'incomplete_existing'}
        prior=json.loads(meta.read_text(encoding='utf-8'))
        return {'id':entry['id'],'result':'already_exists' if prior.get('source_sha256')==entry['source_sha256'] else 'existing_hash_mismatch'}
    source=ROOT/entry['source']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['source_sha256']: raise ValueError(f'Source changed: {source}')
    rgb=np.array(audited['corners_rgba'][:3],dtype=np.int16)
    parent=dest.parent;parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='.building-',dir=parent)); page_number=-1;atlas=None;removed=0
    try:
        with Image.open(source) as gif:
            w,h=gif.size
            for i,frame in enumerate(entry['frames']):
                gif.seek(i); pixels=np.array(gif.convert('RGBA'))
                border=np.concatenate((pixels[0,:,:],pixels[-1,:,:],pixels[:,0,:],pixels[:,-1,:]),axis=0)
                border_distance=np.max(np.abs(border[:,:3].astype(np.int16)-rgb),axis=1)
                if np.mean(border_distance<=TOLERANCE)<.8 and entry['id'] not in ('firemen','powerdame'):
                    raise ValueError(f'Insufficient matching border: {source}, frame {i}')
                if frame['atlas']!=page_number:
                    if atlas is not None: atlas.save(work/f'atlas_{page_number:03d}.png',compress_level=1)
                    page_number=frame['atlas']
                    with Image.open(ASSETS/'extracted'/entry['id']/f'atlas_{page_number:03d}.png') as original:
                        atlas=Image.new('RGBA',original.size)
                distance=np.max(np.abs(pixels[:,:,:3].astype(np.int16)-rgb),axis=2)
                mask=(pixels[:,:,3]==255)&(distance<=TOLERANCE)
                removed+=int(mask.sum());pixels[mask]=0
                x,y,_,_=frame['region'];atlas.paste(Image.fromarray(pixels),(x,y))
            if atlas is not None:atlas.save(work/f'atlas_{page_number:03d}.png',compress_level=1)
        metadata={'id':entry['id'],'source':entry['source'],'source_sha256':entry['source_sha256'],
                  'frame_count':entry['frame_count'],'frames':entry['frames'],'background_rgba':audited['corners_rgba'],
                  'method':f'global RGB chroma key, maximum per-channel difference {TOLERANCE}',
                  'removed_pixels':removed,'status':'candidate_unreviewed',
                  'limitations':'Matching or near-background character/VFX pixels may be removed; near-background halos and fixed logos may remain. firemen and powerdame include frames whose effects cover the border; dragonmout contains pre-existing transparency. Requires visual review of every frame.'}
        (work/'candidate.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.replace(work,dest)
        return {'id':entry['id'],'result':'created','frames':entry['frame_count'],'removed_pixels':removed}
    except Exception:
        shutil.rmtree(work,ignore_errors=True)
        raise


def main():
    catalog=json.loads((ASSETS/'extracted/catalog.json').read_text(encoding='utf-8'))['assets']
    audits={e['id']:e for e in json.loads((ASSETS/'review/corner-audit.json').read_text(encoding='utf-8'))['sources']}
    coverage={e['id']:e for e in json.loads((ASSETS/'review/border-coverage.json').read_text(encoding='utf-8'))['sources']}
    selected=[]
    for e in catalog:
        a=audits[e['id']];b=coverage[e['id']]
        if (b['mean']>=.95 and b['min']>=.8 and a['corners_rgba'][3]==255 and not b['transparent_frames']) or e['id'] in ('dragonmout','firemen','powerdame'):
            selected.append((e,a))
    results=[]
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures={executor.submit(run,*item):item[0]['id'] for item in selected}
        for future in as_completed(futures):
            name=futures[future]
            try: result=future.result()
            except Exception as ex: result={'id':name,'result':'error','error':str(ex)}
            results.append(result);print(f'{len(results)}/{len(selected)} {name}: {result["result"]}',flush=True)
    results.sort(key=lambda x:x['id'].lower())
    (ASSETS/'review/batch-chroma-report.json').write_text(json.dumps({'version':1,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    failures=[r for r in results if r['result'] not in ('created','already_exists')]
    print(f'Processed {len(results)}; failures {len(failures)}',flush=True)
    if failures: raise SystemExit(1)

if __name__=='__main__':main()
