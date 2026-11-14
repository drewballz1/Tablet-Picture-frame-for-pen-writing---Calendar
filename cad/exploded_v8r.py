"""Exploded view of the v8r nook mount (all parts, Z-exploded)."""
import sys; sys.path.insert(0, '.')
import model as m
from render import Scene
m.frame_hole = lambda: m.Manifold()
ring = m.ring_pieces()
RING = m.Manifold.batch_boolean(list(ring.values()), m.M.OpType.Add)
HY = m.HEAD_Y; fx = m.FR_OUT[0] / 2
FR = m.frame() - m.box(fx - 10, fx + 1, HY - 5.5, HY + 5.5, -1, 16.1) \
     - m.box(m.SOCK_X - 8, m.SOCK_X + 8, -m.FR_OUT[1] / 2 - 1, -138, -1, 16.1)
px = fx + m.CUP_WALL + m.CUP_BORE / 2; pz = m.PEN_AXIS_Z
cy = lambda r0, r1, y0, y1: m.Manifold.cylinder(y1 - y0, r0, r1, 32).rotate([-90, 0, 0]).translate([px, y0, pz])
top = HY + 14.0
PEN = cy(0.8, 2.0, top - 158, top - 143) + cy(2.0, 4.57, top - 143, top - 128.5) + cy(4.57, 4.57, top - 128.5, top - 3) + m.Manifold.sphere(4.57, 24).translate([px, top - 3, pz])
HEAD = m.Manifold.cylinder(24, 4.0, 4.0, 32).rotate([0, 90, 0]).translate([px - 4.57 - 24, HY, pz])
SCREWS = m.Manifold.batch_boolean(
    [m.cyl(3.0, -1.5, 0.4, ex, sy * m.EAR_SCREW_Y) + m.cyl(1.5, 0.4, 19.0, ex, sy * m.EAR_SCREW_Y)
     for ex in m.EARS_X for sy in (-1, 1)], m.M.OpType.Add)

OFF = {'mount': -75, 'screws': -38, 'carrier': 0, 'tablet': 52, 'felt': 82, 'liner': 108, 'ring': 150,
       'mat': 196, 'frame': 232}
COL = {'mount': (60, 62, 68), 'screws': (214, 90, 40), 'carrier': (92, 94, 100), 'tablet': (34, 36, 42),
       'adapter': (175, 178, 186), 'cable': (236, 236, 236), 'felt': (150, 120, 90), 'liner': (240, 238, 232),
       'ring': (70, 72, 78), 'mat': (250, 250, 246), 'frame': (176, 122, 74), 'cup': (244, 242, 238),
       'pen': (150, 154, 162), 'head': (225, 225, 228)}

def scene():
    s = Scene(); o = lambda k, dx=0, dy=0: (dx, dy, OFF[k])
    s.add(m.mount(), COL['mount'], 'mount', o('mount'))
    s.add(SCREWS, COL['screws'], 'screws', o('screws'))
    s.add(m.carrier(), COL['carrier'], 'carrier', o('carrier'))
    s.add(m.tablet_body(), COL['tablet'], 'tablet', o('tablet'))
    s.add(m.adapter(), COL['adapter'], 'tablet', o('tablet'))
    s.add(m.charger_cable(), COL['cable'], 'tablet', o('tablet'))
    s.add(m.felt_strips(), COL['felt'], 'felt', o('felt'))
    s.add(m.liner(), COL['liner'], 'liner', o('liner'))
    for k, p in ring.items():
        s.add(p, COL['ring'], 'ring', (k[0] * 6, k[1] * 6, OFF['ring']))
    s.add(HEAD, COL['head'], 'ring', o('ring'))
    s.add(m.matboard(), COL['mat'], 'mat', o('mat'))
    s.add(FR, COL['frame'], 'frame', o('frame'))
    s.add(m.pen_cup_placed(), COL['cup'], 'frame', o('frame'))
    s.add(PEN, COL['pen'], 'frame', o('frame'))
    return s

from PIL import ImageDraw, ImageFont
from render import FONT, FONTB
LEGEND = ['1  Wall mount (black)', '2  Carrier (black)', '3  Tablet + USB-C hub + cable', '4  Felt strips', '5  Liner (white ASA)',
          '6  Filler ring, 4 pieces (black)', '7  Mat', '8  Frame, pen cup (white), pen', '9  8 screws, #4 x 3/4"']
K = 1.15   # anchors below were read off a 2000 px wide preview
FRONT = {1: (1620, 780), 2: (1520, 560), 3: (1100, 720), 4: (960, 700), 5: (900, 720), 6: (1000, 420), 7: (660, 720), 8: (900, 500), 9: (1610, 1045)}
BACK = {1: (560, 930), 2: (600, 640), 3: (950, 870), 4: (1055, 900), 5: (1120, 900), 6: (1280, 1100), 7: (1340, 700), 8: (1440, 820), 9: (510, 1185)}
def badges(img, pts, title, sub):
    d = ImageDraw.Draw(img); f = ImageFont.truetype(FONTB, 30); g = ImageFont.truetype(FONT, 27)
    for n, (x, y) in pts.items():
        x, y = x * K, y * K
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(255, 255, 255), outline=(20, 20, 20), width=3)
        d.text((x, y), str(n), font=f, fill=(20, 20, 20), anchor='mm')
    y0 = 120
    for t in LEGEND:
        d.text((30, y0), t, font=g, fill=(20, 20, 20)); y0 += 38
    return img
def front(path):
    s = scene(); s.render(-48, 24, size=(2300, 1700), margin=(620, 420, 170, 90))
    s.title('Nook mount v8r: exploded, from the front', 'Numbers run wall to room. Parts 2 to 5 snap together as the tablet module; 8 screws fix the module to the frame.')
    badges(s.img, FRONT, '', '').save(path)
def back(path):
    s = scene(); s.render(138, 24, size=(2300, 1700), margin=(420, 620, 170, 90))
    s.title('Nook mount v8r: exploded, from behind', 'Same numbering. Wall side toward you.')
    badges(s.img, BACK, '', '').save(path)
if __name__ == '__main__':
    front('../images/exploded_front.png'); back('../images/exploded_back.png')
