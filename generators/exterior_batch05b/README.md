# Exterior utility diorama props

Three original, unbranded assets in meters: roadside convex mirror on pole, residential AC outdoor condenser, and steel drainage grate with receiver frame.

Each asset directory contains a portable GLB, one editable compressed Blender 4.3.2 file, metadata and reviewed JPEG views. Use the documented installation origin; the GLB is Y-up and Blender is Z-up. These props are for visual scenes, not fabrication or equipment operation.

Rebuild geometry with Blender 4.3.2:

    ASSET_OUTPUT_ROOT=/absolute/output SKIP_RENDER=1 blender -b -t 2 --python scripts/build_assets.py

To build one item, also set ONLY_ASSETS=street_drain_grate (or another asset ID). The output root is independent of source location. SKIP_RENDER avoids legacy diagnostic preview creation; final photography uses the separately pinned photography renderer.

Run saved-file checks:

    ASSET_OUTPUT_ROOT=/absolute/output blender -b -t 2 --python scripts/validate_geometry.py

See docs/reference-and-use.md for references, construction, limitations and functional checks, and docs/asset-standard.md for the review standard. Canonical photography configuration and exact input/output records are under photography/preview_standard_v1. Local diagnostic proof scenes remain available for review but are excluded from the intended minimal distribution manifest.
