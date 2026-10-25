# Optional integrations and longer videos

The renderer is local and provider-neutral. It does not connect to model APIs, ComfyUI, or editors automatically. The host agent supplies filesystem/shell tools and any image tools.

## Pixel editors

Inspect the installed editor's supported CLI/UI. Export equal-sized PNG cels with fixed pivots and palette. Place them inside the scene directory and reference `{"image":"sprites/cel-0.png"}`. Do not assume an Aseprite license, executable path, or flags. The renderer does not parse .aseprite or slice sprite sheets.

## ComfyUI or image services

Confirm actual available nodes, models, credentials, prices, and licenses before integrating. Prefer a stable source/reference sheet followed by deliberate cels over independently regenerated frames. Inspect temporal drift. Never ship tokens or private reference photos with public examples. Do not describe an untested integration as ready to run.

## Existing frames

Import palette-compliant, equal-sized native PNGs as sprites and list them in one animation layer. Set frame_ticks for holds and frames for the full timeline. Scaled output frames are different from native source cels.

## Multi-shot assembly

Create one scene per shot with common dimensions, scale, fps, and codec. FFmpeg's concat demuxer can join compatible rendered MP4s. Use trusted paths with correct concat-file quoting and subprocess argument arrays, never shell interpolation of user text. Verify shot order and final duration. Assembly is a separate step; the CLI has no multi-shot timeline editor.

Audio needs a separate explicit mixing step using licensed/user-supplied material. No built-in music, subtitles, voiceover, lip sync, or generative video is provided.

## Official references

- https://pillow.readthedocs.io/en/stable/reference/Image.html
- https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
- https://ffmpeg.org/ffmpeg.html
- https://ffmpeg.org/ffmpeg-filters.html

Check current documentation when changing integrations. The included scripts are authoritative about supported repository features.
