#!/usr/bin/env python3
"""Validate each candidate against its original; this cannot prove semantic quality."""
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'Asset/Character'


def verify(path):
    m=json.loads(path.read_text(encoding='utf-8'));source=ROOT/m['source']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=m['source_sha256']: raise ValueError('source hash mismatch')
    base=np.array(m['background_rgba'][:3],dtype=np.int16); page=None; number=None; removed=0
    with Image.open(source) as gif:
        if gif.n_frames!=m['frame_count'] or len(m['frames'])!=m['frame_count']:raise ValueError('frame count mismatch')
        try:
            for i,f in enumerate(m['frames']):
                gif.seek(i);before=np.array(gif.convert('RGBA'))
                if f['atlas']!=number:
                    if page is not None:page.close()
                    number=f['atlas'];page=Image.open(path.parent/f'atlas_{number:03d}.png')
                x,y,w,h=f['region']; after=np.array(page.crop((x,y,x+w,y+h)))
                if before.shape!=after.shape or f['duration_ms']!=gif.info.get('duration',0):raise ValueError(f'frame {i}: metadata')
                distance=np.max(np.abs(before[:,:,:3].astype(np.int16)-base),axis=2)
                expected=(before[:,:,3]==255)&(distance<=5)
                if np.any(after[expected]!=0) or not np.array_equal(before[~expected],after[~expected]):raise ValueError(f'frame {i}: pixels')
                removed+=int(expected.sum())
        finally:
            if page is not None:page.close()
    if removed!=m['removed_pixels']:raise ValueError('removed pixel count')
    return {'id':m['id'],'frames':m['frame_count'],'pixel_check':'passed','visual_review':'pending'}


def main():
    paths=[p for p in sorted((ASSETS/'batch_candidates').glob('*/candidate.json')) if not json.loads(p.read_text(encoding='utf-8')).get('derived_from')];results=[];failures=[]
    with ProcessPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(verify,p):p for p in paths}
        for future in as_completed(futures):
            try:
                result=future.result();results.append(result);print(f'{len(results)}/{len(paths)} {result["id"]}: pixel check passed',flush=True)
            except Exception as error:
                failures.append({'path':str(futures[future]),'error':str(error)}); print(f'FAIL {futures[future]}: {error}',flush=True)
    report={'version':1,'limitation':'Pixel checks do not establish whether erased pixels belong to character or VFX.','results':sorted(results,key=lambda r:r['id'].lower()),'failures':failures}
    (ASSETS/'review/batch-chroma-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS {len(results)} GIFs / {sum(r["frames"] for r in results)} frames; failures {len(failures)}',flush=True)
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
