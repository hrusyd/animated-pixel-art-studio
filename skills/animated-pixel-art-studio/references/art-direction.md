# Pixel art and motion direction

## Composition and clusters

Choose one focal action or visual focus. At 160x90, silhouettes and three readable depth planes matter more than surface detail. For detailed environments use a larger native canvas such as 640x360 and author separate components according to [component-workflow.md](component-workflow.md). Separate value groups and leave breathing room near edges. Compose portrait scenes directly at a portrait native resolution; never stretch a landscape frame.

Start with 8..24 colors. Share shadows across materials. Build deliberate clusters, consistent diagonal stair steps, and selective highlights. Keep outline thickness consistent. Avoid blanket dithering, pillow shading, disconnected pixel noise, and smooth gradients. Inspect native resolution and nearest-neighbor enlargement.

## Character consistency

Record head/body ratio, eye line, costume colors, facing, light direction, and pivot. Keep cel canvas size fixed. Sketch contact poses first. For walking, hold the planted foot while the other passes; sliding a static sprite does not communicate walking. Compare supplied reference identity explicitly.

## Motion

Start around 8..16 fps and 4..8 cels for a small cycle, adapting to the brief. Hold key poses and include anticipation/follow-through where appropriate. Use one primary action and one or two secondary movements at different periods. A cat can blink every four seconds while steam changes every second. Avoid moving everything at once.

For loops, place the closing pose at time N, render frames 0..N-1, and make periodic motion divide N. Wrap particles outside the frame or behind geometry. Do not duplicate the first frame at the end just to satisfy a metric. Evaluate velocity and phase as well as image similarity.

## Generated assets

If an image tool is available, specify subject, canvas, palette, viewpoint, pivot, lighting, and action poses. Request hard pixel clusters, no antialiasing/gradients, equal cel dimensions, and consistent ground contact. Inspect every candidate. Generated sheets can have inconsistent cell spacing, drifting identities, and baked checkerboards. Correct through authorized editing tools or explicitly permitted processing. A high-resolution raster with blocky texture is not automatically native pixel art.

## Acceptance checklist

1. Action reads without narration.
2. Silhouette/value groups remain clear at native size.
3. Pixel scale and edge treatment are consistent.
4. Cels preserve proportions, pivot, and palette.
5. Feet, props, and shadows move coherently.
6. Last-to-first transition has no unintended jump.
7. Encoded format, dimensions, and timing match the brief.

Report only checks performed. If playback is unavailable, say that inspection covered stills and frame diagnostics.
