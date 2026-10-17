# Independent bed and sofa review

Both source revisions2 pass the saved-shape and early-shading gate. Exact Blend/GLB hashes are pinned in approval.json; final photography and exact package acceptance are separate.

Primary IKEA product photos, dimensions and assembly drawings were independently inspected. These are original generic adaptations. The bed keeps a900×2000mm mattress with wooden ledges and16slats; the sofa uses two separate cushions and a timber/deck support structure rather than claiming the reference product's exact steel/spring/ABS construction.

Both formats were independently reopened. All meshes are finite and weld-normalized manifold with UVs, packed image materials and nonzero volume; no duplicate/degenerate triangles or nonadjacent self-intersections. Bidirectional format comparison is within15nm for bed and exact for sofa. Four legs/posts are grounded. Structural and cushion intersections were reviewed by named object pair and classified as concealed joints, upholstery embedment, support contact or sewn piping.

The bed support path is posts to side/end rails, rails to ledgers, ledgers to16slats, slats to mattress and pillow. Rounded finite bedding volumes and all headboard bar joints were inspected. Initial foot-post/rail top-face overlap and mattress/head-post interference were corrected by a narrower post section and revised rail endpoints/heights. Final mattress/post interference is zero.

The sofa has four ground legs engaging the lower frame, crossmember and deck beneath the upholstered seat, internal arm panels joined to the frame, and rear posts/crossbar supporting the padded back. Seat/back cushioning and embedded piping are static geometric representations, not deformable cloth or load-certified furniture.

An important audit correction: Blender BVH overlap did not report exact coplanar faces at the sofa lower-frame corners. Direct grouping by unoriented plane followed by projected triangle clipping exposed4same-facing overlap joints. Revision2 raises side rails2mm, preserving positive structural engagement while removing coincident external planes. The direct method now reports zero coplanar overlaps for sofa. Bed retains10triangle-pair overlaps, all opposite-facing ledger ends butting into posts; these are concealed mating surfaces, not exposed overlays. Original1200px revision2 underside images confirm the black corner artifacts are gone.

All28 revision2 low-sample images were individually viewed at original resolution across both formats and front/back/top/side/underside/close-up/structure views. Rounded fabric shading, wood-grain axes, bedding seating, support/frame joints and material parity passed. The generator was run independently in an isolated temporary directory; both regenerated GLBs are byte-identical to delivered files. No source model edits were made by reviewer.

The renderer and specification must stay byte-identical to the frozen standard. Each final JPEG and record will be individually bound to source/core hashes in canonical_full_sets.json after visual review. Publication remains paused and no GitHub operations were performed.
