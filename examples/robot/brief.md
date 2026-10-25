# Little Beacon

An original tiny floating robot hovers over a quiet landing pad against a dark navy background. Square 128 x 128 native canvas, 6x nearest-neighbor scale, 12 fps, 24 frames, exactly 2 seconds. Deliver native GIF and 768 x 768 silent MP4 with editable scene and lossless PNG frames.

The robot has a broad head, small torso, short arms, mint eyes, a warm amber antenna and a cyan thruster. Head/body ratio is approximately 28:18 in width; eye line is fixed at sprite row 14, nozzle at row 37, light comes from upper left. Sparse stars and a low horizon preserve breathing room.

Twelve locked colors: navy background/shadows, blue steel, pale mint highlights, cyan light, amber accents. All assets are original palette-key sprites authored in build_scene.py. No downloaded or generated raster assets, paid services or external providers are used. The blank preset supplied the structural starting point; its content is replaced.

The hover moves through a 24-frame cycle with a closing key at frame 24, rendered frames 0–23. The thruster cycles every 6 frames and a two-frame blink occurs once per 24 frames. GIF loops; the MP4 contains one silent cycle. Editable source is scene.json and build_scene.py; the renderer also packages source/scene.json with its output.
