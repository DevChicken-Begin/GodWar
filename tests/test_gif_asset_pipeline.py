"""Regression tests for GIF decoding and atlas metadata."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
from tools.extract_gif_assets import extract


class GifExtractionTest(unittest.TestCase):
    def test_frames_and_durations_survive_transparency_and_disposal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'sample.gif'
            first = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
            second = Image.new('RGBA', first.size, (0, 0, 0, 0))
            ImageDraw.Draw(first).rectangle((3, 3, 12, 12), fill=(255, 0, 0, 255))
            ImageDraw.Draw(second).rectangle((20, 20, 30, 30), fill=(0, 255, 0, 255))
            first.save(source, save_all=True, append_images=[second], duration=[40, 130],
                       loop=0, disposal=2, transparency=0)
            entry = extract(source, root / 'out')
            self.assertEqual(entry['frame_count'], 2)
            self.assertEqual([f['duration_ms'] for f in entry['frames']], [40, 130])
            self.assertEqual(entry['loop'], 0)
            gif = Image.open(source)
            for i, frame in enumerate(entry['frames']):
                gif.seek(i)
                original = gif.convert('RGBA')
                with Image.open(root / 'out/sample' / f'atlas_{frame["atlas"]:03d}.png') as page:
                    x, y, w, h = frame['region']
                    actual = page.crop((x, y, x + w, y + h))
                self.assertIsNone(ImageChops.difference(original, actual).getbbox(alpha_only=False))
            gif.close()

class BackgroundCandidateTest(unittest.TestCase):
    def test_background_clear_preserves_enclosed_matching_pixels(self):
        from tools.remove_flat_background_candidate import clear_background
        background = (4, 50, 71, 255)
        image = Image.new('RGBA', (9, 9), background)
        draw = ImageDraw.Draw(image)
        draw.rectangle((2, 2, 6, 6), fill=(255, 0, 0, 255))
        draw.point((4, 4), fill=background)
        result = clear_background(image, background, [(0, 0), (8, 0), (0, 8), (8, 8)])
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 0, 0))
        self.assertEqual(result.getpixel((2, 2)), (255, 0, 0, 255))
        self.assertEqual(result.getpixel((4, 4)), background)

if __name__ == '__main__':
    unittest.main()
