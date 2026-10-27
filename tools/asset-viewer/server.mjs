import { createServer } from 'node:http';
import { readdir, stat } from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../', import.meta.url));
const uiRoot = path.join(root, 'tools/asset-viewer');
const assetRoot = path.join(root, 'Asset/Character');
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.gif': 'image/gif', '.png': 'image/png', '.jpg': 'image/jpeg', '.mp4': 'video/mp4' };

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
      if (['/api/candidates', '/api/refined-candidates', '/api/cleanup-candidates', '/api/batch-candidates', '/api/special-candidates', '/api/temporal-candidates', '/api/shared-scene-candidates'].includes(url.pathname)) {
        const candidateDir = {'/api/candidates': 'candidates', '/api/refined-candidates': 'refined_candidates', '/api/cleanup-candidates': 'cleanup_candidates', '/api/batch-candidates': 'batch_candidates', '/api/special-candidates': 'special_candidates', '/api/temporal-candidates': 'temporal_candidates', '/api/shared-scene-candidates': 'shared_scene_candidates'}[url.pathname];
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
      else if (decoded === '/app.js' || decoded === '/style.css') file = path.join(uiRoot, decoded.slice(1));
      else if (decoded.startsWith('/Asset/Character/')) {
        const relative = decoded.slice('/Asset/Character/'.length);
        if (!/^(vfx|extracted|candidates|refined_candidates|cleanup_candidates|batch_candidates|special_candidates|temporal_candidates|shared_scene_candidates|review|characters)\//.test(relative)) { res.writeHead(404).end('Not found'); return; }
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
