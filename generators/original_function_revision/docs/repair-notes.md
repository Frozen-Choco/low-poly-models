# Original shelf and mug functional repair

## References independently checked by maker
- IKEA IVAR assembly AA-2204612-7, step 7: https://www.ikea.com/au/en/assembly_instructions/ivar-side-unit__AA-2204612-7-100.pdf . Rear cross braces fasten with four screws to the rear upright faces. Shelves are supported independently. The reference is used for external rear-brace topology, not dimensions or an exact product reproduction.
- IKEA OBSERVATÖR: https://www.ikea.com/us/en/p/observatoer-cross-brace-galvanized-87749600/ . Galvanized cross brace, intended to stabilize a shelving structure.
- KINTO SCS-S03 ceramic mug: https://kinto.co.jp/products/20754 . Manufacturer photography checked for connected upper and lower ceramic handle roots, open finger aperture and glaze appearance. The source is a construction/material reference, not an exact reproduction.

## Shelf defect and repair
Frozen baseline diagonals occupy y=.160 and .163 m, inside boards whose rear edge is y=.175 m. Each intersects the two uninterrupted middle shelfboards, away from support joints. The revised flat steel braces are 12 mm wide and 3 mm thick, centered at y=.186 and .191 m. The closest brace face clears the shelf rear by 9.5 mm. At the crossing, the two brace surfaces have 2 mm separation. Four modeled welded post standoffs bridge rear post faces to the brace fronts, with screw shanks, washers and heads. Ends attach at x=±.435 m, z=.18 and 1.41 m. This inferred generic steel bracket assembly is physically coherent but is not an IKEA part copy or engineering certification.

Board dimensions, upright locations, shelf elevations, finish and front silhouette remain unchanged. Intentional post/corner joinery and support/board contact remain. The anti-racking diagonals no longer pass through storage surfaces. Real furniture requires installation appropriate to its environment, including anti-tip anchorage; this artwork does not certify installation safety.

## Mug defect and repair
Both saved baseline formats had a 0.272072 mm minimum lower-root gap over 63,838 sampled surface points. The upper handle root already intersects the outer wall. Only the lower eight of 33 handle path rings change: the endpoint moves inward 3 mm with a quadratic taper and a maximum 1 mm tube-radius flare. Mid-handle geometry, opening, the entire vessel body, lip, inner wall, floor and upper root remain unchanged. The lower root embeds in the exterior wall without protruding into the cavity. Separate intersecting body/handle meshes represent a ceramic joint; this is an illustration asset, not a watertight fabrication solid.

## Reproduction and review
Use Blender 4.3.2, two threads:

    ONLY_ASSETS=open_shelf,mug blender -b -t 2 --python scripts/build_assets.py
    blender -b -t 2 --python scripts/validate_assets.py
    blender -b -t 2 --python scripts/measure.py
    blender -b -t 2 --python scripts/mug_joint.py
    blender -b -t 2 --python scripts/inspect_saved.py

The build script is self-contained and embeds all materials. No texture dependencies. Validation cleans degenerate pole triangles before final export, reopens Blend and GLB, compares bounds/triangles and enforces 100 MB maximum. Saved-file independent reviewer approval is required before publication. Maker measurements and renders are evidence, not independent approval. Historical baseline hashes are retained for comparison; no local baseline folder is needed for regeneration.

## Maker verification results
- Shelf: 2,088 triangles; GLB 145,512 bytes; Blend 107,084 bytes. Dimensions 0.905 × 0.372 × 1.510 m, including rear hardware.
- Mug: 1,684 triangles; GLB 40,140 bytes; Blend 110,299 bytes. Dimensions 0.123 × 0.086 × 0.108 m.
- Both saved formats: zero degenerate triangles, finite vertex coordinates, exact matching imported bounds. Both shelf braces have zero surface intersections with all four boards.
- Lower mug root: minimum signed surface distance −2.84325 mm in both formats (63,838 samples), confirming exterior-wall embedding. Mid-handle inner surface remains x=.052 m at z=.057 m (unchanged); cavity center ray reaches floor at z=.013 m and underside at z=0.
- Source reconstruction in a separate directory produced byte-identical GLBs for both assets. See `source_reproducibility.json`; this validates the source-generated geometry/material payload while editable Blend containers include save-dependent metadata.
- All eight original furniture/mug Blend/GLB baseline hashes remain unchanged; see `baseline_unchanged.json`.
- Preview set covers both formats, front/back/side/top/underside, roots/brace crossing/board clearance and alternate cool lighting. Context renders show ordinary shelf storage placement and mug placement on a tabletop. Context-only objects are not in delivered GLBs.
- No texture files required; PBR materials embedded. Independent final audit remains the release gate.

## Independent-review correction before freeze
The first repair candidate used a tracking quaternion that rotated the strip cross-section incorrectly. Independent review found 12 mm actual world-Y depth and crossing overlap. R2 uses an explicit orthonormal basis; `brace_basis_check.json` now verifies actual saved geometry in both formats: A y=.184500009–.187500000 m, B y=.189500004–.192499995 m, crossing clearance .002000004 m and board clearance .009500009 m. Earlier candidate is superseded; the frozen manifest identifies only R2 shelf and unchanged approved-candidate mug.

## Published layout and reproduction

Delivered models live at repository-root assets/. Generator source, evidence and this document live under generators/original_function_revision/. From that generator directory, run the build command above FIRST with ONLY_ASSETS=open_shelf,mug; it creates a separate local assets/ directory. Then run the validation and measurement commands against those regenerated local files. Do not run the generator from repository root or copy generated files over published models without independent review. Geometry evidence source fields use these generator-local build paths. The public package manifest records each original source path and its repository-relative published mapping.

The previews/geometry.json diagnostic records the revised shelf only; mug measurements are in mug_joint.json and measurements.json. frozen_manifest.json paths are repository-root paths.
