---
name: animated-pixel-art-studio
description: Create original animated pixel art scenes, sprite animations, seamless loops, GIFs, PNG sequences, and MP4 videos with editable source. Use for pixel art video, retro animated scenes, pixel loops, sprite walk cycles, or an animated pixel art studio workflow. Includes a local Python renderer and editable starters; no model API is required.
---

# Animated Pixel Art Studio

Turn the user's idea into an actual animation and editable scene. Do not stop at prompts or storyboards unless that is the requested deliverable.

## Establish the brief

Extract subject, action, mood, aspect ratio, duration, loop intent, and delivery format. Reuse supplied references. Ask only for missing details that materially change the concept. Otherwise state defaults and proceed: 160x90 native pixels, 12 fps, 48 frames (4 seconds), 6x integer upscale, fixed palette, looping GIF plus MP4 if FFmpeg is available. Use 90x160 for portrait, 128x128 for square.

Write a concise `brief.md` beside the scene with composition, palette, timing, asset origin, assumptions, and deliverables. For long videos create a shot list; do not silently shorten an explicit requested duration. A shot is limited to 600 frames and 40 million native frame pixels.

## Locate tools and choose assets

Resolve paths relative to this SKILL.md, not the caller's working directory. `<skill>` means this folder, `<python>` the active Python 3.10+ interpreter.

```text
<python> -m pip install "Pillow>=11.3,<13"
<python> <skill>/scripts/studio.py doctor
<python> <skill>/scripts/studio.py init --preset rainy-cafe --out <project>/scene.json
```

Use an isolated environment for dependencies. Read [scene-format.md](references/scene-format.md) before authoring JSON. Choose `rainy-cafe`, `campfire`, `walk-cycle`, or `blank` as a structural starting point. Change composition, assets, palette, and motion to satisfy the brief. Renaming a preset does not complete a custom request.

For code-authored art use palette-key sprite rows, rectangles, or original PNG cels. If an image generation/editing tool is available and relevant, use it according to the host's rules. Preserve reference identity and inspect candidate assets. Generated images do not guarantee exact grids or consistent cels. Imported PNGs must already be native resolution, <=512x512, use the scene palette, and have alpha 0 or 255. Do not silently quantize or downsample a reference expected to remain exact.

When no image tool is available, construct original pixel assets with the renderer and explain that route. Do not require paid APIs or fabricate ComfyUI nodes. Read [integrations.md](references/integrations.md) only for external providers/editors or multi-shot work.

## Design pixels and motion

Read [art-direction.md](references/art-direction.md). Lock palette, native canvas, proportions, pivot, and light direction. Use readable silhouettes, deliberate clusters, integer coordinates, and nearest-neighbor resizing. Avoid blur, antialiasing, random texture, or per-frame palette shifts.

Separate background, subject, foreground, and effects. Use authored cels for meaningful actions; use position tracks for translation, parallax, or bobbing. Maintain cel dimensions and foot contact. Add holds and anticipation as appropriate. For loops make motion/cel periods divide the frame count, include the closing key at `frames`, and render 0..frames-1. Inspect the last-to-first transition. A GIF loop flag alone does not make motion seamless.

For expensive external generation, make a small proof render before a large batch. Do not impose an approval pause unless missing authorization actually requires one.

## Render and verify

```text
<python> <skill>/scripts/studio.py validate <project>/scene.json
<python> <skill>/scripts/studio.py render <project>/scene.json --out <project>/render-v1 --formats png,gif,mp4
```

Use a new or empty output folder. If FFmpeg is absent, render `png,gif`, state that MP4 is pending, and give the rerun command. Never claim an uncreated MP4 is delivered.

Read `report.json`. Open `poster.png` and `contact-sheet.png` using available image inspection tools. Inspect GIF/video playback when supported. Check silhouette, stray pixels, proportions, feet, flicker, clipping, and the loop boundary. The automated metric is a heuristic, not an artistic quality score. Do not require identical first/last frames, which may introduce a pause. Fix issues and render to a new versioned folder.

If video inspection is available, verify encoded dimensions, duration, fps, and frame count. H.264/yuv420p can alter color edges; PNGs are the lossless masters. Odd dimensions get one black padding pixel on the right/bottom. GIF is native resolution with centisecond timing. Use PNG/MP4 for scaled output.

## Deliver

Provide requested video/GIF, editable `source/scene.json` and imported PNGs, poster/contact sheet, and actual settings/checks. Link exact files. State limitations such as missing audio, failed encoding, or playback not inspected. The renderer produces silent video.

Do not publish user outputs, push them to a public repo, or spend paid credits merely because this skill is installed. Follow user scope and host authorization rules.
