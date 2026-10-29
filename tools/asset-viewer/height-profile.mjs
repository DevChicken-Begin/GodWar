// One live source of height targets for both browser previews.
export function resolveHeightProfile(profile, targets) {
  const id = profile.id;
  const sourceId = ({ crapit_main: 'crapit', crapit_secondary: 'crapit', moxie_repaired: 'moxie' })[id] || id;
  const entry = targets.get(sourceId);
  if (!entry || entry.source_sha256 !== profile.source_sha256) throw new Error(`Không tìm thấy chiều cao hiện hành cho ${id}.`);
  const height = id === 'crapit_secondary' ? entry.parts?.[1]?.target_height_px : entry.target_height_px;
  const reference = Number(profile.reference_height_px);
  if (!Number.isFinite(height) || height <= 0 || !Number.isFinite(reference) || reference <= 0) throw new Error(`Mốc kích thước không hợp lệ cho ${id}.`);
  return { ...profile, target_height_px: height, display_scale: height / reference };
}
