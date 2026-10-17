# ベッド・ソファ

Two original generic furniture models. Each includes an editable Blender file and GLB under100MB, and11 canonical JPEG views. Source photographs and manufacturer geometry are not redistributed. Final exact source-package acceptance is recorded in reviews/bed_sofa_integration/source_package_approval.json and bound to reviews/bed_sofa_integration/source_manifest.json.

Assets: assets/furniture. Regeneration, source URLs, design rationale, attachment graph and validation: generators/furniture_batch12a. Frozen photography and exact hash-bound records: generators/furniture_batch12a_preview_standard_v1. Raw diagnostics and draft assets are omitted.

Regenerate using Blender4.3.2 from repository root:
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/furniture_batch12a/scripts/build_assets.py
Outputs appear under the generator directory without overwriting delivered assets. Select one asset by appending -- bed or -- sofa.

ベッド: static single bed, wooden posts/rails,16 slats on continuous ledgers,900×2000mm mattress and pillow. Separate editable parts with natural longitudinal/end-grain textures. ソファ: static two-seat sofa, four wooden legs, lower rails and seat deck, padded arms/back, two seat and back cushions. Original generic construction differs from reference materials and proportions. No cloth physics, recliner mechanism, load certification or product endorsement.

Photography example:
SOURCE_ROOT="$PWD" OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/furniture_batch12a_preview_standard_v1/render.py -- bed preview
Substitute sofa or another recorded view. relocation.json maps original production records to packaged paths. Keep common lighting, materials, exposure,1200px resolution and512sample ceiling unchanged.
