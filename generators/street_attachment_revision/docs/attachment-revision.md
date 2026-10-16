# Street attachment/contact revision

Two original generic Japanese-style diorama assets are repaired: traffic_signal and railway_crossing_lowered. This revision does not modify the recycling cabinet, approved signal palette, active lamp phases, or any other assets. Static props, artist-estimated dimensions; not construction plans or safety certification.

## Sources inspected and limits

- Sankosha, crossing crossmark AL: https://sankosha-s.co.jp/rail/rail_f_keihyou.html and manufacturer drawing https://sankosha-s.co.jp/rail/img/f/rail_f_s3.jpg. The manufacturer explicitly specifies a mounting plate and bolts, with U-bolts fixing that assembly to the warning mast. That connection principle informs the added plate/U-bolts. This model does not reproduce the product's 75-degree X, 5 mm aluminium blades, exact sizes, or certification. Its existing silhouette is retained; bracket dimensions are original artist estimates.
- Kyosan official barrier brochure: https://www.kyosan.co.jp/product/pdf/signal06_01.pdf. Inspected product photographs and text show separate pedestal/drive, shaft/socket and straight-arm configurations, including weightless variants. This supports preserving this assembly type. The brochure does not establish a precise upper stop for this generic model. Rather than asserting an undocumented limit, the whole drive/foundation/boom was moved 100 mm outboard and tested through 90 degrees. Export remains static lowered, without animation or internal mechanism.
- Nippon Signal official family: https://www.signal.co.jp/products/traffic/traffic_lineup/ and Osaka Police installation examples https://www.police.pref.osaka.lg.jp/kotsu/kisei/shingouki/12111.html establish Japanese horizontal signal context. Detailed rear attachment evidence is the supplemental installation photograph https://signallift1.com/wp-content/uploads/2020/06/ns-thin4-ed1151ab.jpg, showing a short flexible cable from support arm underside to rear housing. The replacement follows that connection principle, with artist-estimated cable path and glands. It does not claim to reconstruct hidden wiring or the exact pictured signal.

Reference photographs are private review inputs, not included as redistributed textures or published artwork. Both models remain original mesh geometry, no paid services, external generation, or third-party meshes/textures.

## Before and after

Traffic signal baseline: floating short vertical conduit, 57.421 mm away from mast and at least 1 mm clear of housing; rear service gasket detached by 3 mm. Replaced with a smooth 18 mm diameter flexible loop physically entering glands attached to the arm and rear cover. Gasket/cover/screws move together 3 mm toward housing; screw heads move a further 1 mm to seat in the cover. Existing housing/mast PBR values and all LED phases are exactly retained. Existing official-photo-informed palette remains approximate, not calibrated paint reflectance.

Crossing baseline: mast stops 10 mm above base plate; crossbuck has no bridging attachment; at a hypothetical 90-degree raised pose the arm touches the right warning hood. Mast bottom ring now meets plate top at z=.270 m. Existing upper stripes/mast attachments are unchanged. Added mounting plate and two U-bolts provide a connected crossbuck-to-mast load path. Entire separate gate unit moves +.100 m X, including concrete foundation, drive, rear cover/screws, shaft, hub, socket, clamp bolts and boom. New pivot is (.650,-.250,.880) m in Blender Z-up coordinates.

## Saved-file verification

See binary_manifest.json for exact reviewed Blend/GLB SHA-256, byte counts and Git blob SHA-1. functional/validation.json measures both reopened Blend and separately imported GLB, including contact overlap and planar support gaps. functional/assembly_test.json independently records mesh validity and the entire moving assembly sweep, not just an isolated boom. All changed binaries have zero area-zero triangles and finite coordinates.

The boom, pivot hub, socket and clamp bolts were tested at 361 poses (0 to 90 degrees, .25-degree increments) against all remaining static mesh parts. Only intentional hub/drive-shaft coupling is excluded from collision rejection. No unwanted surface intersections are reported. Sampled tests are not a proof of every intermediate assembly clearance. For the previously failing hood specifically, a conservative continuous bound is available: over 0–90 degrees the boom is at x >= pivot_x - maximum_radius = .650-.057=.593 m; right hood maximum x=.51100004 m. Thus that pair has at least .08199996 m X separation continuously, irrespective of Y/Z. This bound is not claimed for every component or a real vehicle/train installation.

Contact tolerances: mast/plate and gasket/housing planar surfaces meet to floating-point tolerance (~3e-8 m and ~8e-9 m respectively). Overlap tests verify cable/gland/arm/cover contact and U-bolt/mast/plate contact; such controlled overlap at joints is intentional for this visual asset. No structural strength, ingress protection, electrical functionality, mechanism gearing or manufacturing fit is certified.

## Visual evidence

functional/ contains actual saved Blend and GLB front/rear/side/underside/contact and raised-pose diagnostic renders, plus read-only clipped sections. Section cuts are uncapped diagnostic surfaces, not claims of hidden cavities. Workbench lighting is used to reveal geometry, not to certify final material appearance. previews/ has controlled before/after detail and base comparisons, plus neutral and alternate light directions; assets/ contains current canonical preview/back/detail/base JPEGs. These Cycles renders retain the source materials and use neutral studio light, AgX, 24 samples, 800 square resolution. They do not replace functional tests.

## Reproduction

Run with Blender 4.3.2, CPU and two threads:

    blender -b --threads 2 --python scripts/repair.py
    blender -b --threads 2 --python scripts/validate.py
    blender -b --threads 2 --python scripts/assembly_test.py
    blender -b --threads 2 --python scripts/render.py
    blender -b --threads 2 --python scripts/sections.py
    python scripts/package.py

All paths resolve relative to this revision folder. baseline/ contains exact immutable published input Blend files and metadata, asserted by SHA-256 before editing. Those input binaries matched published GitHub commit f2b79a4a710e58e207d46e646ff660e3c2596ef6 in the independent baseline audit. Repair writes exclusively to assets/. ONLY_ASSETS=traffic_signal or railway_crossing_lowered scopes rebuilding. Do not rebuild frozen binaries after approval; any binary change requires a fresh manifest and exact-file review. Blend container timestamps can differ on reproduction; approved delivery is identified by its exact hash, not assumed from procedural similarity. Original baseline directories are never modified.

Approval is granted only by the independent reviewer for the exact files. No publication is performed by these scripts.

## Independent outcome

The current exact model files passed independent source-grounded functional review. Public measurements and source are supplied here; private review records are not distributed. Regeneration changes require a fresh independent review before release.

## Published layout

Canonical downloads are repository-root assets/street/<id>/. From this generator directory, run the repair command FIRST; it writes isolated local assets/<id>/ outputs for subsequent validation and rendering. Those local outputs are not the published canonical files. Baseline inputs are immutable historical examples, not current deliverables. The public manifest supplies explicit canonical paths.
