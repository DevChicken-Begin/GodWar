import test from 'node:test';
import assert from 'node:assert/strict';
import { createAssetServer } from './server.mjs';

test('candidate timelines switch frame counts and restore the original timeline', async (t) => {
  const server = createAssetServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  const nativeFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = nativeFetch; });
  globalThis.fetch = (url, ...rest) => nativeFetch(new URL(url, origin), ...rest);
  globalThis.requestAnimationFrame = () => 0;
  globalThis.Option = class { constructor(text, value) { this.textContent = text; this.value = value; } };
  globalThis.Image = class {
    set src(value) { this.width = 2048; this.height = 2048; queueMicrotask(() => this.onload()); }
    async decode() {}
  };
  class Element {
    constructor(id) { this.id = id; this.value = ''; this.children = []; this.events = {}; this.style = {}; this.className = ''; }
    addEventListener(name, callback) { this.events[name] = callback; }
    setAttribute() {}
    replaceChildren(...children) { this.children = children; if (this.id === 'variant' && children.length) this.value = children[0].value; }
    append(child) { this.children.push(child); }
    add(child) { this.children.push(child); }
    getBoundingClientRect() { return { width: 400, height: 500 }; }
    getContext() { return { clearRect() {}, save() {}, restore() {}, translate() {}, scale() {}, drawImage() {} }; }
  }
  const elements = new Map();
  globalThis.document = {
    getElementById(id) { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); },
    createElement() { return new Element(''); },
  };
  globalThis.window = { addEventListener() {} };
  for (const [id, value] of [['speed', '1'], ['zoom', '1'], ['timing', 'source']]) document.getElementById(id).value = value;
  await import('./app.js');
  const el = (id) => document.getElementById(id);
  for (let i = 0; i < 100 && !el('asset-list').children.length; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.ok(el('asset-list').children.length, 'catalog loaded');
  function select(name) {
    el('search').value = name;
    el('search').events.input();
    const button = el('asset-list').children.find((x) => x.textContent === name);
    assert.ok(button, name);
    button.events.click();
  }
  select('agon');
  assert.equal(el('variant').value, 'measured:agon');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /khung ảnh 475 × 400 px · cao tham chiếu 90 px/);
  assert.equal(el('frame').max, '49');
  select('airpot');
  assert.equal(el('variant').value, 'measured:airpot');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 80 px/);
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 300 * 80 / 144) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 300 * 80 / 144) < 0.01);
  select('aminao');
  assert.equal(el('variant').value, 'measured:aminao');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 70 px/);
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 560 * 70 / 154) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 560 * 70 / 154) < 0.01, 'viewer and scene use the same round-two scale');
  const wrappedFetch = globalThis.fetch;
  const targets = await (await wrappedFetch('/Asset/Character/characters/height-targets.json')).json();
  targets.assets.find((item) => item.id === 'aminao').target_height_px = 71;
  globalThis.fetch = (url, ...args) => String(url).endsWith('/height-targets.json')
    ? Promise.resolve(new Response(JSON.stringify(targets), { status: 200 }))
    : wrappedFetch(url, ...args);
  await el('refresh-size').events.click();
  globalThis.fetch = wrappedFetch;
  assert.match(el('asset-info').textContent, /cao tham chiếu 71 px/);
  assert.match(el('size-feedback').textContent, /Đã cập nhật aminao: 71 px/);
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 560 * 71 / 154) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 560 * 71 / 154) < 0.01, 'refresh applies changed metadata');
  select('crapit');
  assert.equal(el('variant').value, 'measured:crapit_main');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 100 px/);
  el('variant').value = 'measured:crapit_secondary';
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 40 px/);
  assert.equal(el('frame').max, '23');
  for (const [name, last] of [['Trex', '48'], ['ethan', '71'], ['jaying', '20']]) {
    select(name);
    assert.equal(el('variant').value, `measured:${name}`);
    assert.equal(el('frame').max, last);
    assert.equal(el('variant').children.some((option) => option.value === 'batch12_native_candidates'), name !== 'jaying');
  }
  select('momo');
  assert.equal(el('variant').value, 'measured:momo');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 85 px/);
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 948 * 85 / 408) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 948 * 85 / 408) < 0.01, 'momo uses the round-three scale');
  assert.deepEqual(el('variant').children.map(option => option.value), ['extracted', 'measured:momo']);
  el('variant').value = 'detail_oct29_candidates';
  await el('variant').events.change();
  assert.match(el('stage-message').textContent, /đã được thay thế/);
  for (const [name, last] of [['shellhost', '40']]) {
    select(name);
    assert.equal(el('variant').value, `measured:${name}`);
    el('variant').value = 'detail_oct29_candidates';
    await el('variant').events.change();
    assert.match(el('asset-info').textContent, name === 'momo' ? /658 × 658/ : /520 × 520/);
    for (let i = 0; i < 100 && el('canvas').style.width !== (name === 'momo' ? '658px' : '520px'); i++) await new Promise((resolve) => setTimeout(resolve, 20));
    assert.equal(el('canvas').style.width, name === 'momo' ? '658px' : '520px');
    el('variant').value = 'revision_candidates';
    await el('variant').events.change();
    assert.match(el('asset-info').textContent, name === 'momo' ? /506 × 506/ : /520 × 520/);
    el('variant').value = 'scene_spot_candidates';
    await el('variant').events.change();
    assert.match(el('asset-info').textContent, name === 'momo' ? /440 × 440/ : /520 × 520/);
    assert.ok(el('variant').children.some((option) => option.value === 'scene_mask_candidates'));
    assert.equal(el('frame').max, last);
    assert.ok(el('variant').children.some((option) => option.value === 'batch12_detail_candidates'));
  }
  select('conden');
  for (let i = 0; i < 100 && el('frame').max !== '47'; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(el('variant').value, 'measured:conden');
  assert.equal(el('frame').max, '47');
  assert.ok(!el('variant').children.some((option) => option.value === 'measured:conden_tuned'));
  el('variant').value = 'speed_60fps_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '56');
  el('variant').value = 'detail_oct28_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '52');
  assert.match(el('asset-info').textContent, /960 × 720/);
  el('variant').value = 'repaired_v5_candidates';
  await el('variant').events.change();
  assert.equal(el('variant').value, 'repaired_v5_candidates');
  assert.equal(el('frame').max, '55');
  select('dragonot');
  for (let i = 0; i < 100 && el('variant').value !== 'measured:dragonot'; i++) await new Promise((resolve) => setTimeout(resolve, 20));
  await el('variant').events.change();
  assert.equal(el('variant').value, 'measured:dragonot');
  assert.match(el('asset-info').textContent, /cao tham chiếu 100 px/);
  assert.equal(el('frame').max, '48');
  assert.deepEqual(el('variant').children.map(option => option.value), ['extracted', 'measured:dragonot']);
  el('variant').value = 'godot_pilot';
  await el('variant').events.change();
  assert.match(el('stage-message').textContent, /đã được thay thế/);
  select('nox');
  assert.equal(el('variant').value, 'measured:nox');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 87 px/);
  assert.deepEqual(el('variant').children.map(option => option.value), ['extracted', 'measured:nox']);
  el('variant').value = 'detail_oct29_candidates';
  await el('variant').events.change();
  assert.match(el('stage-message').textContent, /đã được thay thế/);
  assert.equal(el('frame').max, '46');
  select('Kahn');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /cao tham chiếu 87 px/);
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 360 * 87 / 211) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 360 * 87 / 211) < 0.01, 'Kahn uses the round-three scale');
  for (const [name, height, last] of [
    ['buffao', 80, 67], ['scosrian', 85, 55], ['dump', 80, 109],
    ['scorpit', 80, 39], ['Domrico', 85, 99], ['hecfaom', 85, 67], ['Impector', 80, 61],
    ['Actem', 85, 65], ['Hatomin', 80, 50], ['Trainxoan', 85, 52], ['urguro', 90, 46],
  ]) {
    select(name);
    assert.equal(el('variant').value, `measured:${name}`);
    await el('variant').events.change();
    assert.match(el('asset-info').textContent, new RegExp(`cao tham chiếu ${height} px`));
    assert.equal(el('frame').max, String(last));
    assert.deepEqual(el('variant').children.map(option => option.value), ['extracted', `measured:${name}`]);
  }
  el('search').value = 'hemsiss';
  el('search').events.input();
  assert.ok(!el('asset-list').children.some((item) => item.textContent === 'hemsiss'));
  select('buffao');
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /khung ảnh 200 × 200 px/);
  let prevented = false;
  el('stage').events.wheel({ deltaY: -1, preventDefault() { prevented = true; } });
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 200 * 80 / 104 * 1.2) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(prevented, 'wheel zoom suppresses page scrolling over the animation');
  assert.equal(el('zoom').value, 'wheel');
  assert.equal(el('wheel-option').textContent, '1.2×');
  assert.equal(el('canvas').width, 200, 'zoom keeps the full source frame');
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 200 * 80 / 104 * 1.2) < 0.01, 'wheel zooms in');
  el('stage').events.wheel({ deltaY: 1, preventDefault() {} });
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 200 * 80 / 104) < 0.01); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 200 * 80 / 104) < 0.01, 'wheel zooms out');
  el('zoom').value = 'fit';
  el('stage').events.wheel({ deltaY: -1, preventDefault() {} });
  for (let i = 0; i < 100 && !(Math.abs(parseFloat(el('canvas').style.width) - 480) < 0.2); i++) await new Promise(resolve => setTimeout(resolve, 20));
  assert.ok(Math.abs(parseFloat(el('canvas').style.width) - 480) < 0.2, 'wheel zoom continues from fitted size');
  el('zoom').value = '1';
  select('moxie');
  assert.equal(el('variant').value, 'measured:moxie_repaired');
  assert.match(el('variant').children.find((option) => option.value === 'measured:moxie_repaired').textContent, /^Đã chốt/);
  assert.match(el('variant').children.find((option) => option.value === 'measured:moxie').textContent, /^Tham khảo cũ/);
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /660 × 250/);
  assert.equal(el('frame').max, '96');
  el('variant').value = 'repaired_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '96');
  assert.match(el('asset-info').textContent, /340 × 250/);
  el('variant').value = 'batch_candidates';
  await el('variant').events.change();
  assert.match(el('asset-info').textContent, /300 × 250/);
  select('blacktiger');
  el('variant').value = 'motion_v2_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '51');
  el('variant').value = 'special_candidates';
  await el('variant').events.change();
  assert.equal(el('frame').max, '25');
});
