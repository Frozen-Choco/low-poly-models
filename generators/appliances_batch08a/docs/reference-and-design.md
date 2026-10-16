# Home appliances: original generic designs

Status: independent mixed revision 12 saved-model and cheap-view gate passed. All 28 final canonical photographs passed independent visual and provenance review. Exact-package acceptance is recorded separately. Latest asset metadata identifies current exact saved hashes; earlier revision logs are historical only.

## Primary evidence

- Panasonic NE-FL1C specification: https://panasonic.jp/range/products/NE-FL1C/spec.html — 488×380×298 mm exterior,405 mm including handle, side-opening door,332×365×206 mm flatbed cavity. Accessed2026-10-16. Product reference https://panasonic.jp/range/products/NE-FL1C.html. Official product photograph https://panasonic.jp/content/dam/panasonic/jp/ja/range/products/ne-fl1c/img/sns_thumb.jpg inspected directly: white rectangular case, dark left-side door/window, vertical pull and right control cluster. Dimensions and flatbed layout guide scale, not exact copying.
- Zojirushi NL-BX05: https://www.zojirushi.co.jp/syohin/rice/ricecooker/nl-bx/ —235×325×195 mm,365 mm open height, compact micom/resistive cooker and broad shallow5 mm pot. Accessed2026-10-16. Official exterior and cutaway-pot images inspected directly; rounded housing, separate control region, rear hinge, steam opening, dark coated pot and thick bottom inform generic design. No reference pixels are used as model textures. Manual URL was found, but the large PDF was not read.

## Design and dimensional interpretation

Names are exactly 電子レンジ and 炊飯器. Stable English IDs are microwave_oven and rice_cooker. No manufacturer logo, brand name or rating/certification is inscribed. Source measurements establish appliance-class scale; all wall gauges, clearances, hinge construction, generic controls, cord routing, feet and ivory finish are original authoring assumptions. Model metadata separately states reference dimensions, modeled body/cavity dimensions and complete actual bounds including unplugged cable and hardware. These are not engineering replicas.

Microwave has a continuous case with integral metal-colored open cavity, separate seated ceramic flat floor, actual rear vent recesses and recessed opaque equipment baffle; no continuous functional airflow path or cooling certification is claimed. The real door frame/window, vertical handle, fixed/moving hinge leaves, coaxial axles, receiver recesses, controls, feet and unplugged cord are separate editable components. Usable handle clearance is25 mm. The smoked window is intentionally opaque at miniature scale; the full cavity becomes visible when the door opens. Generic modeled cavity is350 mm wide,335 mm deep,218 mm high, not the source's exact cavity.

Rice cooker has a closed-bottom hollow housing, dark internal liner, separate closed-bottom pot resting on an explicit support seat, rear hinge, connected metal inner lid, sealing ring and continuous steam bore through lid/plate. The release button is visible on the top surface. Front controls and LCD are unlit. Four feet share the ground plane. An unplugged cable connects at the rear strain relief. Pot geometry is generic and does not claim the source's exact5 mm wall throughout.

## Mechanism scope and limitations

One rigid hinge animation per asset, frames1–151: closed at1, fully open at61–91, closed again at151. Microwave range0–90 degrees; cooker range0–100 degrees. Other parts are static. Inner pot and lid plate are individually editable objects, but no extraction sequence is provided. Controls/latches are visual representations only. No electrical operation, heating, pressure, sealing certification, food safety, interlock behavior or manufacturing strength is simulated or asserted. Shaft/barrel and fixed assembly buried engagements are intentional; exposed coplanar overlays or unrelated moving-part penetrations are not permitted. Exact intended support graph is in configs/attachments.json.

## Materials, topology and delivery

Metric BlenderZ-up/GLBY-up, −Y front in Blender, feet atZ0. Materials are restrained glTF PBR constants: coated steel, satin ivory and charcoal polymers, dark smoked panel, satin metal, dark coated pot, ceramic and rubber. UV maps are included; no external texture dependency. Every delivered asset has one editable Blend and one animated GLB, below100MB. Regeneration uses scripts/build_assets.py; validation independently reloads both saved formats and checks world-space finite geometry, manifold solids, triangle areas, UV/material presence and grounding. Independent review additionally checks full attachment, coplanarity, swept motion and rest support.

## Photography

Cheap all-angle closed/open diagnostics are explicitly noncanonical, 480 px / 12 samples / two CPU threads and source-hash bound. Canonical preparation copies the published shared renderer and standard byte-for-byte; no per-object exposure/material edits. Current frozen core is 1200 px, 512 maximum samples with adaptive sampling, AgX, two CPU threads, no denoising. Render-only open pose inputs derive solely from frame 61 of the delivered GLB, without changing source geometry/materials or writing another Blend. These poses are evidence inputs, not additional catalog models. Canonical execution requires independent gate and parent capacity allocation; final photo and exact-package approval is separate.
