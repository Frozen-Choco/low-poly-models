# Historical geometry/function research record

This original record describes the pre-standard diagnostic photography. Canonical photographs now use the unchanged common preview-standard-v1 renderer, with intact clock glass and no shadow overrides. Historical inspection images remain explicitly diagnostic. See ../README.md for portable source reproduction and ../../utility_preview_standard_v1/README.md for current photography.

# Reference and construction gate

Original generic unbranded diorama props, checked 2026-10-16. Reference photos and drawings were directly viewed; reference pixels/meshes are not included in the assets. This is geometric plausibility review, not engineering or load certification.

## Wooden stool

Official Pine Factory small stool: https://www.pinefactory.jp/product.php?code=stool-s-na
Photo: https://www.pinefactory.jp/upload/images/dining/stool/s-na/stool-s01_s.jpg
Assembly view: https://www.pinefactory.jp/upload/images/dining/stool/s-na/tool-skumi_a.jpg

Observed: round solid seat, four square-section splayed legs, upper side rails, staggered lower round stretchers; assembly image exposes two side frames, underside mounting cleats and fasteners. Reference nominal 280×280×450 mm. Original model uses a 300mm seat and 450mm height. Leg rings are cut horizontally so four felt soles sit flat. Upper rails touch mounting cleats, cleats touch the underside of the seat. Stretchers extend into legs as plausible concealed joints. Exact joinery depths, material texture, and sizes are artist-inferred; this is not a dimension-perfect replica. A stool must not be treated as a ladder and stretcher load capacity is not claimed.

## Plastic bucket with steel bail

Official Risu RABA-KET 8L: https://www.risu.co.jp/products/search/detail/t000100014292/
Photo: https://www.risu.co.jp/group/search/file/file0030/t010000002972.jpg
Engineering drawing: https://www.risu.co.jp/group/search/cad/BR8.pdf
Official catalog: https://www.risu-kogyo.co.jp/protools/pdf/catalog_protools.pdf
Manufacturer store material corroboration for related Active Bucket: https://store.shopping.yahoo.co.jp/risu-onlineshop/13030-7.html

Observed photo/drawing: tapered PE/EVA vessel; 280mm circular upper rim, 217mm body height, 187.7mm base, raised pierced ears to approximately 235mm; pouring lip extends depth approximately 301mm. Metal bail hooks thread through holes in raised ears; cylindrical molded grip encloses crown. Model preserves that topology with a continuous closed bottom and open mouth, integral lip and pierced ears. White body, stainless bail, dark gray grip. Wall/base thickness, exact hook bends and handle height are inferred; no stamped volumes, capacity calibration, watertightness or safety claims. No unrelated bolted pivot mechanism substituted.

## Wall clock

Official Seiko QXA709B: https://www.seiko-clock.co.jp/product-personal/wall_clock/standard/qxa709b.html
Rear photo: https://www.seiko-clock.co.jp/product-personal/QXA709B_back.jpg
Oblique photo: https://www.seiko-clock.co.jp/product-personal/QXA709B_diagonal.jpg
Manual: https://www.seiko-clock.co.jp/product-personal/up_files/AKX-055P.pdf

Observed: molded circular frame, front glass, recessed dial and layered coaxial hands; recessed rear quartz mechanism with AA battery access, adjustment knob, screw-fastened rear cover, upper hanging aperture/recess. Model intentionally uses generic bar indices and no maps, text, logos or proprietary dial. Original 300mm diameter differs from 368mm reference. Front glass is a real 1.8mm disc with portable PBR transmission. Hour/minute/seconds blades occupy separated depths with common spindle. A true boolean keyhole and backing recess admit a small screw head; contact feet establish rear wall plane and keep battery/knob from wall. Mechanism is exterior-only, not a working timepiece.

## Planned checks

Saved GLB and compressed Blend reread; finite coordinates, nonzero triangle areas, part/dimension consistency, image packing and file limits. Front/side/rear/underside/close views and two contextual light conditions. Stool: all four soles coplanar, seat/cleat/rail/leg connectivity and centered support polygon. Bucket: vessel cross-section, bottom closure, coaxial attachment holes, upright and swung handle poses with rim clearance. Clock: dial/hand/glass axial gaps, pivot coincidence and keyhole screw seating against wall. Final exact hashes are frozen only after independent review; no publication by this worker.

## Functional results and correction

- Saved-GLB ray measurements: both seat/cleat gaps are approximately -0.00000003m (floating-point tolerance); both cleat/rail gaps are zero. All four felt soles lie at z=0.
- Bucket base inner z=0.010m and outer z=0.004m give 6mm central base; the peripheral foot contacts z=0. Center-up ray escapes the open mouth. Mid-height horizontal wall measurement is approximately 3.76mm.
- An initial radial-only rim test was insufficient and falsely passed a 135-degree handle pose. Independent review caught actual grip/lip and later bail/body intersections. That pose is rejected, removed and not part of the deliverable. Actual saved-mesh BVH sweeps agree: 90.9 degrees is clear; 91.0 degrees starts grip/pouring-lip contact. This is the normal physical resting stop; the handle is not expected to pass through the vessel. Final functional views show 90 and 90.9 degrees only.
- Clock keyhole head entry, upper neck and backing recess are true openings; ray tests also hit the solid mounting shoulder. Test screw head is placed entirely beyond the bridge shoulder. Hand layering leaves 2.1mm between retaining cap and glass rear surface.
- Fresh-layout source reproduction under /tmp with explicit ASSET_OUTPUT_ROOT matched geometry, dimensions, mesh counts and GLB byte counts for all three props. ONLY_ASSETS test exported only the requested bucket. No external textures, absolute package paths or other batches are required to build.
- Clock preview glass has render-only shadow visibility disabled to reduce caustic sampling noise. The actual asset retains real transmission glass; no mesh/material substitution is used. Front glass is hidden only in the specifically named hand-layer inspection view.
