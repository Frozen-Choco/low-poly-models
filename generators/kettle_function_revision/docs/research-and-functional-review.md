# Kettle functional revision

## Manufacturer evidence inspected

1. [Miyazaki Objet kettle product page](https://miyazaki-ss.co.jp/product/%E3%82%B1%E3%83%88%E3%83%AB-2/), inspected 2026-10-16. Manufacturer lists 18-8 stainless body/lid and phenolic handle/knob. Its [product photograph](https://miyazaki-ss.co.jp/wp-content/uploads/2022/12/kettle-scaled.jpg) visibly places handle feet fore and aft, in the spout plane. Its [in-use pouring photograph](https://miyazaki-ss.co.jp/wp-content/uploads/2022/12/020_d.jpg) shows pouring while holding the arch and retaining the lid with the other hand. These visual observations, rather than an inferred convention, determine the revision.
2. [Yoshikawa aikata kettle](https://www.yoshikawa-lifestyle.com/products/aikata-stainless-kettle/), inspected 2026-10-16. The manufacturer explicitly describes a lifting handle lock and specially shaped lid/body retention. These are product-specific features; this generic model does not claim to reproduce those mechanisms.

Reference JPEGs were downloaded only for inspection. They are excluded from the distributable manifest and are not textures or deliverables. This is still an original generic kettle, not a replica of a named product.

## Exact root cause

The original model put the spout along +X but its carrying arch in the YZ plane, with opposite feet on ±Y and a common hinge axis Y. That is a mechanically coherent folding bow, but the free hinge rotation coincides with the rotation needed to tip the kettle toward its spout. A hand rotating this arch about Y can swing the handle relative to the body instead of transmitting the intended pouring torque. The earlier visual/mesh review did not verify this real-world functional relationship. The error is the orientation of the entire handle-and-hinge assembly relative to the spout, not an inherently invalid in-plane hinge pin.

## Repair

The revised arch lies in XZ, aligned fore–aft with the spout. Its feet and coaxial hinge pins are on X. Separate fixed shoulder mounting feet, fixed cheeks and moving stainless tangs show the actual load path. The fold axis X is perpendicular to the pouring axis Y: lateral fold is permitted, while fore–aft pouring torque is transmitted through the handle and attachments. A wider insulated crown provides a plausible gripping surface.

The shell, open spout and knob are preserved. The lid is also repaired: its original flared underside interfered with the 55 mm-radius neck during initial extraction. The replacement has a straight skirt of 53.8 mm outer radius and 52.6 mm inner radius, with a seating flange above the rim. The flange underside sits 2 micrometres above z145 mm to avoid contact-only numerical ambiguity. This tiny modeled separation is not a manufacturing tolerance specification. The other two household models and the entire prior approved batch remain untouched.

## Verification and limits

- Before/after top, side and three-quarter images are fresh imports of the respective saved GLBs.
- Carrying arch center reaches z=259 mm; crown underside is approximately 249 mm. Knob top is 176 mm, leaving approximately 73 mm vertical space under the central grip.
- The folded inspection rotates only moving tangs and arch by 90 degrees around the shared X axis through z=152 mm. The lid/knob lift 105 mm vertically after lateral folding.
- The pour inspection rotates the whole kettle 35 degrees about Y around the grip center, with a vertical translation to position it over a receiving cup. The blue stream is an illustrative trajectory, not simulated water.
- The loose lid is held in place in this inspection, consistent with the manufacturer photograph showing a second hand. The model has no claimed self-locking lid or certified safety mechanism.
- This is a visual/kinematic asset check, not manufacturing engineering, load/friction testing, hot-water safety certification, ergonomics certification or fluid simulation.

## Additional geometric evidence

The saved-GLB mechanism audit measures at least 71.60 mm clearance between the knob and the central 30 mm gripping region. At the lateral-fold endpoint, projected triangle bounding boxes establish a conservative 22.71 mm radial gap between the moving assembly and the full vertical lid-removal cylinder. A separate diagnostic tests triangle intersections against the shell, lid, knob, spout and fixed shoulder bases every one degree from -90 to +90 degrees. This is a sampled sweep, not a proof for every continuous angle. Intentional pin/bore bearing interfaces and moving-to-moving attachment overlaps are excluded.

The separate contact diagnostic uses blue finger/palm clearance envelopes and an orange fingertip envelope touching the lid knob. The labels explicitly identify these as diagnostic envelopes, not hand anatomy. They are excluded from the kettle GLB and editable asset Blend. Their role is to make the grip-space and retained-lid assumptions visible rather than silently leave the lid in place in a tilted pose.


## Initial extraction defect and repair

Independent testing caught a second defect missed by the earlier mesh review: the original lid expanded to radius 57 mm below the 55 mm neck opening, so a final exploded pose concealed interference during the first 1–2 mm of lift. The revised straight 53.8 mm skirt provides 1.2 mm radial clearance in the neck. Extraction is tested against saved body triangles at 0.1 mm intervals through the first 5 mm, then 0.25 mm through 15 mm and 1 mm through 105 mm. The archived before GLB and its lid remain unchanged.
