# Installation notes

Model v8r. Steps agreed during design review, in the order you would do them. **Nothing here has been proven on a finished build yet** (see the README's status section); treat measured numbers as targets and mark holes from the printed parts, not from this list.

## 1. Bench test before anything is glued

- Chain: wall charger → USB-C extension → adapter (PD port) → tablet, with the Statik pen charger in the adapter.
- Bench result without the extension: tablet and pen both charge through the adapter. Repeat with the extension in the chain.
- Try the button combinations for forced restart and recovery on the bench, so they are known before the tablet is boxed in.

## 2. Frame: pen charger slot (right side)

- Position: frame's right-hand side (seen from the front), cut in from the back edge.
- Size: 11 mm wide, 10.5 mm deep from the back edge. The front 14 mm of the frame side stays untouched.
- Method (chosen): drill, so the slot ends in a round bottom.
  - Bit: 7/16" (11 mm), brad-point or Forstner preferred.
  - Centre mark: 132.5 mm down from the frame's top outer edge, 5 mm in from the back edge.
    (Pen lowered 24 mm on 2026-11-13; it was 108.5. Check against the printed ring's tunnel before drilling.)
  - Clamp a scrap block hard against the frame's back edge and drill through the joint line.
  - Drill from the outside face inward so tear-out lands inside.
  - Pare the two sides straight back to the edge so the mouth is a full 11 mm (the charger head must lift out with the ring).
  - Leave the bottom round.

## 3. Pen charger (Statik, 8 mm magnetic head, 10.08 mm barrel)

- Head goes straight out through the ring's printed tunnel (11.4 wide, open at the back; pen axis 4.7 mm in front of the frame's back face) and the frame slot. No bend.
- Glue the head into the ring tunnel, never to the wood. Tape the frame slot while the glue sets.
- Head face sits about 1.7 mm proud of the wood.
- Set the position with the pen docked in its cup while the glue sets.
- To remove the frame later: ring and charger lift out of the open slot together.

## 4. Pen cup (white)

- Attaches to the wood on the frame's right side, below the charger head. Strong double-sided tape or glue.
- Place it last, with the pen on the charger, so the pen sets the cup height.

## 5. USB-C socket (bottom left)

- Extension: 240 W, 2 ft, right-angle male → female. Trim the ring's socket tunnel (20 wide) to its female end.
- Length: internal path is about 51 cm. 2 ft (0.6 m) is ideal; 3 ft works, spare folds once up and down the left side gap.
- Path: adapter PD port → down the right side gap → along the bottom between carrier and ring → socket tunnel
  in the ring's bottom rail at the left (180 mm left of centre, 16 mm wide).
- Glue the female end into the ring tunnel. This is the strain relief.
- Frame: open slot at the bottom edge in line with the tunnel (same idea as the pen charger slot). Size to the female end.
- Steady the adapter with two felt offcuts: one under it (1.0 mm gap), one over it (0.6 mm gap).

## 6. Frame to module

- 8 ears on the carrier, #4 × 3/4" flat-head wood screws, 2 mm pilot holes in the frame's back flat.
- Top ears are at −86, −50, +50, +130 mm from centre (top-left ear moved in on 2026-11-13); bottom ears at −130, −50, +50, +130.
  Mark pilots from the printed part, not from these numbers.

## 7. Buttons with the unit off the wall

- Day to day: no buttons needed (screen and volume are handled in software).
- Physical access is from behind, with the unit lifted off the wall mount, by finger.
- The top-left corner of the surround (seen from the front; top RIGHT seen from behind) is cut away outside the
  tablet's edge, in the carrier and the liner. The tablet's rim is bare there.
  - Power: left edge (seen from the front), 15–28 mm from the top.
  - Volume rocker: top edge, 16–40 mm from the left.
- The camera pocket on the back is the landmark for the corner.
- Fallback: a flat stick about 6 × 2 mm also reaches the volume through two sloped reliefs in the ring's top rail.

## Change log (late design changes, v8r)

- Pen cup: closed on the wood side, round holes, no flange, white.
- Service bay removed; pen charger goes straight through an 11 mm ring tunnel and a frame slot; glued to the ring.
- Statik head measured: 8 mm.
- USB window extended down (to y −95); right snap moved to y +85; right locator moved to y 55–65.
- Ring cable groove removed; USB-C socket tunnel added, bottom LEFT (outlet is to the left).
- Bottom locator bosses and left locator finger lowered to z 9 so the cable passes in front of them.
- Top-left ear moved from −130 to −86 to open the volume window from behind.
- Two volume reliefs added to the ring's top rail.
- Finger bay: carrier and liner cut away outside the tablet edge at the top-left corner (to 46 mm along the top, 38 mm down the side); the liner's 1.6 mm face strip stays.
- Bay profile rounded (r4 fillets at the cut ends, tablet-radius corner, rounded skirt ends).
- Rear camera window: open right through the carrier, rib cage across it removed; a 2.4 mm rim round the window stands on the wall side in place of the ribs. The rear camera is usable when the unit is off the wall.
- Measured adapter + right-angle cord stack: 38–39 mm out from the tablet edge (11 mm spare to the ring).
- Pen lowered 24 mm: charger head now 16 mm above the frame's mid-height (was 40); cup bottom ends about 19 mm above the frame's bottom edge. Lower than that and the charger connector runs into the right-angle charge plug. Right ring joint moved up to y 38.
- Liner is printed in two versions: P3a with speaker slits on the face, P3b plain (mic slits only; speakers exit through the side slots). Choose after seeing both.
- Camera/sensor notch replaced by two flared holes on both liners, level with each other, 4 mm from the tablet's top edge. The flare leans up and sideways and is held back at the bottom, so the screen-opening slope is untouched: camera 4.0 mm at the glass → 5.0 mm at the face; light sensor 2.5 → 3.8 mm.
- Mic (and speaker) dimples on the liner face shortened to 1 mm from the mat's edge (were 2 mm at the mics); sound path unchanged.
- Statik barrel measured 10.08 mm: pen axis moved 0.8 mm toward the wall (10.7) so the barrel clears the tunnel roof; tunnel 11.4 wide.
- Charge plug measured 11.11 mm thick: fits (it sits in the open side gap, about 1 mm from the mat's back and 5 mm from the wall).
- Print-service feedback (print service, 2026-11-13): slots should be 0.8 mm or wider; white should be thick over a black bezel. Result: the narrowest printed slot is 1.2 mm (no change needed); the liner's white face is now 2.4 mm thick (was 1.6). The frame therefore sits 0.8 mm further from the wall (back 6.8 mm off the wall); pen, slot and screw positions relative to the frame are unchanged.
- White face now 3.0 mm (TD research: Bambu PETG HF White TD 2.9, Basic White 3.7-3.9, Prusament Signal White 3.4). Prototype order: white ASA (see PRINTING.md).
- Wall mount 6 -> 5 mm thick (straight top edge 2 -> 1 mm; the 4 mm 45 deg hooking slope unchanged) to pay for it. Frame back now 6.4 mm off the wall, face 31.4 (was 6.8 / 31.8).
- USB-C socket tunnel widened to 20 mm; ring pieces printed 100% infill so the tunnel can be trimmed to the actual female end. The female end may also stick out behind the frame (tunnel is open at the back). Cut the frame slot to suit.
- Extension used: 240 W, 2 ft, right-angle male to female. Path needs about 47 cm of cable; 61 cm leaves about 14 cm spare in the left side gap.
- Decisions: no accent line on the liner; front speaker slits still undecided (kept for now).
