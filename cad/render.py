"""Tiny z-buffer rasterizer + callouts for CAD-style review renders."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def mesh_arrays(man):
    m = man.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3].astype(np.float64)
    f = np.asarray(m.tri_verts).astype(np.int64)
    return v, f

def rot(az, el):
    a, e = math.radians(az), math.radians(el)
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    return Rx @ Ry

class Scene:
    def __init__(self):
        self.items = []   # (verts, faces, color, name)

    def add(self, man, color, name='', offset=(0, 0, 0)):
        v, f = mesh_arrays(man)
        v = v + np.asarray(offset, float)
        self.items.append((v, f, np.asarray(color, float), name))

    def add_mesh(self, v, f, color, name=''):
        self.items.append((np.asarray(v, float), np.asarray(f, np.int64), np.asarray(color, float), name))

    def render(self, az, el, size=(1800, 1250), ss=2, margin=(330, 330, 80, 80), bg=(250, 250, 248),
               light=(-0.4, 0.6, 0.7), fit_names=None, zoom=1.0, center=None, scale=None):
        R = rot(az, el)
        W, H = size[0] * ss, size[1] * ss
        allv = [it[0] @ R.T for it in self.items if (fit_names is None or it[3] in fit_names)]
        P = np.vstack(allv)
        lo, hi = P[:, :2].min(0), P[:, :2].max(0)
        ml, mr, mt, mb = [m * ss for m in margin]
        sc = min((W - ml - mr) / (hi[0] - lo[0]), (H - mt - mb) / (hi[1] - lo[1])) * zoom
        if scale is not None:
            sc = scale * ss          # fixed px/mm (animations)
        c = (lo + hi) / 2 if center is None else (np.asarray(center, float) @ R.T)[:2]
        ox = ml + (W - ml - mr) / 2 - c[0] * sc
        oy = mt + (H - mt - mb) / 2 + c[1] * sc
        self._proj = (R, sc, ox, oy, ss)
        zb = np.full((H, W), -np.inf)
        col = np.zeros((H, W, 3))
        pid = np.full((H, W), -1, np.int32)
        nrm = np.zeros((H, W, 3))
        L = np.asarray(light, float); L /= np.linalg.norm(L)
        for k, (v, f, color, name) in enumerate(self.items):
            pv = v @ R.T
            sx = pv[:, 0] * sc + ox
            sy = oy - pv[:, 1] * sc
            sz = pv[:, 2]
            tri = f
            a, b, cc = pv[tri[:, 0]], pv[tri[:, 1]], pv[tri[:, 2]]
            n = np.cross(b - a, cc - a)
            nl = np.linalg.norm(n, axis=1, keepdims=True); nl[nl == 0] = 1
            n = n / nl
            shade = 0.42 + 0.58 * np.clip(n @ L, 0, 1) + 0.12 * np.clip(n[:, 2], 0, 1)
            for t in range(len(tri)):
                if n[t, 2] <= 1e-6:
                    continue      # back-face cull (closed meshes)
                i0, i1, i2 = tri[t]
                xs = np.array([sx[i0], sx[i1], sx[i2]]); ys = np.array([sy[i0], sy[i1], sy[i2]])
                x0, x1 = int(max(0, math.floor(xs.min()))), int(min(W - 1, math.ceil(xs.max())))
                y0, y1 = int(max(0, math.floor(ys.min()))), int(min(H - 1, math.ceil(ys.max())))
                if x1 < x0 or y1 < y0:
                    continue
                den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
                if abs(den) < 1e-9:
                    continue
                gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
                w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
                w2 = 1 - w0 - w1
                inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
                if not inside.any():
                    continue
                z = w0 * sz[i0] + w1 * sz[i1] + w2 * sz[i2]
                sub = zb[y0:y1 + 1, x0:x1 + 1]
                upd = inside & (z > sub)
                if not upd.any():
                    continue
                sub[upd] = z[upd]
                col[y0:y1 + 1, x0:x1 + 1][upd] = np.clip(color * shade[t], 0, 255)
                pid[y0:y1 + 1, x0:x1 + 1][upd] = k
                nrm[y0:y1 + 1, x0:x1 + 1][upd] = n[t]
        img = np.empty((H, W, 3)); img[:] = bg
        m = pid >= 0
        img[m] = col[m]
        # feature edges
        edge = np.zeros((H, W), bool)
        for dy, dx in ((0, 1), (1, 0)):
            p2 = np.roll(pid, (-dy, -dx), (0, 1))
            n2 = np.roll(nrm, (-dy, -dx), (0, 1))
            z2 = np.roll(zb, (-dy, -dx), (0, 1))
            e = (pid != p2) | ((nrm * n2).sum(2) < 0.85)
            with np.errstate(invalid='ignore'):
                e |= (np.abs(zb - z2) > 1.2) & np.isfinite(zb) & np.isfinite(z2)
            e &= (pid >= 0) | (p2 >= 0)
            edge |= e
        edge = edge | np.roll(edge, 1, 0) if ss >= 3 else edge
        img[edge] = img[edge] * 0.25 + np.array([25, 25, 28]) * 0.75
        im = Image.fromarray(img.astype(np.uint8)).resize(size, Image.LANCZOS)
        self.img = im
        self.draw = ImageDraw.Draw(im)
        return im

    def p2d(self, pt):
        R, sc, ox, oy, ss = self._proj
        q = np.asarray(pt, float) @ R.T
        return ((q[0] * sc + ox) / ss, (oy - q[1] * sc) / ss)

    # ------------------------------------------------------------- annotation
    def callouts(self, items, fs=19):
        """items: list of (pt3d, text, side) side in 'L','R','T','B'. Auto-stacked per side."""
        f = ImageFont.truetype(FONT, fs)
        W, H = self.img.size
        groups = {'L': [], 'R': [], 'T': [], 'B': []}
        for pt, text, side in items:
            groups[side].append((self.p2d(pt), text))
        d = self.draw
        for side, g in groups.items():
            if not g:
                continue
            if side in 'LR':
                g.sort(key=lambda t: t[0][1])
                n = len(g)
                ys = np.linspace(110, H - 90, n + 2)[1:-1] if n > 1 else [g[0][0][1]]
                # keep near natural y but evenly spaced
                nat = [p[1] for p, _ in g]
                ys = self._spread(nat, 110, H - 70, 46 + 22 * max(t.count('\n') for _, t in g))
                for (p, text), y in zip(g, ys):
                    lines = text.split('\n')
                    tw = max(d.textlength(s, font=f) for s in lines)
                    th = len(lines) * (fs + 5)
                    x = 18 if side == 'L' else W - 18 - tw
                    bx0, by0 = x - 8, y - th / 2 - 6
                    bx1, by1 = x + tw + 8, y + th / 2 + 4
                    ax = bx1 if side == 'L' else bx0
                    d.line([(ax, y), (p[0], p[1])], fill=(40, 40, 46), width=2)
                    d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(214, 90, 40), outline=(40, 40, 46))
                    d.rounded_rectangle([bx0, by0, bx1, by1], 6, fill=(255, 255, 255), outline=(40, 40, 46), width=2)
                    for i, s in enumerate(lines):
                        d.text((x, by0 + 5 + i * (fs + 5)), s, fill=(25, 25, 30), font=f)
            else:
                g.sort(key=lambda t: t[0][0])
                nat = [p[0] for p, _ in g]
                xs = self._spread(nat, 160, W - 160, 300)
                for (p, text), x in zip(g, xs):
                    lines = text.split('\n')
                    tw = max(d.textlength(s, font=f) for s in lines)
                    th = len(lines) * (fs + 5)
                    y = 22 if side == 'T' else H - 22 - th
                    bx0, by0, bx1, by1 = x - tw / 2 - 8, y - 6, x + tw / 2 + 8, y + th + 4
                    ay = by1 if side == 'T' else by0
                    d.line([(x, ay), (p[0], p[1])], fill=(40, 40, 46), width=2)
                    d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(214, 90, 40), outline=(40, 40, 46))
                    d.rounded_rectangle([bx0, by0, bx1, by1], 6, fill=(255, 255, 255), outline=(40, 40, 46), width=2)
                    for i, s in enumerate(lines):
                        d.text((x - tw / 2, by0 + 5 + i * (fs + 5)), s, fill=(25, 25, 30), font=f)

    @staticmethod
    def _spread(nat, lo, hi, gap):
        n = len(nat)
        ys = list(np.clip(nat, lo, hi))
        for _ in range(200):
            moved = False
            for i in range(1, n):
                if ys[i] - ys[i - 1] < gap:
                    mid = (ys[i] + ys[i - 1]) / 2
                    ys[i - 1], ys[i] = mid - gap / 2, mid + gap / 2
                    moved = True
            ys = list(np.clip(ys, lo, hi))
            if not moved:
                break
        # final forward pass to guarantee spacing
        for i in range(1, n):
            ys[i] = max(ys[i], ys[i - 1] + gap)
        if n and ys[-1] > hi:
            shift = ys[-1] - hi
            ys = [y - shift for y in ys]
        return ys

    def arrow(self, a3, b3, text=None, color=(214, 90, 40), width=6, fs=20, text_off=(10, -30)):
        a, b = self.p2d(a3), self.p2d(b3)
        d = self.draw
        d.line([a, b], fill=color, width=width)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        L, Wd = 22, 12
        p1 = (b[0] - L * math.cos(ang) + Wd * math.sin(ang), b[1] - L * math.sin(ang) - Wd * math.cos(ang))
        p2 = (b[0] - L * math.cos(ang) - Wd * math.sin(ang), b[1] - L * math.sin(ang) + Wd * math.cos(ang))
        d.polygon([b, p1, p2], fill=color)
        if text:
            f = ImageFont.truetype(FONTB, fs)
            mx, my = (a[0] + b[0]) / 2 + text_off[0], (a[1] + b[1]) / 2 + text_off[1]
            lines = text.split('\n')
            tw = max(d.textlength(s, font=f) for s in lines)
            th = len(lines) * (fs + 5)
            d.rounded_rectangle([mx - 8, my - 6, mx + tw + 8, my + th + 2], 6, fill=(255, 244, 236), outline=color, width=2)
            for i, s in enumerate(lines):
                d.text((mx, my - 2 + i * (fs + 5)), s, fill=(120, 45, 15), font=f)

    def title(self, text, sub=None):
        d = self.draw
        d.text((22, 16), text, fill=(25, 25, 30), font=ImageFont.truetype(FONTB, 30))
        if sub:
            d.text((24, 56), sub, fill=(90, 90, 96), font=ImageFont.truetype(FONT, 18))

    def note(self, text, xy=None, fs=17):
        d = self.draw
        f = ImageFont.truetype(FONT, fs)
        W, H = self.img.size
        lines = text.split('\n')
        tw = max(d.textlength(s, font=f) for s in lines)
        th = len(lines) * (fs + 5)
        x, y = xy if xy else (W - tw - 30, H - th - 26)
        d.rounded_rectangle([x - 10, y - 8, x + tw + 10, y + th + 4], 8, fill=(246, 246, 240), outline=(150, 150, 150), width=1)
        for i, s in enumerate(lines):
            d.text((x, y + i * (fs + 5)), s, fill=(60, 60, 66), font=f)
