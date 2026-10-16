# Fore–aft kettle handle repair

An isolated revision of stainless_kitchen_kettle. Prior batch03a stays frozen; the bowl and board are unchanged.

Reproduce using Blender 4.3.2:

    blender -b -t 2 --python scripts/build_kettle.py
    blender -b -t 2 --python scripts/verify_revision.py
    blender -b -t 2 --python scripts/audit_mechanism.py
    blender -b -t 2 --python scripts/diagnostic_grip_and_sweep.py
    python scripts/package_manifest.py

ASSET_OUTPUT_ROOT controls the revised asset output folder. Verification reads the archived baseline GLB included in baseline/ only to render before images; its bytes match the original batch03a kettle. Render threads are fixed at two and denoising is disabled. Geometry and materials are original. External manufacturer photographs are inspection references only and excluded from the package manifest.

See docs/research-and-functional-review.md for actual manufacturer evidence, exact mechanical diagnosis, the repair and stated verification limits. Revised GLB and compressed editable Blend are in assets/stainless_kitchen_kettle. Standard previews, before/after top/side/three-quarter comparisons and posed pour/lid-removal evidence are included. No publication is performed.
