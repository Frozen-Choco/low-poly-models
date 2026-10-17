# トースター・扇風機

Two original generic domestic appliance models. Each includes an editable Blender file and GLB under 100 MB, and 11 canonical JPEG views. Source photographs and manufacturer geometry are not redistributed. Final exact source-package acceptance is recorded in reviews/toaster_fan_integration/source_package_approval.json and bound to reviews/toaster_fan_integration/source_manifest.json.

Assets: assets/appliances. Regeneration, source URLs, design rationale, attachment graph and validation: generators/appliances_batch14a. Frozen photography and exact hash-bound records: generators/appliances_batch14a_preview_standard_v1. Raw diagnostics and draft assets are omitted.

Regenerate using Blender 4.3.2 from repository root:
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/appliances_batch14a/scripts/build_assets.py
Outputs appear under the generator directory without overwriting delivered assets. Select one asset by appending -- toaster or -- electric_fan.

トースター: static 2-slot appliance with real shell thickness and open slots, internal bread cages, heater substrates, linked lever and sliding crumb tray clearance. 扇風機: static 7-blade fan with solid pitched blades, open wire guards, retained rims, rear-supported head and weighted base. Manufacturer dimensions/materials/morphology inform original generic construction. Internal electrical machinery, cable beyond strain relief, heating/airflow simulation and safety certification are not included.

Photography example:
SOURCE_ROOT="$PWD" OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/appliances_batch14a_preview_standard_v1/render.py -- toaster preview
Substitute electric_fan or another recorded view. relocation.json maps original production records to packaged paths. Keep common lighting, materials, exposure, 1200px resolution and 512 sample ceiling unchanged.
