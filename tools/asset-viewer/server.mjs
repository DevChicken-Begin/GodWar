import { createServer } from 'node:http';
import { readFile, readdir, stat } from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../', import.meta.url));
const uiRoot = path.join(root, 'tools/asset-viewer');
const assetRoot = path.join(root, 'Asset/Character');
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.gif': 'image/gif', '.png': 'image/png', '.jpg': 'image/jpeg', '.mp4': 'video/mp4' };

function inside(base, target) {
  const relative = path.relative(base, target);
  return relative !== '' && !relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative);
}

export function createAssetServer() {
  return createServer(async (req, res) => {
    try {
      if (req.method !== 'GET' && req.method !== 'HEAD') {
        res.writeHead(405, { Allow: 'GET, HEAD' }).end(); return;
      }
      const url = new URL(req.url, 'http://localhost');
      if (url.pathname === '/api/assets') {
        const [catalog, removed] = await Promise.all([
          readFile(path.join(assetRoot, 'extracted/catalog.json'), 'utf8').then(JSON.parse),
          readFile(path.join(assetRoot, 'characters/removed.json'), 'utf8').then(JSON.parse),
        ]);
        const excluded = new Set(removed.ids);
        catalog.assets = catalog.assets.filter((asset) => !excluded.has(asset.id));
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }).end(req.method === 'HEAD' ? '' : JSON.stringify(catalog)); return;
      }
      if (['/api/candidates', '/api/refined-candidates', '/api/cleanup-candidates', '/api/batch-candidates', '/api/special-candidates', '/api/temporal-candidates', '/api/shared-scene-candidates', '/api/detailed-candidates', '/api/foot-candidates', '/api/scene-detail-candidates', '/api/remaining-scene-candidates', '/api/spot-candidates', '/api/pixel-candidates', '/api/pixel-120-candidates', '/api/native-candidates', '/api/oct28-fix-candidates', '/api/pixel-180-candidates', '/api/scorpit-repair-candidates', '/api/logo-candidates', '/api/scene-protected-candidates', '/api/pixel-220-candidates', '/api/sharp-candidates', '/api/scorpit-repair18-candidates', '/api/fine-candidates', '/api/detail-130-candidates', '/api/fire-speck-candidates', '/api/fire-orphan-candidates', '/api/fire-deep-candidates', '/api/motion-v2-candidates', '/api/repaired-candidates', '/api/repaired-v2-candidates', '/api/repaired-v5-candidates', '/api/detail-oct28-candidates', '/api/speed-oct28-candidates', '/api/speed-60fps-candidates', '/api/conden-60fps-candidates', '/api/tune-60fps-candidates', '/api/batch12-native-candidates', '/api/batch12-detail-candidates', '/api/scene-mask-candidates', '/api/scene-mask-deep-candidates', '/api/scene-mask-deeper-candidates', '/api/scene-spot-candidates', '/api/revision-candidates'].includes(url.pathname)) {
        const candidateDir = {'/api/candidates': 'candidates', '/api/refined-candidates': 'refined_candidates', '/api/cleanup-candidates': 'cleanup_candidates', '/api/batch-candidates': 'batch_candidates', '/api/special-candidates': 'special_candidates', '/api/temporal-candidates': 'temporal_candidates', '/api/shared-scene-candidates': 'shared_scene_candidates', '/api/detailed-candidates': 'detailed_candidates', '/api/foot-candidates': 'foot_candidates', '/api/scene-detail-candidates': 'scene_detail_v3_candidates', '/api/remaining-scene-candidates': 'remaining_scene_candidates', '/api/spot-candidates': 'spot_candidates', '/api/pixel-candidates': 'pixel_candidates', '/api/pixel-120-candidates': 'pixel_120_candidates', '/api/native-candidates': 'native_candidates', '/api/oct28-fix-candidates': 'oct28_fix_candidates', '/api/pixel-180-candidates': 'pixel_180_candidates', '/api/scorpit-repair-candidates': 'scorpit_repair_candidates', '/api/logo-candidates': 'logo_candidates', '/api/scene-protected-candidates': 'scene_protected_candidates', '/api/pixel-220-candidates': 'pixel_220_candidates', '/api/sharp-candidates': 'sharp_candidates', '/api/scorpit-repair18-candidates': 'scorpit_repair18_candidates', '/api/fine-candidates': 'fine_candidates', '/api/detail-130-candidates': 'detail_130_candidates', '/api/fire-speck-candidates': 'fire_speck_candidates', '/api/fire-orphan-candidates': 'fire_orphan_candidates', '/api/fire-deep-candidates': 'fire_deep_candidates', '/api/motion-v2-candidates': 'motion_v2_candidates', '/api/repaired-candidates': 'repaired_candidates', '/api/repaired-v2-candidates': 'repaired_v2_candidates', '/api/repaired-v5-candidates': 'repaired_v5_candidates', '/api/detail-oct28-candidates': 'detail_oct28_candidates', '/api/speed-oct28-candidates': 'speed_oct28_candidates', '/api/speed-60fps-candidates': 'speed_60fps_candidates', '/api/conden-60fps-candidates': 'conden_60fps_candidates', '/api/tune-60fps-candidates': 'tune_60fps_candidates', '/api/batch12-native-candidates': 'batch12_native_candidates', '/api/batch12-detail-candidates': 'batch12_detail_candidates', '/api/scene-mask-candidates': 'scene_mask_candidates', '/api/scene-mask-deep-candidates': 'scene_mask_deep_candidates', '/api/scene-mask-deeper-candidates': 'scene_mask_deeper_candidates', '/api/scene-spot-candidates': 'scene_spot_candidates', '/api/revision-candidates': 'revision_candidates'}[url.pathname];
        let directories = [];
        try { directories = await readdir(path.join(assetRoot, candidateDir), { withFileTypes: true }); }
        catch (error) { if (error.code !== 'ENOENT') throw error; }
        const names = [];
        for (const dir of directories) {
          if (!dir.isDirectory()) continue;
          try { await stat(path.join(assetRoot, candidateDir, dir.name, 'candidate.json')); names.push(dir.name); }
          catch (error) { if (error.code !== 'ENOENT') throw error; }
        }
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }).end(req.method === 'HEAD' ? '' : JSON.stringify(names)); return;
      }
      let decoded;
      try { decoded = decodeURIComponent(url.pathname); }
      catch { res.writeHead(400).end('Invalid URL'); return; }
      let file;
      if (decoded === '/') file = path.join(uiRoot, 'index.html');
      else if (decoded === '/app.js' || decoded === '/style.css' || decoded === '/render-frame.mjs' || decoded === '/timing.mjs') file = path.join(uiRoot, decoded.slice(1));
      else if (decoded.startsWith('/Asset/Character/')) {
        const relative = decoded.slice('/Asset/Character/'.length);
        if (!/^(vfx|extracted|candidates|refined_candidates|cleanup_candidates|batch_candidates|special_candidates|temporal_candidates|shared_scene_candidates|detailed_candidates|foot_candidates|scene_detail_v3_candidates|remaining_scene_candidates|spot_candidates|pixel_candidates|pixel_120_candidates|native_candidates|oct28_fix_candidates|pixel_180_candidates|scorpit_repair_candidates|logo_candidates|scene_protected_candidates|pixel_220_candidates|sharp_candidates|scorpit_repair18_candidates|fine_candidates|detail_130_candidates|fire_speck_candidates|fire_orphan_candidates|fire_deep_candidates|motion_v2_candidates|repaired_candidates|repaired_v2_candidates|repaired_v5_candidates|detail_oct28_candidates|speed_oct28_candidates|speed_60fps_candidates|conden_60fps_candidates|tune_60fps_candidates|batch12_native_candidates|batch12_detail_candidates|scene_mask_candidates|scene_mask_deep_candidates|scene_mask_deeper_candidates|scene_spot_candidates|revision_candidates|review|characters)\//.test(relative)) { res.writeHead(404).end('Not found'); return; }
        file = path.resolve(assetRoot, relative);
        if (!inside(assetRoot, file)) { res.writeHead(404).end('Not found'); return; }
      } else { res.writeHead(404).end('Not found'); return; }
      const info = await stat(file);
      if (!info.isFile()) { res.writeHead(404).end('Not found'); return; }
      res.writeHead(200, { 'Content-Type': mime[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': info.size, 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff' });
      if (req.method === 'HEAD') res.end(); else createReadStream(file).on('error', () => res.destroy()).pipe(res);
    } catch (error) {
      if (!res.headersSent) res.writeHead(error.code === 'ENOENT' ? 404 : 500).end(error.code === 'ENOENT' ? 'Not found' : 'Server error');
      else res.destroy();
    }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 4173);
  const host = process.env.HOST || '127.0.0.1';
  const server = createAssetServer();
  server.listen(port, host, () => console.log(`GodWar asset viewer: http://${host}:${port}`));
}
