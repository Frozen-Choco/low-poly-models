# Batch 03a: Japanese household diorama props

Three original, generic objects: a stainless kitchen kettle, ceramic rice bowl, and solid wooden cutting board. All dimensions are meters and the origin is at the support plane. Geometry and texture art are newly generated; no third-party imagery or exact manufacturer replicas are included.

Each asset contains a self-contained GLB, compressed editable Blender 4.3.2 source, four JPG inspection angles, canonical preview.jpg/back.jpg aliases, and metadata. Every studio image is rendered from a fresh import of its delivered GLB. Context images also import these GLBs, with hash provenance and physical support surfaces.

Reproduce with Blender 4.3.2:

    blender -b -t 2 --python scripts/build_assets.py
    blender -b -t 2 --python scripts/validate_and_context.py
    python scripts/package_manifest.py

ASSET_OUTPUT_ROOT may point at an isolated output directory for all asset files. Scripts never traverse or modify other batch asset directories. Context and validation outputs are written only into this batch root. Render threads are capped at two, Cycles denoising is disabled. No external APIs or downloaded media are needed. Packed original PNG grain textures are embedded in the board GLB and Blend; metal and ceramic use portable PBR materials.

Validation reopens saved Blender files, freshly imports GLBs, compares dimensions/triangle/part counts, checks degenerate triangles, image self-containment, canonical aliases, and file-size limits. Validation is structural; an independent visual review remains required. The manifest freezes every deliverable by SHA-256 and byte count. No publication is performed by these scripts.
