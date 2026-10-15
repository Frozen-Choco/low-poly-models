# Japanese crossing and public recycling props — batch 02b, revision 5

Pending independent review; no publishing authority implied.

- `assets/railway_crossing_lowered/`: GLB, compressed editable Blend, three JPG views plus canonical preview.jpg/back.jpg aliases, metadata. Lowered boom / left red lamp illuminated / right red lamp dark.
- `assets/public_recycling_bin/`: GLB, compressed editable Blend, three JPG views plus canonical preview.jpg/back.jpg aliases, metadata. Closed service door with true insertion openings and hollow liner.
- `previews/`: contextual JPGs under neutral daylight and alternate light, plus editable review scene. Ground/rail presentation geometry is not in either standalone GLB.
- `validation.json`: saved Blend reopen and GLB reimport checks.
- `catalog.json`: compatible catalog keys including metric dimensions, triangles and binary byte counts.
- `manifest.json`: exact SHA-256 transfer candidates, mapping assets to `assets/street/<id>/` and source/docs/review evidence to `generators/batch02b/`.
- `docs/design-notes.md`: component inventory, omissions, construction/material decisions and references.

Rebuild with Blender 4.3.2 from any directory:

    blender -b --threads 4 --python lowpoly_batch02b/scripts/build_assets.py
    blender -b --threads 4 --python lowpoly_batch02b/scripts/validate_assets.py
    blender -b --threads 4 --python lowpoly_batch02b/scripts/render_context.py
    python lowpoly_batch02b/scripts/package_manifest.py

All paths resolve relative to scripts. No external image/texture inputs, APIs, or paid services. Rebuilds can have different Blender binary hashes due to serialization; validate dimensions, counts and appearance anew and regenerate manifest before transferring a regenerated revision. All assets and previews are comfortably under 100 MB per file.

## Published layout reproduction

From repository root, use ASSET_OUTPUT_ROOT="$PWD/assets/street" before each Blender command and run scripts in `generators/batch02b/scripts/`. For example:

    ASSET_OUTPUT_ROOT="$PWD/assets/street" blender -b --threads 4 --python generators/batch02b/scripts/build_assets.py

The same environment setting applies to validation, context rendering and manifest packaging. Without it, isolated development output defaults to the generator folder’s `assets/` subdirectory. Source/docs and review evidence remain namespaced; standalone assets resolve at the canonical catalog path.

The gallery-compatible `preview.jpg` and `back.jpg` files are byte-identical aliases of `front_three_quarter.jpg` and `rear.jpg`. Generation and optional bin reframing refresh both aliases; validation verifies equality.
