# Construction references and bounded-use limitations

These are original generic Japan-compatible diorama meshes, not certified mechanisms, exact commercial replicas or downloaded manufacturer geometry. Reference photographs/manuals informed visible construction and proportions only. No manufacturer downloads are distributed.

## Bicycle

- Bridgestone Ebridge U E60U1 single-speed chain family specification: https://www.bscycle.co.jp/products/brands/EBRIDGE/E60U12021/E60U1_2.html . The source confirms the 26-inch wheel family, steel frame/carrier, chain drive, 31-tooth front sprocket, front caliper and rear roller brake. No belt or derailleur mechanism is mixed into this model.
- Official family appearance: https://www.bscycle.co.jp/items/images/bodies/img_ebridgeU_2021_cmlbn@2x.jpg . Shared shapes only; the pictured family variant's shifter is not authority for this single-speed configuration.
- Official city-bike manual, including paired-stand lock/release on page33: https://ethicle.bscycle.co.jp/cdn/shop/t/1/assets/manual_ia01659.pdf?v=34569525418549151281689146098 . Manual listing: https://ethicle.bscycle.co.jp/pages/manual-list .
- Roller-brake exterior component relationships: https://si.shimano.com/en/pdfs/si/IM31D/SI-IM31D-000-ENG.pdf . A distinct fixed casing stop, exposed cable, movable link and cable clamp are represented; internal rollers, force transmission and return action are not simulated.

The delivered pose is parked on front tire and paired-stand feet, with the rear wheel lifted and ring-lock bolt retracted. Rear brake housing is modeled for this pose; it must be regenerated/deformed for a supplied steered pose. Crank diagnostics counter-rotate pedal platforms but are geometric clearance tests, not an assertion of riding while supported on the stand. Stand retraction involves lifting/rolling the frame; its fixed-frame diagnostic can dip about3mm below the original floor at an intermediate angle. The modeled spring and hooked anchors have plausible connections in the delivered pose, but spring force and changing coil length during retraction are not simulated. Positive trail, wheelbase, rear sprocket, tube thicknesses and hidden details include authoring assumptions listed in configs/design.json.

## Folding platform handcart

- Kanatsu PLA150-DX basic family: https://www.kanatsu.com/product/167/ . 730×490mm platform,170mm deck top,890mm handle and100mm wheels informed the generic asset.
- Compatible polymer-fork swivel/fixed caster references: https://www.kanatsu.com/product/448/ and https://www.kanatsu.com/product/450/ .
- Official construction/operation catalog: https://www.kanatsu.com/catalog/pdf/catalog2019.pdf . Upright lock and separate foot release informed the open cheek slots and lock tongue.
- Related-family folded envelope only: https://www.kanatsu.com/wp/wp-content/uploads/2015/09/FoldingHandle.jpg . No brake system from a different cart variant is added.

The cart handle folds only after the separate release bar is moved. Stationary base sockets and caster mounting plates remain fixed in the appropriate tests. Hidden latch spring behavior is not simulated. Deck rib pattern and hidden joint dimensions are inferred. The polymer deck is one continuous manifold mesh, including top skin, perimeter and crossing ribs. Load proxy checks prove placement clearance only; they do not confer a payload rating. All kinematic checks are sampled geometric diagnostics, not strength, stability or product-safety certification.

A geometry change invalidates older file hashes, pose evidence and photographs. The exact final review and immutable photograph records determine release acceptance, not the original metadata's build-time status.
