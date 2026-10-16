# Apple skin correction

The user's wood-like-material report invalidates the previous material approval. Previously accepted geometry, stalk and calyx are retained exactly.

## Cause, not a saturation adjustment

The prior baked albedo contains sinusoidal terms driven mainly by horizontal UV longitude: sin(x*160 + ...) and sin(x*460 + ...). These impose repeated long bands around the fruit and converge radially near the poles. Their continuity and regular spacing read as wood grain. Uniform roughness 0.43 and broad smooth reflection reinforce a dry/varnished crafted-object interpretation. This was a material-design failure even though the mesh and previous inspection tests passed.

## Reference

The actual Aomori Apple Association Fuji photograph was visually reinspected: https://aomori-ringo.or.jp/starcut/variety.html and https://aomori-ringo.or.jp/starcut/img/cut/38-fuji.png . The reference has irregular fine pale lenticels, varied red blush/mottling and a modest wax-like reflection. It does not justify continuous evenly spaced grain. This remains a generic red apple, not a claim to reproduce a branded/cultivar-specific specimen.

## Revised construction

- No continuous longitude-dependent stripe term.
- Direction-balanced multiscale spherical noise, baked to a portable image, creates irregular pigment patches without a UV seam or polar stripe convergence.
- Fine, softly edged lenticels vary in size, brightness and spacing. Sampling is uniform by sphere surface area; UV ellipse dimensions compensate for meridian distortion.
- Metallic 0; IOR 1.5 (the portable glTF dielectric default); specular IOR level 0.5; no clearcoat and no deep groove normal map. Wax is approximated through restrained spatial roughness variation around 0.375, not metallic reflectance or thick varnish.
- Exact raw values and image ranges are in material_revision.json. Image pixels, geometry and materials are original; no downloaded image is used as an asset texture.

## Required evidence

Compare delivered GLB imports before/after at identical camera, exposure, size and lighting; inspect extracted base-color pixels separately from illumination. Include neutral front/rear/top close and alternate-light comparisons. Preserve geometry hashes and validate saved Blend and GLB. Final photography/freezing awaits the shared specification. Do not publish or count this as approved until independent material review passes.

A first trial at darker pigment and roughness around 0.29 removed wood grain but overcorrected toward dark lacquer. It was rejected. Generated image pixels/exported PNG values are treated as sRGB albedo values; the revised pigment is moderately brighter and roughness increased to a restrained wax sheen. This is a documented material change, not a lighting/exposure compensation.

## Material review outcome

The second candidate passed independent rear, top, rotated-neutral-light and single-light GLB inspection against actual apple references. The repeated bands and polar radial pattern are absent. Three broad highlights in the shared studio are fixture reflections; the single-light check shows restrained wax-like skin. Exact GLB/Blend geometry streams remain unchanged. Approval binds model/material bytes only; final standardized photography and complete-package freeze are separate gates.
