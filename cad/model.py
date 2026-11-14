"""Nook Calendar Station mount - placeholder geometry (mm).
X right, Y up, Z out from the wall (wall face at Z=0). Origin = screen centre.
All tablet feature positions are estimates from Lenovo renders; verify on arrival.
"""
import math
import numpy as np
import manifold3d as M
from manifold3d import Manifold, CrossSection, JoinType

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def rrect(w, h, r, z0, z1, cx=0, cy=0):
    cs = CrossSection.square([w - 2 * r, h - 2 * r], center=True).offset(r, JoinType.Round, circular_segments=24)
    return cs.extrude(z1 - z0).translate([cx, cy, z0])

def frustum(w0, h0, z0, w1, h1, z1):
    """Rect w0*h0 at z0 growing to w1*h1 at z1 (for 45 deg bevels)."""
    pts = []
    for (w, h, z) in ((w0, h0, z0), (w1, h1, z1)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts.append([sx * w / 2, sy * h / 2, z])
    return Manifold.hull_points(pts)

def cyl(r, z0, z1, x, y, seg=32):
    return Manifold.cylinder(z1 - z0, r, r, seg).translate([x, y, z0])

def cyl_y(r, y0, y1, x, z, seg=32):
    """Cylinder along Y."""
    return Manifold.cylinder(y1 - y0, r, r, seg).rotate([-90, 0, 0]).translate([x, y0, z])

def hull_prism_y(profile_top, profile_bot, y_top, y_bot):
    """Hull of an XZ polygon at y_top and another at y_bot."""
    pts = [[x, y_top, z] for x, z in profile_top] + [[x, y_bot, z] for x, z in profile_bot]
    return Manifold.hull_points(pts)

# ---------------------------------------------------------------- parameters
TAB_W, TAB_H, TAB_T, TAB_R = 291.8, 189.2, 6.9, 8.2
SCR_W, SCR_H = 273.6, 171.0
LINER_OPEN = (SCR_W + 2.0, SCR_H + 2.0)      # lands ~1 mm onto the bezel each side
LINER_W, LINER_H = 320.0, 216.0               # fits a 340 x 320 mm bed
# front camera + ambient light sensor, top bezel, centred (ESTIMATE: verify on arrival)
FCAM_Y = TAB_H / 2 - 4.0          # middle of the top bezel
FCAM_W, FCAM_TOP = 26.0, 4.0      # window width (camera + sensor), reaches 4 mm above FCAM_Y
LINER_REVEAL = 8.0                            # visible liner ring inside the matboard
# Heimlove 11 x 17" teak frame, hung landscape (product drawing values; verify on arrival)
MAT_W, MAT_H, MAT_T = 432.0, 279.0, 1.01      # RABBET inside size (measured 2026-11-12) + mat thickness
MATB = (428.0, 276.0)                         # the mat itself (measured): smaller than the rabbet, centred by the ring lip
MAT_OPEN = (293.0, 192.0)                     # included mat opening 11.5 x 7.5"
FR_SIGHT = (432.0 - 2 * 6.11, 279.0 - 2 * 6.11)                     # display opening 16.6 x 10.6"
FR_OUT = (432.0 + 18.0, 279.0 + 18.0)                       # outer edge 17.8 x 11.8"
FR_DEPTH = 25.0                               # 1" front to back
RAB_D = 12.14                                   # rabbet depth: UNKNOWN, assumed 8 mm
FR_ROUND = 5.0                                # rounded front edge

# Z stack (assembled)
Z_PLATE0, Z_PLATE_BASE, Z_RIB = 0.0, 2.5, 7.0
# v3: two small wall plates nest in pockets in the carrier back; the carrier's own ribs bear on the wall.
T_P = 5.0                  # wall plate thickness
Z_CAR_BACK = 0.3           # carrier rib tips (bear on the wall)
DZ = (T_P + 0.5 + 1.5) - 12.5    # shift of everything in front vs v2 (tablet back 12.5 -> 8.0)
Z_BACKER0, Z_BACKER1 = 7.5, 10.5   # backer board screwed to the frame's back
Z_FLANGE1 = 12.5 + DZ      # carrier skin front = tablet back (8.0)
Z_TAB0, Z_TAB1 = Z_FLANGE1, Z_FLANGE1 + TAB_T
Z_FELT1 = Z_TAB1 + 0.6     # felt compressed to its hard stop
Z_LIN1 = Z_FELT1 + 3.0     # liner face front. Face 3.0 thick (was 1.6, then 2.4): white PETG needs about its TD (Bambu PETG HF White 2.9) to hide black
HOOK_Z1, HOOK_Z0 = Z_LIN1 - 1.0, Z_LIN1 - 3.2   # hook: retaining face 1.0 behind the liner face, ramp back to 3.2
Z_MAT1 = Z_LIN1 + MAT_T
Z_FR_BACK = Z_MAT1 - RAB_D          # frame back face (module sits mostly behind it)
Z_FR_FACE = Z_FR_BACK + FR_DEPTH

# cleat geometry
TAPER = math.radians(10)
RAIL_Y0, RAIL_Y1 = -60.0, 60.0                # rail length 120
RAIL_X_BOT = 128.0                            # male outer face |x| at bottom (at wall side)
DOVE = 5.0                                    # dovetail undercut depth

# ---------------------------------------------------------------- parts
def frame():
    W, H, r = FR_OUT[0], FR_OUT[1], FR_ROUND
    parts = [box(-W / 2, W / 2, -H / 2, H / 2, Z_FR_BACK, Z_FR_FACE - r)]
    for k in range(1, 7):                          # rounded outer front edge (quarter round, stepped hull)
        a = math.radians(90 * k / 6)
        parts.append(box(-W / 2 + r * (1 - math.cos(a)), W / 2 - r * (1 - math.cos(a)), -H / 2 + r * (1 - math.cos(a)), H / 2 - r * (1 - math.cos(a)), Z_FR_FACE - r, Z_FR_FACE - r + r * math.sin(a)))
    f = Manifold.hull(Manifold.batch_boolean(parts, M.OpType.Add))
    f -= box(-MAT_W / 2, MAT_W / 2, -MAT_H / 2, MAT_H / 2, Z_FR_BACK - 1, Z_MAT1)   # rabbet
    # sight opening, rounded inner front edge
    f -= frustum(FR_SIGHT[0], FR_SIGHT[1], Z_MAT1 - 0.01, FR_SIGHT[0], FR_SIGHT[1], Z_FR_FACE - 3)
    f -= frustum(FR_SIGHT[0], FR_SIGHT[1], Z_FR_FACE - 3.01, FR_SIGHT[0] + 6, FR_SIGHT[1] + 6, Z_FR_FACE + 0.01)
    f -= frame_hole()
    return f

def matboard():
    m = box(-MATB[0] / 2, MATB[0] / 2, -MATB[1] / 2, MATB[1] / 2, Z_LIN1, Z_MAT1)
    m -= frustum(MAT_OPEN[0], MAT_OPEN[1], Z_LIN1 - 0.01, MAT_OPEN[0] + 3.0, MAT_OPEN[1] + 3.0, Z_MAT1 + 0.01)
    return m

def liner(front_spk=True, cam='holes'):
    """front_spk=False: no speaker slits on the front (speakers exit through the side slots only).
    cam='holes': two round holes (front camera, light sensor) instead of the notch."""
    face = box(-LINER_W / 2, LINER_W / 2, -LINER_H / 2, LINER_H / 2, Z_FELT1, Z_LIN1)
    face -= frustum(LINER_OPEN[0], LINER_OPEN[1], Z_FELT1 - 0.01, LINER_OPEN[0] + 3.2, LINER_OPEN[1] + 3.2, Z_LIN1 + 0.01)
    # pocket walls round the tablet
    pw, ph = TAB_W + 1.0, TAB_H + 1.0
    walls = box(-LINER_W / 2, LINER_W / 2, -LINER_H / 2, LINER_H / 2, Z_TAB0, Z_FELT1)
    walls -= rrect(pw, ph, 5.0, Z_TAB0 - 1, Z_FELT1 + 0.01)     # small corner radius: tablet corners (r ~8.2) get >1.5 mm of room
    # (removed 2026-11-12, user: no hard plastic on the glass; the snaps set the spacing, felt takes up tolerance)
    ledge = Manifold() if True else box(-pw / 2, pw / 2, -ph / 2, ph / 2, Z_TAB1, Z_FELT1) - box(-pw / 2 + 2.5, pw / 2 - 2.5, -ph / 2 + 2.5, ph / 2 - 2.5, Z_TAB1 - 1, Z_FELT1 + 1)
    l = face + walls + ledge
    # 1 mm lead-in chamfer on the back outer edge so the snap hooks ride over it
    ch = 1.0
    l = l ^ Manifold.hull(box(-LINER_W / 2 + ch, LINER_W / 2 - ch, -LINER_H / 2 + ch, LINER_H / 2 - ch, Z_TAB0, Z_TAB0 + 0.01)
                          + box(-LINER_W / 2, LINER_W / 2, -LINER_H / 2, LINER_H / 2, Z_TAB0 + ch, Z_LIN1))
    # lighten / clip-screw bosses region left as is
    # front camera / light sensor window: notch up from the screen opening, 45 deg bevel like the opening
    y0, y1 = SCR_H / 2 - 2.0, FCAM_Y + FCAM_TOP
    nb = rrect(FCAM_W, y1 - y0, 3.0, Z_FELT1 - 0.01, Z_FELT1, cy=(y0 + y1) / 2)
    nt = rrect(FCAM_W + 3.2, y1 - y0 + 3.2, 4.6, Z_LIN1, Z_LIN1 + 0.01, cy=(y0 + y1) / 2 + 1.6)
    if cam == 'notch':
        l -= Manifold.hull(nb + nt)
        l -= box(-FCAM_W / 2, FCAM_W / 2, y0, y1, Z_TAB1 - 0.1, Z_FELT1 + 0.01)   # hard-stop ledge stops short of the window
    else:
        # two flared holes (user 2026-11-13: holes, not a notch; no filled slope; flare them, 'just not as much at the bottom').
        # The camera sits 4 mm from the top, so the flare leans upward: the front circle is bigger and shifted up, which
        # keeps 0.8 mm of wall to the screen opening's bevel at the bottom and opens wide at the top and sides.
        xs = tab_x(136.3)
        def lean_hole(x, r_back, r_front, up):
            d = lambda r, dy, z: Manifold.cylinder(0.02, r, r, 64).translate([x, FCAM_Y + dy, z])
            return Manifold.hull(d(r_back, 0.0, Z_FELT1 - 0.02) + d(r_front, up, Z_LIN1))
        l -= lean_hole(0.0, 2.0, 2.5, 0.8)       # front camera: 4.0 at the glass -> 5.0 at the face (bottom edge 1.7 below centre)
        l -= lean_hole(xs, 1.25, 1.9, 0.4)       # light sensor: 2.5 -> 3.8 (bottom edge 1.5 below centre)
    l -= liner_cuts(mics=False, speakers=False)
    l -= sound_channels(front_spk)
    l -= adapter_pocket()
    cuts, hooks = liner_springs()
    l -= cuts
    l += hooks
    l -= button_bay() ^ box(-400, 400, -400, 400, -50, Z_FELT1)      # face strip stays, everything behind it goes
    return l

def tab_x(from_left):
    return -TAB_W / 2 + from_left

def tab_y(from_top):
    return TAB_H / 2 - from_top

# ---- Directlinx 2-in-1 USB-C OTG + PD adapter (DL 726-006): 38.6 x 16.1 x 8.2 mm (Directlinx drawing)
# USB-C plug on one long face (~15.5 mm from the closed end), PD USB-C input on the opposite long face
# (near the closed end), USB-A on the end. Installed: plug into the tablet's right edge, body runs along
# the edge with the USB-A end pointing UP; PD input faces outward (away from the tablet).
AD_L, AD_W, AD_T = 38.6, 16.1, 8.2           # along the edge (y), outward (x), thickness (z)
AD_GAP = 5.0                                 # plug collar: body face sits ~5 mm off the tablet edge (verify)
AD_X0 = TAB_W / 2 + AD_GAP
AD_Z = Z_TAB0 + 2.5                    # port centre height
AD_PLUG_FROM_CLOSED = 15.5
# Flipped (user 2026-11-08): USB-A end DOWN, closed end up.
AD_Y1 = AD_PLUG_FROM_CLOSED - 1.15                  # closed end (top)
AD_Y0 = AD_Y1 - AD_L                         # USB-A end (bottom)
AD_PD_Y = AD_Y1 - 12.0                       # PD input position on the outer face (approx.)

def adapter():
    body = rrect(AD_W, AD_L, 2.0, AD_Z - AD_T / 2, AD_Z + AD_T / 2, cx=AD_X0 + AD_W / 2, cy=(AD_Y0 + AD_Y1) / 2)
    collar = box(TAB_W / 2 + 0.2, AD_X0 + 0.5, -4.6, 4.6, AD_Z - 2.6, AD_Z + 2.6)
    blade = box(TAB_W / 2 - 6.5, TAB_W / 2 + 0.3, -4.2, 4.2, AD_Z - 1.3, AD_Z + 1.3)
    a = body + collar + blade
    a -= box(AD_X0 + 1.8, AD_X0 + AD_W - 1.8, AD_Y0 - 1, AD_Y0 + 9, AD_Z - 2.6, AD_Z + 2.6)      # USB-A socket (bottom end)
    a -= box(AD_X0 + AD_W - 7, AD_X0 + AD_W + 1, AD_PD_Y - 4.5, AD_PD_Y + 4.5, AD_Z - 1.7, AD_Z + 1.7)  # PD USB-C input (outer face)
    return a

STATIK_PLUG_L = 36.0                          # USB-A plug + boot, estimate (Statik 360 Gen 2)
def usba_plug():
    """Statik's straight USB-A plug into the adapter's bottom end, pointing down."""
    y_end = AD_Y0 + 8
    return rrect(AD_W - 4.0, STATIK_PLUG_L, 1.5, AD_Z - 3.6, AD_Z + 3.6, cx=AD_X0 + AD_W / 2, cy=y_end - STATIK_PLUG_L / 2)

def pd_plug():
    """Straight USB-C plug into the adapter's PD input, pointing outward."""
    return box(AD_X0 + AD_W - 6, AD_X0 + AD_W + 22, AD_PD_Y - 4.2, AD_PD_Y + 4.2, AD_Z - 2.0, AD_Z + 2.0)

def adapter_pocket():
    """v8: one big window for the adapter, both plugs and the cables (user: 'lots of room'; adapter not measured).
    From the tablet edge out through the liner wall and the carrier skirt, y -70 .. adapter top + 3."""
    return box(TAB_W / 2 - 0.5, CW / 2 + 1, -95.0, AD_Y1 + 3.0, AD_Z - AD_T / 2 - 1.0, Z_FELT1 - 0.3)     # down to -95: the Statik plug + boot hang ~40 mm below the adapter (photo 2026-11-12)

SPK_Y = ((44, 75), (116.5, 147))          # speaker slot spans, mm from the tablet's top edge (estimates)
MIC_X = ((82.5, 94.5), (206.8, 218.8))        # mic slot spans, mm from the tablet's left edge (estimates)
SEAM_D = 0.6                            # depth of the hidden groove under the mat edge
SEAM_VIS = 1.0                          # how far the groove reaches out from under the mat edge

def seam_vents():
    """Liner only. Sound/air path that comes out under the matboard's edge: a vertical link from the
    tablet-edge slot up to the liner face (hidden under the mat), then a shallow groove in the liner
    face that runs out from under the mat edge by SEAM_VIS. Seen from the front it reads as the mat's
    shadow line. Speakers: their side slots also stay open to the back/side. Mics: slot is blind
    (closed on the outside) so the mic only hears through the seam."""
    zf = Z_LIN1
    mx, my = MAT_OPEN[0] / 2, MAT_OPEN[1] / 2       # mat edge (back face)
    v = []
    for y0, y1 in SPK_Y:
        ya, yb = tab_y(y1), tab_y(y0)
        for s in (-1, 1):
            a, b = sorted((s * (TAB_W / 2 + 0.7), s * (mx + 3.0)))
            v.append(box(a, b, ya, yb, Z_TAB1 - 1.0, zf + 0.1))                 # link up to the face
            a, b = sorted((s * (mx - SEAM_VIS), s * (mx + 3.0)))
            v.append(box(a, b, ya, yb, zf - SEAM_D, zf + 0.1))                  # groove out from under the mat
    for x0, x1 in MIC_X:
        xa, xb = tab_x(x0), tab_x(x1)
        v.append(box(xa, xb, TAB_H / 2 - 1, TAB_H / 2 + 3.5, Z_TAB0 - 1, Z_TAB1 - 0.2))   # blind slot at the mic
        v.append(box(xa, xb, TAB_H / 2 + 0.7, my + 3.0, Z_TAB1 - 1.0, zf + 0.1))          # link up to the face
        v.append(box(xa, xb, my - SEAM_VIS, my + 3.0, zf - SEAM_D, zf + 0.1))             # groove
    return Manifold.batch_boolean(v, M.OpType.Add)

def seam_deflectors():
    """Liner only (user idea): 45 deg fills in the back corner of each sound slot.
    Mics: fill the back-outer corner of the blind slot, so sound coming down the seam is turned
    toward the mic port and the dead pocket behind it shrinks. Speakers: a 45 deg ramp in the lower
    (wall-side) half of the side slot, just past the seam link, turns part of the sound forward
    into the seam; the upper half stays open so sound still goes out the side."""
    zb = Z_TAB0                                   # liner back (the carrier skin closes it)
    d = []
    y1 = TAB_H / 2 + 3.5                          # outer end of the blind mic slot
    leg = y1 - (TAB_H / 2 + 0.05)                 # 45 deg, from the outer wall to the tablet edge
    for x0, x1 in MIC_X:
        xa, xb = tab_x(x0), tab_x(x1)
        pts = [(x, y, z) for x in (xa, xb) for (y, z) in ((y1, zb), (y1 - leg, zb), (y1, zb + leg))]
        d.append(Manifold.hull_points(pts))
    xs = MAT_OPEN[0] / 2 + 3.0                    # just past the seam link
    h = (Z_TAB1 - Z_TAB0) / 2                     # lower half only
    for y0, y1s in SPK_Y:
        ya, yb = tab_y(y1s), tab_y(y0)
        for sg in (-1, 1):
            pts = [(sg * x, y, z) for y in (ya, yb) for (x, z) in ((xs, zb), (xs + h, zb), (xs + h, zb + h))]
            d.append(Manifold.hull_points(pts))
    return Manifold.batch_boolean(d, M.OpType.Add)

def _stroke(pts, w):
    """2D stroke (round joins/caps) of an open polyline, as a CrossSection."""
    parts = []
    for (a, b) in zip(pts[:-1], pts[1:]):
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b - a; L = np.hypot(*d)
        if L < 1e-9: continue
        n = np.array([-d[1], d[0]]) / L * w / 2
        parts.append(CrossSection([[a - n, b - n, b + n, a + n]]))
    for p in pts:
        parts.append(CrossSection.circle(w / 2, 20).translate(list(p)))
    out = parts[0]
    for p in parts[1:]: out = out + p
    return out

def _arc(c, r, a0, a1, n=10):
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

def _rounded_poly(pts, radii, n=8):
    """Polygon with selected corners filleted. pts CCW; radii[i] = fillet radius at pts[i] (0 = sharp)."""
    out = []
    N = len(pts)
    for i in range(N):
        p0, p1, p2 = np.array(pts[i - 1], float), np.array(pts[i], float), np.array(pts[(i + 1) % N], float)
        r = radii[i]
        if r <= 0:
            out.append(tuple(p1)); continue
        u0 = (p0 - p1) / np.linalg.norm(p0 - p1); u2 = (p2 - p1) / np.linalg.norm(p2 - p1)
        ang = math.acos(np.clip(u0 @ u2, -1, 1))
        d = r / math.tan(ang / 2)
        a0, a2 = p1 + u0 * d, p1 + u2 * d
        bis = (u0 + u2) / np.linalg.norm(u0 + u2)
        c = p1 + bis * r / math.sin(ang / 2)
        t0 = math.atan2(*(a0 - c)[::-1]); t2 = math.atan2(*(a2 - c)[::-1])
        dt = (t2 - t0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            t = t0 + dt * k / n
            out.append((c[0] + r * math.cos(t), c[1] + r * math.sin(t)))
    return CrossSection([out])

# sound tunnel, local (s, t): s = outward from the tablet edge face, t = Z  (user trace 2026-11-10)
TUN_W = 1.2            # tunnel width (top and port legs)
TUN_W_IN = 0.8         # inlet leg, between the island and the mat's back face
TUN_TIP = -0.6         # island's 45 deg tip at the liner face (s); mouth = TUN_TIP .. mat edge
PORT_T = (Z_TAB0 + Z_TAB1) / 2

def sound_channel_2d(s_m):
    """Tunnel (not a chamber): mouth just under the mat edge, between the mat and a 45 deg chamfer on
    the island tip; inlet leg up behind the mat; over the top; down onto the port. Island corners r 0.6,
    outer bends concentric. Square drop at the port end onto the tablet-edge clearance."""
    tf = Z_LIN1
    t_in = tf - TUN_W_IN                      # island face toward the room
    t_pr = PORT_T + TUN_W / 2                 # island face toward the wall (port leg)
    t_out = PORT_T - TUN_W / 2                # tunnel outer wall at the port leg
    s_top = max(s_m + 0.9, 1.5)               # island top
    s_out = s_top + TUN_W                     # tunnel outer wall at the top leg
    s_tip_face = s_m - 1.0                    # visible dimple = 1.0 mm from the mat's edge (user 2026-11-13: less obvious; was TUN_TIP = -0.6, 2 mm at the mics)
    s_ch = s_tip_face + (tf - t_in)           # 45 deg chamfer meets the island's room face
    ri = 0.6
    # island: rounded over the tunnel; its 45 deg tip blends softly into the tunnel (D) and into the
    # liner face (E); flat on the liner face beyond the tip
    island = _rounded_poly([(0.5, t_pr), (s_top, t_pr), (s_top, t_in), (s_ch, t_in),
                            (s_tip_face, tf), (-0.9, tf), (-0.9, Z_TAB1), (0.5, Z_TAB1)],
                           [0, 0.3, ri, 0.6, 0.5, 0, 0, 0], n=10)    # port-leg corner 0.3: keeps the fin tip >= 0.8
    # outer wall: big bend at the port leg; the top-left corner (where the liner meets the mat's back)
    # is rounded so the wall curves down tangent to the mat
    outer = _rounded_poly([(-0.7, t_out), (s_out, t_out), (s_out, tf), (s_m + 0.2, tf),
                           (s_m + 0.2, tf + 0.2), (-0.7, tf + 0.2)],
                          [0, ri + TUN_W, 1.2, 0, 0, 0], n=10)
    return outer - island

def _place(cs2d, kind, a, b, edge, sign=1):
    """Extrude a local (s, t) section along [a, b] and put it at a tablet edge."""
    g = cs2d.extrude(b - a)                        # (s, t, w)
    if kind == 'top':                              # y = edge + s, z = t, x = a + w
        return g.transform([[0, 0, 1, a], [1, 0, 0, edge], [0, 1, 0, 0]])
    return g.transform([[sign, 0, 0, sign * edge], [0, 0, 1, a], [0, 1, 0, 0]])   # side: x = +-(edge + s)

def sound_channels(front_spk=True):
    """Liner only (user: '45s everywhere / swoopy channels'). Replaces seam_vents + seam_deflectors."""
    out = []
    mic = sound_channel_2d(MAT_OPEN[1] / 2 - TAB_H / 2)
    for x0, x1 in MIC_X:
        out.append(_place(mic, 'top', tab_x(x0), tab_x(x1), TAB_H / 2))
    spk = sound_channel_2d(MAT_OPEN[0] / 2 - TAB_W / 2)
    s_m = MAT_OPEN[0] / 2 - TAB_W / 2
    for y0, y1 in SPK_Y:
        ya, yb = tab_y(y1), tab_y(y0)
        for sg in (-1, 1):
            if front_spk:
                out.append(_place(spk, 'side', ya, yb, TAB_W / 2, sg))
            # side exits (sound out the side too): 5 mm slots with 2 mm webs, so each roof is a short bridge
            xa, xb = sorted((sg * (TAB_W / 2 + (1.0 if front_spk else 0.3)), sg * (LINER_W / 2 + 1)))
            n = int((yb - ya + 2) // 7)
            y = ya + ((yb - ya) - (n * 7 - 2)) / 2
            for k in range(n):
                out.append(box(xa, xb, y + 7 * k, y + 7 * k + 5, PORT_T - TUN_W / 2, PORT_T + TUN_W / 2))
    return Manifold.batch_boolean(out, M.OpType.Add)

def _rect2(x0, x1, y0, y1):
    return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])

def button_bay():
    """Finger bay (user 2026-11-13): the top-left corner (seen from the front) of the surround is cut away outside the
    tablet's edge, so power and volume can be pressed with a finger from behind when the unit is off the wall.
    L shape: along the top edge to 46 mm from the left, down the left edge to 38 mm from the top (stops short of the speaker).
    Profile rounded per the user's red markup: r4 fillets where the cut ends meet the skirt, the corner follows the
    tablet's own corner radius, and the cut ends of the skirt are rounded on the outside."""
    e = 0.3
    xe, ye = tab_x(46.0), tab_y(38.0)
    bay = _rect2(-400, xe, TAB_H / 2 + e, 400) + _rect2(-400, -TAB_W / 2 - e, ye, 400)
    solid = _rect2(-CW / 2, CW / 2, -CH / 2, CH / 2)
    for x in (-86.0, -50.0, 50.0, 130.0):
        solid += _rect2(x - 14.0, x + 14.0, CH / 2 - 1, 400)
    u = bay + (_rect2(-400, 400, -400, 400) - solid)
    rnd = lambda cs, r: cs.offset(r, JoinType.Round, circular_segments=48)
    u = rnd(rnd(u, -4.0), 4.0)                    # fillets in the carrier's inside corners
    u = rnd(rnd(u, TAB_R), -TAB_R)                # round the carrier's outside corners (tablet corner, skirt ends)
    u = u ^ _rect2(-CW / 2 - 5, xe + 4.5, ye - 12, CH / 2 + 5)      # this corner only
    return u.extrude(150).translate([0, 0, -50])

def camera_window_2d():
    r = 6.0
    return CrossSection.square([CAM_W - 2 * r, CAM_H + 1 - 2 * r], center=True).offset(r, JoinType.Round, circular_segments=24).translate([tab_x(30.5), tab_y(23.5)])

def liner_cuts(mics=True, speakers=True):
    """Reliefs for buttons, slots for mics/speakers, USB-C and pogo pins, in the pocket wall."""
    z0, z1 = Z_TAB0 - 1, Z_TAB1 - 0.2
    top, bot = TAB_H / 2, -TAB_H / 2
    left, right = -TAB_W / 2, TAB_W / 2
    cuts = []
    # volume buttons (top edge, x 10-42 from left) and power (left edge, y 6-38 from top)
    cuts.append(box(tab_x(6), tab_x(46), top - 2, top + 20, z0, z1))
    cuts.append(box(left - 20, left + 2, tab_y(42), tab_y(2), z0, z1))
    # mics (top edge) - generous slots
    for x0, x1 in (MIC_X if mics else ()):
        cuts.append(box(tab_x(x0), tab_x(x1), top - 1, top + 20, z0, z1))
    # speakers, both short edges
    for y0, y1 in (SPK_Y if speakers else ()):
        cuts.append(box(left - 20, left + 1, tab_y(y1), tab_y(y0), z0, z1))
        cuts.append(box(right - 1, right + 20, tab_y(y1), tab_y(y0), z0, z1))
    # USB-C (right edge middle) - notch for a right-angle plug
    cuts.append(box(right - 1, right + 20, tab_y(106), tab_y(82), Z_TAB0 - 1, Z_TAB1 + 0.3))
    # pogo pins + guide pins (bottom middle)
    # (bottom relief removed 2026-11-12: only keyboard pins/slots there, nothing needs access)
    return Manifold.batch_boolean(cuts, M.OpType.Add)

def felt_strips():
    pw, ph = TAB_W, TAB_H
    t0, t1 = Z_TAB1, Z_FELT1
    a, b = 3.2, 7.2
    g = FCAM_W / 2 + 3      # top strip split: keep the felt off the front camera / sensor
    parts = [box(-pw / 2 + 12, -g, ph / 2 - b, ph / 2 - a, t0, t1), box(g, pw / 2 - 12, ph / 2 - b, ph / 2 - a, t0, t1),
             box(-pw / 2 + 12, pw / 2 - 12, -ph / 2 + a, -ph / 2 + b, t0, t1),
             box(-pw / 2 + a, -pw / 2 + b, -ph / 2 + 12, ph / 2 - 12, t0, t1),
             box(pw / 2 - b, pw / 2 - a, -ph / 2 + 12, ph / 2 - 12, t0, t1)]
    return Manifold.batch_boolean(parts, M.OpType.Add)

def tablet_body():
    t = rrect(TAB_W, TAB_H, TAB_R, Z_TAB0, Z_TAB1)
    # rear camera bump (back, top-left seen from the front)
    t += rrect(46, 31, 5, Z_TAB0 - 2.1, Z_TAB0 + 0.1, cx=tab_x(30.45), cy=tab_y(23.5))
    return t

def tablet_glass():
    return box(-SCR_W / 2, SCR_W / 2, -SCR_H / 2, SCR_H / 2, Z_TAB1, Z_TAB1 + 0.05)

def calendar_marks():
    """Thin coloured bars on the screen so the front reads as the calendar."""
    rng = np.random.default_rng(7)
    out = []
    cols, rows = 7, 5
    x0, x1, y0, y1 = -SCR_W / 2, SCR_W / 2, -SCR_H / 2, SCR_H / 2
    hdr = 24
    gw, gh = (x1 - x0) / cols, (y1 - y0 - hdr) / rows
    z0, z1 = Z_TAB1 + 0.05, Z_TAB1 + 0.1
    grid = []
    for c in range(1, cols):
        grid.append(box(x0 + c * gw - 0.3, x0 + c * gw + 0.3, y0, y1 - hdr, z0, z1))
    for r in range(1, rows + 1):
        yy = y1 - hdr - (r - 1) * gh if r > 1 else y1 - hdr
        grid.append(box(x0, x1, yy - 0.3, yy + 0.3, z0, z1))
    colors = [(232, 120, 110), (110, 160, 220), (120, 190, 130), (230, 180, 80)]
    for i in range(18):
        c, r, k = rng.integers(cols), rng.integers(rows), rng.integers(2)
        bx = x0 + c * gw + 2
        by = y1 - hdr - r * gh - 6 - k * 7
        out.append((box(bx, bx + gw - 4, by - 4, by, z0, z1 + 0.02), colors[rng.integers(4)]))
    hdrbar = box(x0, x1, y1 - hdr, y1, z0, z1)
    return Manifold.batch_boolean(grid, M.OpType.Add), hdrbar, out

CW, CH = 325.0, 221.0          # carrier outer (skirt) size
SKIRT_T = 2.2
Z_SKIRT1 = 19.0 + DZ
EAR_X, EAR_W, EAR_Y, = 110.0, 24.0, 120.0
Z_EAR0 = Z_FLANGE1 - 2.0
# v5b: moved clear of the corner lugs (x 92-128) and the cable exit on the right side
SNAPS = [('T', -75), ('T', 0), ('T', 145), ('B', -145), ('B', -75), ('B', 75), ('B', 145), ('L', -85), ('R', 85)]   # R moved up: the USB window now runs down to y -95
SNAP_L, SNAP_Z0, SNAP_Z1 = 20.0, 14.0 + DZ, 18.0 + DZ   # (v5 chassis tabs, superseded)
BEAM_T, BEAM_H, BEAM_GAP = 2.0, 4.5, 1.5   # v6 liner spring: thickness, height from the face, slot width
HOOK_D = 1.3                                # hook stands 1.0 proud of the liner face (0.7 past the 0.3 gap)

def _snap_frame(side, pos):
    """Return (axis, sign) helpers: wall plane coordinate and along-wall coordinate."""
    if side in 'TB':
        return 'y', (CH / 2 if side == 'T' else -CH / 2), pos
    return 'x', (CW / 2 if side == 'R' else -CW / 2), pos

def snap_cuts_and_hooks():
    """U-slots that free a horizontal beam in the skirt wall (flexes in the layer plane),
    plus the hook bump on the beam's inner face at its free end."""
    cuts, hooks = [], []
    g = 1.0
    for side, pos in SNAPS:
        ax, wall, a = _snap_frame(side, pos)
        s_in = -1 if wall > 0 else 1                     # inward direction
        w0, w1 = (wall - 0.01, wall + s_in * (SKIRT_T + 0.01)) if s_in < 0 else (wall - 0.01, wall + SKIRT_T + 0.01)
        lo_w, hi_w = min(wall, wall + s_in * SKIRT_T) - 0.05, max(wall, wall + s_in * SKIRT_T) + 0.05
        a0, a1 = a - SNAP_L / 2, a + SNAP_L / 2
        # slots: above, below, and at the free end (a1)
        parts = [(a0, a1 + g, SNAP_Z1, SNAP_Z1 + g), (a0, a1 + g, SNAP_Z0 - g, SNAP_Z0), (a1, a1 + g, SNAP_Z0 - g, SNAP_Z1 + g)]
        for (p0, p1, z0, z1) in parts:
            if ax == 'y':
                cuts.append(box(p0, p1, lo_w, hi_w, z0, z1))
            else:
                cuts.append(box(lo_w, hi_w, p0, p1, z0, z1))
        # hook: bump 0.9 mm inward at the free end, ramped
        inner = wall + s_in * SKIRT_T
        if ax == 'y':
            hooks.append(box(a1 - 5, a1, min(inner, inner + s_in * 0.9), max(inner, inner + s_in * 0.9), 15.5 + DZ, 17.3 + DZ))
        else:
            hooks.append(box(min(inner, inner + s_in * 0.9), max(inner, inner + s_in * 0.9), a1 - 5, a1, 15.5 + DZ, 17.3 + DZ))
    return Manifold.batch_boolean(cuts, M.OpType.Add), Manifold.batch_boolean(hooks, M.OpType.Add)

def liner_springs():
    """v6: spring beams cut into the liner's outer edge at the face side. In the liner's print (face down) the beam
    stands on the bed and flexes in the layer plane; nothing overhangs except the 1 mm hook ledge.
    Cantilever 20 x 2.0 x 4.5, fixed at a0, free at a1; a 1.2 slot inside it doubles as the release slot."""
    cuts, hooks = [], []
    zb0 = Z_LIN1 - BEAM_H
    for side, pos in SNAPS:
        ax, sg, e = _snap_geom(side, pos)
        a0, a1 = pos - SNAP_L / 2, pos + SNAP_L / 2
        cuts.append(_edge_box(side, a0, a1 + BEAM_GAP, e - BEAM_T - BEAM_GAP, e - BEAM_T, zb0 - 1.0, Z_LIN1 + 0.1))   # inner slot
        cuts.append(_edge_box(side, a1, a1 + BEAM_GAP, e - BEAM_T - BEAM_GAP, e + 0.1, zb0 - 1.0, Z_LIN1 + 0.1))      # free-end slot
        cuts.append(_edge_box(side, a0, a1 + BEAM_GAP, e - BEAM_T - BEAM_GAP, e + 0.1, zb0 - 1.0, zb0))               # slot behind the beam
        # hook: full 1.0 at the front (retaining face), ramps to 0 toward the back (lead-in)
        f = _edge_box(side, a1 - 5, a1, e - 0.01, e + HOOK_D, HOOK_Z1 - 0.7, HOOK_Z1)
        r = _edge_box(side, a1 - 5, a1, e - 0.01, e, HOOK_Z0, HOOK_Z0 + 0.01)
        hooks.append(Manifold.hull(f + r))
    return Manifold.batch_boolean(cuts, M.OpType.Add), Manifold.batch_boolean(hooks, M.OpType.Add)

def liner_catches():
    """Grooves in the liner's outer wall that the hooks click into."""
    g = []
    for side, pos in SNAPS:
        ax, wall, a = _snap_frame(side, pos)
        lw = (LINER_W / 2 if ax == 'x' else LINER_H / 2) * (1 if wall > 0 else -1)
        a1 = a + SNAP_L / 2
        if ax == 'y':
            g.append(box(a1 - 6, a1 + 1, min(lw, lw - math.copysign(1.1, lw)), max(lw, lw - math.copysign(1.1, lw)) + 0.01 * 0, 15.3 + DZ, 17.5 + DZ))
        else:
            g.append(box(min(lw, lw - math.copysign(1.1, lw)), max(lw, lw - math.copysign(1.1, lw)), a1 - 6, a1 + 1, 15.3 + DZ, 17.5 + DZ))
    return Manifold.batch_boolean(g, M.OpType.Add)

# ---- v4 wall mount (user idea 2026-11-09): ONE trapezoid mount on the wall with its tapered edges on the
# outside (45 deg dovetail bevel, 10 deg taper, narrow at the top). The carrier has a matching cavity in the
# middle of its back with lips on the inside edges. Cavity runs on below the mount for the lift-off, with a gap
# above the mount so it never tops out. Carrier ribs bear on the wall.
M_Y0, M_Y1 = -55.0, 55.0          # mount bottom / top
M_TOP_HW = 80.0                    # half-width at the top (front face, widest)
M_T = T_P                          # 6 thick
M_EDGE = 1.0                       # vertical edge at the front; 45 deg bevel underneath (narrower at the wall)
LIFT = 24.0
TOP_GAP = 5.0
SKIN = 1.5
Z_POCKET = M_T + 0.5               # cavity floor (carrier skin back face)
CAV_Y0, CAV_Y1 = M_Y0 - LIFT - 1.0, M_Y1 + TOP_GAP

def m_hw(y):
    return M_TOP_HW + (M_Y1 - y) * math.tan(TAPER)

PLAT_IN = 4.0          # plateau inset from the mount's edge
FELT_T = 0.0           # no felt on the plateau (user 2026-11-12)
PLAT_TOP = Z_FLANGE1 - 0.3            # hard backstop 0.3 mm behind the tablet back (7.7)

def mount_felt():
    """Vertical felt strips on the plateau (gaps between them let air rise)."""
    out = []
    for x in np.arange(-60, 61, 20.0):
        out.append(box(x - 6, x + 6, M_Y0 + PLAT_IN + 3, M_Y1 - PLAT_IN - 3, PLAT_TOP, PLAT_TOP + FELT_T))
    return Manifold.batch_boolean(out, M.OpType.Add)

def mount():
    def prof(y):
        hw = m_hw(y); bev = M_T - M_EDGE
        return [(-hw + bev, 0.0), (hw - bev, 0.0), (hw, bev), (hw, M_T), (-hw, M_T), (-hw, bev)]
    m = hull_prism_y(prof(M_Y1), prof(M_Y0), M_Y1, M_Y0)
    # backing plateau: carries the tablet back (through the open cavity) straight into the wall
    def pprof(y):
        hw = m_hw(y) - PLAT_IN
        return [(-hw, M_T - 0.01), (hw, M_T - 0.01), (hw, PLAT_TOP), (-hw, PLAT_TOP)]
    m += hull_prism_y(pprof(M_Y1 - PLAT_IN), pprof(M_Y0 + PLAT_IN), M_Y1 - PLAT_IN, M_Y0 + PLAT_IN)
    for (x, y) in ((-55, 38), (55, 38), (-75, -40), (75, -40), (0, 0)):      # 5 countersunk #6, spread out
        m -= cyl(1.85, -1, M_T + 1, x, y)
        m -= Manifold.cylinder(2.7, 1.85, 4.4, 24).translate([x, y, PLAT_TOP - 2.7 + 0.01])
    return m

def plate():
    return mount()

def cavity():
    def prof(y):
        hw = m_hw(y) + 0.7; bev = M_T - M_EDGE
        a = hw - bev - 1.0                       # lip face parallel to the mount's bevel, carried on to Z = -1
        return [(-a, -1.0), (a, -1.0), (hw, bev), (hw, Z_POCKET), (-hw, Z_POCKET), (-hw, bev)]
    return hull_prism_y(prof(CAV_Y1), prof(CAV_Y0), CAV_Y1, CAV_Y0)

# ---- v6 (2026-11-09): printability + airflow
# * Cavity left open through the skin (a 209 x 140 roof can't bridge). The wall mount gets a raised backing
#   plateau + felt, so the tablet back is carried straight into the wall over the opening.
# * Extra rib at y = 78 splits the top cells (bridges were 33 mm; playbook limit ~28).
# * Snap springs moved to the liner (they print on the bed there); the chassis gets catch blocks with a groove.
# * Slat vents in the skin (each slot runs rib to rib, so every strip between slots is a short bridge) and chimney
#   notches in the horizontal ribs, rim and cavity band, so air rises behind the tablet.
CAM_RING = False
CAM_W, CAM_H = 56.0, 40.0
RIBS_X = (-140, -120, -99, -55, -11, 11, 55, 99, 120, 140)
RIBS_Y = (-95, -60, 60, 78, 95)
SLOT_W, SLOT_P = 2.0, 5.0            # vent slot width / pitch (3 mm strips)
NOTCH_H, NOTCH_L, NOTCH_P = 3.0, 8.0, 22.0
CATCH_L = 30.0                       # catch block length on the skirt

def _snap_geom(side, pos):
    """(axis along the edge, sign of the outward normal, edge coordinate of the liner's outer face)."""
    if side in 'TB':
        return 'x', (1 if side == 'T' else -1), LINER_H / 2
    return 'y', (1 if side == 'R' else -1), LINER_W / 2

def _edge_box(side, a0, a1, n0, n1, z0, z1):
    """Box in edge coordinates: a along the edge, n = distance out from the centre (+ outward), z."""
    ax, sg, _ = _snap_geom(side, 0)
    p0, p1 = sorted((sg * n0, sg * n1))
    return box(a0, a1, p0, p1, z0, z1) if ax == 'x' else box(p0, p1, a0, a1, z0, z1)

def vent_slots():
    """Slat vents through the skin, behind the tablet only, outside the cavity band. Slots run rib to rib."""
    zs0 = Z_FLANGE1 - SKIN
    xs = sorted(RIBS_X + (-CW / 2 + SKIRT_T - 1.0, CW / 2 - SKIRT_T + 1.0))
    ys = sorted(RIBS_Y + (-CH / 2 + SKIRT_T - 1.0, CH / 2 - SKIRT_T + 1.0))
    out = []
    tw, th = TAB_W / 2 - 4, TAB_H / 2 - 4
    for x0, x1 in zip(xs[:-1], xs[1:]):
        for y0, y1 in zip(ys[:-1], ys[1:]):
            cx0, cx1, cy0, cy1 = x0 + 1.0, x1 - 1.0, y0 + 1.0, y1 - 1.0      # cell between rib faces
            if cx1 - cx0 < 6 or cy1 - cy0 < 6:
                continue
            along_y = (cy1 - cy0) <= (cx1 - cx0)                          # slots run across the short span
            if along_y:
                n = int((cx1 - cx0 - 3.0) // SLOT_P)
                st = (cx0 + cx1) / 2 - (n - 1) * SLOT_P / 2
                for k in range(n):
                    x = st + k * SLOT_P
                    out.append(box(x - SLOT_W / 2, x + SLOT_W / 2, cy0, cy1, zs0 - 0.01, Z_FLANGE1 + 0.01))
            else:
                n = int((cy1 - cy0 - 3.0) // SLOT_P)
                st = (cy0 + cy1) / 2 - (n - 1) * SLOT_P / 2
                for k in range(n):
                    y = st + k * SLOT_P
                    out.append(box(cx0, cx1, y - SLOT_W / 2, y + SLOT_W / 2, zs0 - 0.01, Z_FLANGE1 + 0.01))
    v = Manifold.batch_boolean(out, M.OpType.Add)
    keep = box(-tw, tw, -th, th, -5, 20)                                    # only where the tablet is behind
    def band_prof(y, extra):
        hw = m_hw(y) + 0.7 + extra
        return [(-hw, -5), (hw, -5), (hw, 20), (-hw, 20)]
    band = hull_prism_y(band_prof(CAV_Y1 + 8, 8), band_prof(CAV_Y0 - 8, 8), CAV_Y1 + 8, CAV_Y0 - 8)
    bump = rrect(58, 42, 8, -5, 20, cx=tab_x(30), cy=tab_y(23))
    blk = box(138, CW / 2, -58, 20, -5, 20)                                 # adapter backing block
    return (v ^ keep) - band - bump - blk

def chimney_notches():
    """One 8 x 3 mm notch per cell in each horizontal member (rim top/bottom, cross ribs, cavity band top/bottom),
    centred in the cell between the vertical ribs, never at a rib crossing, never in a lug or the lip sides."""
    z0, z1 = Z_CAR_BACK - 1, Z_CAR_BACK + NOTCH_H
    inner = CW / 2 - SKIRT_T
    xs = sorted(RIBS_X + (-inner, inner))
    cells = [(a + 1.0, b - 1.0) for a, b in zip(xs[:-1], xs[1:])]          # gaps between vertical faces
    def band_out(y):                                                         # half-width of the cavity band at y, or 0
        if CAV_Y0 - 6 <= y <= CAV_Y1 + 6:
            return m_hw(min(max(y, CAV_Y0), CAV_Y1)) + 0.7 + 6 + 1.0
        return 0.0
    def free(c0, c1, block):                                                 # parts of [c0,c1] outside the blocked intervals
        segs = [(c0, c1)]
        for b0, b1 in block:
            nxt = []
            for s0, s1 in segs:
                if b1 <= s0 or b0 >= s1:
                    nxt.append((s0, s1)); continue
                if b0 > s0: nxt.append((s0, b0))
                if b1 < s1: nxt.append((b1, s1))
            segs = nxt
        return [sg for sg in segs if sg[1] - sg[0] >= NOTCH_L + 2]
    out = []
    def notch_row(y0, y1, block, only=None):
        for c0, c1 in cells:
            if only and not (only[0] <= (c0 + c1) / 2 <= only[1]):
                continue
            for s0, s1 in free(c0, c1, block):
                xc = (s0 + s1) / 2
                out.append(box(xc - NOTCH_L / 2, xc + NOTCH_L / 2, y0, y1, z0, z1))
    lugs_t = [(x - 14.0 - 1, x + 14.0 + 1) for x in (-86.0, -50.0, 50.0, 130.0)]
    lugs_b = [(x - 14.0 - 1, x + 14.0 + 1) for x in (-130.0, -50.0, 50.0, 130.0)]
    notch_row(CH / 2 - SKIRT_T - 1, CH / 2 + 1, lugs_t)                      # rim top
    notch_row(-CH / 2 - 1, -CH / 2 + SKIRT_T + 1, lugs_b)                    # rim bottom
    for y in RIBS_Y:
        bo = band_out(y)
        notch_row(y - 1.5, y + 1.5, [(-bo, bo)] if bo else [])               # cross ribs, outside the cavity band
    # cavity band top and bottom (lets the cavity breathe), inside the cavity's own width only
    for yb, yc in ((CAV_Y1, (CAV_Y1 - 2, CAV_Y1 + 7)), (CAV_Y0, (CAV_Y0 - 7, CAV_Y0 + 2))):
        hw = m_hw(yb) + 0.7 - 3.0
        notch_row(yc[0], yc[1], [(-400, -hw), (hw, 400)])
    return Manifold.batch_boolean(out, M.OpType.Add)

def catch_blocks():
    """Skirt raised locally to the liner face at each snap, with a groove on its inside for the liner's hook."""
    blocks, grooves = [], []
    for side, pos in SNAPS:
        ax, sg, e = _snap_geom(side, pos)
        n_out = (CH / 2 if ax == 'x' else CW / 2)
        a1 = pos + SNAP_L / 2
        blk = _edge_box(side, pos - CATCH_L / 2, pos + CATCH_L / 2, n_out - SKIRT_T, n_out + 0.3, HOOK_Z0 - 1.2, Z_LIN1)
        # 0.8 mm lead-in chamfer on the inner front edge
        ch = _edge_box(side, pos - CATCH_L / 2 - 1, pos + CATCH_L / 2 + 1, n_out - SKIRT_T - 0.01, n_out - SKIRT_T + 0.8, Z_LIN1 - 0.8, Z_LIN1 + 0.01)
        cut = Manifold.hull(ch.scale([1, 1, 1]))
        blocks.append(blk)
        grooves.append(_edge_box(side, a1 - 6.5, a1 + 0.5, n_out - SKIRT_T - 0.01, n_out - SKIRT_T + HOOK_D + 0.2, HOOK_Z0 - 0.2, HOOK_Z1 + 0.2))
        # chamfer: hull of the inner-front edge line and a point 0.8 back + 0.8 out
        p = _edge_box(side, pos - CATCH_L / 2 - 1, pos + CATCH_L / 2 + 1, n_out - SKIRT_T - 0.01, n_out - SKIRT_T, Z_LIN1 - 0.8, Z_LIN1 + 0.01)
        q = _edge_box(side, pos - CATCH_L / 2 - 1, pos + CATCH_L / 2 + 1, n_out - SKIRT_T - 0.01, n_out - SKIRT_T + 0.8, Z_LIN1, Z_LIN1 + 0.01)
        grooves.append(Manifold.hull(p + q))
    return Manifold.batch_boolean(blocks, M.OpType.Add), Manifold.batch_boolean(grooves, M.OpType.Add)

def carrier():
    zs0 = Z_FLANGE1 - SKIN
    c = box(-CW / 2, CW / 2, -CH / 2, CH / 2, zs0, Z_FLANGE1)
    rim = box(-CW / 2, CW / 2, -CH / 2, CH / 2, Z_CAR_BACK, zs0) - box(-CW / 2 + SKIRT_T, CW / 2 - SKIRT_T, -CH / 2 + SKIRT_T, CH / 2 - SKIRT_T, -1, zs0 + 1)
    c += rim
    def ring_prof(y, extra):
        hw = m_hw(y) + 0.7 + extra
        return [(-hw, Z_CAR_BACK), (hw, Z_CAR_BACK), (hw, zs0), (-hw, zs0)]
    ring = hull_prism_y(ring_prof(CAV_Y1 + 6, 6), ring_prof(CAV_Y0 - 6, 6), CAV_Y1 + 6, CAV_Y0 - 6) ^ box(-CW / 2, CW / 2, -CH / 2 + 1, CH / 2 - 1, Z_CAR_BACK, zs0)
    c += ring
    ribs = [box(x - 1.0, x + 1.0, -CH / 2, CH / 2, Z_CAR_BACK, zs0) for x in RIBS_X]
    ribs += [box(-CW / 2, CW / 2, y - 1.0, y + 1.0, Z_CAR_BACK, zs0) for y in RIBS_Y]
    # rib ring round the camera-bump hole, so every edge of that hole is supported
    if CAM_RING:
        ribs.append(rrect(54, 38, 7, Z_CAR_BACK, zs0, cx=tab_x(30), cy=tab_y(23)) - rrect(50, 34, 6, Z_CAR_BACK - 1, zs0 + 1, cx=tab_x(30), cy=tab_y(23)))
    # solid block behind the adapter pocket (the pocket thins the skin there), from the wall up
    ribs.append(box(140, CW / 2 - SKIRT_T + 0.01, -99, 22, Z_CAR_BACK, zs0))
    c += Manifold.batch_boolean(ribs, M.OpType.Add)
    c -= chimney_notches()
    # cavity for the wall mount, open through the skin
    c -= cavity()
    def open_prof(y):
        hw = m_hw(y) + 0.7
        return [(-hw, Z_POCKET - 0.1), (hw, Z_POCKET - 0.1), (hw, Z_FLANGE1 + 0.1), (-hw, Z_FLANGE1 + 0.1)]
    c -= hull_prism_y(open_prof(CAV_Y1), open_prof(CAV_Y0), CAV_Y1, CAV_Y0)
    sk = box(-CW / 2, CW / 2, -CH / 2, CH / 2, Z_FLANGE1, Z_SKIRT1) - box(-CW / 2 + SKIRT_T, CW / 2 - SKIRT_T, -CH / 2 + SKIRT_T, CH / 2 - SKIRT_T, Z_FLANGE1 - 1, Z_SKIRT1 + 1)
    c += sk
    blocks, grooves = catch_blocks()
    c += blocks
    c -= grooves
    c += lugs()
    c -= lug_slots()
    c -= rrect(CAM_W, CAM_H + 1, 6, Z_FLANGE1 - 3.0, Z_FLANGE1 + 1, cx=tab_x(30.5), cy=tab_y(23.5))   # bump measured 46 x 31, ~2.1 tall: 3 deep, ribs included   # bump 46 x 30 + 5 mm each side (position is an estimate)
    c -= adapter_pocket()
    c -= liner_cuts(mics=False) ^ box(-400, 400, -400, 400, Z_FLANGE1, 100)        # openings in the skirt only, skin left whole
    _ey0, _ey1 = AD_Y0 + 8 - STATIK_PLUG_L - 12, AD_Y0 + 8 - STATIK_PLUG_L + 1
    c -= box(CW / 2 - SKIRT_T - 1, CW / 2 + 1, _ey0, _ey1, Z_FLANGE1, 100)   # cable exit full height (no sliver over it)
    c -= box(CW / 2 - SKIRT_T - 1, CW / 2 + 1, 15.0, 21.0, Z_FLANGE1, 100)   # no 3 mm stub left between the right-side openings
    # rear camera window (user 2026-11-13): open right through, no rib cage across it; a rim round it takes the
    # place of the ribs and stands on the wall side like they did
    cw = camera_window_2d()
    c += (cw.offset(2.4, JoinType.Round, circular_segments=24) - cw).extrude(Z_FLANGE1 - 1.4 - Z_CAR_BACK).translate([0, 0, Z_CAR_BACK])
    c -= cw.extrude(60).translate([0, 0, -30])
    c -= button_bay()
    return c

# ---- v5 clip interface (2026-11-09): solid corner lugs instead of thin ears.
# Each lug is a block on the carrier's outer wall, wall to near the frame back, with a slot cut in from the
# outside. The clip's arm slides into the slot; the slot roof is held on three sides (no cantilever tab).
LUG_HW = 14.0                     # ear half-width (x)
EARS_TOP_X = (-86.0, -50.0, 50.0, 130.0)   # top-left ear moved in (2026-11-13): leaves the volume-button window open from behind
EARS_X = (-130.0, -50.0, 50.0, 130.0)   # 4 ears per long side = 8 (user 2026-11-12: more than 4)
LUG_Y1 = 120.0                    # lug outer face |y|
SLOT_HW = 13.5                    # slot half-width (arm 26 wide + 0.5 each side)
SLOT_Z0, SLOT_Z1 = 2.5, 7.0       # slot floor / roof
ARM_Z0, ARM_Z1 = 2.5, 5.5         # rigid arm, 3 thick
FOAM_T = 1.5                      # adhesive EVA/neoprene pad on the arm (free thickness); squeezed by the measured fit
Z_LUG1 = None                     # set below (frame back - 0.3)

def _lug_z1():
    return Z_FR_BACK - 0.15      # ears 0.15 shy: the screws pull the liner firmly onto the mat before the ears bottom on the wood

# v8 (2026-11-12, rabbet measured 12.14): the frame back is only ~6 mm off the wall, so the lugs become solid
# EARS that run from the carrier out under the ring and onto the frame's back flat, and are screwed straight
# into the teak. No clips. The ear is wall-to-frame-back solid, so it prints on the bed.
EAR_Y1 = FR_OUT[1] / 2 - 1.5                 # ear end, 0.5 inside the frame's outer edge
EAR_SCREW_Y = MAT_H / 2 + 4.0                # screw in the 9 mm back flat
def lugs():
    out = []
    for sy in (-1, 1):
        for x in (EARS_TOP_X if sy > 0 else EARS_X):
            y0, y1 = sorted((sy * (CH / 2 - SKIRT_T), sy * EAR_Y1))
            out.append(box(x - LUG_HW, x + LUG_HW, y0, y1, Z_CAR_BACK, _lug_z1()))
    return Manifold.batch_boolean(out, M.OpType.Add)

def lug_slots():
    """Screw holes: #4 flat-head wood screw, countersunk from the wall side."""
    out = []
    for sy in (-1, 1):
        for x in (EARS_TOP_X if sy > 0 else EARS_X):
            y = sy * EAR_SCREW_Y
            out.append(cyl(1.6, Z_CAR_BACK - 1, _lug_z1() + 1, x, y))
            out.append(Manifold.cylinder(1.6, 3.0, 1.6, 24).translate([x, y, Z_CAR_BACK - 0.01]))
    return Manifold.batch_boolean(out, M.OpType.Add)

def frame_clip(sx, sy):
    """Rigid clip: block screwed to the frame back + a short arm that slides into the lug slot.
    The arm tip bears on the slot's inner end (carries the frame's weight on top clips, stops lift on bottom ones);
    a foam pad on the arm presses the slot roof (module -> liner -> mat -> frame lip)."""
    x = sx * EAR_X
    yb0, yb1 = MAT_H / 2 + 0.4, FR_OUT[1] / 2 - 0.4
    ya = CH / 2 + 0.3                                         # arm tip, 0.3 off the slot end
    arm = box(x - 13, x + 13, ya, LUG_Y1 + 0.6, ARM_Z0, ARM_Z1)
    blk = box(x - 13, x + 13, LUG_Y1 + 0.6, yb1, ARM_Z0, Z_FR_BACK)
    cl = arm + blk
    cl -= box(x - 14, x + 14, LUG_Y1 + 0.6 + 4, yb0, ARM_Z1 + 2.0, Z_FR_BACK + 1)   # lighten over the rabbet, keep a 2+3 mm spine
    yh = (yb0 + yb1) / 2
    cl -= cyl(1.85, ARM_Z0 - 1, Z_FR_BACK + 1, x, yh)
    cl -= Manifold.cylinder(2.7, 4.4, 1.85, 24).translate([x, yh, ARM_Z0 - 0.01])
    if sy < 0:
        cl = cl.mirror([0, 1, 0])
    return cl

def foam_pads():
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * EAR_X
            y0, y1 = sorted((sy * (CH / 2 + 1.5), sy * (LUG_Y1 - 0.5)))
            out.append(box(x - 12, x + 12, y0, y1, ARM_Z1, SLOT_Z1))
    return Manifold.batch_boolean(out, M.OpType.Add)

def frame_clips():
    return Manifold.batch_boolean([frame_clip(sx, sy) for sx in (-1, 1) for sy in (-1, 1)], M.OpType.Add)

def backer():
    b = box(-FR_OUT[0] / 2 + 2, FR_OUT[0] / 2 - 2, -FR_OUT[1] / 2 + 2, FR_OUT[1] / 2 - 2, Z_BACKER0, Z_BACKER1)
    b -= box(-316 / 2 - 0.5, 316 / 2 + 0.5, -212 / 2 - 0.5, 212 / 2 + 0.5, Z_BACKER0 - 1, Z_BACKER1 + 1)
    for x in (-150, 0, 150):
        for y in (-108, 108):
            b -= cyl(1.4, Z_BACKER0 - 1, Z_BACKER1 + 1, x, y)
    b -= box(-316 / 2 + 18, -316 / 2 + 25, -FR_OUT[1] / 2 + 20, -100, Z_BACKER0 - 1, Z_BACKER1 + 1)  # cable slot
    for x in (-205, 205):
        for y in (-150, 0, 150):
            b -= cyl(1.85, Z_BACKER0 - 1, Z_BACKER1 + 1, x, y)
    return b

# ---- pen dock (on the frame's right side)
PEN_L, PEN_D = 158.0, 9.13
PEN_X = FR_OUT[0] / 2 + 6.0 + PEN_D / 2      # pen axis x
PEN_Z = Z_FR_BACK + 7.0                       # = rail centre (rail 14 wide, flush with the frame back)
CUP_H = 52.0
PEN_DOCK_Y = -3.2                             # dock height is free again (cable loops up to it); back to the original spot
CUP_Y0 = PEN_DOCK_Y - 3 - (PEN_L - 14.0)
PORT_FROM_TOP = 14.0

def pen(lift=0.0):
    y0 = CUP_Y0 + 3 + lift
    body = cyl_y(PEN_D / 2, y0 + 12, y0 + PEN_L - 4, PEN_X, PEN_Z)
    tip = Manifold.cylinder(12, 0.8, PEN_D / 2, 24).rotate([-90, 0, 0]).translate([PEN_X, y0, PEN_Z])
    cap = Manifold.sphere(PEN_D / 2, 24).scale([1, 0.9, 1]).translate([PEN_X, y0 + PEN_L - 4, PEN_Z])
    p = body + tip + cap
    # flat (magnet side) faces the frame (-X)
    p -= box(PEN_X - PEN_D / 2 - 1, PEN_X - PEN_D / 2 + 0.8, y0 + 14, y0 + PEN_L - 8, PEN_Z - 5, PEN_Z + 5)
    return p, y0

def mag_tip(lift=0.0):
    y0 = CUP_Y0 + 3 + lift
    yp = y0 + PEN_L - PORT_FROM_TOP
    return box(PEN_X - PEN_D / 2 - 1.8, PEN_X - PEN_D / 2 + 0.8, yp - 4.5, yp + 4.5, PEN_Z - 2, PEN_Z + 2)

def pen_cup():
    r_in, r_out = PEN_D / 2 + 1.0, PEN_D / 2 + 3.0
    cup = Manifold.cylinder(CUP_H, r_out, r_out + 1.5, 32).rotate([-90, 0, 0]).translate([PEN_X, CUP_Y0, PEN_Z])
    cup -= Manifold.cylinder(CUP_H, r_in, r_in + 1.2, 32).rotate([-90, 0, 0]).translate([PEN_X, CUP_Y0 + 3, PEN_Z])
    # mount web to the frame side
    web = box(FR_OUT[0] / 2, PEN_X, CUP_Y0, CUP_Y0 + CUP_H, PEN_Z - 4, PEN_Z + 4)
    web -= Manifold.cylinder(CUP_H, r_in, r_in + 1.2, 32).rotate([-90, 0, 0]).translate([PEN_X, CUP_Y0 + 3, PEN_Z])
    return cup + web

def dock_pad():
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    pad = box(FR_OUT[0] / 2, PEN_X - PEN_D / 2 - 1.8, yp - 14, yp + 14, PEN_Z - 7, PEN_Z + 7)
    # rounded look: chamfer via hull with a smaller face
    pad = Manifold.hull(pad + box(FR_OUT[0] / 2, FR_OUT[0] / 2 + 0.5, yp - 18, yp + 18, PEN_Z - 9, PEN_Z + 9))
    pad -= Manifold.cylinder(20, STATIK_HEAD_D / 2 + 0.3, STATIK_HEAD_D / 2 + 0.3, 32).rotate([0, 90, 0]).translate([FR_OUT[0] / 2 - 5, yp, PEN_Z])
    return pad

RAIL_W = 14.0                                           # bore 10.2 + ~1.9 mm walls
RAIL_Z0, RAIL_Z1 = Z_FR_BACK, Z_FR_BACK + RAIL_W        # flush with the frame back, on the 1" flat side
RAIL_R = 3.0                                            # round-over on the outer long edges
MAG_MID_Y = ((CUP_Y0 + CUP_H) + (CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP)) / 2      # middle of the spine, between cup and head
MAG_TOP_Y = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP + 12.5                           # spare pocket near the top
def _rail_block(x0, depth, y0, y1, r):
    """Straight profile: flat sides square off the glue face, round-over on the two outer long edges."""
    r = min(r, depth - 0.5, (RAIL_Z1 - RAIL_Z0) / 2)
    core = box(x0, x0 + depth - r, y0, y1, RAIL_Z0, RAIL_Z1)
    e1 = cyl_y(r, y0, y1, x0 + depth - r, RAIL_Z0 + r, 32)
    e2 = cyl_y(r, y0, y1, x0 + depth - r, RAIL_Z1 - r, 32)
    return Manifold.hull(core + e1 + e2) ^ box(x0, x0 + depth, y0, y1, RAIL_Z0, RAIL_Z1)

def pen_rail():
    """One-piece cup + dock pad, glued to the frame's right side. Same straight profile all the way: the cup is just
    a deeper section of the rail (no taper, no flare). Prints glue face down; overhangs <= 45 deg."""
    x0 = FR_OUT[0] / 2                                   # glue face
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    x_pad = PEN_X - PEN_D / 2 - 1.8                      # pad face = magnetic face plane
    y_top = yp + 20
    rb = PEN_D / 2 + 0.55                                # bore radius
    zc = (RAIL_Z0 + RAIL_Z1) / 2
    cup_d = (PEN_X + rb * 1.414 + 1.4) - x0              # 1.4 mm over the bore's 45 deg peak
    spine = _rail_block(x0, x_pad - x0, CUP_Y0, y_top, 1.5)           # thin part: small round-over so the head face stays on the flat
    cup = _rail_block(x0, cup_d, CUP_Y0, CUP_Y0 + CUP_H, RAIL_R)
    r = spine + cup
    y0p = CUP_Y0 + 3                                     # where the pen's nib would sit
    bore = Manifold.cylinder(CUP_H - 12, rb, rb, 48).rotate([-90, 0, 0]).translate([PEN_X, y0p + 12, zc])
    peak = Manifold.hull(bore + box(PEN_X + rb * 1.41 - 0.01, PEN_X + rb * 1.41, y0p + 12, CUP_Y0 + CUP_H + 1, zc - 0.01, zc + 0.01))
    # cone seat = the pen's taper + 0.2 mm, so the pen rests on its taper; nib relief so the tip never carries weight
    r0, r1 = 0.8 + 0.2, PEN_D / 2 + 0.2
    seat = Manifold.cylinder(12.01, r0, r1, 48).rotate([-90, 0, 0]).translate([PEN_X, y0p, zc])
    seat = Manifold.hull(seat + Manifold.hull_points([[PEN_X + r0 * 1.41, y0p, zc], [PEN_X + r1 * 1.41, y0p + 12.01, zc]]))
    relief = Manifold.cylinder(4.0, 1.6, 1.6, 24).rotate([-90, 0, 0]).translate([PEN_X, y0p - 1.5, zc])
    relief = Manifold.hull(relief + box(PEN_X + 2.25, PEN_X + 2.26, y0p - 1.5, y0p + 2.5, zc - 0.01, zc + 0.01))
    ym = CUP_Y0 + CUP_H - 1.99
    mouth = Manifold.cylinder(2, rb, rb + 1.0, 48).rotate([-90, 0, 0]).translate([PEN_X, ym, zc])
    r -= peak + seat + relief + mouth
    # head through-hole (dowel into the frame)
    r -= Manifold.cylinder(20, STATIK_HEAD_D / 2 + 0.3, STATIK_HEAD_D / 2 + 0.3, 32).rotate([0, 90, 0]).translate([x0 - 5, yp, PEN_Z])
    r -= Manifold.cylinder(2.71, 3.15, 3.15, 32).rotate([0, 90, 0]).translate([x_pad - 2.7, MAG_MID_Y, PEN_Z])
    r -= Manifold.cylinder(2.71, 3.15, 3.15, 32).rotate([0, 90, 0]).translate([x_pad - 0.6 - 2.71, MAG_TOP_Y, PEN_Z])
    return r

def pad_magnets_rail():
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    x_pad = PEN_X - PEN_D / 2 - 1.8
    return Manifold.cylinder(2.6, 3.0, 3.0, 24).rotate([0, 90, 0]).translate([x_pad - 2.65, MAG_MID_Y, PEN_Z])   # only the middle one fitted

def dock_socket():
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    return box(PEN_X - PEN_D / 2 - 2.0, PEN_X - PEN_D / 2 - 1.8, yp - 5, yp + 5, PEN_Z - 2.5, PEN_Z + 2.5)

# ---- cables (simple tubes)
CABLE_PTS = {}
def tube(points, r=1.8):
    segs = []
    for a, b in zip(points[:-1], points[1:]):
        segs.append(Manifold.hull(Manifold.sphere(r, 12).translate(a) + Manifold.sphere(r, 12).translate(b)))
    return Manifold.batch_boolean(segs, M.OpType.Add)

def charger_cable():
    """Charger -> adapter PD input (outer face) -> out into the rabbet space -> down -> across the bottom -> behind the frame, bottom left."""
    z = AD_Z + 2.5                  # front layer of the rabbet space (pen cable runs behind, at Z ~13)
    x1 = AD_X0 + AD_W + 22
    xc = TAB_W / 2 + 33.0           # right-angle plug: 38-39 mm out from the tablet edge (measured), cable ~5 in from that
    yg = -(CH / 2 + ((MAT_H - 0.6) / 2 - FILL_BAND)) / 2      # middle of the gap between the carrier's bottom wall and the ring
    pts = [(xc, AD_PD_Y, AD_Z), (xc, yg + 8, 12.6), (xc - 8, yg, 12.6), (SOCK_X + 8, yg, 12.6), (SOCK_X, yg - 6, 12.6), (SOCK_X, -160.0, 12.6)]
    CABLE_PTS['charger'] = pts
    return tube(pts, 2.2) + pd_plug()

def pen_cable():
    """Statik 3 ft: USB-A down out of the adapter, spare cable looped along the bottom band, up the gap between the
    module and the frame's right side, then out to the head's boot, which comes out of the frame's back face."""
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    z = 11.0 + DZ
    xa = AD_X0 + AD_W / 2
    y_plug_end = AD_Y0 + 8 - STATIK_PLUG_L
    xr = 200.0
    xb = PEN_X - PEN_D / 2 - 1.8 - HEAD_BARREL + 1
    zf = 12.3                       # loop runs in channels on the back of the rabbet filler                     # loop in the front layer of the rabbet, clear of the frame clips
    pts = [(xa, y_plug_end, AD_Z), (xa + 4, y_plug_end - 7, 13 + DZ), (172, y_plug_end - 12, 13 + DZ), (172, -116, 13 + DZ), (162, -126, zf),
           (40, -126, zf), (30, -131, zf), (40, -136, zf), (185, -136, zf), (xr, -126, z),     # spare loop along the bottom
           (xr, yp - 20, z), (xb - 6, yp - 6, Z_FR_BACK - 9), (xb, yp, Z_FR_BACK - 7)]
    CABLE_PTS['pen'] = pts
    return tube(pts, 1.6) + usba_plug()

STATIK_HEAD_D = 8.0      # magnetic head diameter, measured 2026-11-13
HEAD_BARREL = 10.0       # magnetic face to swivel, placeholder until measured
def frame_hole():
    """Drill the head bore through the side at PEN_Z, then two saw kerfs from the back face + chisel -> U-slot.
    Lets the head drop in from behind with its cable swivelled 90 deg toward the wall. Hidden: rail covers it outside,
    moulding face covers it in front."""
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    rr = STATIK_HEAD_D / 2 + 0.5
    hole = Manifold.cylinder(14, rr, rr, 32).rotate([0, 90, 0]).translate([MAT_W / 2 - 2, yp, PEN_Z])
    slot = box(MAT_W / 2 - 2, MAT_W / 2 + 12, yp - rr, yp + rr, Z_FR_BACK - 1, PEN_Z)
    return hole + slot

def statik_head():
    """Straight barrel through the wall (face flush with the pad face), swivel turned 90 deg, cable boot toward the wall."""
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    x_face = PEN_X - PEN_D / 2 - 1.8
    xs = x_face - HEAD_BARREL
    barrel = Manifold.cylinder(HEAD_BARREL, STATIK_HEAD_D / 2, STATIK_HEAD_D / 2, 32).rotate([0, 90, 0]).translate([xs, yp, PEN_Z])
    knuckle = Manifold.sphere(STATIK_HEAD_D / 2 - 0.5, 24).translate([xs + 1, yp, PEN_Z])
    boot = Manifold.cylinder(PEN_Z - (Z_FR_BACK - 6), 4.0, 4.0, 24).translate([xs + 1, yp, Z_FR_BACK - 6])
    return barrel + knuckle + boot

def pad_magnets():
    """6 x 2.6 mm magnets (on hand) in the dock pad, above and below the socket, axis along x."""
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    out = []
    for dy in (-11, 11):
        out.append(Manifold.cylinder(2.6, 3.0, 3.0, 24).rotate([0, 90, 0]).translate([PEN_X - PEN_D / 2 - 1.8 - 2.6 - 0.6, yp + dy, PEN_Z]))
    return Manifold.batch_boolean(out, M.OpType.Add)

def pen_magnets(lift=0.0):
    """Approximate positions of the pen's own magnets along its flat (not published by Lenovo)."""
    y0 = CUP_Y0 + 3 + lift
    out = []
    for yy in (40, 75, 110):
        out.append(box(PEN_X - PEN_D / 2 + 1.0, PEN_X - PEN_D / 2 + 3.5, y0 + yy - 6, y0 + yy + 6, PEN_Z - 2, PEN_Z + 2))
    return Manifold.batch_boolean(out, M.OpType.Add)

def wall(w=900, h=700):
    return box(-w / 2, w / 2, -h / 2 - 50, h / 2 - 50, -6, 0)

SCREW_L = 19.0   # #6 x 3/4" flat head wood screw
def frame_screws():
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * EAR_X
            yh = sy * (MAT_H / 2 + 0.4 + FR_OUT[1] / 2 - 0.4) / 2
            z0 = ARM_Z0
            head = Manifold.cylinder(2.6, 4.2, 1.75, 24).translate([x, yh, z0 + 0.1])
            shank = Manifold.cylinder(SCREW_L - 2.6, 1.75, 1.2, 16).translate([x, yh, z0 + 2.7])
            out.append(head + shank)
    return Manifold.batch_boolean(out, M.OpType.Add)

# ---- rabbet filler (2026-11-09): the frame expects glass + mat + photo + backer in the rabbet. Without the glass,
# the outer part of the mat (beyond the liner) has nothing behind it and can bow back off the lip.
# A printed band fills the rabbet behind the mat's outer edge, flush with the frame back; the four frame-clip
# blocks sit over it. 4 L-shaped pieces (fit the bed), joints at the middles. Cable channels on its back.
FILL_BAND = 20.0

def rabbet_filler():
    ow, oh = MAT_W - 0.6, MAT_H - 0.6
    iw, ih = ow - 2 * FILL_BAND, oh - 2 * FILL_BAND
    z0, z1 = Z_FR_BACK, Z_LIN1                      # frame back to the mat's back (6.5 with an 8 mm rabbet)
    f = box(-ow / 2, ow / 2, -oh / 2, oh / 2, z0, z1) - box(-iw / 2, iw / 2, -ih / 2, ih / 2, z0 - 1, z1 + 1)
    # joints at the middles -> 4 L pieces
    f -= box(-0.25, 0.25, -oh, oh, z0 - 1, z1 + 1)
    f -= box(-ow, ow, -0.25, 0.25, z0 - 1, z1 + 1)
    return f

def filler_cut():
    """Channels on the filler's back for the cables (open to the back), + relief round the Statik head."""
    charger_cable(); pen_cable()
    segs = []
    for key, r in (('charger', 1.8), ('pen', 1.6)):
        pts = CABLE_PTS[key]
        for a, b in zip(pts[:-1], pts[1:]):
            ends = []
            for p in (a, b):
                ends += [Manifold.sphere(r + 0.5, 12).translate(p), Manifold.sphere(r + 0.5, 12).translate([p[0], p[1], Z_FR_BACK - 3])]
            segs.append(Manifold.hull(Manifold.batch_boolean(ends, M.OpType.Add)))
    yp = CUP_Y0 + 3 + PEN_L - PORT_FROM_TOP
    segs.append(Manifold.cylinder(30, STATIK_HEAD_D / 2 + 1.0, STATIK_HEAD_D / 2 + 1.0, 32).rotate([0, 90, 0]).translate([MAT_W / 2 - 25, yp, PEN_Z]))
    return Manifold.batch_boolean(segs, M.OpType.Add)

def filler():
    return rabbet_filler() - filler_cut()

# ======================================================================================
# v7 proposal (2026-11-12): filler RING with dovetail joints + TOE-CLAMP frame clips
# ======================================================================================
DT_NECK, DT_FLARE, DT_LEN, DT_CLR = 8.0, 12.0, 6.0, 0.25

RING_SHY = 0.3      # ring back sits 0.3 below the frame back (felt shim takes up the rest)
RING_J = {'top': 0.0, 'bottom': 0.0, 'left': 0.0, 'right': 46.0}     # right joint moved up: its 20 mm tongue (26..46) stays clear of the pen-charger tunnel (10.3..21.7)
SOCK_X = -180.0      # USB-C socket position along the bottom rail (under the LEFT side gap: the outlet is to the left)
HEAD_Y = 16.0        # lowered 2026-11-13 (user: cup near the bottom); 14 is the lowest that clears the right-angle PD plug. was 40.0        # Statik head height on the frame's right side (pen port level)
BAY_Y = (-30.0, 60.0)  # service bay in the ring's right rail for the Statik body + cable    # joint positions (mid-sides)

LAP_L = 20.0
def _tail(axis, sign, pos, at=0.0):
    """In-plane LAP tongue (2D) at a joint (replaces the dovetail, 2026-11-12: fit must not depend on print
    tolerance). The owner piece keeps the OUTER half of the band for LAP_L past the joint line; the other piece
    keeps the inner half. Prints flat, no overhang; glued; the frame rabbet lines the pieces up."""
    o = 1 if pos > 0 else -1
    if axis == 'x':
        x0, x1 = sorted((at - sign * 0.6, at + sign * LAP_L)); y0, y1 = sorted((pos, pos + o * 30))
    else:
        y0, y1 = sorted((at - sign * 0.6, at + sign * LAP_L)); x0, x1 = sorted((pos, pos + o * 30))
    return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])

def ring_locators():
    """Fingers on the ring's inner edge that centre the tablet module in the frame (0.3 clear of the carrier skirt).
    Top/bottom: 2 short bosses each (x = +-30). Left: one finger at y = -10. Right: one at y = 60."""
    ih = (MAT_H - 0.6) / 2 - FILL_BAND; iw = (MAT_W - 0.6) / 2 - FILL_BAND
    z0, z1 = Z_FR_BACK + RING_SHY, 14.0
    out = []
    for x in (-30.0, 30.0):
        out.append(box(x - 5, x + 5, CH / 2 + 0.3, ih + 0.5, z0, z1))
        out.append(box(x - 5, x + 5, -ih - 0.5, -CH / 2 - 0.3, z0, 9.8))      # low: the charger cable passes in front of these
    out.append(box(-iw - 0.5, -CW / 2 - 0.3, -15, -5, z0, 9.8))          # below the left joint, on solid skirt between the speakers
    out.append(box(CW / 2 + 0.3, iw + 0.5, 55, 65, z0, z1))
    return Manifold.batch_boolean(out, M.OpType.Add)

def ring_cable_cut():
    """Charger-cable channel only. The pen/Statik routing is being redesigned (no pen rail; head in the frame
    side, pen cup below it), so its channel is left out until that is drawn."""
    charger_cable()
    segs = []
    pts = CABLE_PTS['charger']
    for a, b in zip(pts[:-1], pts[1:]):
        ends = []
        for p in (a, b):
            ends += [Manifold.sphere(2.3, 12).translate(p), Manifold.sphere(2.3, 12).translate([p[0], p[1], Z_FR_BACK - 3])]
        segs.append(Manifold.hull(Manifold.batch_boolean(ends, M.OpType.Add)))
    return Manifold.batch_boolean(segs, M.OpType.Add)

def ring_pieces():
    """The rabbet filler as 4 L pieces that dovetail into one ring (glue once). Returns {(sx,sy): Manifold}."""
    ow, oh = MAT_W - 0.6, MAT_H - 0.6
    iw, ih = ow - 2 * FILL_BAND, oh - 2 * FILL_BAND
    zb = Z_FR_BACK + RING_SHY
    ring = (box(-ow / 2, ow / 2, -oh / 2, oh / 2, zb, Z_LIN1)
            - box(-iw / 2, iw / 2, -ih / 2, ih / 2, zb - 1, Z_LIN1 + 1))
    # USB-C socket tunnel (user 2026-11-12): a short male-female extension ends here, so the wall cord unplugs at the frame
    ring -= box(SOCK_X - 10.0, SOCK_X + 10.0, -oh / 2 - 1, -ih / 2 + 1, zb - 1, Z_LIN1 - 1.0)   # 20 wide (user: room to fit any female end; print solid so it can be trimmed)
    # low lip on the front that fits round the mat's edge and centres it
    ring += (box(-ow / 2, ow / 2, -oh / 2, oh / 2, Z_LIN1 - 0.01, Z_LIN1 + 0.8)
             - box(-MATB[0] / 2 - 0.4, MATB[0] / 2 + 0.4, -MATB[1] / 2 - 0.3, MATB[1] / 2 + 0.3, Z_LIN1 - 1, Z_LIN1 + 2))
    ring += ring_locators()
    # volume-button reliefs (2026-11-13): two sloped pockets in the back of the top rail so a flat stick, slid in from
    # behind along the frame back, reaches each end of the volume rocker. 12 wide each (bridge 12), 4 mm pier between.
    for xc in (tab_x(20.0), tab_x(36.0)):
        pts = [[x, y, z] for x in (xc - 6.0, xc + 6.0) for (y, z) in ((ih / 2 - 1, zb - 1), (ih / 2 - 1, 11.6), (oh / 2 + 1, zb - 0.2), (oh / 2 + 1, zb - 1))]
        ring -= Manifold.hull_points(pts)
    # pen-charger tunnel (user 2026-11-12: the Statik head goes STRAIGHT in, no 90 deg bend, no service bay):
    # a slot through the right rail in line with the pen's charging port, open at the back, 1 mm roof under the mat
    ring -= box(ow / 2 - FILL_BAND - 1, ow / 2 + 1, HEAD_Y - 5.7, HEAD_Y + 5.7, zb - 1, Z_LIN1 - 1.0)      # head 8.0 dia, barrel 10.08 dia (measured 2026-11-13): 11.4 wide, open at the back
    yb = oh / 2 - FILL_BAND / 2
    xb = ow / 2 - FILL_BAND / 2
    J = RING_J
    def rect(x0, x1, y0, y1):
        return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])
    B = 400
    # quadrant masks: the vertical split is x = J['top'] in the top half and x = J['bottom'] in the bottom half;
    # the horizontal split is y = J['left'] on the left and y = J['right'] on the right
    quad = {(-1, 1): rect(-B, J['top'], J['left'], B) ^ rect(-B, 0, J['left'], B) + rect(-B, J['top'], 0 if J['left'] < 0 else J['left'], B) ^ rect(-B, J['top'], J['left'], B),
            }
    quad = {
        (-1, 1): rect(-B, J['top'], J['left'], B) ^ rect(-B, B, 0, B) + (rect(-B, 0, J['left'], 0) if J['left'] < 0 else CrossSection()),
        (1, 1): rect(J['top'], B, J['right'], B),
        (-1, -1): rect(-B, J['bottom'], -B, J['left']),
        (1, -1): rect(J['bottom'], B, -B, J['right']),
    }
    # (assumes J['top'] == J['bottom'] and J['left'] == 0; the right joint may move)
    quad[(-1, 1)] = rect(-B, J['top'], J['left'], B)
    SL = 1.0
    joints = [
        ((-1, 1), (1, 1), _tail('x', 1, yb, J['top'])),       # top rail: left piece's tail into the right piece
        ((1, -1), (-1, -1), _tail('x', -1, -yb, J['bottom'])),  # bottom rail: right piece's tail into the left piece
        ((-1, -1), (-1, 1), _tail('y', 1, -xb, J['left'])),     # left side: lower piece's tail up
        ((1, 1), (1, -1), _tail('y', -1, xb, J['right'])),      # right side: upper piece's tail down
    ]
    slides = [(SL, 0), (-SL, 0), (0, SL), (0, -SL)]
    gaps = [rect(J['top'], J['top'] + SL, 0, B), rect(J['bottom'] - SL, J['bottom'], -B, 0), rect(-B, 0, J['left'], J['left'] + SL), rect(0, B, J['right'] - SL, J['right'])]
    for (own, oth, t), sl, gapm in zip(joints, slides, gaps):
        sl = list(sl)
        quad[own] = quad[own] + t
        quad[oth] = quad[oth] - t.offset(DT_CLR, JoinType.Miter) - t.translate(sl) - gapm
    z0, z1 = Z_FR_BACK - 1, Z_LIN1 + 2
    out = {}
    for k, cs in quad.items():
        parts = (ring ^ cs.extrude(z1 - z0).translate([0, 0, z0])).decompose()
        out[k] = max(parts, key=lambda p: p.volume())      # drop slivers left by the cable channels
    return out

# toe-clamp clip: rigid, heel on the frame back at the outer edge, 0.8 clearance under the body,
# screw near the heel; tightening tips the clip so the toe presses the lug roof (module -> mat -> frame lip)
TOE_GAP = 0.3            # nominal toe-to-roof gap before tightening
CLIP_CLR = 0.8           # body clearance to the frame back / ring
HEEL_W = 2.0

def toe_clip(sx, sy):
    x = sx * EAR_X
    yb1 = FR_OUT[1] / 2 - 0.4                     # outer end, 0.4 inside the frame edge
    ya = CH / 2 + 0.3                             # toe tip, 0.3 off the slot end (bears on it for weight)
    zt = SLOT_Z1 - TOE_GAP                        # toe top
    arm = box(x - 13, x + 13, ya, LUG_Y1 + 0.6, ARM_Z0, zt)
    body = box(x - 13, x + 13, LUG_Y1 + 0.6, yb1, ARM_Z0, Z_FR_BACK - CLIP_CLR)
    heel = box(x - 13, x + 13, yb1 - HEEL_W, yb1, Z_FR_BACK - CLIP_CLR - 0.01, Z_FR_BACK)
    cl = arm + body + heel
    yh = (MAT_H / 2 + 0.4 + yb1) / 2               # screw in the middle of the frame's back face
    cl -= cyl(1.85, ARM_Z0 - 1, Z_FR_BACK + 1, x, yh)
    cl -= Manifold.cylinder(2.7, 4.4, 1.85, 24).translate([x, yh, ARM_Z0 - 0.01])
    if sy < 0:
        cl = cl.mirror([0, 1, 0])
    return cl

def toe_clips():
    return Manifold.batch_boolean([toe_clip(sx, sy) for sx in (-1, 1) for sy in (-1, 1)], M.OpType.Add)


# ---- pen cup (v8, 2026-11-12): glued to the frame's right side below the Statik head. Local frame = print frame:
# x = out from the frame side (glue face at x = 0), y = along the frame depth, z = up. Prints upright, no supports.
CUP_H, CUP_SEAT, CUP_BORE = 25.0, 9.0, 10.2
CUP_WALL = 1.2       # closed wall on the frame (wood) side
def pen_cup_v8():
    """v8b (user 2026-11-12): closed on the frame side, round holes (no slot), no flange.
    Glue face = the whole flat back (x = 0)."""
    r = CUP_BORE / 2
    cx = CUP_WALL + r
    body = Manifold.hull(box(0, 1, -8.5, 8.5, 0, CUP_H) + cyl(3.0, 0, CUP_H, cx + r, -5.5) + cyl(3.0, 0, CUP_H, cx + r, 5.5))
    cut = cyl(3.0, -1, CUP_SEAT + 0.01, cx, 0)                                              # drain / nib clearance, right through
    cut += Manifold.cylinder(6.0, 3.0, r, 48).translate([cx, 0, CUP_SEAT])                  # cone seat (pen rests on its taper)
    cut += cyl(r, CUP_SEAT + 6.0 - 0.01, CUP_H + 1, cx, 0, 48)                              # straight bore
    cut += Manifold.cylinder(0.8, r, r + 0.5, 48).translate([cx, 0, CUP_H - 0.79])          # small flare at the mouth
    return body - cut

PEN_AXIS_Z = Z_FR_BACK + 4.73    # pen / charger axis from the wall. Statik barrel measured 10.08 dia (2026-11-13): 4.73 in front of the frame's back;
                     # clears the ring tunnel's roof (Z_LIN1 - 1.0 = 16.9) by 0.36

def pen_cup_placed():
    """Cup on the frame's right side, pen port level with HEAD_Y (seat ring is 128.5 + 7.7 below the port)."""
    y0 = HEAD_Y - 128.5 - 7.7 - CUP_SEAT
    return pen_cup_v8().transform([[1, 0, 0, FR_OUT[0] / 2], [0, 0, 1, y0], [0, -1, 0, PEN_AXIS_Z]])
