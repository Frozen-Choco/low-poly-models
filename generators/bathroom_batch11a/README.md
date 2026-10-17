# トイレ・洗面台

Two original generic unbranded bathroom fixtures for diorama use. Each includes an editable Blender file and GLB under100MB. トイレ has14 canonical JPEG views including independent seat/lid open and bowl interior. 洗面台 has12 views. Source photographs and manufacturer geometry are not redistributed.

Assets are in assets/bathroom. Regeneration, design rationale, attachment graph and validation are in generators/bathroom_batch11a. Frozen photography and exact hash-bound records are in generators/bathroom_batch11a_preview_standard_v1. Raw diagnostics and draft assets are deliberately omitted. Final exact source-package acceptance is recorded in reviews/bathroom_integration/source_package_approval.json and bound to reviews/bathroom_integration/source_manifest.json.

Regenerate with Blender4.3.2 from repository root:
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/bathroom_batch11a/scripts/build_assets.py
Outputs appear under the generator directory without overwriting delivered assets. Select a single asset by appending -- toilet or -- washbasin.

トイレ: frame1 closed, lid opens88 degrees during1–31, seat opens82 degrees during31–61, hold to91, close by151. A shared axis with separate rotating barrels supports both motions. Tank cover and plumbing are static editable parts. Floor drain socket is recessed6mm inside the skirt. Simplified visible drainage is not a fluid simulation.
洗面台: static editable pedestal, basin, side-lever faucet and plumbing. Rear mounting plane y=.2595m assumes an installation wall, which is not included. Pedestal floor support and wall brackets are distinct. Open overflow, drain and outlet are visually connected; no hydraulic or internal valve simulation.

Closed photography example:
SOURCE_ROOT="$PWD" OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 blender -b -t 2 --python-exit-code 1 --python generators/bathroom_batch11a_preview_standard_v1/render.py -- toilet preview
Substitute washbasin or another recorded view. To regenerate render-only open pose from delivered GLB, run generators/bathroom_batch11a/scripts/prepare_poses.py with Blender. Then use toilet_open open or toilet_open interior. Render-only poses are not extra catalog models and are omitted from this lean package. relocation.json maps original production records to packaged paths. Keep the shared lighting, materials, exposure,1200px resolution and512sample ceiling unchanged.
