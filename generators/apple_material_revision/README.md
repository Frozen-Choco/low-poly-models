# Apple material revision

This package corrects the published apple's wood-like skin. It does not add a new asset. The geometry, stem and calyx are byte-for-byte unchanged in the material modification step; geometry hash and saved-model tests are recorded separately.

The published old material is a comparison input only, not the approved result. The exact approved geometry Blend is included under inputs so regeneration does not depend on another batch or a private workspace.

Rebuild with Blender 4.3.2:

    blender -b -t 2 --python-exit-code 1 --python scripts/revise_material.py
    python scripts/extract_material.py

ASSET_OUTPUT_ROOT can isolate the output asset directory. APPLE_SOURCE_BLEND is an explicit optional source override. Default input is package-local inputs/approved_apple_geometry.blend, with inputs/metadata.json beside it. The source input is never changed.

Original texture pixels only. No downloaded photographs are embedded as textures. See docs/diagnosis.md for root cause, actual reference, rejected first trial and PBR rationale. material_revision.json records exact values and geometry preservation. glb_pbr.json is extracted from the delivered GLB itself.

The exact saved model/material has passed independent review, including rear/top/alternate and a separate single-light test. Canonical photographs use the independently reviewed preview_standard_v1 pipeline. No publication is performed by these tools.

Current canonical images are repository-root assets/food/whole_red_apple/. Historical before/after images under history/comparison_final are clearly superseded-versus-current material comparisons; their provenance records shared capture parameters and hashes, not a standalone regeneration tool. Use generators/preview_standard_v1 for current photograph reproduction. The original generators/batch04a images/material are historical and must not overwrite this revision.
