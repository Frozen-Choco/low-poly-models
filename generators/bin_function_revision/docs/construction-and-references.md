# Generic recycling cabinet: construction and servicing revision

## Evidence and interpretation

Sources inspected 2026-10-16:
- https://www.teramoto.co.jp/products/7306/ specifies the Teramoto FT can-bin body at approximately 460 × 462 × 950 mm and its inner container at 410 × 435 × 525 mm; powder-coated electrogalvanized cabinet and recycled polypropylene container. The model is **not** that product. The documented 525 mm container height supports choosing a shorter internal container rather than forcing an implausible tilt.
- https://www.teramoto.co.jp/trashbox_ft_touchless_support/howtouse/ describes turning the front door lever, opening the front door and pulling out the inner container to fit a bag. Its lock-lever and bag/container diagrams were independently downloaded and visually inspected. It is a related touchless family, not evidence that this generic bin contains a sensor, electronic lid or identical hardware.
- https://www.teramoto.co.jp/trushbox_ft_series/ includes an open-door collection photograph, independently downloaded and inspected: an interior container is accessible behind a side-hinged door. The pictured drink collector has a different trolley/container and is used solely for the access principle.

Reference images in `reference/` are private review material, excluded from the publishing manifest. Do not republish manufacturer images.

## Deliberate changes from frozen baseline

- Retain exterior cabinet size, side and rear sheets, weather cap, blue two-hole fascia, chutes, pictograms, gray door and overall silhouette.
- Extend the recessed plinth top from 90 to 96 mm, contacting the existing floor bottom at 96 mm; floor widens from 440 to 466 mm to contact both side sheets as well as rear panel. Plinth footprint remains 420 ×380 mm.
- Inner container changes from 600 to 525 mm height, with bottom seated at floor top 114 mm. Outer footprint remains378 ×350 mm. Top is 639 mm, 46 mm below fascia bottom 685 mm. This sacrifices unproven volume for straightforward servicing and leaves more space for falling cans/bottles. Do not advertise the real maker's 67 L capacity for this smaller generic liner.
- Replace the solid slab named gasket with a moving perimeter seal behind the door. No fixed solid sheet crosses the service aperture.
- Trim the door upper edge 8 mm and move its upper return 8 mm down, producing about 5 mm clearance below fascia. This is a necessary minor exterior seam correction.
- Build explicit three-knuckle hinges, attached leaves, pins and screws; fixed outside knuckles and moving center knuckle. The two hinges share vertical axis (-.224,-.248,0).
- Extend the visible lock barrel through the skin, add an explicit quarter-turn cam and attached right-side keeper. A 90° turn retracts the cam from behind the keeper before opening. The detailed key tumbler internals are omitted.
- Add true through handgrips near the liner rim for hand lifting and withdrawal.

## Service procedure and proof scope

Production Blend and GLB remain closed and unanimated. Mesh custom properties identify `fixed`, `door`, `latch`, `liner` service groups. The reproducible verification script independently reopens both formats and rotates the cam 90° about Y through (.16,-.206,.62), rotates door plus unlocked cam 110° clockwise about Z through (-.224,-.248,0), lifts the liner 2 mm by hand, then translates it 650 mm toward-Y. No tilt is needed. Return sequence reverses those operations. The liner should be supported by an operator during withdrawal; the proof does not claim self-support in free air.

The latch and door sweeps use saved mesh BVH intersection checks, with intentional pin/knuckle mating interfaces excluded and disclosed. Linear container extraction additionally uses a conservative swept bounding-box corridor: zero obstacle overlap establishes continuous free clearance between sampled positions. The floor support at the closed pose is intentional contact. The initial 2 mm upward lift is also checked by its swept envelope. Sampled rotational testing is not an industrial tolerance or dynamics certification.

One mixed can/bottle liner is intentional. The two actual holes and open chutes discharge over its open interior. No waste, bags, fire rating, rainproofing, anchorage strength, accessibility compliance or installation certification is claimed. Sheltered public-space context is an artistic interpretation. All unlabeled dimensions and mechanical details are original design estimates, not measurements or manufacturer claims.
