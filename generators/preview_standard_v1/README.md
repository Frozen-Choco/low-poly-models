# Product photography v1

Reproduce the saved GLB's materials and geometry in Blender 4.3.2 (Cycles CPU), with Python Pillow 11.1.0 available to Blender. No generated textures, retouching, denoising or per-object exposure adjustments are used.

From the repository root:

```sh
SOURCE_ROOT="$PWD" blender -b -t 2 --python generators/preview_standard_v1/render.py -- whole_red_apple side
```

Outputs are written beneath this generator's `repo/assets/` directory, with exact input, camera, light and output hashes in `records/`. The input GLB must match `inputs.json`; the renderer imports it into a temporary scene and never saves or exports model geometry. Each invocation renders fresh. Limit concurrent invocations to the CPU resources available.

## Shared photographic controls

- 1200 × 1200 RGB JPEG, quality 95; Cycles 512-sample ceiling, adaptive threshold 0.005, seed 0, two CPU threads, no denoise.
- AgX Medium High Contrast, exposure 0, gamma 1; fixed neutral world and white key/fill/rim disk lights. All values are in `standard.json`.
- Imported copies are normalized to a longest world dimension of two units. Camera framing fits exact projected vertices to 80% of the frame's longest axis. This presents comparable apparent size; it does not imply common physical scale or alter source geometry.
- The whole lighting rig rotates with the camera by the same rule for every asset. Material-dependent brightness and reflections remain faithful to the GLB.
- Elevated views use a shared neutral floor. Horizontal axial and underside views hide that floor and composite transparent rendering over fixed sRGB (184,184,184), avoiding a bright world or horizon. These inspection views have no floor contact shadow.
- `alternate_light` uses the same camera and a second standardized light direction: mirror the base rig's X offsets before camera-relative rotation, preserving energy, color and exposure.
- Semantic close-ups use documented targets in `detail_targets.json`; they retain the shared studio and must magnify the object at least 1.2× relative to its whole-object fit. Their crop intentionally excludes unrelated geometry.

## View names and compatibility aliases

`preview` is the front three-quarter hero; `back` is the opposing three-quarter view. `rear`, `side`/`right`, `left`, `top`, and `underside` are true axial inspections. Detail names identify the feature described in `detail_targets.json`. `front_three_quarter.jpg` aliases `preview.jpg`; `underside_axial.jpg` aliases `underside.jpg`. Other aliases are declared in `views.json`. A JPEG alias copies bytes exactly; a PNG alias losslessly encodes the final JPEG's decoded RGB pixels.

Historical before/after material evidence belongs in separately labeled historical folders and retains its original input hashes. It is not a current product photograph. This pipeline does not overwrite such evidence.

## Verification and rollout

`audit.py` verifies this version's immutable source/config hashes, input GLB hashes, published output records, image dimensions and aliases. Per-asset records list which images have completed this standard. The presence of an input or planned view in these configs does not assert that its new photos have been published. Reproducibility depends on Blender/Pillow versions and CPU rendering behavior; decoded-pixel equality is the relevant comparison, with JPEG-byte equality checked separately.
