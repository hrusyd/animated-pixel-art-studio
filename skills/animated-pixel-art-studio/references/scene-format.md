# Scene format v1

The Python validator is authoritative. Unknown object fields are rejected. JSON is data only: no executable expressions or remote URLs.

## Minimal scene

```json
{
  "version": 1,
  "name": "Bouncing ember",
  "canvas": [96, 64],
  "fps": 12,
  "frames": 24,
  "scale": 6,
  "loop": true,
  "palette": {"0": "#111827", "a": "#e38b66", "b": "#f8e8c8"},
  "background": "0",
  "sprites": {"ember": {"rows": [".a.", "aba", ".a."]}},
  "layers": [
    {"rect": [96, 8], "color": "a", "x": 0, "y": 56},
    {"sprite": "ember", "motion": {"keys": [[0, 8, 50], [12, 84, 20], [24, 8, 50]]}}
  ]
}
```

## Properties

| Property | Meaning |
| --- | --- |
| `version` | Required, exactly 1 |
| `name` | Required nonempty string |
| `canvas` | Required [width,height], each 1..512 |
| `fps` | Required integer 1..50 |
| `frames` | Required integer 1..600; duration = frames/fps |
| `scale` | Integer 1..12, default 4; scaled dimensions <=4096 |
| `loop` | Boolean, default true; GIF loop metadata and QA warning only |
| `palette` | 1..64 single-character keys with #RRGGBB values; dot is reserved |
| `background` | Required palette key; backgrounds are opaque |
| `sprites` | Object of up to 256 named sprites, optional |
| `layers` | 1..512 layers, drawn back to front in list order |

Width * height * frames must be <=40,000,000. This bounds routine workloads, not every resource cost. Keep sprite collections modest and split large scenes into shots.

## Sprites and layers

A sprite has exactly one of `rows` or `image`. Rows are equal-width strings using palette keys and `.` for transparency. PNG image paths must remain inside the scene directory; escaping symlinks and traversal are rejected. PNGs must be native resolution, <=512x512, binary alpha, and exact palette colors. No automatic resampling or palette reduction occurs.

Each layer has exactly one of:

- `rect: [width,height]` plus `color: "a"`.
- `sprite: "name"` for a static cel.
- `animation: ["cel-0","cel-1"]` plus optional `frame_ticks: 3` for repeating cels. All cels must have equal canvas sizes. Repeat a name for extra holds. Default frame_ticks is 1.

`x/y` default to 0 and indicate top-left position. Offscreen portions clip. Optional `name` is a label. `visible: [start,end_exclusive]` limits visibility, otherwise the layer appears throughout. Animation time is global, not relative to visibility start.

## Motion

`motion: {"keys": [[0,10,20],[12,16,18],[24,10,20]], "period":24, "interpolation":"linear"}`

Keys are absolute [frame,x,y], starting at frame 0 with strictly increasing times up to `frames`. Motion overrides x/y. Linear interpolation rounds to integer pixels; `step` holds until the next key. After the last key position holds. Optional period wraps local time; keys cannot extend beyond it. Loop flags do not wrap tracks. For continuity include a closing key at period with the starting position. A closing key at `frames` is valid but is not rendered.

## Outputs

- `poster.png`: first frame at integer output scale.
- `frames/frame_0000.png` etc.: lossless scaled frames when png or mp4 is requested. Retained even for MP4-only requests.
- `animation.gif`: native resolution, shared palette, no dithering. Centisecond timing is distributed to preserve total duration within 5ms. Pillow may coalesce identical adjacent frames while retaining duration.
- `animation.mp4`: scaled H.264/yuv420p, no audio. Plays once; looping is a player setting.
- `contact-sheet.png`: up to eight samples.
- `report.json`: dimensions, timing, unique frames, hashes, and boundary diagnostics; no artistic quality guarantee.
- `source/scene.json`: editable source and imported PNGs with paths preserved.

Encoding failure exits nonzero and may leave partial artifacts. Fix the cause and use another empty output folder. Existing files are never overwritten by rendering.
