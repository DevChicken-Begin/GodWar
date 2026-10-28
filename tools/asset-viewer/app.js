import { renderFrame } from './render-frame.mjs';
import { frameDuration } from './timing.mjs';

const $ = (id) => document.getElementById(id);
const state = { assets: [], candidates: new Set(), refined: new Set(), cleanup: new Set(), batch: new Set(), special: new Set(), temporal: new Set(), sharedScene: new Set(), detailed: new Set(), foot: new Set(), sceneDetail: new Set(), remainingScene: new Set(), spots: new Set(), pixel: new Set(), pixel120: new Set(), native: new Set(), oct28: new Set(), pixel180: new Set(), scorpitRepair: new Set(), logos: new Set(), protectedScene: new Set(), pixel220: new Set(), sharp: new Set(), scorpitRepair18: new Set(), fine: new Set(), detail130: new Set(), detailOct28: new Set(), speedOct28: new Set(), speed60fps: new Set(), conden60fps: new Set(), tune60fps: new Set(), batch12Native: new Set(), batch12Detail: new Set(), sceneMask: new Set(), sceneMaskDeep: new Set(), sceneMaskDeeper: new Set(), sceneSpot: new Set(), revision: new Set(), fireSpeck: new Set(), fireOrphan: new Set(), fireDeep: new Set(), motionV2: new Set(), repaired: new Set(), repairedV2: new Set(), repairedV5: new Set(), baseSelected: null, variantRequest: 0, quality: new Map(), reviews: new Map(), audits: new Map(), selected: null, index: 0, rangeStart: 0, rangeEnd: 0, playing: true, lastTick: null, elapsed: 0, generation: 0, cache: new Map() };
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
  state.variantRequest++;
  state.baseSelected = asset;
  state.selected = asset;
  $('timing').value = 'source';
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
  if (state.detailed.has(atlasId)) $('variant').add(new Option('Xử lý chi tiết · chưa duyệt', 'detailed_candidates'));
  if (state.foot.has(atlasId)) $('variant').add(new Option('Xử lý vùng chân · chưa duyệt', 'foot_candidates'));
  if (state.sceneDetail.has(atlasId)) $('variant').add(new Option('Xử lý nền xanh chi tiết · chưa duyệt', 'scene_detail_v3_candidates'));
  if (state.remainingScene.has(atlasId)) $('variant').add(new Option('Xử lý nền xanh bổ sung · chưa duyệt', 'remaining_scene_candidates'));
  if (state.spots.has(atlasId)) $('variant').add(new Option('Sửa điểm nền cục bộ · chưa duyệt', 'spot_candidates'));
  if (state.pixel.has(atlasId)) $('variant').add(new Option('Pixel hóa · chưa duyệt', 'pixel_candidates'));
  if (state.pixel120.has(atlasId)) $('variant').add(new Option('Pixel chi tiết hơn · chưa duyệt', 'pixel_120_candidates'));
  if (state.native.has(atlasId)) $('variant').add(new Option('Tách nền nguyên kích thước · chưa duyệt', 'native_candidates'));
  if (state.oct28.has(atlasId)) $('variant').add(new Option('Sửa cục bộ mới · chưa duyệt', 'oct28_fix_candidates'));
  if (state.pixel180.has(atlasId)) $('variant').add(new Option('Pixel thêm 50% · chưa duyệt', 'pixel_180_candidates'));
  if (state.scorpitRepair.has(atlasId)) $('variant').add(new Option('Phục hồi chữ frame 19 · chưa duyệt', 'scorpit_repair_candidates'));
  if (state.logos.has(atlasId)) $('variant').add(new Option('Tách chữ · chưa duyệt', 'logo_candidates'));
  if (state.protectedScene.has(atlasId)) $('variant').add(new Option('Tách nền cảnh · chưa duyệt', 'scene_protected_candidates'));
  if (state.pixel220.has(atlasId)) $('variant').add(new Option('Chi tiết nét hơn · chưa duyệt', 'pixel_220_candidates'));
  if (state.sharp.has(atlasId)) $('variant').add(new Option('Độ nét +20% · chưa duyệt', 'sharp_candidates'));
  if (state.scorpitRepair18.has(atlasId)) $('variant').add(new Option('Phục hồi chữ frame 18–20 · chưa duyệt', 'scorpit_repair18_candidates'));
  if (state.fine.has(atlasId)) $('variant').add(new Option('Pixel mịn thử · chưa duyệt', 'fine_candidates'));
  if (state.motionV2.has(atlasId)) $('variant').add(new Option('Chuyển động nội suy · chưa duyệt', 'motion_v2_candidates'));
  if (state.repairedV5.has(atlasId)) $('variant').add(new Option('Conden tên đầy đủ · tăng tốc', 'repaired_v5_candidates'));
  if (state.repairedV2.has(atlasId)) $('variant').add(new Option('Conden mũi tên bay · 70 ms', 'repaired_v2_candidates'));
  if (state.repaired.has(atlasId)) $('variant').add(new Option(atlasId === 'moxie' ? 'Phục dựng vật thể · chưa duyệt' : 'Thêm đường bay · chưa duyệt', 'repaired_candidates'));
  if (state.fireDeep.has(atlasId)) $('variant').add(new Option('Fireknight lọc sâu · chưa duyệt', 'fire_deep_candidates'));
  if (state.fireOrphan.has(atlasId)) $('variant').add(new Option('Fireknight lọc điểm lẻ · chưa duyệt', 'fire_orphan_candidates'));
  if (state.fireSpeck.has(atlasId)) $('variant').add(new Option('Fireknight lọc đốm thử · chưa duyệt', 'fire_speck_candidates'));
  if (state.revision.has(atlasId)) $('variant').add(new Option(atlasId === 'momo' ? 'Mịn thử, lớn thêm 15% · chưa duyệt' : 'Sửa đốm chân frame 36 · chưa duyệt', 'revision_candidates'));
  if (state.sceneSpot.has(atlasId)) $('variant').add(new Option(atlasId === 'momo' ? 'Sửa đốm, phóng to 10% · chưa duyệt' : 'Sửa vệt frame 37 · chưa duyệt', 'scene_spot_candidates'));
  if (state.sceneMaskDeeper.has(atlasId)) $('variant').add(new Option('Lọc xanh sâu hơn · chưa duyệt', 'scene_mask_deeper_candidates'));
  if (state.sceneMaskDeep.has(atlasId)) $('variant').add(new Option('Lọc xanh hai tham chiếu · chưa duyệt', 'scene_mask_deep_candidates'));
  if (state.sceneMask.has(atlasId)) $('variant').add(new Option('Lọc nền xanh bổ sung · chưa duyệt', 'scene_mask_candidates'));
  if (state.batch12Native.has(atlasId)) $('variant').add(new Option('Lô mới · tách nền gốc · chưa duyệt', 'batch12_native_candidates'));
  if (state.batch12Detail.has(atlasId)) $('variant').add(new Option('Lô mới · nội suy 120% · chưa duyệt', 'batch12_detail_candidates'));
  if (state.tune60fps.has(atlasId)) $('variant').add(new Option(atlasId === 'conden' ? 'Tên bay đều · 60 FPS · thử' : 'Tốc độ ×2 · 60 FPS · thử', 'tune_60fps_candidates'));
  if (state.conden60fps.has(atlasId)) $('variant').add(new Option('Tên bay liên tục · 60 FPS · thử', 'conden_60fps_candidates'));
  if (state.speed60fps.has(atlasId)) $('variant').add(new Option(atlasId === 'conden' ? 'Tên bay 60 FPS · thử' : 'Tốc độ ×3 · 60 FPS · thử', 'speed_60fps_candidates'));
  if (state.speedOct28.has(atlasId)) $('variant').add(new Option(atlasId === 'conden' ? 'Tên bay ×100 · thử' : 'Tốc độ cơ bản ×5 · thử', 'speed_oct28_candidates'));
  if (state.detailOct28.has(atlasId)) $('variant').add(new Option(atlasId === 'dragonmout' ? 'Độ phân giải +40% · chưa duyệt' : 'Độ phân giải +20% · chưa duyệt', 'detail_oct28_candidates'));
  if (state.detail130.has(atlasId)) $('variant').add(new Option('Thử nội suy 130% · chưa duyệt', 'detail_130_candidates'));
  if (atlasId === 'tigerknight' && state.detail130.has(atlasId)) $('variant').add(new Option('Tigerknight lọc nền toàn bộ · chưa duyệt', 'tiger_clean_all_130'));
  if (atlasId === 'tigerknight' && state.detail130.has(atlasId)) $('variant').add(new Option('Tigerknight sửa nền frame 64 · chưa duyệt', 'tiger_clean_130'));
  if (state.revision.has(atlasId)) $('variant').value = 'revision_candidates';
  else if (state.sceneSpot.has(atlasId)) $('variant').value = 'scene_spot_candidates';
  else if (state.sceneMaskDeeper.has(atlasId)) $('variant').value = 'scene_mask_deeper_candidates';
  else if (state.sceneMaskDeep.has(atlasId)) $('variant').value = 'scene_mask_deep_candidates';
  else if (state.sceneMask.has(atlasId)) $('variant').value = 'scene_mask_candidates';
  else if (state.batch12Detail.has(atlasId)) $('variant').value = 'batch12_detail_candidates';
  else if (state.tune60fps.has(atlasId)) $('variant').value = 'tune_60fps_candidates';
  else if (state.conden60fps.has(atlasId)) $('variant').value = 'conden_60fps_candidates';
  else if (state.speed60fps.has(atlasId)) $('variant').value = 'speed_60fps_candidates';
  else if (state.speedOct28.has(atlasId)) $('variant').value = 'speed_oct28_candidates';
  else if (state.detailOct28.has(atlasId)) $('variant').value = 'detail_oct28_candidates';
  else if (atlasId === 'conden' && state.repairedV5.has(atlasId)) $('variant').value = 'repaired_v5_candidates';
  else if (atlasId === 'conden' && state.repairedV2.has(atlasId)) $('variant').value = 'repaired_v2_candidates';
  else if (atlasId === 'tigerknight' && state.detail130.has(atlasId)) $('variant').value = 'tiger_clean_all_130';
  else if (state.fireDeep.has(atlasId)) $('variant').value = 'fire_deep_candidates';
  else if (state.detail130.has(atlasId)) $('variant').value = 'detail_130_candidates';
  else if (state.fine.has(atlasId)) $('variant').value = 'fine_candidates';
  else if (state.pixel220.has(atlasId)) $('variant').value = 'pixel_220_candidates';
  else if (state.sharp.has(atlasId)) $('variant').value = 'sharp_candidates';
  else if (state.scorpitRepair18.has(atlasId)) $('variant').value = 'scorpit_repair18_candidates';
  else if (state.logos.has(atlasId)) $('variant').value = 'logo_candidates';
  else if (state.protectedScene.has(atlasId)) $('variant').value = 'scene_protected_candidates';
  else if (state.pixel180.has(atlasId)) $('variant').value = 'pixel_180_candidates';
  else if (state.scorpitRepair.has(atlasId)) $('variant').value = 'scorpit_repair_candidates';
  else if (state.pixel120.has(atlasId)) $('variant').value = 'pixel_120_candidates';
  else if (state.native.has(atlasId)) $('variant').value = 'native_candidates';
  else if (state.oct28.has(atlasId)) $('variant').value = 'oct28_fix_candidates';
  else if (state.pixel.has(atlasId)) $('variant').value = 'pixel_candidates';
  else if (state.spots.has(atlasId)) $('variant').value = 'spot_candidates';
  else if (state.remainingScene.has(atlasId)) $('variant').value = 'remaining_scene_candidates';
  else if (state.sceneDetail.has(atlasId)) $('variant').value = 'scene_detail_v3_candidates';
  else if (state.foot.has(atlasId)) $('variant').value = 'foot_candidates';
  else if (state.detailed.has(atlasId)) $('variant').value = 'detailed_candidates';
  else if (state.special.has(atlasId)) $('variant').value = 'special_candidates';
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
  if (['repaired_v2_candidates', 'repaired_v5_candidates', 'detail_oct28_candidates', 'speed_oct28_candidates', 'speed_60fps_candidates', 'conden_60fps_candidates', 'tune_60fps_candidates', 'scene_spot_candidates', 'revision_candidates'].includes($('variant').value)) void applyVariant();
  else render();
}

function loadPage(url) {
  if (!state.cache.has(url)) {
    const promise = new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = async () => {
        try {
          // Preloading is useful only if decoding finishes before the page is used.
          if (image.decode) await image.decode();
          resolve(image);
        } catch { reject(new Error('Không giải mã được atlas.')); }
      };
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
  $('frame-label').textContent = `Frame ${state.index + 1} / ${asset.frames.length} (chỉ số ${state.index}${frame.source_index !== undefined ? ` · frame nguồn ${frame.source_index + 1}` : asset.sourceStart ? ` · frame nguồn ${state.index + asset.sourceStart}` : ''})`;
  const duration = frameDuration(frame, $('timing').value);
  const durationText = (ms) => String(Math.round(ms * 100) / 100);
  $('duration-label').textContent = $('timing').value !== 'source' ? `${durationText(duration)} ms · thử (nguồn ${durationText(frame.duration_ms)} ms)` : `${durationText(duration)} ms`;
  $('play').textContent = state.playing ? 'Tạm dừng' : 'Phát';
  $('note').textContent = variant === 'extracted'
    ? 'Atlas nguồn có thể bao gồm nền, nhân vật và VFX trong cùng một ảnh. Vòng lặp tại đây dùng để xem liên tục.'
    : 'Bản thử xóa nền chưa duyệt: có thể còn nền hoặc mất chi tiết nhân vật/VFX. Hãy so với atlas nguồn.';
  if (variant === 'fine_candidates' || variant === 'detail_130_candidates') $('note').textContent = 'Bản thử làm mịn cạnh chưa duyệt: có thể thay đổi viền hoặc VFX; bản nền đầu vào cũng có thể còn lỗi. Hãy so với phiên bản trước và atlas nguồn.';
  if (variant === 'detail_130_candidates') $('note').textContent += ' Viewer dùng frame nội suy 130% và giữ kích thước hiển thị; nội suy không tạo thêm chi tiết gốc.';
  if (variant === 'detail_oct28_candidates') $('note').textContent = 'Bản nội suy tăng độ phân giải, giữ kích thước hiển thị; không tạo thêm chi tiết nguồn. Cần so sánh viền, hiệu ứng và chuyển động.';
  if (variant === 'revision_candidates') $('note').textContent = asset.id === 'momo' ? 'Bản thử tăng kích thước 15%, tăng mật độ pixel 20% và làm mềm viền. Không khôi phục chi tiết nguồn.' : 'Loại đốm theo mẫu frame 36 khi vùng ảnh khớp hoàn toàn; cần duyệt khi phát.';
  if (variant === 'scene_spot_candidates') $('note').textContent = asset.id === 'momo' ? 'Sửa đốm theo mẫu và tăng toàn bộ canvas 10%; khớp chân theo neo giữa đáy. Cần duyệt chuyển động.' : 'Sửa vệt xanh quanh frame 37, giữ khoảng bảo vệ sát nhân vật. Cần duyệt viền và hiệu ứng.';
  if (['scene_mask_deep_candidates', 'scene_mask_deeper_candidates'].includes(variant)) $('note').textContent = 'Lọc xanh theo tham chiếu chưa duyệt; màu nền trùng nhân vật/VFX có thể bị xóa. So từng frame với bản trước trên nền sáng và tối.';
  if (variant === 'scene_mask_candidates') $('note').textContent = 'Bản lọc xanh bổ sung chưa duyệt; màu nền có thể trùng nhân vật/VFX. So với bản trước trên nền sáng và tối.';
  if (variant === 'batch12_detail_candidates' || variant === 'batch12_native_candidates') $('note').textContent = 'Bản tách nền và chữ chưa duyệt: có thể còn nền hoặc mất chi tiết/VFX. Nội suy 120% không tạo chi tiết gốc.';
  if (variant === 'tune_60fps_candidates') $('note').textContent = asset.id === 'conden' ? 'Tên bay đều theo nhịp 60 FPS; cần kiểm tra khi phát.' : 'Tốc độ khoảng 2× bản gốc; thời lượng căn theo nhịp 60 FPS.';
  if (variant === 'conden_60fps_candidates') $('note').textContent = 'Tên tiếp tục bay qua từng nhịp 60 FPS; thân tên được phục dựng và cần duyệt khi phát.';
  if (variant === 'speed_60fps_candidates') $('note').textContent = asset.id === 'conden' ? 'Tên có 9 vị trí, mỗi vị trí một nhịp 60 FPS; cần kiểm tra khi phát.' : 'Tốc độ khoảng 3×; thời lượng căn theo nhịp 60 FPS.';
  if (variant === 'speed_oct28_candidates') $('note').textContent = asset.id === 'conden' ? 'Tên bay nhanh gấp 100 lần; có thể không nhìn thấy ở tần số màn hình thông thường.' : 'Tốc độ cơ bản nhanh gấp 5; có thể bỏ qua frame trên thiết bị.';
  if (variant === 'motion_v2_candidates') $('note').textContent = 'Frame xen giữa được nội suy chuyển động; có thể biến dạng hoặc giật ở đoạn thay đổi nhanh. Tổng thời gian vẫn theo nguồn.';
  if (variant === 'repaired_candidates' || variant === 'repaired_v2_candidates' || variant === 'repaired_v5_candidates') $('note').textContent = asset.id === 'moxie' ? 'Phần vật thể ngoài mép GIF được phục dựng từ frame trước; cần kiểm tra đường bay và hình dáng.' : 'Đường bay được dựng từ hiệu ứng nguồn; frame thêm là tổng hợp và cần kiểm tra khi phát.';
  if (variant === 'tiger_clean_all_130') $('note').textContent = 'Bản thử lọc xanh toàn bộ frame; màu xanh có thể trùng chi tiết nhân vật hoặc hiệu ứng. Hãy so với bản trước.';
  if (variant === 'tiger_clean_130') $('note').textContent = 'Bản thử giữ độ chi tiết 130% và lọc xanh ở chỉ số 63–64. Màu xanh có thể trùng chi tiết nhân vật; cần so với bản trước.';
  if (variant === 'fire_speck_candidates' || variant === 'fire_orphan_candidates' || variant === 'fire_deep_candidates') $('note').textContent = 'Bản lọc thử mới chỉ xóa một phần chấm xanh; nhiều đốm vẫn còn và có thể ảnh hưởng hiệu ứng. Hãy so với bản trước.';
  const quality = state.quality.get(asset.source.split('/').pop().replace(/\.gif$/i, ''));
  if (quality) $('note').textContent += ` ${quality.issue}`;
  const highDetail = variant === 'revision_candidates' || variant === 'scene_spot_candidates' || ['scene_mask_deep_candidates', 'scene_mask_deeper_candidates'].includes(variant) || variant === 'scene_mask_candidates' || variant === 'batch12_detail_candidates' || (['speed_oct28_candidates', 'speed_60fps_candidates', 'conden_60fps_candidates', 'tune_60fps_candidates'].includes(variant) && asset.frame_files) || variant === 'detail_oct28_candidates' || variant === 'detail_130_candidates' || variant === 'tiger_clean_130' || variant === 'tiger_clean_all_130';
  const detailFolder = variant === 'tiger_clean_all_130' ? 'clean_all_v2_130_frames' : variant === 'tiger_clean_130' ? 'clean_130_frames' : 'detail_130_frames';
  const detailUrl = (index) => variant === 'revision_candidates' ? `/Asset/Character/revision_candidates/${pathPart(asset.atlasId || asset.id)}/frame_${String(index).padStart(3, '0')}.png` : variant === 'scene_spot_candidates' ? `/Asset/Character/scene_spot_candidates/${pathPart(asset.atlasId || asset.id)}/frame_${String(index).padStart(3, '0')}.png` : ['scene_mask_deep_candidates', 'scene_mask_deeper_candidates'].includes(variant) ? `/Asset/Character/${variant}/${pathPart(asset.atlasId || asset.id)}/frame_${String(index).padStart(3, '0')}.png` : variant === 'scene_mask_candidates' ? `/Asset/Character/scene_mask_candidates/${pathPart(asset.atlasId || asset.id)}/frame_${String(index).padStart(3, '0')}.png` : variant === 'batch12_detail_candidates' ? `/Asset/Character/batch12_detail_candidates/${pathPart(asset.atlasId || asset.id)}/frame_${String(index).padStart(3, '0')}.png` : ['speed_oct28_candidates', 'speed_60fps_candidates', 'conden_60fps_candidates', 'tune_60fps_candidates'].includes(variant) ? `/Asset/Character/${asset.frames[index].image_variant}/${pathPart(asset.atlasId || asset.id)}/frame_${String(asset.frames[index].image_index).padStart(3, '0')}.png` : variant === 'detail_oct28_candidates' ? `/Asset/Character/detail_oct28_candidates/${pathPart(asset.atlasId || asset.id)}/frame_${String(index).padStart(3, '0')}.png` : `/Asset/Character/review/${pathPart(asset.atlasId || asset.id)}/${detailFolder}/frame_${String(index).padStart(3, '0')}.png`;
  const imageVariant = ['speed_oct28_candidates', 'speed_60fps_candidates', 'conden_60fps_candidates', 'tune_60fps_candidates'].includes(variant) ? asset.image_variant : variant;
  const url = highDetail ? detailUrl(state.index) : `/Asset/Character/${imageVariant}/${pathPart(asset.atlasId || asset.id)}/atlas_${String(frame.atlas).padStart(3, '0')}.png`;
  try {
    const image = await loadPage(url);
    if (version !== state.generation) return;
    const width = variant === 'revision_candidates' ? asset.size[0] : frame.region[2];
    const canvas = $('canvas');
    const zoom = $('zoom').value;
    canvas.style.width = zoom === 'fit' ? '100%' : `${width * Number(zoom)}px`;
    canvas.style.height = zoom === 'fit' ? '100%' : 'auto';
    renderFrame(canvas, context, image, highDetail ? [0, 0, image.width, image.height] : frame.region, $('flip').checked);
    $('stage-message').hidden = true;
    // Load the next atlas in advance; keep only the current and next pages.
    let nextPage = frame.atlas;
    for (let offset = 1; offset < asset.frames.length; offset++) {
      const page = asset.frames[(state.index + offset) % asset.frames.length].atlas;
      if (page !== frame.atlas) { nextPage = page; break; }
    }
    const nextUrl = `/Asset/Character/${imageVariant}/${pathPart(asset.atlasId || asset.id)}/atlas_${String(nextPage).padStart(3, '0')}.png`;
    const keep = new Set([url]);
    if (highDetail) {
      if (variant === 'tune_60fps_candidates' && asset.id === 'conden' && state.index >= 38) {
        for (let i = 44; i < asset.frames.length; i++) { const preload = detailUrl(i); keep.add(preload); loadPage(preload).catch(() => {}); }
      }
      const span = state.rangeEnd - state.rangeStart + 1;
      for (let offset = 1; offset <= Math.min(4, span - 1); offset++) {
        const index = state.rangeStart + ((state.index - state.rangeStart + offset) % span);
        const prefetch = detailUrl(index); keep.add(prefetch); loadPage(prefetch).catch(() => {});
      }
    } else if (nextUrl !== url) { keep.add(nextUrl); loadPage(nextUrl).catch(() => {}); }
    for (const key of state.cache.keys()) if (!keep.has(key)) state.cache.delete(key);
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
$('timing').addEventListener('change', () => { state.lastTick = null; state.elapsed = 0; render(); });
$('zoom').addEventListener('change', render);
async function applyVariant() {
  const variant = $('variant').value;
  const base = state.baseSelected;
  if (!base) return;
  const request = ++state.variantRequest;
  let selected = base;
  if (variant === 'motion_v2_candidates' || variant === 'repaired_candidates' || variant === 'repaired_v2_candidates' || variant === 'repaired_v5_candidates' || variant === 'detail_oct28_candidates' || variant === 'speed_oct28_candidates' || variant === 'speed_60fps_candidates' || variant === 'conden_60fps_candidates' || variant === 'tune_60fps_candidates' || variant === 'scene_spot_candidates' || variant === 'revision_candidates') {
    try {
      const response = await fetch(`/Asset/Character/${variant}/${pathPart(base.atlasId || base.id)}/candidate.json`);
      if (!response.ok) throw new Error('Không tải được metadata bản thử.');
      const data = await response.json();
      if (request !== state.variantRequest) return;
      selected = { ...base, frames: data.frames, frame_count: data.frames.length, size: data.display_size || base.size, frame_files: data.frame_files, image_variant: data.image_variant };
    } catch (error) {
      $('stage-message').hidden = false;
      $('stage-message').textContent = error.message;
      return;
    }
  }
  state.selected = selected;
  state.index = 0; state.elapsed = 0; state.lastTick = null;
  state.rangeStart = 0; state.rangeEnd = selected.frames.length - 1;
  $('frame').min = '0'; $('frame').max = String(state.rangeEnd);
  $('segment-start').max = String(state.rangeEnd); $('segment-start').value = '0';
  $('segment-end').max = String(state.rangeEnd); $('segment-end').value = String(state.rangeEnd);
  $('asset-info').textContent = `${selected.frame_count} frame · ${selected.size[0]} × ${selected.size[1]} px · ${selected.source}`;
  state.cache.clear();
  render();
}
$('variant').addEventListener('change', applyVariant);
$('flip').addEventListener('change', render);
$('background').addEventListener('change', (event) => { $('stage').className = `stage ${event.target.value}`; });

async function init() {
  try {
    const [catalogResponse, candidatesResponse, inventoryResponse, auditResponse, refinedResponse, splitsResponse, cleanupResponse, batchResponse, specialResponse, temporalResponse, qualityResponse, sharedSceneResponse, detailedResponse, footResponse, sceneDetailResponse, remainingSceneResponse, spotResponse, pixelResponse, pixel120Response, nativeResponse, oct28Response, pixel180Response, scorpitRepairResponse, logoResponse, protectedResponse, pixel220Response, sharpResponse, scorpitRepair18Response, fineResponse, detail130Response, fireSpeckResponse, fireOrphanResponse, fireDeepResponse, motionV2Response, repairedResponse, repairedV2Response, repairedV5Response, detailOct28Response, speedOct28Response, speed60fpsResponse, conden60fpsResponse, tune60fpsResponse, batch12NativeResponse, batch12DetailResponse, compositeResponse, sceneMaskResponse, sceneMaskDeepResponse, sceneMaskDeeperResponse, sceneSpotResponse, revisionResponse] = await Promise.all([
      fetch('/api/assets'), fetch('/api/candidates'), fetch('/Asset/Character/review/inventory.json'), fetch('/Asset/Character/review/background-audit.json'), fetch('/api/refined-candidates'), fetch('/Asset/Character/extracted/split-catalog.json'), fetch('/api/cleanup-candidates'), fetch('/api/batch-candidates'), fetch('/api/special-candidates'), fetch('/api/temporal-candidates'), fetch('/Asset/Character/review/background-review-status.json'), fetch('/api/shared-scene-candidates'), fetch('/api/detailed-candidates'), fetch('/api/foot-candidates'), fetch('/api/scene-detail-candidates'), fetch('/api/remaining-scene-candidates'), fetch('/api/spot-candidates'), fetch('/api/pixel-candidates'), fetch('/api/pixel-120-candidates'), fetch('/api/native-candidates'), fetch('/api/oct28-fix-candidates'), fetch('/api/pixel-180-candidates'), fetch('/api/scorpit-repair-candidates'), fetch('/api/logo-candidates'), fetch('/api/scene-protected-candidates'), fetch('/api/pixel-220-candidates'), fetch('/api/sharp-candidates'), fetch('/api/scorpit-repair18-candidates'), fetch('/api/fine-candidates'), fetch('/api/detail-130-candidates'), fetch('/api/fire-speck-candidates'), fetch('/api/fire-orphan-candidates'), fetch('/api/fire-deep-candidates'), fetch('/api/motion-v2-candidates'), fetch('/api/repaired-candidates'), fetch('/api/repaired-v2-candidates'), fetch('/api/repaired-v5-candidates'), fetch('/api/detail-oct28-candidates'), fetch('/api/speed-oct28-candidates'), fetch('/api/speed-60fps-candidates'), fetch('/api/conden-60fps-candidates'), fetch('/api/tune-60fps-candidates'), fetch('/api/batch12-native-candidates'), fetch('/api/batch12-detail-candidates'), fetch('/Asset/Character/extracted/composite-catalog.json'), fetch('/api/scene-mask-candidates'), fetch('/api/scene-mask-deep-candidates'), fetch('/api/scene-mask-deeper-candidates'), fetch('/api/scene-spot-candidates'), fetch('/api/revision-candidates')
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
    if (detailedResponse.ok) state.detailed = new Set(await detailedResponse.json());
    if (footResponse.ok) state.foot = new Set(await footResponse.json());
    if (sceneDetailResponse.ok) state.sceneDetail = new Set(await sceneDetailResponse.json());
    if (remainingSceneResponse.ok) state.remainingScene = new Set(await remainingSceneResponse.json());
    if (spotResponse.ok) state.spots = new Set(await spotResponse.json());
    if (pixelResponse.ok) state.pixel = new Set(await pixelResponse.json());
    if (pixel120Response.ok) state.pixel120 = new Set(await pixel120Response.json());
    if (nativeResponse.ok) state.native = new Set(await nativeResponse.json());
    if (oct28Response.ok) state.oct28 = new Set(await oct28Response.json());
    if (pixel180Response.ok) state.pixel180 = new Set(await pixel180Response.json());
    if (scorpitRepairResponse.ok) state.scorpitRepair = new Set(await scorpitRepairResponse.json());
    if (logoResponse.ok) state.logos = new Set(await logoResponse.json());
    if (protectedResponse.ok) state.protectedScene = new Set(await protectedResponse.json());
    if (pixel220Response.ok) state.pixel220 = new Set(await pixel220Response.json());
    if (sharpResponse.ok) state.sharp = new Set(await sharpResponse.json());
    if (scorpitRepair18Response.ok) state.scorpitRepair18 = new Set(await scorpitRepair18Response.json());
    if (fineResponse.ok) state.fine = new Set(await fineResponse.json());
    if (detail130Response.ok) state.detail130 = new Set(await detail130Response.json());
    if (fireSpeckResponse.ok) state.fireSpeck = new Set(await fireSpeckResponse.json());
    if (fireOrphanResponse.ok) state.fireOrphan = new Set(await fireOrphanResponse.json());
    if (fireDeepResponse.ok) state.fireDeep = new Set(await fireDeepResponse.json());
    if (motionV2Response.ok) state.motionV2 = new Set(await motionV2Response.json());
    if (repairedResponse.ok) state.repaired = new Set(await repairedResponse.json());
    if (repairedV2Response.ok) state.repairedV2 = new Set(await repairedV2Response.json());
    if (repairedV5Response.ok) state.repairedV5 = new Set(await repairedV5Response.json());
    if (detailOct28Response.ok) state.detailOct28 = new Set(await detailOct28Response.json());
    if (speedOct28Response.ok) state.speedOct28 = new Set(await speedOct28Response.json());
    if (speed60fpsResponse.ok) state.speed60fps = new Set(await speed60fpsResponse.json());
    if (conden60fpsResponse.ok) state.conden60fps = new Set(await conden60fpsResponse.json());
    if (tune60fpsResponse.ok) state.tune60fps = new Set(await tune60fpsResponse.json());
    if (batch12NativeResponse.ok) state.batch12Native = new Set(await batch12NativeResponse.json());
    if (batch12DetailResponse.ok) state.batch12Detail = new Set(await batch12DetailResponse.json());
    if (sceneMaskResponse.ok) state.sceneMask = new Set(await sceneMaskResponse.json());
    if (sceneMaskDeepResponse.ok) state.sceneMaskDeep = new Set(await sceneMaskDeepResponse.json());
    if (sceneMaskDeeperResponse.ok) state.sceneMaskDeeper = new Set(await sceneMaskDeeperResponse.json());
    if (sceneSpotResponse.ok) state.sceneSpot = new Set(await sceneSpotResponse.json());
    if (revisionResponse.ok) state.revision = new Set(await revisionResponse.json());
    if (qualityResponse.ok) state.quality = new Map((await qualityResponse.json()).sources.map((item) => [item.id, item]));
    if (splitsResponse.ok) state.assets.push(...(await splitsResponse.json()).assets);
    if (compositeResponse.ok) state.assets.push(...(await compositeResponse.json()).assets);
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
      while (state.elapsed >= frameDuration(state.selected.frames[state.index], $('timing').value)) {
        state.elapsed -= frameDuration(state.selected.frames[state.index], $('timing').value);
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
