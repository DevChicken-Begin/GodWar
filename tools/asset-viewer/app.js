const $ = (id) => document.getElementById(id);
const state = { assets: [], candidates: new Set(), refined: new Set(), cleanup: new Set(), batch: new Set(), special: new Set(), temporal: new Set(), sharedScene: new Set(), quality: new Map(), reviews: new Map(), audits: new Map(), selected: null, index: 0, rangeStart: 0, rangeEnd: 0, playing: true, lastTick: null, elapsed: 0, generation: 0, cache: new Map() };
const context = $('canvas').getContext('2d');
const pathPart = (value) => encodeURIComponent(value);

function listAssets() {
  const query = $('search').value.trim().toLocaleLowerCase();
  const matches = state.assets.filter((asset) => asset.id.toLocaleLowerCase().includes(query));
  $('count').textContent = `${matches.length} / ${state.assets.length}`;
  const list = $('asset-list');
  list.replaceChildren();
  if (!matches.length) { const p = document.createElement('p'); p.className = 'empty'; p.textContent = 'Không tìm thấy GIF phù hợp.'; list.append(p); return; }
  for (const asset of matches) {
    const button = document.createElement('button');
    button.className = `asset-item${state.selected?.id === asset.id ? ' active' : ''}`;
    button.textContent = asset.id;
    button.setAttribute('aria-pressed', String(state.selected?.id === asset.id));
    button.addEventListener('click', () => selectAsset(asset));
    list.append(button);
  }
}

function selectAsset(asset) {
  state.selected = asset;
  state.index = 0;
  state.elapsed = 0;
  state.lastTick = null;
  state.cache.clear();
  $('asset-name').textContent = asset.id;
  $('asset-info').textContent = `${asset.frame_count} frame · ${asset.size[0]} × ${asset.size[1]} px · ${asset.source}`;
  $('source-link').href = `/${asset.source.split('/').map(pathPart).join('/')}`;
  $('source-link').hidden = false;
  state.rangeStart = 0; state.rangeEnd = asset.frames.length - 1;
  $('frame').min = '0'; $('frame').max = String(state.rangeEnd);
  $('segment-start').max = String(state.rangeEnd); $('segment-start').value = '0';
  $('segment-end').max = String(state.rangeEnd); $('segment-end').value = String(state.rangeEnd);
  $('segment-message').textContent = '';
  $('variant').replaceChildren(new Option('Atlas nguồn', 'extracted'));
  const atlasId = asset.atlasId || asset.id;
  if (state.candidates.has(atlasId)) $('variant').add(new Option('Tách nền viền · chưa duyệt', 'candidates'));
  if (state.refined.has(atlasId)) $('variant').add(new Option('Tách nền nâng cao · chưa duyệt', 'refined_candidates'));
  if (state.cleanup.has(atlasId)) $('variant').add(new Option('Lọc nền mạnh · chưa duyệt', 'cleanup_candidates'));
  if (state.batch.has(atlasId)) $('variant').add(new Option('Tách nền theo màu · chưa duyệt', 'batch_candidates'));
  if (state.special.has(atlasId)) $('variant').add(new Option('Xử lý nền riêng · chưa duyệt', 'special_candidates'));
  if (state.temporal.has(atlasId)) $('variant').add(new Option('Trừ nền cảnh · chưa duyệt', 'temporal_candidates'));
  if (state.sharedScene.has(atlasId)) $('variant').add(new Option('Đối chiếu nền chung · chưa duyệt', 'shared_scene_candidates'));
  if (state.special.has(atlasId)) $('variant').value = 'special_candidates';
  else if (state.cleanup.has(atlasId) && atlasId === 'aminao') $('variant').value = 'cleanup_candidates';
  else if (state.sharedScene.has(atlasId)) $('variant').value = 'shared_scene_candidates';
  else if (state.temporal.has(atlasId)) $('variant').value = 'temporal_candidates';
  else if (state.batch.has(atlasId)) $('variant').value = 'batch_candidates';
  else if (state.refined.has(atlasId)) $('variant').value = 'refined_candidates';
  else if (state.candidates.has(atlasId)) $('variant').value = 'candidates';
  const sourceId = asset.source.split('/').pop().replace(/\.gif$/i, '');
  const audit = state.audits.get(sourceId);
  const auditLabels = {transparent_all_frames: 'Nguồn có trong suốt ở mọi frame', mixed_transparency: 'Nguồn có độ trong suốt không đồng nhất', solid_border_candidate: 'Nền viền phẳng; cần duyệt tách nền', complex_or_varying_border: 'Nền phức tạp hoặc thay đổi; cần xử lý riêng'};
  if (audit) $('asset-info').textContent += ` · ${auditLabels[audit.category] || 'Chưa kiểm tra nền'}`;
  const review = state.reviews.get(asset.source);
  const box = $('observations');
  box.replaceChildren();
  if (review?.observations?.length) {
    const title = document.createElement('strong'); title.textContent = 'Ghi chú kiểm duyệt bước đầu'; box.append(title);
    const list = document.createElement('ul');
    for (const observation of review.observations) {
      const item = document.createElement('li');
      item.textContent = `Frame ${observation.frames.join('–')}: ${observation.observation}`;
      list.append(item);
    }
    box.append(list);
  } else { box.textContent = 'Nguồn này chưa có ghi chú kiểm duyệt.'; }
  listAssets();
  render();
}

function loadPage(url) {
  if (!state.cache.has(url)) {
    const promise = new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error('Không tải được atlas.'));
      image.src = url;
    });
    state.cache.set(url, promise);
    promise.catch(() => state.cache.delete(url));
  }
  return state.cache.get(url);
}

async function render() {
  const version = ++state.generation;
  const asset = state.selected;
  if (!asset) return;
  const frame = asset.frames[state.index];
  const variant = $('variant').value;
  $('frame').value = String(state.index);
  $('frame-label').textContent = `Frame ${state.index + 1} / ${asset.frames.length} (chỉ số ${state.index}${asset.sourceStart ? ` · frame nguồn ${state.index + asset.sourceStart}` : ''})`;
  $('duration-label').textContent = `${frame.duration_ms} ms`;
  $('play').textContent = state.playing ? 'Tạm dừng' : 'Phát';
  $('note').textContent = variant === 'extracted'
    ? 'Atlas nguồn có thể bao gồm nền, nhân vật và VFX trong cùng một ảnh. Vòng lặp tại đây dùng để xem liên tục.'
    : 'Bản thử xóa nền chưa duyệt: có thể còn nền hoặc mất chi tiết nhân vật/VFX. Hãy so với atlas nguồn.';
  const quality = state.quality.get(asset.source.split('/').pop().replace(/\.gif$/i, ''));
  if (quality) $('note').textContent += ` ${quality.issue}`;
  const url = `/Asset/Character/${variant}/${pathPart(asset.atlasId || asset.id)}/atlas_${String(frame.atlas).padStart(3, '0')}.png`;
  try {
    const image = await loadPage(url);
    if (version !== state.generation) return;
    const [x, y, width, height] = frame.region;
    const canvas = $('canvas'); canvas.width = width; canvas.height = height;
    const zoom = $('zoom').value;
    canvas.style.width = zoom === 'fit' ? '100%' : `${width * Number(zoom)}px`;
    canvas.style.height = zoom === 'fit' ? '100%' : 'auto';
    context.imageSmoothingEnabled = false;
    context.save();
    if ($('flip').checked) { context.translate(width, 0); context.scale(-1, 1); }
    context.drawImage(image, x, y, width, height, 0, 0, width, height);
    context.restore();
    $('stage-message').hidden = true;
    // Load the next atlas in advance; keep only the current and next pages.
    let nextPage = frame.atlas;
    for (let offset = 1; offset < asset.frames.length; offset++) {
      const page = asset.frames[(state.index + offset) % asset.frames.length].atlas;
      if (page !== frame.atlas) { nextPage = page; break; }
    }
    const nextUrl = `/Asset/Character/${variant}/${pathPart(asset.atlasId || asset.id)}/atlas_${String(nextPage).padStart(3, '0')}.png`;
    if (nextUrl !== url) loadPage(nextUrl).catch(() => {});
    for (const key of state.cache.keys()) if (key !== url && key !== nextUrl) state.cache.delete(key);
  } catch (error) {
    if (version !== state.generation) return;
    $('stage-message').textContent = `${error.message} ${url}`;
    $('stage-message').hidden = false;
  }
}

$('apply-segment').addEventListener('click', () => {
  if (!state.selected) return;
  const start = Number($('segment-start').value), end = Number($('segment-end').value);
  if ($('segment-start').value === '' || $('segment-end').value === '' || !Number.isInteger(start) || !Number.isInteger(end) || start < 0 || end < start || end >= state.selected.frames.length) {
    $('segment-message').textContent = 'Khoảng frame không hợp lệ.'; return;
  }
  $('segment-message').textContent = '';
  state.rangeStart = start; state.rangeEnd = end; state.index = start;
  state.elapsed = 0; state.lastTick = null;
  $('frame').min = String(start); $('frame').max = String(end);
  render();
});
$('reset-segment').addEventListener('click', () => {
  if (!state.selected) return;
  $('segment-start').value = '0'; $('segment-end').value = String(state.selected.frames.length - 1);
  $('apply-segment').click();
});
$('search').addEventListener('input', listAssets);
$('play').addEventListener('click', () => { state.playing = !state.playing; state.lastTick = null; state.elapsed = 0; render(); });
for (const [id, delta] of [['previous', -1], ['next', 1]]) $(id).addEventListener('click', () => {
  if (!state.selected) return;
  state.playing = false;
  state.elapsed = 0;
  state.lastTick = null;
  state.index = state.rangeStart + ((state.index - state.rangeStart + delta + (state.rangeEnd - state.rangeStart + 1)) % (state.rangeEnd - state.rangeStart + 1));
  render();
});
$('frame').addEventListener('input', (event) => { state.index = Number(event.target.value); state.playing = false; state.elapsed = 0; state.lastTick = null; render(); });
$('speed').addEventListener('change', () => { state.lastTick = null; state.elapsed = 0; render(); });
$('zoom').addEventListener('change', render);
$('variant').addEventListener('change', render);
$('flip').addEventListener('change', render);
$('background').addEventListener('change', (event) => { $('stage').className = `stage ${event.target.value}`; });

async function init() {
  try {
    const [catalogResponse, candidatesResponse, inventoryResponse, auditResponse, refinedResponse, splitsResponse, cleanupResponse, batchResponse, specialResponse, temporalResponse, qualityResponse, sharedSceneResponse] = await Promise.all([
      fetch('/Asset/Character/extracted/catalog.json'), fetch('/api/candidates'), fetch('/Asset/Character/review/inventory.json'), fetch('/Asset/Character/review/background-audit.json'), fetch('/api/refined-candidates'), fetch('/Asset/Character/extracted/split-catalog.json'), fetch('/api/cleanup-candidates'), fetch('/api/batch-candidates'), fetch('/api/special-candidates'), fetch('/api/temporal-candidates'), fetch('/Asset/Character/review/background-review-status.json'), fetch('/api/shared-scene-candidates')
    ]);
    if (!catalogResponse.ok) throw new Error('Không tìm thấy catalog. Chạy công cụ tách GIF trước.');
    const catalog = await catalogResponse.json();
    state.assets = catalog.assets;
    if (candidatesResponse.ok) state.candidates = new Set(await candidatesResponse.json());
    if (refinedResponse.ok) state.refined = new Set(await refinedResponse.json());
    if (cleanupResponse.ok) state.cleanup = new Set(await cleanupResponse.json());
    if (batchResponse.ok) state.batch = new Set(await batchResponse.json());
    if (specialResponse.ok) state.special = new Set(await specialResponse.json());
    if (temporalResponse.ok) state.temporal = new Set(await temporalResponse.json());
    if (sharedSceneResponse.ok) state.sharedScene = new Set(await sharedSceneResponse.json());
    if (qualityResponse.ok) state.quality = new Map((await qualityResponse.json()).sources.map((item) => [item.id, item]));
    if (splitsResponse.ok) state.assets.push(...(await splitsResponse.json()).assets);
    if (inventoryResponse.ok) state.reviews = new Map((await inventoryResponse.json()).sources.map((item) => [item.source, item]));
    if (auditResponse.ok) state.audits = new Map((await auditResponse.json()).sources.map((item) => [item.id, item]));
    if (!state.assets.length) throw new Error('Catalog không có GIF nào.');
    selectAsset(state.assets[0]);
  } catch (error) {
    $('stage-message').hidden = false;
    $('stage-message').textContent = error.message;
    $('count').textContent = 'Không thể tải';
  }
}
// Wall-clock playback keeps original frame delays without adding image decode/render time.
function tick(now) {
  if (state.playing && state.selected) {
    if (state.lastTick !== null) {
      state.elapsed += Math.min(now - state.lastTick, 1000) * Number($('speed').value);
      let advanced = false;
      while (state.elapsed >= Math.max(state.selected.frames[state.index].duration_ms, 10)) {
        state.elapsed -= Math.max(state.selected.frames[state.index].duration_ms, 10);
        state.index = state.index >= state.rangeEnd ? state.rangeStart : state.index + 1;
        advanced = true;
      }
      if (advanced) render();
    }
    state.lastTick = now;
  } else state.lastTick = null;
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
init();
