# Print sheet (model v8r)

Units mm. Files in `stl/` are already in print orientation and sit on Z = 0. **No supports on any part.** 0.4 mm nozzle, 0.2 mm layers. Bed needed: 340 × 320 mm (the carrier is the tight part).

| File | Qty | Colour | Size | Bed side | Brim | Notes |
|---|---|---|---|---|---|---|
| P1_wall_mount_black | 1 | black | 199 × 110 × 6.7 | wall face | no | 45° undercut edges. 4 walls. |
| P2_carrier_black | 1 | black | 326 × 294 × 17.2 | wall side (ribs + 8 ears) | 5 mm | Bridges up to about 20 mm between ribs. 4 walls. One corner is cut away on purpose for button access, and there is an open window with a rim beside it for the rear camera. |
| P3a_liner_white_speaker_slits | 1 | white, opaque | 323 × 219 × 10.5 | the white face | 5 mm | The bed side is the visible face. The face is 3.0 mm of solid white: no infill in the face. Sound slots are 1.2 mm wide, nothing narrower. Keep them open (elephant-foot compensation on). |
| P3b_liner_white_plain | 1 | white, opaque | 323 × 219 × 10.5 | the white face | 5 mm | Same part without the face speaker slits (mic slits only). |
| P4a..P4d ring pieces | 1 each | black | up to 236 × 176 × 11.6 | back face, lip up | optional | **100% infill**: they are trimmed by hand to fit the cable socket. Short bridges only (20 mm and 11.4 mm). |
| P5_pen_cup_white | 1 | white | 14.4 × 17 × 25 | bottom, upright | no | Small. Print slowly. |

## Checks run on the model (`cad/deepcheck.py`)
Every part is one solid and fits the bed; largest bridge 19.3 mm; no overhang lip over 2.5 mm; no wall thinner than 0.8 mm; no gap narrower than 0.4 mm; assembly motions are clear; every port's air path reaches the room.

## Material notes
- **White over black needs thickness.** The liner face is 3.0 mm because white filament has to be about as thick as its transmission distance to hide the black felt and bezel behind it. Published transmission distances: Bambu PETG HF White about 2.9 mm, PETG Basic White 3.7 to 3.9 mm, Prusament Signal White 3.4 mm.
- **First prototype order:** the white parts (P3a, P3b, P5) are being printed in ASA, which looked brighter and cooler than PETG HF white in side-by-side photos. ASA warps more on a large flat plate (this one is 323 × 219 mm); if it curls, the 0.4 mm gaps to the carrier and ring stop fitting. Whether ASA is the better choice is not yet known. This page will say once there is a result.
- Two places on the carrier have walls meeting at a sharp angle and leaving a tapering V-shaped notch. They are not slots; it does not matter if the tips fuse.
