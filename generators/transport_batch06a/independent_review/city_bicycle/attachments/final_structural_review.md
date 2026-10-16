# Bicycle comprehensive structural regression — PASS for photography

2026-10-16 10:10 UTC. Final appearance/package gate remains pending. This report supersedes earlier bicycle structural checkpoints.

Exact saved files:
- lowpoly_batch06a/assets/city_bicycle/city_bicycle.blend: SHA256 2ff20d1a2ecb22ec08582b8f65c80d3a89606891bfa9cbbcfc8bec71b3af9c6b, 6,054,520 bytes.
- lowpoly_batch06a/assets/city_bicycle/city_bicycle.glb: SHA256 81d041e09a867838f1ca844935f4d7d3cdd5061fd4d99c591a8e47f2fa716cbd, 2,801,792 bytes.
- Both 84,500 triangles; independently loaded and measured. Finite vertices, no degenerate triangles.

## Verified actual mesh relationships

Reviewer-authored audit.py/audit.json inspect both saved formats, source coordinates and named intended joints. All interpreted attachment edges now have intended contact: basket rear brackets to stem/basket and clamps; axle stays to basket floor and front axle; front/rear mudguard stays to fender and axle; carrier frame/axle struts to frame and rack; saddle rails/clamp/post; ring-lock clamps through explicit bridges to stays; stand legs/feet/hinges/brace/tab, explicit lock lever fastener, both spring hooks; brake caliper support/pads, rear reaction clamp and actuation chain, dynamo clamp, lamp hanger; main frame/head/fork/dropouts. Expected self-comparison/prefix artifacts are excluded, not mistaken for missing joints. Real bearing/assembly separation is retained rather than demanding watertight unions.

Independent expanded obstacle checks now all empty:
- rear seatstays/chainstays/ring-lock/carrier supports versus rear tire;
- front fork/crown/mudguard/basket axle stays versus front tire;
- all rear supports including stand, ring-lock, rear brake and carrier against rear spokes;
- rear mudguard/stand/brake/fender against rear tire.

These checks found and drove real corrections: previously floating basket brackets, rack roots, ring-lock clamps, spring/lever mounts; rear seatstay/tire interference; stand brace/spoke interference. No geometry was accepted merely because limited prior reports passed.

Full saved-file pose regression rerun on these hashes: chain/guard/frame, brake linkage, tire/fender, fork/tire/spoke, steering and pedal/crank bounded clearances remain clean. Stand legs plus bowed brace clear BOTH tire and spokes at 0, 25, 50, 75, 95 degrees of retraction. At 25 degrees the brace reaches approximately -0.003 m relative to the original parked floor; a real lift/roll during stand retraction is expressly required, so this is not an assertion of ground-fixed free motion. Default parked front tire/stand shoes remain on ground; rear tire raised approximately 14 mm. No physical stability, force or certification claims.

## Remaining gates

New source geometry invalidates every earlier bicycle canonical photograph. Request fresh true side and semantic support close-up first, followed by complete canonical required views and alternate lighting, all with frozen common renderer/spec and these input hashes. Only final complete pixels/provenance/package review can grant final acceptance. Spring and rear cable remain deformable real-world parts represented statically; no delivered articulated bicycle animation is claimed.
