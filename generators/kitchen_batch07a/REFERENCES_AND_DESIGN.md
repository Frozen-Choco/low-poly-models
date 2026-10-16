# Kitchen utensils: reference and construction

Research date: 2026-10-16. These are original generic, unbranded Japanese-kitchen-compatible assets, not certified replicas. The current catalog at release_staging/exterior_bicycle/repo/catalog.json was inspected before authoring; no ladle, perforated colander or wood cooking spatula was present.

## Primary sources and observed features

- Stainless ladle: https://www.muji.com/sg/products/cmdty/detail/4550002882761 . Manufacturer states approximately 27 cm and 18%chromium/8%nickel stainless steel. Main official photograph and detail 01 show a thin deep round cup, smoothly flared neck, channelled long handle; detail 02 shows a curled storage hook. Original images: https://img.muji.net/img/item/4550002882761_1260.jpg , https://img.muji.net/img/item/4550002882761_01_400.jpg , https://img.muji.net/img/item/4550002882761_02_400.jpg . Model uses 74 mm bowl diameter,24 mm cavity depth,0.9 mm wall and generic hook dimensions, all authoring assumptions. Approximate bowl capacity 69 ml. Bowl, neck, handle and hook share one continuous sheet topology, solidified to real thickness. Delivered resting pose is numerically solved so bowl/neck underside and hook tip both contact the table; it is not an upright balancing pose.
- Perforated colander: https://yanagi-design.or.jp/catalog/4163/ . Design institute lists 23 cm family at 238 mm diameter×86 mm high and 18-8 stainless. Official profile https://yanagi-design.or.jp/wp-content/uploads/2021/12/418b901e9572f180be162327f21462db-1440x536.jpg shows thin rolled lip and a flattened perforated bottom flowing into flared sides. There is no unsupported added foot or handle. Model gauge 0.55 mm,2.7 mm hole diameter and 6 mm developed-space pitch are generic lightweight authoring choices, not measured manufacturer claims. All 2,233holes pass through the sheet, including the base. Rim shares vertices with the bowl, not a separate coincident surface.
- Wood cooking spatula: https://www.muji.com/sg/products/cmdty/detail/4550512963073 . Manufacturer identifies rubberwood and 70×12×290 mm. Main official photograph https://img.muji.net/img/item/4550512963073_1260.jpg shows an asymmetrical rounded paddle, slim shoulder, genuine hanging hole and pale longitudinal grain; detail photographs show a tapered scraping edge and near-flat broad paddle. Model reproduces the practical family with original dimensions/curves,8 mm hanging bore, solid tapered cross-sections and original understated finite raster fibers. No logos, fake groove geometry, downloaded material textures, or procedural shader nodes.

Reviewer independently downloaded and inspected originals under reviews/batch07a/reference. No duplicate research images are retained in this asset package. URLs and image hashes are recorded in configs/design.json. These images are research evidence and are not distributed as asset textures.

## Manufacturing and use scope

Every model is one connected solid mesh: there are no separate attachments to float, missing fasteners or concealed unsupported joints. Colander drainage and ladle liquid retention are geometry features, not fluid simulations. No engineering load certification is claimed. Spatula handgrip and storage bore are clear; leading edge is thinner than handle. The files use meters, Z-up in Blend and glTF-standard Y-up in GLB, with lowest surface at Z=0 after importing to Blender.

## Review sequence

Generation → independent saved Blend/GLB reload checks → cheap multiangle diagnostics → independent attachment/surface/use/pixel gate → parent authorizes canonical photography. No final photograph or publication is authorized by this batch script. The published preview_standard_v1 core and settings remain untouched.

## Stable resting poses

Independent volume-weighted COM probes exposed initial resting-pose instability before any canonical rendering. Ladle revision5 now solves the global bowl/neck/handle underside minimum against the storage hook, and faces its cavity toward-Y. Spatula revision4 finds the smallest rigid rotation to a convex-hull support facet containing the exact solid-volume COM projection. Reviewer verifies all three final COM projections inside ground-support hulls at1µm tolerance. These are physical pose checks, not rigid-body simulations.

## Canonical first-look corrections

Colander revision2 separates bore-wall normals from smooth sheet surfaces using sharp manufactured edges, eliminating embossed-looking shading without changing positions, thickness or material. Wood spatula revision5 removes a Boolean cutter UV layer so the original longitudinal grain UV is the sole active render UV. The original albedo is unchanged. These supersede earlier model hashes; refreshed independent geometry approval and canonical hero/detail appearance approval both pass.
