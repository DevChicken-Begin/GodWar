#!/usr/bin/env python3
"""Build reversible, explicitly unreviewed height previews for remaining IDs."""
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
OUT = A / 'measured_atlas_pilots'
TARGET = A / 'characters/height-targets.json'
FRAME_BASES = ('detail_oct29_candidates', 'revision_candidates', 'scene_spot_candidates',
               'scene_mask_deeper_candidates', 'scene_mask_deep_candidates', 'scene_mask_candidates',
               'batch12_detail_candidates', 'detail_oct28_candidates', 'detail_130_candidates')
ATLAS_BASES = ('fine_candidates', 'batch12_native_candidates', 'native_candidates',
               'oct28_fix_candidates', 'pixel_220_candidates', 'spot_candidates',
               'remaining_scene_candidates', 'scene_detail_v3_candidates', 'foot_candidates',
               'detailed_candidates', 'special_candidates', 'cleanup_candidates',
               'shared_scene_candidates', 'temporal_candidates', 'batch_candidates',
               'refined_candidates', 'candidates', 'extracted')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def source_frames(entry, base):
    folder = A/base/entry['id']
    if base in FRAME_BASES:
        meta = json.loads((folder/'candidate.json').read_text())
        assert meta['source_sha256'] == entry['source_sha256']
        assert len(meta['frames']) == len(entry['frames'])
        if base == 'detail_130_candidates':
            folder = A/'review'/entry['id']/'detail_130_frames'
        return folder, meta['frames'], True
    return folder, entry['frames'], False


def main():
    targets = json.loads(TARGET.read_text())
    catalog = {e['id']: e for filename in ('catalog.json', 'split-catalog.json')
               for e in json.loads((A/'extracted'/filename).read_text())['assets']}
    for target in targets['assets']:
        name = target['id']
        if name == 'crapit' or (OUT/name/'candidate.json').exists():
            continue
        entry = catalog[name]
        assert sha(ROOT/entry['source']) == entry['source_sha256'] == target['source_sha256']
        base = None
        for candidate in (*FRAME_BASES, *ATLAS_BASES):
            try:
                folder, records, files = source_frames(entry, candidate) if candidate not in FRAME_BASES or (A/candidate/name/'candidate.json').exists() else (None, None, None)
            except (AssertionError, KeyError, ValueError):
                continue
            if folder is None:
                continue
            try:
                if files:
                    path = folder/'frame_000.png'
                    with Image.open(path) as im:
                        frame = im.convert('RGBA')
                else:
                    first = records[0]; x,y,w,h = first['region']
                    path = folder/f'atlas_{first["atlas"]:03d}.png'
                    with Image.open(path) as im:
                        if x+w > im.width or y+h > im.height:
                            continue
                        frame = im.crop((x,y,x+w,y+h)).convert('RGBA')
                bbox = frame.getbbox()
                if bbox is None or frame.getchannel('A').getextrema()[0] == 255:
                    continue
                if not files and not all((folder/f'atlas_{f["atlas"]:03d}.png').is_file() for f in records):
                    continue
                if not files:
                    meta_path = folder/'candidate.json'
                    if meta_path.exists():
                        old = json.loads(meta_path.read_text())
                        if old.get('source_sha256', entry['source_sha256']) != entry['source_sha256']:
                            continue
                        old_frames = old.get('frames', records)
                        if len(old_frames) != len(records) or any(
                            (a.get('atlas'),a.get('region'),a.get('duration_ms')) != (b.get('atlas'),b.get('region'),b.get('duration_ms'))
                            for a,b in zip(old_frames,records)):
                            continue
                    sizes = {}
                    for page_id in {f['atlas'] for f in records}:
                        with Image.open(folder/f'atlas_{page_id:03d}.png') as page:
                            sizes[page_id] = page.size
                    if any(f['region'][0] < 0 or f['region'][1] < 0 or
                           f['region'][0]+f['region'][2] > sizes[f['atlas']][0] or
                           f['region'][1]+f['region'][3] > sizes[f['atlas']][1] for f in records):
                        continue
                base = candidate
                break
            except (FileNotFoundError, OSError):
                continue
        if base is None:
            print('SKIP', name, 'no suitable transparent reference', flush=True)
            continue
        width,height = frame.size
        left,top,right,bottom = bbox
        ref_height = bottom-top
        anchor = [(left+right)/2, bottom]
        flags = ['Vùng alpha có thể chứa vũ khí, hiệu ứng hoặc nhiều vật thể; chưa đo thân bằng mắt.',
                 'Điểm neo ước lượng từ đáy alpha; chưa kiểm duyệt.']
        if left == 0 or top == 0 or right == width or bottom == height or ref_height >= height*.8:
            flags.append('Vùng alpha lớn hoặc chạm mép canvas, có thể gồm nền hoặc bị cắt trong nguồn.')
        OUT.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=f'.{name}-', dir=OUT))
        try:
            frames = []
            hashes = {}
            if files:
                cols,rows = 2048//width, 2048//height
                if not cols or not rows:
                    raise ValueError(f'{name}: frame exceeds atlas limit')
                capacity = cols*rows
                for start in range(0, len(records), capacity):
                    count = min(capacity, len(records)-start)
                    page = Image.new('RGBA',(min(cols,count)*width, math.ceil(count/cols)*height))
                    for slot in range(count):
                        index = start+slot; path = folder/f'frame_{index:03d}.png'
                        hashes[str(path.relative_to(ROOT))] = sha(path)
                        with Image.open(path) as source:
                            im = source.convert('RGBA')
                            assert im.size == (width,height)
                            x,y = slot%cols*width,slot//cols*height
                            page.paste(im,(x,y))
                        frames.append({'atlas':start//capacity,'region':[x,y,width,height],'duration_ms':records[index]['duration_ms']})
                    page.save(stage/f'atlas_{start//capacity:03d}.png',compress_level=3)
            else:
                for page_id in sorted({f['atlas'] for f in records}):
                    path=folder/f'atlas_{page_id:03d}.png'; dest=stage/path.name
                    shutil.copyfile(path,dest); digest=sha(path); assert sha(dest)==digest
                    hashes[str(path.relative_to(ROOT))]=digest
                frames = records
            assert [f['duration_ms'] for f in frames] == [f['duration_ms'] for f in entry['frames']]
            data={'id':name,'source':entry['source'],'source_sha256':entry['source_sha256'],
                  'input_candidate':base,'input_sha256':hashes,'art_source':'existing',
                  'frame_count':len(frames),'frames':frames,'frame_size':[width,height],
                  'target_height_px':target['target_height_px'],'reference_frame':0,
                  'reference_height_px':ref_height,'reference_alpha_bounds':list(bbox),
                  'anchor_px':anchor,'display_scale':target['target_height_px']/ref_height,
                  'measurement_kind':'automatic_alpha_bbox_unreviewed',
                  'status':'automatic_candidate_unreviewed','limitations':' '.join(flags),
                  'method':'Use full frame-0 alpha bounds as provisional reference; preserve all source pixels and one shared scale. Not a verified body measurement.'}
            (stage/'candidate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
            os.rename(stage,OUT/name)
            target.update(reference_frame=0,reference_body_bounds=None,scale=data['display_scale'],
                          status='automatic_alpha_candidate_unreviewed',
                          measured_atlas_candidate=f'Asset/Character/measured_atlas_pilots/{name}/candidate.json')
            TARGET.write_text(json.dumps(targets,ensure_ascii=False,indent=2)+'\n')
            print(name,base,len(frames),'target',target['target_height_px'],'alpha_height',ref_height,flush=True)
        finally:
            if stage.exists(): shutil.rmtree(stage)


if __name__ == '__main__':
    main()
