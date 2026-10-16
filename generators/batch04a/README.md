# Batch 04a: Independently reviewed red apple

Only the independently reviewed original generic red apple is included. Bread and onigiri experiments were held after independent visual review and are excluded from the catalog, manifest, context and default build. They are not counted as completed assets. Dimensions use meters; origins sit at the support plane.

Every asset includes an embedded-texture GLB, editable compressed Blender 4.3.2 source, metadata, seven fresh-GLB inspection renders (front, side, rear, close-up, underside, alternate light, underside detail), and canonical preview.jpg/back.jpg copies. Original generated texture pixels only; no downloaded imagery, brands, external generators, paid tools or APIs.

Rebuild:

    blender -b -t 2 --python-exit-code 1 --python scripts/build_assets.py
    blender -b -t 2 --python-exit-code 1 --python scripts/validate_and_context.py
    python scripts/package_manifest.py

Set ASSET_OUTPUT_ROOT to isolate asset output. All other reports and previews are scoped to this batch. No other batch is changed. Render threads are capped at two and denoising is disabled.

The validation report compares saved Blender geometry against fresh GLB imports, checks bounds, triangles, finite coordinates, zero-area faces, embedded images, sizes, and canonical image aliases. Context scenes freshly import the GLBs and record hashes. The immutable manifest records SHA-256 hashes for independent review. Nothing is published automatically.

The source retains experimental bread/onigiri functions for provenance, but IDS and ONLY_ASSETS guard permit only whole_red_apple in this release. Held local files are outside the manifest and must not be published.

Published layout: canonical model files are at repository-root assets/food/whole_red_apple/. Reproduction writes isolated generator-local assets/whole_red_apple/ by default. Run the build before validation; newly generated files require independent review before replacing published assets.
