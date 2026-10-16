# Eight independently reviewed diorama assets

This integration delivers カーブミラー, 室外機, グレーチング, 自転車, 台車, お玉, ざる and 木べら. Stable IDs, 16 model files and all 79 canonical photographs retain their exact approved bytes. Three additional exterior context/use images are also retained unchanged from the approved minimal source package. These are visual static props with bounded geometric checks, not engineering, safety, manufacturing or load certification.

## Current technical acceptance

- Exterior: reviews/reviewed_eight/exterior_final_approval.json approves exact source manifest aa2429348834d2b3882ae447abb98188f210c968641fc51fdeaf5d1ce5798747, all three models in both formats and 20 canonical views.
- Transport: the bicycle and handcart final reviews under generators/transport_batch06a/independent_review bind the actual model/image hashes and all 24 canonical views. The bicycle review explicitly allows later cart staging; the handcart final review explicitly allows inclusion of its report after its audited manifest. The delivered source snapshot is 0c46c47600cc2a340ba2b50c23973a6a39c26763e8908e50960a610eb9b07455. It is not falsely described as the older manifest directly reviewed by that report.
- Kitchen: reviews/reviewed_eight/kitchen_package_acceptance.json is the final acceptance for source manifest 6a947eeaedbce2bc515b71e472c366501ef255e9bf846a645f578fd29ed34262, resolving the earlier geometry gate's pending photography/package checks. All 35 canonical views are included.

Reports describe the acceptance state and paths at the time they were written. Their references to staging, no publication authorization, or then-pending downstream gates are historical scope statements, not current asset review status. Technical acceptance does not assert a GitHub publication has occurred. Source snapshots and independent reports remain unmodified. Current per-asset metadata and auxiliary catalogs identify final technical approval. The relocation map preserves both original and delivered hashes for each source item and explicitly identifies every metadata/documentation transformation. Rebuilt output requires a new review; unchanged historical generator code may still emit its original verbose titles and build-time status. Current delivered display names are the concise names listed above, bound to stable IDs; generated metadata must be reconciled with current display names and freshly reviewed before any later delivery.

## Reproduction and evidence paths

Transport and kitchen source READMEs under generators/transport_batch06a and generators/kitchen_batch07a give repository-root commands and separate output locations. Use Blender 4.3.2 and documented dependencies. Exact photography renderer, standard, inputs, semantic detail plan and original immutable per-image records are included. Original paths in evidence are provenance, not portable command paths; relocation maps bind those records to the delivered identical bytes.

Exterior geometry: from repository root run ASSET_OUTPUT_ROOT=/absolute/scratch/output SKIP_RENDER=1 blender -b -t 2 --python generators/exterior_batch05b/scripts/build_assets.py. ONLY_ASSETS may select a stable ID. Run validate_geometry.py with the same output root. Do not point output at delivered assets.

Exterior photography: copy generators/exterior_batch05b to a new scratch directory; create scratch/assets/SLUG and copy the delivered assets/exterior/SLUG/SLUG.glb to that directory. Verify each copied GLB against photography/preview_standard_v1/inputs.json. From this scratch directory, run python photography/run_canonical.py; PHOTO_ONLY_ASSETS may select IDs. This retains the original renderer's expected assets/SLUG layout and never modifies delivered assets or original records. All render configuration remains unchanged.

Reference URLs and object-specific simplifications are in generators/exterior_batch05b/docs/reference-and-use.md, generators/transport_batch06a/REFERENCES_AND_LIMITATIONS.md and generators/kitchen_batch07a/REFERENCES_AND_DESIGN.md. Downloaded manufacturer references, private conversation records, raw intermediates, caches, duplicate proof model files and operational logs are excluded.
