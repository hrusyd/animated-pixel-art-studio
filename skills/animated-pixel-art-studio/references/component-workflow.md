# Build the art from components

Use this workflow for detailed environments. A scene is a stack of authored assets with a shared visual language. More layers do not compensate for weak assets.

## 1. Establish one art contract

Record native canvas, pixel size, camera angle, horizon, light direction, shadow colors, material ramps, detail hierarchy, and output scale. Use the same contract for every component. A useful landscape starting point is 640x360, 32..48 shared colors, 10 fps and 3x enlargement. Adapt these choices to the reference rather than blindly keeping them.

Make the palette global before authoring assets. Use warm lit surfaces and shared cool shadows when appropriate. Limit distant contrast and texture. Preserve a quiet focal corridor and foreground framing. Do not make each asset maximally detailed: their detail must serve the whole composition.

## 2. Plan components and their overlap

List each component's purpose, dimensions, anchor, placement, material, light, allowed colors, layer order and motion. Save the list beside the scene as `art-plan.json` or a concise brief. The included `build_environment.py` writes a working example of this contract and inventory.

| Back-to-front group | Author as | Review for |
| --- | --- | --- |
| Sky | Quiet opaque color masses | Value hierarchy; no distracting bands |
| Clouds | Transparent sculpted masses | Silhouette rhythm, light and shadow planes |
| Far peaks | Separate subdued silhouettes | Atmospheric depth and scale |
| Near mountains | Stronger overlapping planes | Ridges, negative space and horizon |
| Water base | Stable surface and bank silhouette | Perspective, reflection placement |
| Terrain | Connected land planes | Path readability and grounded structures |
| Buildings | Separate constructed volumes | Roof planes, joinery, windows, masonry, contact |
| Trees | Trunk plus coherent foliage masses | Branch attachment, leaf clusters, consistent light |
| Bridge and props | Structural assets | Ground contact and correct occlusion |
| Local animated effects | Equal-size transparent cel sequences | Motion confined to the intended region |
| Foreground | Dark framing masses and props | Depth without hiding the focal subject |

Create complete geometry where layers overlap. Put far trees behind buildings and near trees in front. For moving components, draw enough hidden background to avoid holes. Do not cut an object out of a flattened image and assume the pixels behind it exist.

## 3. Author and review individual assets

Choose native pixel drawing code, an authorized pixel editor, or an available image tool according to host rules and the user's requirements. The renderer itself requires no model, MCP server or network. Image generation is optional; never silently introduce a provider or imply it is built in.

For a generated component, give the tool the art contract plus the specific object's perspective, silhouette, material, dimensions, anchor and transparency requirements. A generated raster is only a candidate. Inspect actual pixels and alpha; a checkerboard painted into RGB is not transparency. Do not promise exact palettes, native grids or registered cels without checking them. Retain source and disclose any agreed conversion.

For code-authored components, design primary silhouette and structural planes first, then material clusters. Avoid stacked generic rectangles, equally spaced circular cloud rings, uniform tile grids across incompatible perspectives, and scattered random texture presented as detail. Use deterministic seeds only for subordinate material variation inside a designed mask.

Review each component at native size and integer zoom:

- Is the object recognizable by silhouette alone?
- Are structural planes and light direction coherent?
- Does detail describe the material, rather than cover errors?
- Are edges intentional pixel clusters with no accidental blur?
- Does its scale, contrast and palette belong in this scene?

## 4. Composite and inspect in context

The existing `scene.json` is the executable layer manifest. `sprites` refer to relative PNG paths. `layers` are drawn back-to-front, with top-left `x/y`. Full-canvas transparent assets may all use `[0,0]`; cropped assets require explicit placement. Animated cels must share dimensions and anchor.

```sh
python studio.py layers project/scene.json --out output/layer-review --frame 0
```

Inspect `layers.png`: left column is the isolated component on a diagnostic checkerboard, right column adds it to the stack. Use `isolated/*.png` for native transparent assets, `steps/*.png` for native cumulative composition, and `layers.json` for order/placement/bounds. The checkerboard is preview-only. Filenames use numeric indices, so labels cannot write arbitrary paths. Inactive layers produce transparent isolated images at the requested frame.

Fix tangencies, overlapping outlines, mismatched lighting, floating props and competing focal points. Move or redraw the responsible component, not the entire scene. Review the assembled still before spending time on motion. Technical validation does not replace this review.

## 5. Animate only what needs to move

Use authored cels for cloth, foliage deformation, fire and glints. Keep the flag's pole attachment fixed. Put water highlights above the water and below objects that occlude it, or explicitly mask the highlights to uncovered water. Keep static structures pixel-identical. Position tracks can move a whole layer but cannot bend cloth or synthesize the hidden side of an object.

Render and inspect several frames and the last-to-first boundary. Deliver the editable scene, component PNGs/cels, art contract, layer review and actual GIF/MP4. State which parts were visually reviewed. Do not claim the output matches a professional reference merely because it has comparable dimensions, a fixed palette or passing tests.

## Reproducible environment study

```sh
python skills/animated-pixel-art-studio/scripts/build_environment.py --out work/highland
python studio.py layers work/highland/scene.json --out output/highland-layers
python studio.py render work/highland/scene.json --out output/highland --formats gif,mp4
```

This creates 14 component layers with original transparent PNGs, a shared 42-color palette, a 640x360 scene and 7 seconds of animation. The scene is a workflow study, not a claim of professional-reference parity. Rebuilding to another empty directory reproduces the same assets. Replace or redraw individual components while preserving the art contract and scene references.
