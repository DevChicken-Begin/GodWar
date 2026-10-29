#!/usr/bin/env python3
"""Import supplied GIF references as provisional atlas previews; retain prior Scorpit."""
import hashlib, json, math, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from extract_gif_assets import extract
from import_oct29_gifs import background, key
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'Asset/Character'; SOURCE=ROOT/'13 charnew'
HEIGHTS={'buffao':80,'scosrian':85,'dump':80,'hemsiss':80,'scorpit':80,'Domrico':85,'hecfaom':85,'Impector':80,'Actem':80,'Hatomin':80,'Trainxoan':85,'urguro':80}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 catpath=A/'extracted/catalog.json'; targetpath=A/'characters/height-targets.json'; rosterpath=A/'characters/roster.json'; invpath=A/'review/inventory.json'; statuspath=A/'review/background-review-status.json'
 cat,targets,roster,inv,status=map(read,(catpath,targetpath,rosterpath,invpath,statuspath))
 existing={e['id']:e for e in cat['assets']}; oldtarget=next(x for x in targets['assets'] if x['id']=='scorpit'); assert oldtarget['target_height_px']==80
 stage=A/'charnew_staging'; archive=A/'archive/scorpit_before_charnew'
 if stage.exists() or archive.exists(): raise FileExistsError('Staging/archive exists; inspect before rerun')
 for name in HEIGHTS:
  assert (SOURCE/(name+'.gif')).is_file()
  if name!='scorpit': assert name not in existing and not (A/'vfx'/(name+'.gif')).exists() and not (A/'measured_atlas_pilots'/name).exists()
 stage.mkdir(parents=True); reports=[]
 for name,height in HEIGHTS.items():
  input=SOURCE/(name+'.gif'); temp=stage/name; temp.mkdir(); gifpath=temp/(name+'.gif'); shutil.copyfile(input,gifpath)
  entry=extract(gifpath,temp/'extracted'); entry['source']=f'Asset/Character/vfx/{name if name != "scorpit" else "scorpit_charnew"}.gif'; entry['source_sha256']=digest(input)
  output=temp/'measured'; output.mkdir(); frames=[]; bgcounts={}; removed=[]; first=None
  with Image.open(input) as gif:
   w,h=gif.size; factor=1.2 if name=='Hatomin' else 1; w,h=round(w*factor),round(h*factor); cols=2048//w; rows=2048//h; capacity=cols*rows; page=None; atlas=None
   for i in range(gif.n_frames):
    gif.seek(i); frame=gif.convert('RGBA'); bg=background(frame); color=','.join(map(str,bg.tolist())); bgcounts[color]=bgcounts.get(color,0)+1; cleaned,count=key(frame,bg); removed.append(count)
    if factor!=1:
     cleaned=cleaned.convert('RGBa').resize((w,h),Image.Resampling.LANCZOS).convert('RGBA'); alpha=cleaned.getchannel('A'); cleaned=cleaned.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1,percent=18,threshold=3)); cleaned.putalpha(alpha)
    if i==0: first=cleaned.copy()
    newpage=i//capacity
    if newpage!=page:
     if atlas is not None: atlas.save(output/f'atlas_{page:03d}.png',compress_level=3)
     page=newpage; countpage=min(capacity,gif.n_frames-page*capacity); atlas=Image.new('RGBA',(min(cols,countpage)*w,math.ceil(countpage/cols)*h))
    slot=i%capacity; x=slot%cols*w; y=slot//cols*h; atlas.paste(cleaned,(x,y)); frames.append({'atlas':page,'region':[x,y,w,h],'duration_ms':entry['frames'][i]['duration_ms']})
   atlas.save(output/f'atlas_{page:03d}.png',compress_level=3)
  bbox=first.getbbox(); assert bbox and bbox[3]>bbox[1]; ref=bbox[3]-bbox[1]
  meta={'id':name,'source':entry['source'],'source_sha256':entry['source_sha256'],'art_source':'existing','frame_count':len(frames),'frames':frames,'frame_size':[w,h],'target_height_px':height,'reference_frame':0,'reference_height_px':ref,'reference_alpha_bounds':list(bbox),'anchor_px':[(bbox[0]+bbox[2])/2,bbox[3]],'display_scale':height/ref,'measurement_kind':'automatic_alpha_bbox_unreviewed','status':'automatic_candidate_unreviewed','size_target_approval':'user_updated_round4','background_rgb_frame_counts':bgcounts,'removed_per_frame':removed,'detail_scale':factor,'method':'Per-frame modal border color, RGB distance <= 5 removed; preserve timeline and full frame. Hatomin: premultiplied Lanczos 120% and mild unsharp mask.','limitations':'Unreviewed matte can remove similarly colored detail or retain fringe, lettering and scene; frame-0 alpha bounds can contain effects, not a verified body or anchor. Interpolation cannot recover source detail.'}
  write(output/'candidate.json',meta)
  reports.append({'id':name,'entry':entry,'meta':meta,'source_input':str(input.relative_to(ROOT))})
  print(name, len(frames), [w,h], height, 'bbox',bbox, 'backgrounds',bgcounts,flush=True)
 # Preserve existing Scorpit source and displaced generated previews.
 archive.mkdir(parents=True)
 for folder in ['extracted','measured_atlas_pilots']:
  old=A/folder/'scorpit'; shutil.move(str(old),str(archive/folder))
 write(archive/'original-catalog-entry.json',existing['scorpit']); write(archive/'original-height-target.json',oldtarget)
 for row in reports:
  name=row['id']; entry=row['entry']; meta=row['meta']; temp=stage/name
  dest=ROOT/entry['source']; shutil.copyfile(temp/(name+'.gif'),dest); assert digest(dest)==entry['source_sha256']
  shutil.move(str(temp/'extracted'/name),str(A/'extracted'/name)); shutil.move(str(temp/'measured'),str(A/'measured_atlas_pilots'/name))
  cat['assets']=[e for e in cat['assets'] if e['id']!=name]; cat['assets'].append(entry)
  target={'id':name,'target_height_px':HEIGHTS[name],'source':entry['source'],'source_sha256':entry['source_sha256'],'reference_frame':0,'reference_body_bounds':None,'scale':meta['display_scale'],'status':'automatic_alpha_candidate_unreviewed','measured_atlas_candidate':f'Asset/Character/measured_atlas_pilots/{name}/candidate.json','size_target_approval':'user_updated_round4'}
  targets['assets']=[x for x in targets['assets'] if x['id']!=name]; targets['assets'].append(target)
  roster['entries']=[x for x in roster['entries'] if x['source_id']!=name]; roster['entries'].append({'source_id':name,'provisional_character_name':name,'source':entry['source'],'source_sha256':entry['source_sha256'],'identity_status':'name_from_filename_visual_review_needed','animations':{},'skill':{'status':'unreviewed','name':None,'provenance':None},'attack_range':'unreviewed','notes':'Nguồn mới; frame và nền cần duyệt; chưa phân loại hoạt ảnh.'})
  inv['sources']=[x for x in inv['sources'] if x['source'] not in [entry['source'], 'Asset/Character/vfx/scorpit.gif' if name=='scorpit' else entry['source']]]; inv['sources'].append({'source':entry['source'],'sha256':entry['source_sha256'],'frames':len(meta['frames']),'review_sheets':[],'status':'unreviewed','observations':[],'characters':[]})
  status['sources']=[x for x in status['sources'] if x['id']!=name]; status['sources'].append({'id':name,'status':'visual_review_pending','issue':'Bản mới tách nền cần kiểm tra từng frame; mốc thân và neo chưa duyệt.','variants':['measured_atlas_pilots']})
 cat['assets'].sort(key=lambda e:e['id'].lower()); targets['assets'].sort(key=lambda e:e['id'].lower())
 for p,data in [(catpath,cat),(targetpath,targets),(rosterpath,roster),(invpath,inv),(statuspath,status)]: write(p,data)
 write(A/'characters/charnew-import.json',{'art_source':'existing','sources':[{'id':r['id'],'input':r['source_input'],'sha256':r['entry']['source_sha256'],'frame_count':r['meta']['frame_count'],'target_height_px':r['meta']['target_height_px'],'frame_size':r['meta']['frame_size']} for r in reports],'scorpit_previous_source':'Asset/Character/vfx/scorpit.gif','scorpit_archive':str(archive.relative_to(ROOT))})
 shutil.rmtree(stage)
if __name__=='__main__': main()
