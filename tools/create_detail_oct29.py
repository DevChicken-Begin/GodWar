#!/usr/bin/env python3
"""Create sequential 130% detail candidates from each viewer-preferred frame set."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'Asset/Character'
NAMES = 'aonime botem buffoin comic congpha dragonot ethan hanko jaik jaying kengkeng kungtailee machinen magma mainthen momo nox odin overight panfire shellhost skyles swithin trongit vision warrioram'.split()
BASE = {
    'botem': 'detail_oct28_candidates', 'comic': 'batch12_detail_candidates',
    'dragonot': 'revision_candidates', 'ethan': 'batch12_detail_candidates',
    'jaik': 'detail_oct28_candidates', 'jaying': 'batch12_detail_candidates',
    'mainthen': 'detail_oct28_candidates', 'momo': 'revision_candidates',
    'nox': 'detail_oct28_candidates', 'odin': 'batch12_detail_candidates',
    'overight': 'detail_oct28_candidates', 'panfire': 'batch12_detail_candidates',
    'shellhost': 'revision_candidates', 'skyles': 'detail_oct28_candidates',
}
OUT = A / 'detail_oct29_candidates'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('names', nargs='+', choices=NAMES)
    parser.add_argument('--display-scale', type=float, default=1.0,
                        help='Scale visible size relative to current viewer size; one name only')
    args = parser.parse_args()
    if args.display_scale != 1 and len(args.names) != 1:
        parser.error('--display-scale requires one name')
    if not 0.5 <= args.display_scale <= 1.5 or len(set(args.names)) != len(args.names):
        parser.error('invalid display scale or duplicate name')
    catalog = {item['id']: item for item in json.loads((A / 'extracted/catalog.json').read_text())['assets']}
    for name in args.names:
        if (OUT / name).exists():
            raise FileExistsError(OUT / name)
    for name in args.names:
        entry = catalog[name]
        source = ROOT / entry['source']
        assert sha(source) == entry['source_sha256']
        base = BASE.get(name, 'native_candidates')
        meta_path = A / base / name / 'candidate.json'
        meta = json.loads(meta_path.read_text())
        assert meta['source_sha256'] == entry['source_sha256']
        frames = meta['frames']
        assert len(frames) == entry['frame_count']
        display = meta.get('display_size', entry['size'])
        display_new = [round(d * args.display_scale) for d in display]
        folder = OUT / name
        folder.mkdir(parents=True)
        samples = sorted({round((len(frames) - 1) * k / 11) for k in range(12)})
        sheet = Image.new('RGB', (4 * 240, 3 * 220), '#424242')
        draw = ImageDraw.Draw(sheet)
        hashes = {}
        generated = []
        old_size = new_size = None
        for index, frame in enumerate(frames):
            if base == 'native_candidates':
                path = A / base / name / f'atlas_{frame["atlas"]:03d}.png'
                x, y, w, h = frame['region']
                with Image.open(path) as atlas:
                    original = atlas.crop((x, y, x + w, y + h)).convert('RGBA')
            else:
                path = A / base / name / f'frame_{index:03d}.png'
                with Image.open(path) as image:
                    original = image.convert('RGBA')
            hashes[str(path.relative_to(ROOT))] = sha(path)
            target = (round(original.width * 1.3), round(original.height * 1.3))
            enlarged = original.convert('RGBa').resize(target, Image.Resampling.LANCZOS).convert('RGBA')
            alpha = enlarged.getchannel('A')
            rgb = enlarged.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1, percent=18, threshold=3))
            rgb.putalpha(alpha)
            rgb.save(folder / f'frame_{index:03d}.png', compress_level=3)
            if old_size is None:
                old_size, new_size = list(original.size), list(target)
            else:
                assert list(original.size) == old_size and list(target) == new_size
            generated.append({**frame, 'region': [0, 0, *display], 'detail_size': list(target)})
            if index in samples:
                slot = samples.index(index)
                thumb = rgb.copy()
                thumb.thumbnail((225, 187), Image.Resampling.LANCZOS)
                sx, sy = slot % 4 * 240, slot // 4 * 220
                sheet.paste(thumb, (sx + (240 - thumb.width) // 2, sy + 25), thumb)
                draw.text((sx + 4, sy + 4), f'#{index}', fill='white')
        sheet.save(folder / 'sample.jpg', quality=92)
        result = {
            'id': name, 'source': entry['source'], 'source_sha256': entry['source_sha256'],
            'base_candidate': base, 'base_metadata_sha256': sha(meta_path),
            'base_input_sha256': hashes, 'art_source': 'existing',
            'scale_factor': 1.3, 'display_scale': args.display_scale,
            'base_display_size': display, 'display_size': display_new,
            'base_frame_size': old_size, 'frame_size': new_size,
            'frame_count': len(generated), 'frames': generated,
            'status': 'candidate_unreviewed',
            'method': 'Premultiplied-alpha Lanczos upscale by 30% per axis, then mild RGB unsharp mask (radius 1, 18%, threshold 3); preserve source frame timing. Display size changes only by explicit display_scale.',
            'limitations': 'Interpolation cannot restore missing source detail; sharpening may introduce halos or change effects. Inspect every frame at game size and over light/dark backgrounds.'
        }
        (folder / 'candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(name, base, len(generated), old_size, '->', new_size,
              'display', display, '->', display_new, flush=True)


if __name__ == '__main__':
    main()
