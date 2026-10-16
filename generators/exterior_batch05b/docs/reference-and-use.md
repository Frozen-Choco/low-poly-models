# Exterior utility props: references and construction

Original, unbranded diorama assets. Research and geometry review: 2026-10-16. These are visual models, not fabrication drawings, installation instructions, engineering certification or operational appliances. Photographs/drawings were inspected as references, not copied into asset textures. Reference files retained privately for review are not distribution assets.

## Roadside convex mirror

Primary drawing, directly retrieved and visually inspected: Tsubame Shinko G600-TD-Z36, https://tsubame-shinko.co.jp/wp-content/uploads/2022/10/G600-TD-Z36.pdf
Supplementary Japanese pole/mirror family dimensions: https://sanyo-kq.co.jp/product/カーブミラー/

The primary drawing specifies a 600 mm convex glass face with 2200 mm curvature radius, 5 mm mirror glass, molded FRP rear shell, orange hood, metal retaining rim, rear bolted bracket and 76.3 mm steel pole. This model follows that single glass/FRP construction family, not the superficially similar stainless mirror family. It has a real spherical-cap optical surface, closed 5 mm shell, retained rim, upper rain hood, rear attachment plate, two arms, annular pole collars and bolts. Pole contacts and penetrates the visible concrete footing collar. The below-grade civil foundation is not modeled; the included 340 mm collar is an artist-designed visible placement base, not the manufacturer's full buried foundation. The source drawing's warning placard is omitted rather than fabricating safety text. Rear molded details and hardware dimensions are simplified/inferred.

The opaque silvered-surface material is a portable metallic PBR approximation of the reflective coating. It does not simulate layered glass optics, calibrated field of view, or guaranteed real-time reflections. Appearance and reflections depend on the viewing app's environment, rendering engine and lighting. No painted scene or fake reflected photograph is included.

Checks on saved Blend and GLB: center optical surface projects about 20.5 mm forward; center and sampled radial surface normals face outward; pole enters footing; two bored collars enclose the pole. Both faces and rear bracket are reviewed. A first draft annular winding defect was corrected before final hashes.

## Residential outdoor AC condenser

Primary directly retrieved and visually inspected Daikin RXF20–42F installation diagrams: https://www.daikin.ie/content/dam/document-library/installation-manuals/ac/split/rxf-f/RXF20-42F_Installation%20manual_3PEN748643-15S_English.pdf
Companion guide: https://www.daikin.sk/content/dam/document-library/Installer-reference-guide/ac/split/rxf-f/RXF20-42F_Installer%20reference%20guide_4PEN769827-15G_English.pdf
Product family: https://www.daikin.eu/en_us/products/product.html/RXF-F.html

Reference diagrams show rear/side intake, four feet, two foundation rails, 470×300 mm bolt spacing, bottom drain and paired side service connections. The model uses a generic 740×343×556 mm cabinet envelope above supports. This overseas family is a form/scale reference; the asset is suitable for a Japanese residential diorama but is not a Japanese-market product replica. The cabinet has a real circular discharge opening, three stationary swept fan blades, motor casing with fixed struts and vertical support spine, separate open-wire concentric guard, open side louver bank and individual spaced rear coil fins/tubes. Four feet directly meet the bottom pan and rest through rubber isolators on concrete rails. The pan includes a real drain hole. Two insulated service lines connect at the right-hand service area and route to a wall collar; the collar ends at local y=0.423 m and meets the wall front at world y=0.623 m after the diagnostic placement offset.

This is an exterior static appliance prop. Compressor, refrigerant loop, detailed electrical internals and operational mechanics are not modeled. Hidden thermal/electrical operation and service access are not certified. The rear fin pack and fan are supported visual structures, not a simulated functioning heat pump. Pipe bend dimensions, louver pattern, valve covers and detailed cabinet seams are artist interpretations.

Saved-format tests verify four feet/pan contacts, two motor struts and spine, positive fan/guard clearance, true front discharge and rear/side intake paths, real bottom drain, and paired service pipes. Early floating motor and foot gaps were corrected. A full-quality photo later revealed pinched service-pipe mesh frames; those pipes were rebuilt using parallel-transport cross-sections and smooth 40 mm centerline elbows. Saved-file tests verify circular cross-sections, minimum bend radius and positive paired-route clearance; independent BVH checks found no nonadjacent surface self-intersections. The superseded candidate and images are retained locally but excluded from distribution. Context verifies support rails on ground and piping reaching the wall, with rear intake clearance.

## Steel street drainage grate and frame

Directly viewed steel-bar construction photograph: https://www.takara-kizai.com/product/grating/steel/images/main_photo.jpg
Manufacturer explanation: https://www.takara-kizai.com/product/grating/steel/
Manufacturer section drawing directly inspected: https://www.kaneso.co.jp/seihin/zumen/HXC-6638_DK-600-Z.pdf

Takara shows parallel load-bearing bars, transverse ties and end bands. Kaneso's section shows the steel grate bearing on an L-shaped receiver frame and the open drainage space below. The Kaneso assembly includes an optional basket, which this generic asset does not reproduce. This model is an original rectangular 600×400 mm removable panel with 30 mm bearing-bar depth, steel end bands and welded cross ties, set within a 630×430 mm angle receiver. It is neither a cast-iron grate nor an exact copy of one maker's product. Plain bar surfaces are intentional; no load rating or anti-slip certification is claimed.

All load-bearing bars span the short direction, seat on the two continuous frame shoulders and meet end bands. Grid slots are genuine openings. Outer slot rows overlap the receiver shoulders as expected; central slots lead unobstructed downward. The grid apertures themselves provide a lifting-hook purchase. An 8 mm shaft fits a 24.7 mm slot; an inserted hook can turn below the bar, engage its underside and lift the separate grid vertically without colliding with frame uprights. The diagnostic raised-grid scene illustrates that purchase and retains the supporting concrete walls/void. No opaque panel is hidden below the grate.

Full-quality inspection exposed coincident crossing and receiver faces in the initial separate-box model. The revised grid and receiver are each a single welded boundary-union solid: internal contact faces are removed before small edge bevels and triangulation. The saved formats must contain both named assemblies, have no degenerate triangles, and be closed manifold after merging export-split vertices at 0.1 micrometers. Object-level rays check all 42 bar-end bearing contacts and the real through-slots. Superseded geometry and photos remain local history, outside the distribution.

## Reference retrieval limitations

The original older Daikin -15D PDF URLs were stale and returned 404; the newer -15G guide and -15S manual above were used for actual visual inspection. DKC 65_6-53 and old Daikure catalog links returned HTML instead of PDF; they are not claimed as visually inspected evidence. The replacement Takara photo and Kaneso section establish the relevant steel-bar and frame construction.

## Validation and photography

geometry_validation.json records both saved formats, exact input hashes, finite coordinates, nondegenerate triangles, dimensions/part-count roundtrips, size limits and object-specific tests. reproduction_validation.json records relocated-source ASSET_OUTPUT_ROOT and ONLY_ASSETS checks. No asset file may reach 100,000,000 bytes.

Canonical photographs use unchanged preview_standard_v1 renderer/standard controls in a separate additive configuration. All three assets use the same studio, exposure, 1200×1200 size and 80% projected frame occupancy. This display-fit normalization is only applied to imported photography copies, never to saved asset geometry. Close-up targets are explicitly documented in the detail manifest; alternate_light uses the standard second light direction. Diagnostic images are labeled and are not canonical photography. Local proof Blend scenes are not automatically included in the public package.
