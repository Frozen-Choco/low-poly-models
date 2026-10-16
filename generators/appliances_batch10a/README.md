# テレビ・掃除機

Two original generic Japanese diorama assets. One editable Blender file and one GLB each. テレビ has 12 canonical JPG views; 掃除機 has 14, including bag-lid open and interior. No brand marks, external textures or engineering certification. Final exact source package acceptance: reviews/tv_vacuum_integration/source_package_approval.json.

Assets: assets/appliances. Regeneration sources, references, attachment graph and validation: generators/appliances_batch10a. Reference photographs, draft files and raw PNGs are excluded from this lean candidate.

From package root with Blender4.3.2: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/appliances_batch10a/scripts/build_assets.py . Outputs are written beneath that generator, without overwriting delivered models. テレビ is static. 掃除機 lid closes at frame1, opens 100 degrees at61–91, closes at151. Other parts are static editable geometry; no electrical/suction/hose deformation simulation.

The shared frozen photography core is in generators/appliances_batch10a_preview_standard_v1. Closed example: SOURCE_ROOT="$PWD" OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/appliances_batch10a_preview_standard_v1/render.py -- television preview . Substitute vacuum_cleaner for the other asset.

Render-only open GLB is deliberately omitted. Regenerate from the exact delivered GLB using generators/appliances_batch10a/scripts/prepare_poses.py with Blender; then render vacuum_cleaner_open open or vacuum_cleaner_open interior with the same frozen renderer. The derived pose is a rigid transform only. Original production records are retained; relocation.json maps exact files to their packaged location. Do not change shared lighting, resolution, sampling, exposure or materials.
