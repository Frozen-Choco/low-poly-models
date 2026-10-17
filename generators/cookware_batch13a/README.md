# フライパン・鍋

Two original generic cookware models. Each includes an editable Blender file and GLB under100MB, and11 canonical JPEG views. Source photographs and manufacturer geometry are not redistributed. Final exact source-package acceptance is recorded in reviews/cookware_integration/source_package_approval.json and bound to reviews/cookware_integration/source_manifest.json.

Assets: assets/kitchen. Regeneration, source URLs, design rationale, attachment graph and validation: generators/cookware_batch13a. Frozen photography and exact hash-bound records: generators/cookware_batch13a_preview_standard_v1. Raw diagnostics and draft assets are omitted.

Regenerate using Blender4.3.2 from repository root:
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/cookware_batch13a/scripts/build_assets.py
Outputs appear under the generator directory without overwriting delivered assets. Select one asset by appending -- frying_pan or -- cooking_pot.

フライパン: static open bowl with continuous walls and bottom, shallow coated rivet heads, metal mounting/tang, phenolic grip with hanging hole and induction base. 鍋: static open vessel with real-thickness steel exterior, open loop handles, separate removable lid with locating skirt, steam vents, knob and fasteners. Manufacturer dimensional/morphology references inform original generic construction. Internal metal lamination, cooking/heat simulation and engineering certification are not included.

Photography example:
SOURCE_ROOT="$PWD" OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/cookware_batch13a_preview_standard_v1/render.py -- frying_pan preview
Substitute cooking_pot or another recorded view. relocation.json maps original production records to packaged paths. Keep common lighting, materials, exposure,1200px resolution and512sample ceiling unchanged.
