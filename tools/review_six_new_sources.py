#!/usr/bin/env python3
"""Create unscaled background-subtraction review frames from six original GIFs."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import hashlib, json

NAMES = ['Also', 'Aquamen', 'Diorai', 'Evenl', 'Moregorn', 'Moresword']
OUT = Path('Asset/Character/review/six-import-20261030')
OUT.mkdir(parents=True, exist_ok=True)
frames = {}
for name in NAMES:
    gif = Image.open(name + '.gif')
    frames[name] = []
    for i in range(gif.n_frames):
        gif.seek(i)
        frames[name].append(np.asarray(gif.convert('RGB')).copy())
# Sample across independent sequences to estimate the shared background and logo.
samples = [seq[i] for seq in frames.values() for i in np.linspace(0, len(seq)-1, min(4, len(seq)), dtype=int)]
for name in ['animent', 'overight', 'tigerknight']:
    with Image.open(Path('Asset/Character/vfx') / (name + '.gif')) as gif:
        for i in np.linspace(0, gif.n_frames-1, 8, dtype=int):
            gif.seek(i); samples.append(np.asarray(gif.convert('RGB')).copy())
background = np.median(np.stack(samples), axis=0).astype(np.int16)
Image.fromarray(background.astype(np.uint8)).save(OUT / 'estimated-background.png')
report = []
for name, seq in frames.items():
    source = Path(name + '.gif')
    chosen = sorted(set([0, len(seq)//4, len(seq)//2, 3*len(seq)//4, len(seq)-1]))
    seq_array = np.stack(seq).astype(np.int16)
    first = seq_array[0]
    stable = (np.max(np.abs(seq_array - first), axis=3) <= 8).sum(axis=0) >= len(seq)*0.8
    sheet = Image.new('RGB', (260*len(chosen), 550), 'white')
    draw = ImageDraw.Draw(sheet)
    for j, idx in enumerate(chosen):
        rgb = seq[idx]
        diff = np.max(np.abs(rgb.astype(np.int16)-background), axis=2)
        # Stable logo pixels: only remove colors close to this GIF's first frame.
        yy, xx = np.indices(diff.shape)
        logo = (yy < 150) & stable & (np.max(np.abs(rgb.astype(np.int16)-first), axis=2) <= 10)
        diff[logo] = 0
        rgba = np.dstack([rgb, (diff > 16).astype(np.uint8)*255])
        img = Image.fromarray(rgba).resize((250,250), Image.Resampling.NEAREST)
        for y, color in [(20, '#f0f0f0'), (290, '#171717')]:
            patch = Image.new('RGBA', img.size, color); patch.alpha_composite(img)
            sheet.paste(patch.convert('RGB'), (260*j, y))
        draw.text((260*j+4, 3), f'{name} frame {idx}', fill='black')
        draw.text((260*j+4, 270), 'fond sombre', fill='black')
    sheet.save(OUT / f'{name}-preview.png')
    gif = Image.open(source); durations = []
    for i in range(gif.n_frames):
        gif.seek(i); durations.append(gif.info.get('duration', 0))
    report.append({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'size':list(gif.size),'frame_count':gif.n_frames,'durations_ms':sorted(set(durations)),'sample_frames':chosen,'preview':str(OUT / f'{name}-preview.png')})
(OUT / 'report.json').write_text(json.dumps({'art_source':'existing','status':'analysis_only_unapproved','method':'Median shared scene from six GIFs and three existing independent GIFs; maximum RGB difference > 16 plus stable upper-logo mask; visual preview only.', 'limitations':['Foreground or effects similar to background may disappear; GIF palette and logo overlap may leave residue.', 'No timing, scale or engine output approved.'], 'sources':report},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
