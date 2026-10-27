#!/usr/bin/env python3
"""Build separate source-backed atlases for the three user-named GIF segments."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
SPECS = [('solist',0,51),('namero',52,101),('kukaomni',102,155)]


def main():
    source_entry = next(x for x in json.loads((ASSETS/'extracted/catalog.json').read_text())['assets'] if x['id']=='3 char')
    if hashlib.sha256((ROOT/source_entry['source']).read_bytes()).hexdigest() != source_entry['source_sha256']:
        raise ValueError('Source hash differs from catalog')
    output_entries = []
    for character_id, first, last in SPECS:
        w,h=source_entry['size']; cols=2048//w; rows=2048//h; capacity=cols*rows
        new_frames = []
        for variant in ('extracted','refined_candidates'):
            out = ASSETS/variant/character_id
            if out.exists(): raise ValueError(f'Refusing to overwrite: {out}')
            out.mkdir(parents=True)
            pages={}
            try:
                for start in range(first,last+1,capacity):
                    count=min(capacity,last-start+1); used_cols=min(cols,count); used_rows=math.ceil(count/cols)
                    atlas=Image.new('RGBA',(used_cols*w,used_rows*h))
                    page_number=(start-first)//capacity
                    for src in range(start,start+count):
                        item=source_entry['frames'][src]; old_page=item['atlas']
                        if old_page not in pages:
                            pages[old_page]=Image.open(ASSETS/variant/'3 char'/f'atlas_{old_page:03d}.png')
                        x,y,_,_=item['region']; frame=pages[old_page].crop((x,y,x+w,y+h))
                        local=src-start; target_x=(local%cols)*w; target_y=(local//cols)*h
                        atlas.paste(frame,(target_x,target_y))
                        if variant=='extracted':
                            new_frames.append({'atlas':page_number,'region':[target_x,target_y,w,h],'duration_ms':item['duration_ms'],'source_frame':src})
                    atlas.save(out/f'atlas_{page_number:03d}.png',compress_level=1)
            finally:
                for page in pages.values(): page.close()
            if variant=='refined_candidates':
                parent=json.loads((ASSETS/variant/'3 char/candidate.json').read_text())
                parent.update({'frames':new_frames,'frame_count':len(new_frames),'character_id':character_id,
                               'source_frame_range':[first,last]})
                (out/'candidate.json').write_text(json.dumps(parent,ensure_ascii=False,indent=2)+'\n')
        entry={'id':character_id,'source':source_entry['source'],'source_sha256':source_entry['source_sha256'],
               'size':[w,h],'frame_count':len(new_frames),'loop':source_entry['loop'],
               'atlas_count':math.ceil(len(new_frames)/capacity),'frames':new_frames,'sourceStart':first,
               'classification':'source_segment_unreviewed','animations':{},
               'notes':'User-named character; source segment not yet split into individual animations.'}
        output_entries.append(entry)
        folder=ASSETS/'characters'/character_id
        if folder.exists(): raise ValueError(f'Refusing to overwrite profile: {folder}')
        folder.mkdir(parents=True)
        profile={'id':character_id,'display_name':character_id,'source':entry['source'],'source_sha256':entry['source_sha256'],
                 'source_asset_id':'3 char','first_source_frame':first,'last_source_frame':last,
                 'frame_count':entry['frame_count'],'atlas_roots':{'source':f'Asset/Character/extracted/{character_id}',
                 'candidate':f'Asset/Character/refined_candidates/{character_id}'},
                 'status':'source_segment_unreviewed','animations':{},'skill':{'status':'unreviewed','name':None}}
        (folder/'character.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{character_id}: source frames {first}-{last}, {len(new_frames)} frames')
    (ASSETS/'extracted/split-catalog.json').write_text(json.dumps({'version':1,'assets':output_entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ASSETS/'characters/3-char-splits.json').write_text(json.dumps({'version':1,'characters':[
        {'id':name,'display_name':name,'source_asset_id':'3 char','first_source_frame':first,'last_source_frame':last,'frame_count':last-first+1} for name,first,last in SPECS]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
