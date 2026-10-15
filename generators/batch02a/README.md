# Street props batch 02a — review candidate

Three original Japanese-context diorama props: streetlight, park bench, and traffic cone. No third-party artwork, downloaded geometry, logos, or brand replicas. Dimensions are approximate design choices, not measured engineering specifications. No publication is authorized by this package.

## Artifacts

Each `assets/street/<id>/` contains:
- `<id>.glb`: self-contained glTF 2.0 binary, standard Y-up
- `<id>.blend`: compressed editable source, Z-up, meter units
- `preview.jpg`, `back.jpg`: front three-quarter and rear views
- `detail.jpg`: closer view of curved/material detail (streetlight underside)
- `metadata.json`: dimensions, triangle count, references, sizes, hashes
- `validation.json`: saved-file reopen/reimport geometry checks

The asset collection is named `ASSET | <id>`. `PREVIEW STUDIO` is excluded from the exported GLB and hidden in the normal Blend viewport. Root origins are on the ground, at the mast, bench center, or cone base center. Asset front is Blender -Y.

## Reproduction

Use Blender 4.3.2 or compatible version:

    blender -b --threads 4 --python scripts/build_assets.py
    blender -b --threads 4 --python scripts/validate_assets.py

Set `ONLY_ASSETS` to a comma-separated subset if desired. No external generation API, paid service, or downloaded asset dependency is used. `timber_grain.png` is original deterministic generated artwork, embedded in GLB and packed in Blend; its source algorithm is in the build script. Rebuilds can change compressed container hashes while preserving geometry.

## Limitations

These are visual props, not manufacture-ready objects. Hidden foundations, electrical internals, certified road markings, precise structural connections, and safety compliance are outside scope. The lamp is unlit. White cone sleeves approximate reflective sheeting using ordinary PBR materials, not physically accurate retroreflection. Generic designs do not represent every regional Japanese fixture. Neutral studio lighting is used; rendering in other applications varies.

## Sources

Reference URLs were checked on 2026-10-15 for general Japanese product context. No reference images are included:
- Streetlight: https://www.iwasaki.co.jp/lighting/road_tunnel/anticrime/
- Bench: https://townscape.kotobuki.co.jp/product/bench/
- Bench proportions/context: https://townscape.kotobuki.co.jp/catalogs/images/KTB-42.pdf
- Cone families: https://www.sanko-kk.co.jp/products/safety/corn/

Ready for independent review only after the validation report is present. This package is not a review approval.

## Context and integration

`context/daylight.jpg` and `context/alternate_light.jpg` show the three actual exported GLBs together at meter scale, with pavement contact, neutral daylight, and an alternate light direction. Recreate with `blender -b --threads 4 --python scripts/render_context.py` after building. The context Blend is evidence, not a fourth deliverable prop. Original compact galvanized and ballast finish images are generated and packed along with the timber grain.

Run `python scripts/create_manifest.py` after all files are finished. `review_manifest.json` maps exact relative files and SHA-256 values to canonical `assets/street/<id>/` paths and collision-free `generators/batch02a/` source/evidence paths; it expresses review candidacy, never approval. No absolute private path is required for reproduction.

Published-layout reproduction from the repository root: `ASSET_OUTPUT_ROOT="$PWD" blender -b --threads 4 --python generators/batch02a/scripts/build_assets.py`, then the same command with `validate_assets.py` or `render_context.py`. Without that variable, outputs stay self-contained beside the source. Support reports remain namespaced; the root catalog must be merged by the integrator.

## Evidence render budget

Asset previews use 1000×1000 JPEG, Cycles 64 samples, 3 CPU threads and no denoising (the installed build lacks OpenImageDenoise). Recorded r2 image runtimes ranged from approximately 34 to 169 seconds under shared load. Context images use 1200×1100 at the same sample count. These are review evidence, not 4K beauty renders. The validation script only processes the three explicit IDs in this batch even when `ASSET_OUTPUT_ROOT` points at a shared asset repository.

Revision r3 corrects the bench transverse-brace connection and includes a source-coordinate contact audit. The cone has a solid ballast base and is deliberately non-stackable in this visual model. Manifest regeneration honors ASSET_OUTPUT_ROOT and includes only explicit batch assets/support files.

For the dedicated bench end-grain/joint close-up, run `blender -b --threads 3 --python scripts/render_bench_endgrain.py` (use the same ASSET_OUTPUT_ROOT convention in published layout). `scripts/test_published_layout.py` checks canonical file resolution and verifies an unrelated sentinel asset is untouched.
