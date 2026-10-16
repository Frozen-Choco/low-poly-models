# Traffic cone functional revision

Original generic Japanese-context hollow PVC traffic cone, 0.36 × 0.36 × 0.70 m. This revision corrects the sealed underside of the prior asset and includes verified three-instance nesting. Pending independent review until an external reviewer approves the exact manifest hash.

## Files
- `assets/street/traffic_cone/`: production GLB, compressed editable Blend, front/rear/top/underside JPGs, metadata and saved-file validation.
- `evidence/`: saved three-instance GLB/Blend, stack and section JPGs, diagnostic cutaway Blend and evidence reopen report.
- `docs/construction-and-references.md`: evidence, original estimates and limitations.
- `scripts/`: complete deterministic model source, verification/rendering and packaging scripts.

## Reproduce
Requires Blender 4.3.2 with its bundled Python/NumPy. No network or external asset dependencies.

From this directory:

    blender -b --threads 3 --python scripts/build_cone.py
    blender -b --threads 3 --python scripts/validate_and_demonstrate.py
    blender -b --threads 3 --python scripts/verify_evidence.py
    blender -b --threads 3 --python scripts/render_context.py
    python3 scripts/create_manifest.py

For a published layout with source under `generators/cone_function_revision/`, set `ASSET_OUTPUT_ROOT` to the repository root for all commands. Only the explicit `assets/street/traffic_cone` asset is written. Evidence/support stay beside the generator. The manifest maps production assets to their canonical paths and supporting files into this generator namespace.

Rendering uses 1000 × 1000 pixels, 48 Cycles samples, three CPU threads, neutral daylight studio. Full rebuild and evidence rendering take several minutes. All GLB textures are embedded; Blend images are packed. Limits and factual distinction between manufacturer specification and model estimates are documented separately.

Context rendering requires the already-approved streetlight and park_bench GLBs in the canonical asset tree. If they are in a separate package, set REFERENCE_ASSET_ROOT to that package root. The exact input hashes are recorded in evidence/context_inputs.json; the saved context Blend is self-contained.
