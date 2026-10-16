# Utility geometry source and compact proof package

Original three-model batch05a geometry is frozen by historical/manifest.json and reviews/batch05a/geometry_function_approval.json. The original entire manifest refers to the historical working package and is provenance, not the current publication file list. Main GLBs and exactly one editable Blend per model live under assets/household/. No geometry or material has changed. Historical catalog status text is preserved as original evidence only; current metadata is in the canonical asset folders.

Run Blender 4.3.2 with NumPy, with the working directory set to this generator folder:

    ASSET_OUTPUT_ROOT=/new/output SKIP_RENDER=1 blender -b -t 2 --python scripts/build_assets.py

The source has no other-batch dependencies or input scene requirements; packed original grain is generated deterministically. The canonical editable Blends retain the exact approved originals. ONLY_ASSETS accepts comma-separated IDs. Regeneration is geometry-equivalent; Blender serialization need not produce identical binary hashes.

For proof regeneration, first copy the three approved GLBs into /new/output/assets/<id>/<id>.glb. Run scripts/numeric_use_tests.py, scripts/bail_contact.py and scripts/use_tests.py with the same ASSET_OUTPUT_ROOT. These produce numeric tests and named inspection poses, including full diagnostic Blender scenes locally. Those redundant scenes are intentionally not shipped. Original source scripts are preserved byte-for-byte. Their older lighting and glass-hidden hand inspection are diagnostic only and do not define canonical photographs. scripts/validate_and_context.py requires both GLB and Blend in that output layout.

historical/evidence contains representative existing exact-input geometry proofs, not standardized product photos. The 90.9-degree bucket pose is clear; 91.0 degrees is the first grip/lip collision. This is visual-diorama geometric plausibility, not strength, watertightness or manufacturing certification. No third-party reference images are republished.
