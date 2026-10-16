# Transport assets

 One original GLB and one editable Blend per asset, all canonical JPGs, exact maker source, bounded geometry evidence and immutable photography provenance. Independent final review remains authoritative.

## Reproduce geometry

Use Blender 4.3.2. Run `blender --background --threads 2 --python generators/transport_batch06a/scripts/build_assets.py -- --asset SLUG`. The unchanged generator emits to `generators/transport_batch06a/assets/SLUG/`; compare its GLB to `assets/vehicles/SLUG/SLUG.glb`. This separate output avoids silently replacing delivered files. Run the adjacent `validate_saved.py -- --asset SLUG` to reload both outputs.

## Reproduce photography

Run `SOURCE_ROOT=$PWD blender --background --threads 2 --python generators/transport_preview_standard_v1/render.py -- SLUG VIEW`. Only use IDs/views listed in input manifests and original records. The frozen renderer/settings are byte-identical to published preview_standard_v1. It emits images under its own repo/assets/vehicles tree. No manual light/material/exposure override is permitted.

Original render records retain their actual original filesystem paths. Per-asset relocation manifests map those records to identical delivered images; paths were moved, pixels and GLB bytes were not changed. Delivered metadata records current independent technical acceptance. Unchanged generator code can emit historical build-time statuses; regenerated output requires a new review before delivery.

No manufacturer reference downloads, history, temporary proof Blend files or duplicate source models are included. These are static visual diorama assets with bounded geometric checks, not certified working machinery.
