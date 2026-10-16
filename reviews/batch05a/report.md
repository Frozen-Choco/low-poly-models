# Independent review: batch05a

Status: GEOMETRY_FUNCTION_APPROVED only, bound to geometry_function_approval.json. Final standardized photography and publication approval remain PENDING per the latest parent instruction. Candidate manifest SHA256: cbb07f5fdb6d296c7de1dc5709b33a8679a059c9392ac858ca35dd32c848a12f.

Standard: review_standard_revision/docs/asset-standard.md. Reviewer has not edited production models or published files. Blender 4.3.2 inspection/rendering uses two threads per process. Reference pictures are private evidence only.

## Real-object reference gate
See reference-findings.md for independently opened official manufacturer sources and direct photo/drawing/manual inspections. Early feedback changed initial stool dowel-leg concept to the photographed square-leg side frames, seat cleats and fasteners. Bucket was grounded in Risu's actual PE/EVA Rabucket with pierced ears and hooked steel bail rather than combining all-PP Belc handle architecture with metal. Seiko official rear photo and manual support the clock's keyhole/recess and exposed rear battery/movement arrangement. Original dimensions/details are explicitly distinguished from literal replicas. No hidden electronics or manufacturing/load certification is required or claimed.

## Saved-file visual inspection
Independently reopened each final GLB and Blend, rendered front/back/side/bottom/top/mechanism views and close views of stool joints, bucket hooks and clock mounting/hand depths. Geometry and material appearance agree across the two formats. Blend dark background versus GLB gray background supplies contrasting reflections; both maker daylight and alternate warmer contextual images were inspected with current-GLB provenance verified. They remain diagnostic photographs, pending the new shared photography standard.

- Stool: four square splayed legs, staggered rounded stretchers, upper rails and seat cleats have credible connections. All felt feet are flat and coplanar. Seat silhouette is rounded, while square leg arrises remain crisp but softly sanded. Original subtle warm grain is packed, with some repeated seat-edge striping accepted as stylization.
- Bucket: closed floor, thick continuous tapered shell, integral pour lip and genuinely drilled ears. Wire hooks thread through the ears rather than floating beside them. Stainless bail reads differently from white polymer and gray grip. Center mouth is unobstructed.
- Clock: circular plastic rim, recessed white dial, coaxial layered hands, glass disc, recessed back and true keyhole. Low-sample path-traced glass produces noise; final presentation uses increased samples and render-only shadow handling. The portable GLB retains transmission material; rendering-app support affects glass appearance.

## Independent contact and use tests
Actual saved GLB and Blend produce matching results. contact_results.json records fresh ray and triangle-intersection tests; independent_function_results.json records component bounds and use poses.

Stool: seat-to-cleat gap is -0.000000030 m (numerical tolerance), cleat-to-upper-rail gap 0. Four sole centers at (±111, ±111) mm enclose the centered seat axis; all sole minimum heights are 0. Stretchers embed into leg ends, not floating. This checks shape/contact, not seating loads.

Bucket: center base thickness 6.000 mm, shell radial thickness 3.831/3.756/3.670 mm at 30/100/180 mm heights. Upward ray through center exits mouth unobstructed. Hook and grip rotation share X axis at z=229 mm. Sweeping actual mesh at 5° steps shows clear ordinary rotation from upright through 90°. A finer 0.1° sweep shows no grip/body intersections at 90.9° and first grip/pouring-lip contact at 91.0°. The rim naturally arrests forward folding there. Continuing a rigid transform through the stop produces collisions, as expected, and is not a usable pose. Initial maker 135° clearance claim was incorrect and required removal; an analytic circular-rim test had ignored the pouring lip and grip. No free 180° rotation is claimed. Actual tests exclude no bucket-body collisions; ear/wire clearances were checked separately.

Clock: hour/minute/seconds blades occupy 24.5–25.5, 27.5–28.5 and 30.5–31.5 mm depth. Dial front is 22 mm, glass inner face is 36.1 mm and retaining cap front is 34 mm, leaving positive clearances. Rotating each through 30° sample positions yields no dial/glass collisions. Actual keyhole entry, neck opening and backing recess are open, while both shoulders are solid. A separate 9.6 mm head / 3 mm neck review screw fits beyond the bridge without mesh intersections. Rear feet set a wall plane beyond the battery and knob. This is fit/retention plausibility, not fixing-strength certification.

## Source and packaging
A fresh independent build was run from a relocated copy of source with SKIP_RENDER=1 and a new output root inside the review directory. All regenerated GLB binary chunks are identical to production. JSON is identical after ignoring auto-suffixed mesh datablock names. Embedded images/buffers and PBR roughness/metalness/transmission recorded in reproduction_embedding.json. No reference pixels are used as asset textures.

The 61-file candidate manifest matches all package file hashes/sizes. All saved GLB/Blend finite-coordinate, nondegenerate-triangle, metric-dimension, count and metadata comparisons pass; embedded textures are packed. Canonical diagnostic preview/back aliases match their source views. Context provenance matches current GLBs. Every file is under 100,000,000 bytes. Final standardized photography and publication approval remain pending; this bounded decision does not authorize release. Geometry/material/source changes require re-review, while replacing diagnostic photographs must be assessed by the new photography gate.

Final geometry sizes/counts: stool 7,428 triangles, GLB 681,612 bytes; bucket 13,092 triangles, GLB 276,484 bytes; clock 13,764 triangles, GLB 763,884 bytes (exact file sizes also recorded in approval).
