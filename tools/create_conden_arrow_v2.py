#!/usr/bin/env python3
"""Add review-only projectile travel using crops from each existing animation."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'Asset/Character'
SPECS = {
    'conden': {'source_index': 43, 'crop': (575, 390, 715, 465), 'indices': (44, 45, 46, 47),
               'first_x': 600, 'step': 55, 'y': 390, 'canvas': (960, 720)},
}


def build(name, spec, entry):
    source = ROOT / entry['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
    base = ASSETS / 'batch_candidates' / name
    assert json.loads((base / 'candidate.json').read_text())['source_sha256'] == entry['source_sha256']
    out = ASSETS / 'repaired_v2_candidates' / name
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    def get_frame(index):
        f = entry['frames'][index]
        x, y, w, h = f['region']
        with Image.open(base / f'atlas_{f["atlas"]:03}.png') as image:
            return image.convert('RGBA').crop((x, y, x+w, y+h))
    template = get_frame(spec['source_index']).crop(spec['crop'])
    template.save(out / 'projectile_template.png')
    width, height = spec['canvas']
    columns, rows = 2048 // width, 2048 // height
    capacity = columns * rows
    total = len(entry['frames']) + len(spec['indices'])
    pages, frames = {}, []
    for i, original in enumerate(entry['frames']):
        variants = 2 if i in spec['indices'] else 1
        for part in range(variants):
            frame = Image.new('RGBA', (width, height))
            frame.paste(get_frame(i), (0, 0))
            if variants == 2:
                offset = spec['indices'].index(i)
                x = spec['first_x'] + offset*spec['step'] + part*(spec['step']//2)
                frame.alpha_composite(template, (x, spec['y']))
            j = len(frames)
            page, slot = divmod(j, capacity)
            if page not in pages:
                count = min(capacity, total-page*capacity)
                pages[page] = Image.new('RGBA', (min(columns, count)*width, ((count+columns-1)//columns)*height))
            x, y = (slot % columns)*width, (slot // columns)*height
            pages[page].paste(frame, (x, y))
            duration = original['duration_ms']
            # Keep each added exposure at the source's 70 ms for a visible flight.
            frames.append({'atlas': page, 'region': [x, y, width, height], 'duration_ms': duration,
                           'source_index': i, 'synthetic': variants == 2})
    for page, image in pages.items():
        image.save(out / f'atlas_{page:03}.png')
    meta = {'id': name, 'source': entry['source'], 'source_sha256': entry['source_sha256'], 'base_candidate': 'batch_candidates',
            'frame_count': len(frames), 'frames': frames, 'loop': entry['loop'], 'display_size': list(spec['canvas']),
            'template_source_index': spec['source_index'], 'template_region_xyxy': list(spec['crop']),
            'modified_source_indices': list(spec['indices']), 'method': 'Overlay a crop of the existing arrow-like effect at successive positions, add 70 ms exposures for the selected source frames and extend the right canvas.',
            'status': 'candidate_unreviewed', 'limitations': 'Projectile travel and inserted frames are synthetic; 4 new 70 ms exposures extend the loop by 280 ms. The original art and timing remain available. Check for overlaps or abrupt exits.'}
    (out / 'candidate.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(name, len(entry['frames']), '->', len(frames), 'frames', flush=True)


if __name__ == '__main__':
    catalog = {e['id']: e for e in json.loads((ASSETS / 'extracted/catalog.json').read_text())['assets']}
    for name, spec in SPECS.items():
        build(name, spec, catalog[name])
