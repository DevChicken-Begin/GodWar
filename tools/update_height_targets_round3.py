#!/usr/bin/env python3
"""Replace twenty approved height targets without changing sprite or timing data."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'Asset/Character'
TARGET=A/'characters/height-targets.json'
HISTORY=A/'characters/height-update-round3.json'
VALUES='Kahn:87 choptian:90 comic:85 congpha:85 corepion:65 costmic:75 dracian:95 dragonight:100 dragonot:100 firemen:70 hades:110 iternal:90 jaik:85 kengkeng:90 kumen:80 kungchang:85 midnight:80 momo:85 nox:87 omra:80'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def write(path, value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)

def main():
    if HISTORY.exists():raise FileExistsError(HISTORY)
    changes={p.split(':')[0]:int(p.split(':')[1]) for p in VALUES.split()}
    targets=json.loads(TARGET.read_text());entries={e['id']:e for e in targets['assets']}
    assert len(changes)==20 and len(entries)==143 and set(changes)<=set(entries)
    unchanged={n:e['target_height_px'] for n,e in entries.items() if n not in changes}
    plan=[];proof={}
    for name,height in changes.items():
        e=entries[name];folder=A/'measured_atlas_pilots'/name;path=folder/'candidate.json';m=json.loads(path.read_text())
        assert m['id']==name and m['source_sha256']==e['source_sha256']==sha(ROOT/m['source'])
        assert m['target_height_px']==e['target_height_px'] and m['reference_height_px']>0
        assert m['frame_count']==len(m['frames'])
        pages=sorted({f['atlas'] for f in m['frames']})
        hashes={f'atlas_{p:03d}.png':sha(folder/f'atlas_{p:03d}.png') for p in pages}
        timeline=hashlib.sha256(json.dumps(m['frames'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        proof[name]={'target_height_px':height,'reference_height_px':m['reference_height_px'],
                     'frame_count':m['frame_count'],'frames_sha256':timeline,'atlas_sha256':hashes}
        m['target_height_px']=height;m['display_scale']=height/m['reference_height_px'];m['size_target_approval']='user_updated_round3'
        e['target_height_px']=height;e['scale']=m['display_scale'];e['size_target_approval']='user_updated_round3'
        plan.append((path,m))
    write(HISTORY,{'viewport':[1920,1080],'changes':changes,'unchanged_targets':unchanged,'proof':proof,
                   'note':'Only current target values retained. Atlas bytes, frame geometry and timing unchanged.'})
    for path,m in plan:write(path,m)
    write(TARGET,targets)
    print('Updated',len(plan),'targets;',len(unchanged),'unchanged')

if __name__=='__main__':main()
