export function frameDuration(frame, mode) {
  return ['60', '70', '130'].includes(mode) ? Number(mode) : Math.max(frame.duration_ms, 0.01);
}
