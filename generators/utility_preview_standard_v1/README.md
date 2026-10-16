# Additive utility photography configuration

Three new approved inputs, isolated from the published 20-model configuration. render.py and standard.json are byte-identical to preview-standard-v1 at main 228340d0e621fc9ba6d3223973b6a8172afecfc8, metadata revision 1.0.1. inputs.json, views.json and detail_targets.json are new utility-only configuration; they do not claim to be the original configuration hashes.

From the publication root with Blender 4.3.2 and Pillow 11.1.0:

    SOURCE_ROOT="$PWD" blender -b -t 2 --python generators/utility_preview_standard_v1/render.py -- wall_clock close_up

Fresh output lands under this generator's repo/assets and records directories. Approved input hashes are asserted before and after rendering. The renderer never exports or saves geometry/material changes. Source meters are normalized only in temporary render scenes. All 1200-square JPEGs use q95, Cycles CPU two threads, 512 ceiling/adaptive .005, no denoise, fixed AgX exposure 0 and common neutral camera-relative lighting, 80% full-object framing. Detail crops document semantic features and magnify relative to whole-object framing. Axial/below-object views have the common flat background; elevated views have the common floor. Clock glass stays intact with original shadow/material behavior.

Run at most two simultaneous two-thread renders. Exact alias copies are declared in views.json; do not independently rerender aliases. Run audit.py from this directory to verify the publication layout and published records. Historical source/evidence is under ../utility_batch05a and is distinct from these canonical photographs.
