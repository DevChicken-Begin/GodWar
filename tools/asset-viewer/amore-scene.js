import { resolveHeightProfile } from './height-profile.mjs';

const canvas = document.getElementById('scene');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const image = (url) => new Promise((resolve, reject) => {
  const result = new Image();
  result.onload = () => resolve(result);
  result.onerror = () => reject(new Error(`Không tải được ${url}`));
  result.src = url;
});
const W = 1920, H = 1080, groundSourceY = 194;
let x = 215, direction = 0, playing = true, index = 0, accumulated = 0, last = null;
let map, pageCache = new Map(), frames, profile, requestId = 0, lastDrawable = null, activeId = null;
const others = [[46, 254], [160, 286], [330, 94], [441, 127], [485, 158]];
function draw() {
  const zoom = Number(document.getElementById('world-zoom').value);
  const height = profile.target_height_px;
  const mapScale = W / 512 * zoom, spriteScale = profile.display_scale * zoom / 0.7;
  const mapX = (canvas.width - 512 * mapScale) / 2, mapY = (H - 352 * mapScale) / 2;
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#78a6cf';
  ctx.fillRect(0, 0, canvas.width, H);
  ctx.drawImage(map, mapX, mapY, 512 * mapScale, 352 * mapScale);
  const wanted = frames[index];
  const cached = pageCache.get(wanted.atlas);
  if (cached?.image) lastDrawable = { frame: wanted, image: cached.image };
  else requestPage(wanted.atlas);
  const keep = new Set([wanted.atlas]);
  for (let step = 1; step < frames.length && keep.size < 3; step++) keep.add(frames[(index + step) % frames.length].atlas);
  for (const page of keep) requestPage(page);
  for (const [page, value] of pageCache) if (!keep.has(page) && value.image) pageCache.delete(page);
  if (!lastDrawable) return;
  const [sx, sy, sw, sh] = lastDrawable.frame.region;
  const positions = document.getElementById('six').checked ? [...others, [x, groundSourceY]] : [[x, groundSourceY]];
  for (const [footX, footY] of positions) {
    ctx.drawImage(lastDrawable.image, sx, sy, sw, sh, mapX + footX * mapScale - profile.anchor_px[0] * spriteScale, mapY + footY * mapScale - profile.anchor_px[1] * spriteScale, sw * spriteScale, sh * spriteScale);
  }
  const method = profile.measurement_kind === 'automatic_alpha_bbox_unreviewed' ? 'mốc alpha' : 'mốc tham chiếu';
  status.textContent = `${frames.length} frame · zoom ${Math.round(zoom * 100)}% · kích thước hiện hành: ${height} px · trên cảnh ≈ ${Math.round(height * zoom / 0.7)} px · ${method}`;
}
function tick(now) {
  if (!frames) { last = null; requestAnimationFrame(tick); return; }
  if (last !== null) {
    const dt = Math.min(now - last, 100);
    if (playing) {
      accumulated += dt * Number(document.getElementById('speed').value);
      while (accumulated >= frames[index].duration_ms) { accumulated -= frames[index].duration_ms; index = (index + 1) % frames.length; }
    }
    x = Math.max(195, Math.min(245, x + direction * dt * 0.22 / (W / 512)));
  }
  last = now;
  draw();
  requestAnimationFrame(tick);
}
function setDirection(value) { direction = value; }
for (const [id, value] of [['left', -1], ['right', 1]]) {
  const button = document.getElementById(id);
  button.addEventListener('pointerdown', (event) => { event.preventDefault(); button.setPointerCapture(event.pointerId); setDirection(value); });
  for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) button.addEventListener(event, () => setDirection(0));
}
window.addEventListener('keydown', (event) => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); setDirection(event.key === 'ArrowLeft' ? -1 : 1); } });
window.addEventListener('keyup', (event) => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') setDirection(0); });
window.addEventListener('blur', () => { setDirection(0); last = null; });
document.getElementById('play').addEventListener('click', (event) => { playing = !playing; event.target.textContent = playing ? 'Tạm dừng' : 'Phát'; last = null; });
const sceneContainer = document.getElementById('scene-container');
const phoneView = document.getElementById('phone-view');
const fitMode = document.getElementById('fit-mode');
function updateFitMode() {
  const expand = fitMode.value === 'expand';
  const cover = fitMode.value === 'cover';
  phoneView.dataset.fit = expand ? 'expand' : cover ? 'cover' : 'contain';
  const canvasWidth = expand ? Math.round(H * 2712 / 1220) : W;
  if (canvas.width !== canvasWidth) canvas.width = canvasWidth;
  document.getElementById('fit-status').textContent = expand
    ? 'Mở rộng khung nhìn sang hai bên (khoảng 2401 × 1080), giữ nguyên tỷ lệ nhân vật và map. Phần ngoài ảnh map hiện chỉ có màu nền.'
    : cover
    ? 'Phủ kín 2712 × 1220: cắt khoảng 108 px ở mỗi cạnh trên và dưới của cảnh gốc 1920 × 1080.'
    : 'Giữ đủ cảnh 1920 × 1080: còn khoảng 272 px viền đen ở mỗi bên màn hình 2712 × 1220.';
  document.getElementById('fullscreen-fit').textContent = `${expand ? 'Mở rộng hai bên' : cover ? 'Phủ kín' : 'Giữ đủ cảnh'} · đổi cách fit`;
}
fitMode.addEventListener('change', updateFitMode);
document.getElementById('fullscreen-fit').addEventListener('click', () => {
  fitMode.value = fitMode.value === 'expand' ? 'contain' : fitMode.value === 'contain' ? 'cover' : 'expand';
  updateFitMode();
});
updateFitMode();
document.getElementById('fullscreen').addEventListener('click', async () => {
  const feedback = document.getElementById('fullscreen-status');
  if (!sceneContainer.requestFullscreen) {
    feedback.textContent = 'Trình duyệt không hỗ trợ toàn màn hình; hãy thử Chrome và xoay ngang điện thoại.';
    return;
  }
  try {
    await sceneContainer.requestFullscreen();
    if (globalThis.screen?.orientation?.lock) {
      try { await globalThis.screen.orientation.lock('landscape'); } catch { /* Manual rotation remains available. */ }
    }
    feedback.textContent = 'Đang xem toàn màn hình. Nếu hình vẫn dọc, hãy bật tự xoay và xoay ngang điện thoại.';
  } catch {
    feedback.textContent = 'Không mở được toàn màn hình; hãy thử Chrome và cho phép xoay màn hình.';
  }
});
document.getElementById('exit-fullscreen').addEventListener('click', async () => {
  if (document.fullscreenElement && document.exitFullscreen) await document.exitFullscreen();
  if (globalThis.screen?.orientation?.unlock) globalThis.screen.orientation.unlock();
});
async function loadCharacter(id) {
  const request = ++requestId;
  document.getElementById('size-feedback').textContent = '';
  frames = null;
  last = null;
  lastDrawable = null;
  pageCache = new Map();
  status.textContent = 'Đang tải atlas nhân vật…';
  const root = `/Asset/Character/measured_atlas_pilots/${encodeURIComponent(id)}`;
  const [response, targetResponse] = await Promise.all([
    fetch(`${root}/candidate.json`, { cache: 'no-store' }),
    fetch('/Asset/Character/characters/height-targets.json', { cache: 'no-store' }),
  ]);
  if (!response.ok || !targetResponse.ok) throw new Error('Không tải được kích thước hoặc metadata atlas.');
  const raw = await response.json();
  const targets = new Map((await targetResponse.json()).assets.map((item) => [item.id, item]));
  const data = resolveHeightProfile(raw, targets);
  const firstPage = data.frames[0].atlas;
  const firstImage = await image(`${root}/atlas_${String(firstPage).padStart(3, '0')}.png`);
  if (request !== requestId) return;
  profile = data; profile.atlas_root = root; pageCache.set(firstPage, { image: firstImage }); frames = data.frames; activeId = id;
  index = 0; accumulated = 0; last = null;
}
function requestPage(page) {
  if (pageCache.has(page) || !profile) return;
  if ([...pageCache.values()].filter((entry) => !entry.image).length >= 3) return;
  const cache = pageCache;
  const request = requestId;
  const entry = { image: null };
  cache.set(page, entry);
  image(`${profile.atlas_root}/atlas_${String(page).padStart(3, '0')}.png`).then((loaded) => {
    if (request === requestId && cache.get(page) === entry) entry.image = loaded;
  }).catch(() => {
    if (request === requestId && cache.get(page) === entry) { cache.delete(page); status.textContent = `Không tải được atlas ${page}.`; }
  });
}
document.getElementById('character').addEventListener('change', (event) =>
  loadCharacter(event.target.value).catch((error) => { status.textContent = error.message; }));
async function refreshSize(showFeedback = false) {
  const feedback = document.getElementById('size-feedback');
  if (!frames || !activeId) { if (showFeedback) feedback.textContent = 'Nhân vật chưa tải xong.'; return; }
  const id = activeId, request = requestId;
  try {
    if (showFeedback) feedback.textContent = 'Đang cập nhật…';
    const [response, targetResponse] = await Promise.all([
      fetch(`/Asset/Character/measured_atlas_pilots/${encodeURIComponent(id)}/candidate.json`, { cache: 'no-store' }),
      fetch('/Asset/Character/characters/height-targets.json', { cache: 'no-store' }),
    ]);
    if (!response.ok || !targetResponse.ok) throw new Error('Không cập nhật được kích thước.');
    const raw = await response.json();
    const targets = new Map((await targetResponse.json()).assets.map((item) => [item.id, item]));
    const data = resolveHeightProfile(raw, targets);
    if (request !== requestId || id !== activeId || !frames) return;
    profile.display_scale = data.display_scale;
    profile.target_height_px = data.target_height_px;
    profile.measurement_kind = data.measurement_kind;
    if (showFeedback) feedback.textContent = `Đã cập nhật ${id}: ${data.target_height_px} px.`;
  } catch (error) { if (showFeedback) feedback.textContent = error.message; else status.textContent = error.message; }
}
document.getElementById('refresh-size').addEventListener('click', () => refreshSize(true));
window.addEventListener('focus', () => refreshSize(false));
try {
  const [background, response, approvedResponse] = await Promise.all([image('/Asset/Scenes/amore_scale_test/map.png'), fetch('/api/measured-atlases'), fetch('/Asset/Character/characters/approved-animations-20261029.json')]);
  if (!response.ok || !approvedResponse.ok) throw new Error('Không tải được catalog hoạt ảnh đã chốt');
  const available = new Set(await response.json());
  const approved = await approvedResponse.json();
  const names = approved.assets.flatMap((asset) => asset.profiles.map((profile) => profile.id));
  if (names.some((name) => !available.has(name))) throw new Error('Thiếu atlas hoạt ảnh đã chốt');
  const select = document.getElementById('character');
  select.replaceChildren(...names.sort().map((name) => new Option(name, name)));
  select.value = names.includes('amore') ? 'amore' : names[0];
  if (!select.value) throw new Error('Chưa có atlas đã đo.');
  map = background;
  await loadCharacter(select.value);
  requestAnimationFrame(tick);
} catch (error) { status.textContent = error.message; }
