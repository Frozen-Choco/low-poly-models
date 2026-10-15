# Batch 02b: railway crossing and recycling cabinet

Original geometry; generic Japanese diorama interpretations. Not fabrication plans, standards-certified products, exact manufacturer replicas, or complete operational crossing installations. All dimensions are estimated for scene scale. Review status: awaiting independent review.

## Crossing components and state
One striped warning mast and concrete footing, yellow/black X crossmark, two horizontal circular warning lights with convex red optics and black upper hoods, warning sounder, rear wiring conduit and mounts. One separate electric gate pedestal with service cover, pivot shaft, boom socket and tapered round 4 m yellow/black boom. LOWERED horizontal static boom. Left red lamp is lit, right is dark, representing one alternating phase without animation. No opposite-side gate, rail/road, train-direction indicator, emergency pushbutton, or controller is part of the asset. Context render ground and rails are presentation-only and live in a separate scene.

References consulted 2026-10-15:
- https://www.signal.co.jp/products/railway/faq/faq02/ — identifies barrier, flashing warning lamps/speaker and optional direction display as separate devices.
- https://www.kyosan.co.jp/product/pdf/signal06_01.pdf — electric barrier housings, stand/pivot arrangement, options and weightless variants. The compact four-metre arm and exact enclosure dimensions here are artist estimates rather than claimed catalogue specifications.
- https://www.mlit.go.jp/english/2006/h_railway_bureau/Laws_concerning/14.pdf — yellow/black crossing devices/bars and crossmark. Used only for visual reference, not a compliance claim.

## Recycling cabinet
Single sheltered public-space collection cabinet with two real round insertion holes, deep chutes, hollow removable-style internal liner, two small can/bottle pictograms, two-millimetre side skins with folded returns, gray painted-steel service door with folded returns, barrel-and-leaf hinges and lock, cap and rubber feet. No text or branding. It represents combined can/bottle collection rather than implying a universal Japanese sorting standard. Empty and fixed closed. Fits a sheltered station forecourt or facility entrance; not an all-weather sealed outdoor product claim.

References:
- https://www.teramoto.co.jp/products/10285/ — Japanese stainless separation bin material vocabulary, liner/bag retention, can/bottle sorting.
- https://www.teramoto.co.jp/trushbox_ft_series/ — quiet monochrome commercial cabinet forms and steel cabinet material/form vocabulary; this design deliberately uses a gray painted-steel door rather than claiming bare brushed stainless. This is an original mixed-reference design, not either product.

## Reproduction and limits
Run Blender 4.3.2 with scripts/build_assets.py, then scripts/validate_assets.py, then scripts/render_context.py. All geometry and PBR materials are generated locally without third-party meshes/textures or generation APIs. GLB needs no external texture files. Materials deliberately use subdued metalness/roughness rather than chrome. Surface wear and brushed-metal microtexture are omitted: clean maintained fixtures, not aged photogrammetry. There is no rig, animation, electrical internals, manufacturing fit or safety functionality. Tiny optical ribs, bolts and seam widths are visual approximations. Preview studio is separated from asset collection; GLB contains only asset parts with a single ground-origin root.
