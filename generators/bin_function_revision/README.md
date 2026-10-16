# Generic recycling cabinet functional revision

An isolated, reproducible repair of `public_recycling_bin`. Historical original models remain available in repository history. This package preserves the cabinet appearance, restores real support contacts and supplies a removable 525 mm liner, proper moving door seal, hinge hardware and quarter-turn latch. Detailed evidence, inferences and limits are in `docs/construction-and-references.md`.

## Reproduce

Requires Blender 4.3.2 and Python 3; no downloads, paid services or third-party asset generation. From this directory:

    SKIP_RENDER=1 blender -b --threads 2 --python scripts/build_bin.py
    blender -b --threads 2 --python scripts/verify_service.py
    blender -b --threads 2 --python scripts/validate_geometry.py
    blender -b --threads 2 --python scripts/render_evidence.py
    blender -b --threads 2 --python scripts/validate_evidence.py
    python3 scripts/package_manifest.py

Default output is `assets/public_recycling_bin`. When installed as `generators/bin_function_revision`, set ASSET_OUTPUT_ROOT to the repository's `assets/street` directory for all commands; only this named asset is written. Evidence, source and documentation stay beside the generator. The manifest maps files to canonical publication paths.

## Deliverables

- Closed editable Blend and static GLB, with embedded procedural PBR materials and no textures.
- Front, rear, close-up and underside asset images; preview/back gallery aliases.
- Open-door and withdrawn-liner proof poses in both formats; service cutaway and two sheltered-context images; self-contained context Blend.
- Reopened-file contact, service-motion and geometry validation JSONs.
- Required gallery fields in `catalog_entry.json`; authoritative frozen SHA256 manifest. This package does not edit or publish the gallery.

The inner container is hand-supported during servicing. The depicted liner is not the maker's 67 L product. Production files remain unanimated; the proof transforms and service groups make each state reproducible. Manufacturer reference images are private review material and deliberately excluded from publication.

For trial reproduction, prefer the default generator-local output or a separate ASSET_OUTPUT_ROOT. Rebuilt files require independent review before replacing published canonical assets. No baseline folder is required.
