# Original household office/shipping props

Three generic props: taped corrugated carton, desktop stapler, A4 clipboard.
Each asset folder has embedded-material GLB, compressed editable Blend, metadata, canonical preview/back plus side/underside/detail views.

Rebuild with Blender 4.3.2, no external add-ons:

    ASSET_OUTPUT_ROOT=/absolute/output/root blender -b -t 2 --python scripts/build_assets.py
    ASSET_OUTPUT_ROOT=/absolute/output/root blender -b -t 2 --python scripts/validate_and_context.py
    ASSET_OUTPUT_ROOT=/absolute/output/root python scripts/package_manifest.py

The override is the complete output root. All generated assets, validation, contextual evidence and catalog remain under it. With no override, output is this package root. ONLY_ASSETS can restrict builder to a comma-separated set of the three IDs. Source, reference notes and README are package inputs, not copied by the builder. Textures are original generated, packed image albedos. No external generator or paid service used.

Status: independently reviewed and approved for generic static diorama use. See docs/reference-and-use.md for measured/model-estimated distinctions and simplifications.

Functional evidence rebuild:

    ASSET_OUTPUT_ROOT=/absolute/output/root blender -b -t 2 --python scripts/use_tests.py

SKIP_RENDER=1 permits a geometry/material reproduction smoke test without preview rendering. This does not replace the saved-GLB preview review. The use-pose files are review-only variants, not additional catalog assets.

Additional focused construction views:

    ASSET_OUTPUT_ROOT=/absolute/output/root blender -b -t 2 --python scripts/render_detail_views.py

The builder produces true lateral side views. scripts/render_side_views.py can refresh those alone from saved GLBs. Final package_manifest.py must run after all requested views and validation.

Published layout: canonical assets are at repository-root assets/household/<id>/. Reproduction defaults to isolated generator-local assets/<id>/. Build first, then run validation/tests there; independently review regenerated files before copying to canonical published locations. The public manifest maps source paths to repository paths.
