# Hollow traffic cone: functional correction r1

## Why this revision exists
The earlier asset had an inner tapered wall but a solid square base sealing the cavity. That prevented ordinary cone nesting. The earlier non-stackable limitation did not satisfy the requested ordinary real-world prop. This isolated revision replaces it; the old frozen batch has not been edited.

## Actual-object evidence (checked 2026-10-16)
- Daiichi Smart Cone product page: https://www.idc-daiichi.co.jp/products/smartcone/ . Manufacturer lists 700 × 360 × 360 mm, 3.5 kg, PVC body and recycled-PVC base. These nominal envelope dimensions and material classes are the selected commercial context.
- Manufacturer underside photograph: https://www.idc-daiichi.co.jp/wp/wp-content/uploads/2025/07/smartcone-06.png . Shows the open bottom, orange internal tapered wall, black annular square base, molding pockets/ribs and closed distant tip. Photograph inspected, not redistributed.
- Daiichi PVC Eco Cone: https://www.idc-daiichi.co.jp/products/pvcecocone/ . Explicit stacking-block feature supports the general principle of base-supported stacking. Its different dimensions and formulation are not assigned to this model.
- Nishimatsu publication JP2005220650A: https://patents.google.com/patent/JP2005220650A/ja . Description identifies ordinary cones as hollow with open bottoms and nested storage, and discusses base support maintaining clearance between shells. Used only as functional background, not a claim that this model copies a commercial or patented construction, or any legal assessment.
- Rental-use corroboration: https://topsplan-kanto.jp/rental/ks0070.html . Shows cone underside and nesting in handling; its different nominal size is not used here.

## Original design estimates, not measured commercial specifications
The 3.2 mm nominal radial wall, 4 mm closed top cap, 298 mm underside bore, 28 mm base rim height, 4 mm underside pocket depth, eight ribs, four generic diagonal support lands and 40 mm nesting pitch are original modeling choices. They have not been reverse-engineered or physically measured. The narrow neck is closed, consistent with the selected product photograph; this is not a cone with an open baton socket.

A single continuous surface encloses the PVC material. Interior and exterior meet around the lower aperture through the annular base. The lower opening is real geometry, not transparency or an inverted face. The base has inner and outer bearing rims, shallow underside pockets and radial ribs. Four integral top lands touch the next base's diagonal underside ribs at 40 mm pitch. Thus the nested copies have contact support rather than arbitrary floating placements.

## Verification and limits
`assets/street/traffic_cone/validation.json` records reopened Blend and decoded saved GLB results, geometric seam welding for testing only, full bounds, solid volume, axis ray, dense radial clearance samples, exact boolean intersection tests for adjacent and first/third cones, and four support contacts. The GLB itself retains its normal UV/material vertex seams.

Material volume is approximately 0.002793 m³. Using an explicitly assumed illustrative density range of 1200–1600 kg/m³ gives approximately 3.35–4.47 kg. This is a plausibility check only; the reference's 3.5 kg is not a certified mass of this original model. No density was measured. No claims about manufacturing, compliance, loading, friction, wind resistance or flexible deformation are made.

The three-cone and cutaway evidence is generated from the reimported saved GLB. Cutaways use diagnostic wall colors and are not production assets. Standard glTF PBR approximates white reflective bands; it does not reproduce optical retroreflection. The finish texture is an original seeded 128-pixel image embedded in GLB and packed in Blend. No downloaded geometry, brand markings or reference images are included.
