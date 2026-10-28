// Keep the canvas backing store between equal-sized frames. Resizing it on
// every frame resets the context and can force an expensive reallocation.
export function renderFrame(canvas, context, image, region, flipped) {
  const [x, y, width, height] = region;
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;
  context.clearRect(0, 0, width, height);
  context.imageSmoothingEnabled = false;
  context.save();
  if (flipped) { context.translate(width, 0); context.scale(-1, 1); }
  context.drawImage(image, x, y, width, height, 0, 0, width, height);
  context.restore();
}
