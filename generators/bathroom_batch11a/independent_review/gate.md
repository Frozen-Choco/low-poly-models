# Independent bathroom-fixture review

Approved source revisions: toilet 10, washbasin 8. Exact files and hashes are bound in approval.json. Final canonical-image and package approvals remain separate.

## Source and scale
The reviewer inspected both pages of each primary manufacturer specification sheet, the TOTO 2000px product photograph, and KOHLER 1500px photograph. These are original unbranded generic models, not dimension-identical replicas. TOTO reference width436/depth720/height766mm and KOHLER basin608/depth519/rim-height895mm informed the designs. Full saved dimensions include fittings; reference rim height is not full faucet height.

## Geometry and assembly
Both final Blend/GLB formats have finite grounded meshes, UVs, zero duplicate or degenerate triangles, zero weld-normalized nonmanifold edges, and zero nonadjacent self-intersections. Each file is far below100MB. Both formats agree geometrically at eight sampled poses.

Ceramic walls, bowl openings, pedestal, rear services, drain sockets, supply connections and fixture supports were checked. Early defects were corrected: pedestal pipe penetration, solid drain connectors, absent overflow bore, obstructed internal passages, disconnected stop wheel, unsupported lid hinge, and exposed coincident bottom faces. Independent centerline rays through the modeled drain/overflow/spout paths found no obstructing surfaces. This is a visual geometric check, not hydraulic simulation or installation certification.

The toilet's separate seat/lid barrels rotate around a shared fixed axis. All151 sampled animation frames in both formats showed no unintended moving-body interference after corrections. Pin engagement and seated bumper contacts are intentional. All six bumpers support their corresponding components.2160 samples across the closed bowl aperture were covered by the lid. These sampled checks do not certify manufacturing tolerances or all continuous-time configurations.

The final toilet floor skirt uses a simple open rear service area, avoiding unstable tangent boolean cuts. All other meshes/material bindings matched the motion-tested revision at eight sampled poses. Washing-basin bore-to-overflow outer-wall exact-fit contacts have opposite normals and are concealed; no exposed duplicate surfaces remain.

## Surface and image gate
Original1200px low-sample views were individually inspected. High-quality first-image checks additionally caught a subtle triangular ceramic-normal defect beside the overflow. A controlled diagnostic with the metal insert hidden retained the defect, confirming it was not a cast shadow. Transferring the intact ceramic surface normals onto the original surface eliminated it without changing geometry, materials, or hole-wall normals. The defective photograph set was superseded and excluded from final approval.

Common renderer/specification hashes remain byte-identical to preceding approved batches. Every final image is independently viewed at original resolution and bound to its input/output/record/core hashes in canonical_full_sets.json. Generation and open-pose reproducibility have separate records. Only the exact final package manifest may be accepted for publication by the parent.
