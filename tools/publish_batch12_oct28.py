#!/usr/bin/env python3
"""Publish a validated staged batch while preserving replaced character assets."""
import hashlib,html,json,shutil
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'Asset/Character';S=A/'batch12_stage_v2_20261028';BACK=A/'archive_batch12_20261028'; DUP={'ethan','jaying'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 if BACK.exists():raise FileExistsError(BACK)
 rows=load(S/'manifest.json')['rows'];assert len(rows)==12; names={r['id'] for r in rows}; assert len(names)==12
 paths={'catalog':A/'extracted/catalog.json','roster':A/'characters/roster.json','inventory':A/'review/inventory.json','review':A/'review/background-review-status.json'}; data={k:load(v) for k,v in paths.items()};cat=data['catalog']['assets'];assert {e['id'] for e in cat}&names==DUP
 # Check every staged item and every old source before moving anything.
 for r in rows:
  n=r['id'];e=r['entry']; assert sha(ROOT/f'{n}.gif')==sha(S/'vfx'/f'{n}.gif')==e['source_sha256'];assert (S/'native'/n/'candidate.json').exists() and (S/'detail'/n/'candidate.json').exists()
  if n in DUP:
   old=next(x for x in cat if x['id']==n); assert sha(ROOT/old['source'])==old['source_sha256']
  else:
   for p in [A/'vfx'/f'{n}.gif',A/'extracted'/n,A/'review'/n]:assert not p.exists(),p
  for p in [A/'batch12_native_candidates'/n,A/'batch12_detail_candidates'/n]:assert not p.exists(),p
 BACK.mkdir(); (BACK/'snapshots').mkdir()
 for p in paths.values():shutil.copy2(p,BACK/'snapshots'/p.name)
 shutil.copy2(A/'extracted/index.html',BACK/'snapshots/index.html')
 # Replacements move into archive with their original relative layout.
 for n in sorted(DUP):
  for p in list(A.iterdir()):
   if not p.is_dir() or p in (S,BACK) or p.name.startswith('batch12_stage'):continue
   old=p/n
   if old.is_dir():
    dst=BACK/p.name/n;dst.parent.mkdir(parents=True,exist_ok=True);old.rename(dst)
  p=A/'vfx'/f'{n}.gif';dst=BACK/'vfx'/p.name;dst.parent.mkdir(parents=True,exist_ok=True);p.rename(dst)
 for folder in ['batch12_native_candidates','batch12_detail_candidates']:(A/folder).mkdir(exist_ok=True)
 for row in rows:
  n=row['id'];e=row['entry'];shutil.copy2(S/'vfx'/f'{n}.gif',A/'vfx'/f'{n}.gif');shutil.copytree(S/'extracted'/n,A/'extracted'/n);shutil.copytree(S/'native'/n,A/'batch12_native_candidates'/n);shutil.copytree(S/'detail'/n,A/'batch12_detail_candidates'/n);shutil.copytree(S/'review'/n,A/'review'/n)
  cat[:]=[x for x in cat if x['id']!=n];cat.append(e)
  roster=data['roster']['entries'];roster[:]=[x for x in roster if x.get('source_id')!=n];roster.append({'source_id':n,'provisional_character_name':n,'source':e['source'],'source_sha256':e['source_sha256'],'identity_status':'name_from_filename_visual_review_needed','animations':{},'skill':{'status':'unreviewed','name':None,'provenance':None},'attack_range':'unreviewed','notes':'GIF mới; chưa phân loại hành động hoặc skill.'})
  inventory=data['inventory']['sources'];inventory[:]=[x for x in inventory if x.get('source')!=e['source']];inventory.append({'source':e['source'],'sha256':e['source_sha256'],'frames':e['frame_count'],'review_sheets':row['review_sheets'],'status':'unreviewed','observations':[],'characters':[]})
  review=data['review']['sources'];review[:]=[x for x in review if x.get('id')!=n];review.append({'id':n,'status':'visual_review_pending','issue':'Bản tách nền và chữ chưa duyệt: có thể còn nền hoặc mất chi tiết/VFX; nội suy không khôi phục chi tiết gốc.','variants':['batch12_native_candidates','batch12_detail_candidates']})
 cat.sort(key=lambda x:x['id'].lower());
 for k,p in paths.items():write(p,data[k])
 index=A/'extracted/index.html'; text=index.read_text(); prefix=text.split('<main>')[0];cards=[]
 for e in cat:
  name=html.escape(e['id']);url=quote('../vfx/'+Path(e['source']).name,safe='/');cards.append(f'<article><h2>{name}</h2><img loading="lazy" src="{url}" alt="{name}"><p>{e["frame_count"]} frames · {e["size"][0]} × {e["size"][1]} · chưa kiểm duyệt</p></article>')
 index.write_text(prefix+'<main>'+ '\n'.join(cards)+'</main></html>',encoding='utf8');shutil.copy2(S/'manifest.json',BACK/'manifest.json')
 print('published',len(rows),'sources;',len(cat),'catalog entries;',len(data['roster']['entries']),'roster entries; previous versions:',BACK)
if __name__=='__main__':main()
