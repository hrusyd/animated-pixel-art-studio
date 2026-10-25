#!/usr/bin/env python3
"""Deterministic, local pixel animation renderer. Python 3.10+ and Pillow."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

ASSETS = Path(__file__).resolve().parents[1] / "assets"


class SceneError(ValueError):
    """An actionable scene validation error."""


def require(condition, message):
    if not condition:
        raise SceneError(message)


def integer(value, name, low, high):
    require(type(value) is int and low <= value <= high,
            f"{name} must be an integer from {low} to {high}")
    return value


def fields(obj, allowed, name):
    require(isinstance(obj, dict), f"{name} must be an object")
    require(not (set(obj) - set(allowed)), f"{name}: unknown fields {sorted(set(obj) - set(allowed))}")


def color(value):
    require(isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value),
            f"Use a six-digit #RRGGBB color, got {value!r}")
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def safe_asset(root, name):
    require(isinstance(name, str) and name and not Path(name).is_absolute(),
            "Image paths must be relative to the scene directory")
    path = (root / name).resolve()
    require(path.suffix.lower() == ".png", "Image filenames must end in .png")
    require(path.is_relative_to(root.resolve()), "Image path escapes the scene directory")
    require(path.is_file(), f"Image not found: {name}")
    return path


def make_sprite(spec, palette, root):
    fields(spec, {"rows", "image"}, "sprite")
    require(("rows" in spec) != ("image" in spec), "Sprite needs exactly one of rows or image")
    if "image" in spec:
        with Image.open(safe_asset(root, spec["image"])) as source:
            require(source.format == "PNG", "Imported sprites must be PNG")
            require(source.width <= 512 and source.height <= 512, "Sprite exceeds 512x512 native pixels")
            sprite = source.convert("RGBA")
        allowed = set(palette.values())
        pixels = sprite.get_flattened_data() if hasattr(sprite, "get_flattened_data") else sprite.getdata()
        for r, g, b, a in pixels:
            require(a in (0, 255), "PNG must use binary alpha, no antialiased edges")
            require(a == 0 or (r, g, b) in allowed, "PNG contains colors outside scene palette")
        return sprite
    rows = spec["rows"]
    require(isinstance(rows, list) and 1 <= len(rows) <= 512, "rows must contain 1..512 strings")
    require(all(isinstance(row, str) for row in rows), "Sprite rows must be strings")
    width = len(rows[0])
    require(1 <= width <= 512 and all(len(row) == width for row in rows), "Sprite rows must have equal nonzero widths <=512")
    sprite = Image.new("RGBA", (width, len(rows)))
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            require(char == "." or char in palette, f"Unknown palette symbol {char!r}")
            if char != ".":
                sprite.putpixel((x, y), (*palette[char], 255))
    return sprite


def load_scene(path):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    fields(data, {"version", "name", "canvas", "fps", "frames", "scale", "palette", "background", "sprites", "layers", "loop"}, "scene")
    require(type(data.get("version")) is int and data["version"] == 1, "Scene version must be 1")
    require(isinstance(data.get("name"), str) and data["name"].strip(), "name must be a nonempty string")
    require(isinstance(data.get("canvas"), list) and len(data["canvas"]) == 2, "canvas must be [width, height]")
    w, h = [integer(n, "canvas dimension", 1, 512) for n in data["canvas"]]
    fps = integer(data.get("fps"), "fps", 1, 50)
    count = integer(data.get("frames"), "frames", 1, 600)
    scale = integer(data.get("scale", 4), "scale", 1, 12)
    require(w * h * count <= 40_000_000, "Scene exceeds 40 million native frame pixels; shorten the shot")
    require(w * scale <= 4096 and h * scale <= 4096, "Scaled dimensions exceed 4096")
    require(type(data.get("loop", True)) is bool, "loop must be true or false")
    pal = data.get("palette")
    require(isinstance(pal, dict) and 1 <= len(pal) <= 64, "palette needs 1..64 colors")
    require(all(isinstance(k, str) and len(k) == 1 and k != "." for k in pal), "Palette keys must be single characters other than '.'")
    palette = {k: color(v) for k, v in pal.items()}
    require(isinstance(data.get("background"), str) and data["background"] in palette, "background must be a palette key")
    specs = data.get("sprites", {})
    require(isinstance(specs, dict) and len(specs) <= 256, "sprites must be an object with <=256 entries")
    sprites = {name: make_sprite(spec, palette, path.parent) for name, spec in specs.items()}
    layers = data.get("layers")
    require(isinstance(layers, list) and 1 <= len(layers) <= 512, "layers must contain 1..512 objects")
    for i, layer in enumerate(layers):
        fields(layer, {"name", "rect", "color", "sprite", "animation", "frame_ticks", "x", "y", "motion", "visible"}, f"layer {i}")
        kinds = [k for k in ("rect", "sprite", "animation") if k in layer]
        require(len(kinds) == 1, f"layer {i}: choose rect, sprite, or animation")
        integer(layer.get("x", 0), "x", -4096, 4096)
        integer(layer.get("y", 0), "y", -4096, 4096)
        if "rect" in layer:
            require(isinstance(layer["rect"], list) and len(layer["rect"]) == 2, "rect must be [width, height]")
            for n in layer["rect"]:
                integer(n, "rect size", 1, 1024)
            require(isinstance(layer.get("color"), str) and layer["color"] in palette, "rect color must be a palette key")
        else:
            names = [layer["sprite"]] if "sprite" in layer else layer["animation"]
            require(isinstance(names, list) and 1 <= len(names) <= 600, "animation must be a nonempty list with <=600 entries")
            require(all(isinstance(n, str) and n in sprites for n in names), "Layer references an unknown sprite")
            require(len({sprites[n].size for n in names}) == 1, "Animation cels must have identical canvas sizes")
            integer(layer.get("frame_ticks", 1), "frame_ticks", 1, 600)
        if "visible" in layer:
            v = layer["visible"]
            require(isinstance(v, list) and len(v) == 2, "visible must be [start, end_exclusive]")
            integer(v[0], "visible start", 0, count - 1)
            integer(v[1], "visible end", v[0] + 1, count)
        if "motion" in layer:
            motion = layer["motion"]
            fields(motion, {"keys", "interpolation", "period"}, "motion")
            require(motion.get("interpolation", "linear") in ("linear", "step"), "interpolation must be linear or step")
            keys = motion.get("keys")
            require(isinstance(keys, list) and 1 <= len(keys) <= 601, "motion keys must contain 1..601 [frame,x,y] entries")
            previous = -1
            for key in keys:
                require(isinstance(key, list) and len(key) == 3, "Each motion key must be [frame,x,y]")
                integer(key[0], "key frame", 0, count)
                require(key[0] > previous, "Motion key frames must be strictly increasing")
                previous = key[0]
                for n in key[1:]:
                    integer(n, "key position", -4096, 4096)
            require(keys[0][0] == 0, "First motion key must be at frame 0")
            if "period" in motion:
                period = integer(motion["period"], "period", 1, count)
                require(keys[-1][0] <= period, "Motion keys must not extend beyond period")
    return data, palette, sprites


def position(layer, frame):
    motion = layer.get("motion")
    if not motion:
        return layer.get("x", 0), layer.get("y", 0)
    t = frame % motion["period"] if "period" in motion else frame
    keys = motion["keys"]
    for a, b in zip(keys, keys[1:]):
        if t < b[0]:
            if motion.get("interpolation", "linear") == "step":
                return a[1], a[2]
            ratio = (t - a[0]) / (b[0] - a[0])
            return tuple(round(a[j] + ratio * (b[j] - a[j])) for j in (1, 2))
    return keys[-1][1], keys[-1][2]


def render_frame(data, palette, sprites, index):
    frame = Image.new("RGB", tuple(data["canvas"]), palette[data["background"]])
    draw = ImageDraw.Draw(frame)
    for layer in data["layers"]:
        start, end = layer.get("visible", [0, data["frames"]])
        if not start <= index < end:
            continue
        x, y = position(layer, index)
        if "rect" in layer:
            w, h = layer["rect"]
            draw.rectangle((x, y, x+w-1, y+h-1), fill=palette[layer["color"]])
        else:
            names = layer.get("animation", [layer.get("sprite")])
            sprite = sprites[names[(index // layer.get("frame_ticks", 1)) % len(names)]]
            frame.paste(sprite, (x, y), sprite)
    return frame


def changed_fraction(a, b):
    difference = ImageChops.difference(a, b)
    channels = difference.split()
    mask = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    return 1 - mask.histogram()[0] / (a.width * a.height)


def gif_durations(count, fps):
    # Error diffusion on centiseconds keeps total timing within 5ms of target.
    return [10 * (round((i+1)*100/fps) - round(i*100/fps)) for i in range(count)]


def export(path, output, formats, ffmpeg=None):
    data, palette, sprites = load_scene(path)
    formats = set(formats)
    require(bool(formats) and formats <= {"png", "gif", "mp4"}, "formats must be png, gif, mp4, or a comma-separated combination")
    encoder = ffmpeg or shutil.which("ffmpeg")
    if "mp4" in formats:
        require(encoder is not None, "MP4 needs FFmpeg on PATH (or --ffmpeg PATH); use --formats png,gif otherwise")
    output = Path(output)
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())),
            f"Output must be a new or empty directory: {output}. Choose another --out path.")
    output.mkdir(parents=True, exist_ok=True)
    frames_dir = output / "frames"
    frames_dir.mkdir()
    w, h = data["canvas"]
    scale = data.get("scale", 4)
    count, fps = data["frames"], data["fps"]
    pal_image = Image.new("P", (1, 1))
    values = list(dict.fromkeys(palette.values()))
    flat = [n for value in values for n in value]
    pal_image.putpalette(flat + list(values[0]) * (256-len(values)))
    indexed, hashes, samples, changes = [], [], {}, []
    sample_ids = sorted({round(i*(count-1)/7) for i in range(8)})
    first = previous = None
    for i in range(count):
        frame = render_frame(data, palette, sprites, i)
        if first is None:
            first = frame
        if previous is not None:
            changes.append(changed_fraction(previous, frame))
        previous = frame
        hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
        if i in sample_ids:
            samples[i] = frame.copy()
        if "gif" in formats:
            indexed.append(frame.quantize(palette=pal_image, dither=Image.Dither.NONE))
        enlarged = frame.resize((w*scale, h*scale), Image.Resampling.NEAREST)
        if "png" in formats or "mp4" in formats:
            enlarged.save(frames_dir / f"frame_{i:04d}.png")
        if i == 0:
            enlarged.save(output / "poster.png")
    if "gif" in formats:
        # Store native pixels; GIF playback scales in browsers, preserving small files.
        args = {"loop": 0} if data.get("loop", True) else {}
        indexed[0].save(output / "animation.gif", save_all=True, append_images=indexed[1:],
                        duration=gif_durations(count, fps), optimize=False, disposal=2, **args)
    if "mp4" in formats:
        cmd = [str(encoder), "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
               "-framerate", str(fps), "-i", str(frames_dir / "frame_%04d.png"),
               "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0", "-c:v", "libx264",
               "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output / "animation.mp4")]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        require(result.returncode == 0, f"FFmpeg failed: {result.stderr[-2000:]}")
    thumb_scale = min(scale, max(1, 320 // w), max(1, 240 // h))
    tw, th = w*thumb_scale, h*thumb_scale
    cols = min(4, len(samples))
    sheet = Image.new("RGB", (cols*tw, math.ceil(len(samples)/cols)*(th+18)), "#151824")
    for j, (i, frame) in enumerate(samples.items()):
        x, y = (j % cols)*tw, (j // cols)*(th+18)
        sheet.paste(frame.resize((tw, th), Image.Resampling.NEAREST), (x, y))
        ImageDraw.Draw(sheet).text((x+4, y+th+2), f"frame {i}", fill="white")
    sheet.save(output / "contact-sheet.png")
    boundary = changed_fraction(previous, first)
    warnings = []
    if len(set(hashes)) == 1:
        warnings.append("All frames are identical: this is a still image.")
    if data.get("loop", True) and changes and boundary > max(changes)*1.5 + 0.01:
        warnings.append("Loop boundary changes more pixels than ordinary steps. Inspect playback.")
    report = {"name": data["name"], "canvas": [w,h], "scaled_size": [w*scale,h*scale],
              "mp4_size": [w*scale + (w*scale)%2, h*scale + (h*scale)%2] if "mp4" in formats else None,
              "frames": count, "fps": fps, "duration_seconds": count/fps,
              "unique_frames": len(set(hashes)), "loop": data.get("loop", True),
              "loop_boundary_changed_fraction": boundary,
              "max_adjacent_changed_fraction": max(changes, default=0),
              "gif_duration_ms": sum(gif_durations(count, fps)) if "gif" in formats else None,
              "palette_colors": len(values), "frame_sha256": hashes, "warnings": warnings,
              "formats": sorted(formats), "visual_review_required": True}
    (output / "report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    # Freeze a portable copy including referenced PNGs, with original relative paths.
    source_dir = output / "source"
    source_dir.mkdir()
    shutil.copy2(path, source_dir / "scene.json")
    for spec in data.get("sprites", {}).values():
        if "image" in spec:
            destination = source_dir / spec["image"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(safe_asset(Path(path).parent, spec["image"]), destination)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check Pillow and FFmpeg availability")
    init = sub.add_parser("init", help="Copy an editable starter scene")
    init.add_argument("--preset", choices=["rainy-cafe", "campfire", "walk-cycle", "blank"], default="rainy-cafe")
    init.add_argument("--out", type=Path, required=True)
    check = sub.add_parser("validate", help="Validate a scene without rendering")
    check.add_argument("scene", type=Path)
    render = sub.add_parser("render", help="Render a scene and write QA evidence")
    render.add_argument("scene", type=Path)
    render.add_argument("--out", type=Path, required=True)
    render.add_argument("--formats", default="png,gif", help="png,gif,mp4 (default: png,gif)")
    render.add_argument("--ffmpeg", help="FFmpeg executable path")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            from PIL import __version__
            print(json.dumps({"python": sys.version.split()[0], "pillow": __version__, "ffmpeg": shutil.which("ffmpeg")}, indent=2))
        elif args.command == "init":
            require(not args.out.exists(), f"File already exists: {args.out}")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ASSETS / f"{args.preset}.json", args.out)
            print(f"Created {args.out}")
        elif args.command == "validate":
            data, _, _ = load_scene(args.scene)
            print(f"Valid: {data['name']} ({data['frames']} frames at {data['fps']} fps)")
        else:
            report = export(args.scene, args.out, args.formats.split(","), args.ffmpeg)
            print(json.dumps({"output": str(args.out.resolve()), "duration_seconds": report["duration_seconds"], "warnings": report["warnings"]}, indent=2))
        return 0
    except (SceneError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
