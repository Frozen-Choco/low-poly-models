# Additive batch05b photography configuration

Core render.py, standard.json and version.json are byte-identical to preview_standard_v1 as published in main commit 228340d0e621fc9ba6d3223973b6a8172afecfc8. The original 20-asset input/detail manifests are not modified. This separate folder contains only the new three-asset input hashes and explicit semantic close-up targets.

Published core Git blobs:
- render.py: 1e5fad9575c989982cb32eb35dd6ffda407e0163
- standard.json: a6219981286b79fcca9f91725c1159418fc2fc4b
- version.json: f5985c27ee36edcf19effc6c8b792c9bca08ed4f

Reproduction: run python photography/run_canonical.py. Set PHOTO_ONLY_ASSETS to a comma-separated asset ID list to limit a worker. Each worker runs one two-thread Blender 4.3.2 process at a time and validates existing records before skipping completed renders. A second worker may run only when an authorized CPU slot is free; atomic per-view locks prevent duplicate jobs. Geometry is imported and normalized only in memory. No exported model is changed. Renderer supports SOURCE_ROOT and resolves input repo_path relative to it. Output JPEGs and records are generated inside this additive folder and copied to each asset directory by the runner.

Views: preview, back, side, underside, close_up, alternate_light for each asset, plus mirror bracket_detail and AC service_detail. All use the standard scene/exposure/resolution; only documented semantic detail framing changes. Redundant prototype aliases are excluded from the curated distribution.

Raw intermediates, duplicated generated JPEG copies, logs and local proof scenes are not required distribution inputs. Keep the core/configuration, runner and exact measured JSON records with the canonical asset JPEGs.
