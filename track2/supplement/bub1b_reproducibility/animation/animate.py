"""BUB1B: a continuous, procedural 180-second scientific explainer (3B1B Edition).

Original procedural vector graphics with continuous point-cloud morphing and depth-sorted 3D segments.
Run: python animate.py --quality preview
     python animate.py --quality final
     python animate.py --stills
"""
from __future__ import annotations
import argparse
import json
import math
import shutil
import subprocess
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import cairo
    HAS_CAIRO = True
except ImportError:
    try:
        import cairocffi as cairo
        HAS_CAIRO = True
    except (ImportError, OSError):
        HAS_CAIRO = False

ROOT = Path(__file__).resolve().parent
DURATION = 180.0
BG = '#101318'
WHITE = '#E8E8E5'
MUTED = '#8C939E'
BLUE = '#58C4DD'
TEAL = '#49A88F'
YELLOW = '#FFFF7A'
RED = '#FC6255'
GREEN = '#83C167'
PURPLE = '#B189D9'
GRAY = '#46505A'
DARK_PANEL = '#181C24'
TAU = math.tau


# ---------------------------------------------------------------------------
# MATHEMATICAL & INTERPOLATION PRIMITIVES
# ---------------------------------------------------------------------------

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return float(np.clip(x, lo, hi))


def ease(x: float) -> float:
    """Quintic minimum-jerk interpolation; zero velocity/acceleration at boundaries."""
    x = clamp(x)
    return x * x * x * (10.0 + x * (-15.0 + 6.0 * x))


def ease_out_back(x: float, s: float = 1.25) -> float:
    """Subtle organic overshoot for snapping biological structures into place."""
    x = clamp(x) - 1.0
    return float(x * x * ((s + 1.0) * x + s) + 1.0)


def smooth_pulse(t: float, a: float, b: float) -> float:
    """Smooth bell-shaped activation between t=a and t=b."""
    if t <= a or t >= b:
        return 0.0
    u = (t - a) / (b - a)
    return math.sin(math.pi * ease(u))


def phase(t: float, a: float, b: float) -> float:
    return ease((t - a) / max(1e-9, b - a))


def visible(t: float, a: float, b: float, fade_in: float = 1.4, fade_out: float = 1.4) -> float:
    return phase(t, a, a + fade_in) * (1.0 - phase(t, b - fade_out, b))


def mix(a, b, u: float):
    u = float(u)
    return np.asarray(a, dtype=float) * (1.0 - u) + np.asarray(b, dtype=float) * u


def hex_to_rgba_float(hexcolor: str, opacity: float = 1.0):
    r = int(hexcolor[1:3], 16) / 255.0
    g = int(hexcolor[3:5], 16) / 255.0
    b = int(hexcolor[5:7], 16) / 255.0
    return (r, g, b, clamp(opacity))


def color_pil(hexcolor: str, opacity: float = 1.0):
    return tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5)) + (round(255 * clamp(opacity)),)


def bezier_curve(p0, p1, p2, p3, num: int = 64) -> np.ndarray:
    u = np.linspace(0.0, 1.0, num)[:, None]
    p0, p1, p2, p3 = map(lambda p: np.asarray(p, dtype=float), (p0, p1, p2, p3))
    return ((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 +
            3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3)


def catmull_rom(points: np.ndarray, subdivisions: int = 5) -> np.ndarray:
    """Smooth C1 spline through control points."""
    p = np.asarray(points, dtype=float)
    if len(p) < 3:
        return p
    x = np.vstack([p[0], p, p[-1]])
    t = np.linspace(0.0, 1.0, subdivisions, endpoint=False)[None, :, None]
    p0, p1, p2, p3 = x[:-3, None], x[1:-2, None], x[2:-1, None], x[3:, None]
    out = 0.5 * ((2 * p1) + (-p0 + p2) * t +
                 (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                 (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
    return np.vstack([out.reshape(-1, p.shape[1]), p[-1]])


def resample_curve(pts: np.ndarray, n: int = 240) -> np.ndarray:
    """Resample any 2D polyline to exactly `n` arc-length-uniform vertices for seamless morphing."""
    p = np.asarray(pts, dtype=float)
    if len(p) < 2:
        return np.repeat(p[:1], n, axis=0)
    diffs = np.diff(p, axis=0)
    seg_lengths = np.linalg.norm(diffs, axis=1)
    cum = np.r_[0.0, np.cumsum(seg_lengths)]
    total = cum[-1]
    if total < 1e-9:
        return np.repeat(p[:1], n, axis=0)
    targets = np.linspace(0.0, total, n)
    idx = np.clip(np.searchsorted(cum, targets, side='right') - 1, 0, len(p) - 2)
    local_u = (targets - cum[idx]) / np.maximum(1e-9, seg_lengths[idx])
    return p[idx] + diffs[idx] * local_u[:, None]


@lru_cache(maxsize=128)
def cached_font(path: str, pixels: int):
    return ImageFont.truetype(path, pixels)


# ---------------------------------------------------------------------------
# HIGH-PRECISION VECTOR / SUPERSAMPLED CANVAS
# ---------------------------------------------------------------------------

class Canvas:
    """Hybrid Vector Canvas: Uses PyCairo for sub-pixel anti-aliased geometry when available,
    or high-factor supersampled PIL with smooth alpha compositing."""

    def __init__(self, width: int = 1920, supersample: float = 2.0):
        self.width = int(width)
        self.height = round(width * 9 / 16)
        self.use_cairo = HAS_CAIRO
        # If PyCairo is unavailable, force at least 4.0x supersampling to eliminate PIL jaggedness
        effective_ss = supersample if self.use_cairo else max(supersample, 4.0)
        self.scale = (self.width / 1920.0) * effective_ss
        self.size = (round(1920 * self.scale), round(1080 * self.scale))

        if self.use_cairo:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size[0], self.size[1])
            self.ctx = cairo.Context(self.surface)
            self.ctx.set_antialias(cairo.ANTIALIAS_BEST)
            self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            r, g, b, _ = hex_to_rgba_float(BG, 1.0)
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.paint()
            self.image = None
            self.d = None
        else:
            self.image = Image.new('RGB', self.size, BG)
            self.d = ImageDraw.Draw(self.image, 'RGBA')

        self._text_queue = []

    def p(self, pt):
        return (float(pt[0]) * self.scale, float(pt[1]) * self.scale)

    def font(self, size: float, italic: bool = False):
        f = 'LMRoman10-Italic.otf' if italic else 'LMRoman10-Regular.otf'
        font_path = ROOT / 'assets' / f
        if not font_path.exists():
            raise FileNotFoundError(f'Missing font: {font_path}. Extract the complete ZIP, including assets/.')
        return cached_font(str(font_path), max(1, round(size * self.scale)))

    def text(self, text: str, xy, size: float = 36, fill: str = WHITE,
             alpha: float = 1.0, anchor: str = 'mm', italic: bool = False):
        alpha = clamp(alpha)
        if alpha < 0.002 or not text:
            return
        self._text_queue.append((text, xy, size, fill, alpha, anchor, italic))

    def _slice_polyline(self, pts: np.ndarray, reveal: float) -> np.ndarray:
        if reveal >= 0.999:
            return pts
        lengths = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
        if lengths[-1] < 1e-9:
            return pts[:1]
        cut = clamp(reveal) * lengths[-1]
        i = min(int(np.searchsorted(lengths, cut)), len(pts) - 1)
        if i <= 0:
            return pts[:1]
        u = (cut - lengths[i - 1]) / max(1e-9, lengths[i] - lengths[i - 1])
        return np.vstack([pts[:i], mix(pts[i - 1], pts[i], u)])

    def line(self, pts, fill: str = WHITE, width: float = 3.0, alpha: float = 1.0, reveal: float = 1.0):
        alpha = clamp(alpha)
        if alpha < 0.002 or reveal <= 0.001:
            return
        p = np.asarray(pts, dtype=float)
        if len(p) < 2:
            return
        if reveal < 0.999:
            p = self._slice_polyline(p, reveal)
            if len(p) < 2:
                return

        if self.use_cairo:
            self.ctx.new_path()
            scaled = p * self.scale
            self.ctx.move_to(float(scaled[0, 0]), float(scaled[0, 1]))
            for x, y in scaled[1:]:
                self.ctx.line_to(float(x), float(y))
            self.ctx.set_source_rgba(*hex_to_rgba_float(fill, alpha))
            self.ctx.set_line_width(max(0.6, width * self.scale))
            self.ctx.stroke()
        else:
            self.d.line([self.p(v) for v in p], fill=color_pil(fill, alpha),
                        width=max(1, round(width * self.scale)), joint='curve')

    def polygon(self, pts, fill: str = None, stroke: str = None, width: float = 2.0, alpha: float = 1.0):
        alpha = clamp(alpha)
        if alpha < 0.002:
            return
        p = np.asarray(pts, dtype=float)
        if len(p) < 3:
            return
        if self.use_cairo:
            self.ctx.new_path()
            scaled = p * self.scale
            self.ctx.move_to(float(scaled[0, 0]), float(scaled[0, 1]))
            for x, y in scaled[1:]:
                self.ctx.line_to(float(x), float(y))
            self.ctx.close_path()
            if fill:
                self.ctx.set_source_rgba(*hex_to_rgba_float(fill, alpha))
                if stroke:
                    self.ctx.fill_preserve()
                else:
                    self.ctx.fill()
            if stroke:
                self.ctx.set_source_rgba(*hex_to_rgba_float(stroke, alpha))
                self.ctx.set_line_width(max(0.6, width * self.scale))
                self.ctx.stroke()
        else:
            coords = [self.p(v) for v in p]
            self.d.polygon(coords,
                           fill=color_pil(fill, alpha) if fill else None,
                           outline=color_pil(stroke, alpha) if stroke else None)
            if stroke and width > 1:
                self.line(np.vstack([p, p[0]]), stroke, width, alpha)

    def dashed(self, a, b, fill: str = WHITE, width: float = 2.2, alpha: float = 1.0, dash: float = 11.0):
        alpha = clamp(alpha)
        if alpha < 0.002:
            return
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        dist = float(np.linalg.norm(b - a))
        if dist < 1e-3:
            return
        if self.use_cairo:
            self.ctx.save()
            self.ctx.set_dash([dash * self.scale, dash * 0.75 * self.scale])
            self.line([a, b], fill, width, alpha)
            self.ctx.restore()
        else:
            n = max(1, int(dist / (1.8 * dash)))
            for i in range(n):
                self.line([mix(a, b, i / n), mix(a, b, (i + 0.55) / n)], fill, width, alpha)

    def circle(self, xy, radius: float, fill: str = None, stroke: str = WHITE,
               width: float = 2.0, alpha: float = 1.0, fill_alpha: float = None):
        alpha = clamp(alpha)
        if alpha < 0.002 or radius <= 0.05:
            return
        fa = alpha if fill_alpha is None else clamp(fill_alpha)
        x, y = float(xy[0]), float(xy[1])
        if self.use_cairo:
            self.ctx.new_path()
            self.ctx.arc(x * self.scale, y * self.scale, radius * self.scale, 0, TAU)
            if fill:
                self.ctx.set_source_rgba(*hex_to_rgba_float(fill, fa))
                if stroke:
                    self.ctx.fill_preserve()
                else:
                    self.ctx.fill()
            if stroke:
                self.ctx.set_source_rgba(*hex_to_rgba_float(stroke, alpha))
                self.ctx.set_line_width(max(0.6, width * self.scale))
                self.ctx.stroke()
        else:
            bbox = (*self.p((x - radius, y - radius)), *self.p((x + radius, y + radius)))
            self.d.ellipse(bbox,
                           fill=color_pil(fill, fa) if fill else None,
                           outline=color_pil(stroke, alpha) if stroke else None,
                           width=max(1, round(width * self.scale)) if stroke else 0)

    def ellipse(self, xy, rx: float, ry: float, fill: str = None, stroke: str = WHITE,
                width: float = 2.0, alpha: float = 1.0, fill_alpha: float = 0.0):
        alpha = clamp(alpha)
        if alpha < 0.002 or rx <= 0.1 or ry <= 0.1:
            return
        t_pts = np.linspace(0, TAU, 120, endpoint=False)
        pts = np.c_[xy[0] + rx * np.cos(t_pts), xy[1] + ry * np.sin(t_pts)]
        if fill and fill_alpha > 0.001:
            self.polygon(pts, fill=fill, stroke=None, alpha=fill_alpha)
        if stroke:
            self.line(np.vstack([pts, pts[0]]), fill=stroke, width=width, alpha=alpha)

    def rounded_rect(self, xy, w: float, h: float, r: float = 12.0,
                     fill: str = None, stroke: str = None, width: float = 2.0,
                     alpha: float = 1.0, fill_alpha: float = None):
        alpha = clamp(alpha)
        if alpha < 0.002 or w <= 0.5 or h <= 0.5:
            return
        fa = alpha if fill_alpha is None else clamp(fill_alpha)
        x, y = xy[0] - w / 2.0, xy[1] - h / 2.0
        r = min(r, w / 2.0, h / 2.0)
        corners = [
            (x + w - r, y + r, -math.pi / 2, 0),
            (x + w - r, y + h - r, 0, math.pi / 2),
            (x + r, y + h - r, math.pi / 2, math.pi),
            (x + r, y + r, math.pi, 3 * math.pi / 2),
        ]
        pts = []
        for cx, cy, a0, a1 in corners:
            ang = np.linspace(a0, a1, 10)
            pts.append(np.c_[cx + r * np.cos(ang), cy + r * np.sin(ang)])
        poly = np.vstack(pts)
        if fill and fa > 0.001:
            self.polygon(poly, fill=fill, stroke=None, alpha=fa)
        if stroke:
            self.line(np.vstack([poly, poly[0]]), fill=stroke, width=width, alpha=alpha)

    def arrow(self, a, b, fill: str = WHITE, width: float = 3.0, alpha: float = 1.0,
              reveal: float = 1.0, head: float = 14.0):
        alpha = clamp(alpha)
        if alpha < 0.002 or reveal <= 0.01:
            return
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        tip = mix(a, b, clamp(reveal))
        self.line([a, tip], fill, width, alpha)
        vec = b - a
        norm = float(np.linalg.norm(vec))
        if norm < 1e-4:
            return
        v = vec / norm
        n = np.array([-v[1], v[0]])
        h_scale = head * clamp(reveal * 2.5)
        self.polygon([tip, tip - v * h_scale + n * (h_scale * 0.52),
                      tip - v * h_scale - n * (h_scale * 0.52)],
                     fill=fill, stroke=fill, width=1.0, alpha=alpha)

    def glow(self, xy, r: float, fill: str = YELLOW, alpha: float = 1.0):
        alpha = clamp(alpha)
        if alpha < 0.002 or r <= 0.1:
            return
        for mult, a_w in [(2.9, 0.03), (2.1, 0.07), (1.45, 0.15), (0.95, 0.32)]:
            self.circle(xy, r * mult, fill=fill, stroke=None, alpha=alpha * a_w)
        self.circle(xy, r * 0.42, fill=WHITE, stroke=None, alpha=alpha * 0.85)

    def finish(self) -> Image.Image:
        if self.use_cairo:
            buf = self.surface.get_data()
            arr = np.ndarray(shape=(self.size[1], self.size[0], 4), dtype=np.uint8, buffer=buf)
            rgb = arr[:, :, [2, 1, 0]].copy()
            self.image = Image.fromarray(rgb, 'RGB')
            self.d = ImageDraw.Draw(self.image, 'RGBA')

        for text, xy, size, fill, alpha, anchor, italic in self._text_queue:
            self.d.text(self.p(xy), text, font=self.font(size, italic),
                        fill=color_pil(fill, alpha), anchor=anchor)

        if self.image.size != (self.width, self.height):
            return self.image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return self.image


# ---------------------------------------------------------------------------
# STRUCTURAL DATA & REUSABLE BIOLOGICAL GEOMETRY
# ---------------------------------------------------------------------------

DATA = json.loads((ROOT / 'assets/bubr1_ca.json').read_text())
CA = np.array([a['xyz'] for a in DATA['atoms']], dtype=float)
CA_CENTER = CA.mean(axis=0)
CA -= CA_CENTER
CA_RADIUS = np.max(np.linalg.norm(CA, axis=1))
CA /= CA_RADIUS
N_INDEX = 1002 - 740
POLAR_ATOMS = {'978:N': [-28.142, -4.773, 30.857], '978:O': [-28.539, -2.902, 28.718], '998:O': [-32.756, -4.115, 26.491], '1002:ND2': [-30.719, -4.844, 28.311], '1002:OD1': [-30.163, -6.409, 29.752]}
CONTACT_PAIRS = [("1002:OD1", "978:N"), ("1002:ND2", "998:O"), ("1002:ND2", "978:O")]


# Actual video time drives secondary movement independently of narrative pacing.
ACTUAL_TIME = 0.0
STORY_TIME = 0.0

def motion_time(t):
    return t + ACTUAL_TIME - STORY_TIME

def protein_rotation(t):
    t = motion_time(t)
    theta = 0.42 + 0.30 * math.sin(t * 0.16) + 0.10 * math.cos(t * 0.09)
    phi = -0.28 + 0.19 * math.sin(t * 0.12)
    cy, sy, cx, sx = math.cos(theta), math.sin(theta), math.cos(phi), math.sin(phi)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    return rx @ ry

# Monotone cubic Hermite clock: continuous speed across all act boundaries.
CLOCK_X = np.array([0, 20, 40, 60, 80, 105, 150, 165, 180], dtype=float)
CLOCK_Y = np.array([0, 19, 39, 59, 81, 108, 140, 162, 180], dtype=float)
CLOCK_D = np.diff(CLOCK_Y) / np.diff(CLOCK_X)
CLOCK_M = np.r_[CLOCK_D[0], np.zeros(7), CLOCK_D[-1]]
for _i in range(1, len(CLOCK_X)-1):
    _h0, _h1 = np.diff(CLOCK_X)[_i-1:_i+1]
    _w0, _w1 = 2*_h1+_h0, _h1+2*_h0
    CLOCK_M[_i] = (_w0+_w1)/(_w0/CLOCK_D[_i-1]+_w1/CLOCK_D[_i])

def story_clock(t):
    t = float(np.clip(t, 0, DURATION))
    i = min(len(CLOCK_X)-2, max(0, int(np.searchsorted(CLOCK_X, t)-1)))
    h = CLOCK_X[i+1]-CLOCK_X[i]
    u = (t-CLOCK_X[i])/h
    return ((2*u**3-3*u**2+1)*CLOCK_Y[i] + (u**3-2*u**2+u)*h*CLOCK_M[i]
            + (-2*u**3+3*u**2)*CLOCK_Y[i+1] + (u**3-u**2)*h*CLOCK_M[i+1])

def project_protein_3d(t: float, center=(960.0, 520.0), scale: float = 340.0, unfold: float = 0.0):
    """Returns 3D rotated coordinates (x_screen, y_screen, z_depth) for depth-sorted rendering."""
    q = CA @ protein_rotation(t).T

    pts_2d = np.c_[q[:, 0], -q[:, 1]] * scale + np.asarray(center, dtype=float)
    z_depth = q[:, 2].copy()

    if unfold > 0.001:
        u = np.linspace(0.0, 1.0, len(pts_2d))
        coil_x = center[0] + (u - 0.5) * scale * 2.15
        coil_y = center[1] + scale * 0.14 * np.sin(u * TAU * 3.5 + t * 0.6)
        pts_2d = mix(pts_2d, np.c_[coil_x, coil_y], unfold)
        z_depth = mix(z_depth, np.zeros_like(z_depth), unfold)

    return pts_2d, z_depth


def draw_protein_3d(c: Canvas, t: float, center=(960.0, 520.0), scale: float = 340.0,
                    alpha: float = 1.0, unfold: float = 0.0, base_color: str = BLUE,
                    highlight_n1002: bool = True):
    """Renders the C-alpha trace with painter-sorted depth (foreground segments thicker & brighter)."""
    pts_2d, z_depth = project_protein_3d(t, center, scale, unfold)
    sub = 4
    curve_2d = catmull_rom(pts_2d, subdivisions=sub)
    curve_z = np.interp(np.linspace(0, len(z_depth) - 1, len(curve_2d)),
                        np.arange(len(z_depth)), z_depth)

    # Group into small chunks of 3 segments for fast Z-sorted painters algorithm
    step = 3
    chunks = []
    for i in range(0, len(curve_2d) - 1, step):
        seg = curve_2d[i:min(i + step + 1, len(curve_2d))]
        z_mean = float(np.mean(curve_z[i:min(i + step + 1, len(curve_2d))]))
        chunks.append((z_mean, seg))

    chunks.sort(key=lambda item: item[0])

    # Subtle outer halo
    c.line(curve_2d, base_color, width=max(4.0, scale * 0.032), alpha=alpha * 0.07)

    for z_val, seg in chunks:
        depth_u = clamp((z_val + 0.75) / 1.5)
        w = (1.6 + 3.6 * depth_u) * (scale / 340.0) ** 0.65
        seg_alpha = alpha * (0.25 + 0.72 * depth_u)
        col = base_color if depth_u > 0.35 else GRAY
        c.line(seg, fill=col, width=w, alpha=seg_alpha)

    if highlight_n1002:
        q = pts_2d[N_INDEX]
        c.glow(q, max(7.0, scale * 0.048), YELLOW, alpha)

    return pts_2d, z_depth


def chromatid_arm_curve(xy, h: float = 82.0, side: int = 1, split: float = 0.0) -> np.ndarray:
    x, y = xy
    shift = side * split
    p0 = (x + shift - side * h * 0.28, y - h * 0.50)
    p1 = (x + shift + side * h * 0.16, y - h * 0.10)
    p2 = (x + shift + side * h * 0.16, y + h * 0.10)
    p3 = (x + shift - side * h * 0.28, y + h * 0.50)
    return bezier_curve(p0, p1, p2, p3, 48)


def draw_chromosome(c: Canvas, xy, h: float = 82.0, fill: str = BLUE,
                    alpha: float = 1.0, split: float = 0.0, kt_glow: float = 0.35):
    if alpha < 0.002:
        return
    x, y = xy
    for side in (-1, 1):
        arm = chromatid_arm_curve(xy, h, side, split)
        c.line(arm, fill=fill, width=h * 0.13, alpha=alpha * 0.28)
        c.line(arm, fill=fill, width=h * 0.075, alpha=alpha * 0.92)
        kt_pos = (x + side * (split + h * 0.09), y)
        c.circle(kt_pos, h * 0.045, fill=YELLOW, stroke=None, alpha=alpha * (0.45 + 0.55 * kt_glow))
    if kt_glow > 0.05:
        c.glow((x, y), h * 0.14 * (0.6 + 0.6 * kt_glow), YELLOW, alpha * kt_glow)


def draw_spindle_rig(c: Canvas, t: float, center=(960.0, 500.0), rx: float = 560.0, ry: float = 275.0,
                     alpha: float = 1.0, unattached_idx: int = -1, attach_progress: float = 1.0,
                     lag_idx: int = -1, lag_amount: float = 0.0, anaphase_split: float = 0.0):
    """Renders a cohesive, biologically detailed mitotic spindle with curved Bézier microtubules."""
    if alpha < 0.002:
        return
    cx, cy = center
    # Double-layered cell cortex membrane
    c.ellipse(center, rx, ry, stroke=GRAY, width=3.0, alpha=alpha * 0.75)
    c.ellipse(center, rx * 0.965, ry * 0.965, stroke=GRAY, width=1.2, alpha=alpha * 0.28)

    pole_dx = rx * 0.82
    poles = [(cx - pole_dx, cy), (cx + pole_dx, cy)]

    n_chrom = 5
    y_span = ry * 1.18
    chrom_ys = np.linspace(cy - y_span * 0.5, cy + y_span * 0.5, n_chrom)

    # Background astral / interpolar curved microtubules
    for s in (-1, 1):
        px, py = cx + s * pole_dx, cy
        for arc_y in (-ry * 0.72, -ry * 0.45, ry * 0.45, ry * 0.72):
            ctrl1 = (px - s * rx * 0.22, py + arc_y * 0.85)
            ctrl2 = (cx - s * rx * 0.10, py + arc_y * 0.95)
            curve = bezier_curve((px, py), ctrl1, ctrl2, (cx, py + arc_y * 0.75), 36)
            c.line(curve, GREEN, width=1.4, alpha=alpha * 0.15)

    # Kinetochore microtubule bundles and chromosomes
    for i, y_ch in enumerate(chrom_ys):
        wobble = 8.5 * math.sin(motion_time(t) * 1.15 + i * 1.3) * (1.0 - 0.7 * anaphase_split)
        x_ch = cx + wobble
        kt_glow = 0.2
        col = BLUE if i % 2 == 0 else PURPLE

        if i == unattached_idx:
            # Drifts from displaced/unattached state into clean equatorial alignment
            offset_x = -rx * 0.24 * (1.0 - attach_progress)
            offset_y = -18.0 * (1.0 - attach_progress)
            x_ch += offset_x
            y_ch += offset_y
            kt_glow = 1.0 - 0.75 * attach_progress

        if i == lag_idx and lag_amount > 0.001:
            x_ch += rx * 0.28 * lag_amount
            col = RED if lag_amount > 0.25 else col
            kt_glow = 0.85 * lag_amount

        split_dist = anaphase_split * rx * 0.34
        if i == lag_idx and lag_amount > 0.25:
            # Mis-segregation: lagging chromosome fails to split evenly
            split_dist *= (1.0 - 0.75 * lag_amount)

        for s_idx, s in enumerate((-1, 1)):
            px, py = poles[s_idx]
            target_x = x_ch + s * split_dist
            target_y = y_ch
            # If right-side kinetochore is not yet attached in Act I
            if i == unattached_idx and s == 1 and attach_progress < 0.99:
                tip = mix((px - rx * 0.32, (py + target_y) * 0.5), (target_x, target_y), attach_progress)
            else:
                tip = (target_x, target_y)
            ctrl1 = (px - s * rx * 0.25, py + (target_y - py) * 0.35)
            ctrl2 = (tip[0] + s * rx * 0.18, py + (target_y - py) * 0.88)
            mt_curve = bezier_curve((px, py), ctrl1, ctrl2, tip, 40)
            c.line(mt_curve, GREEN, width=2.2, alpha=alpha * 0.42)

        draw_chromosome(c, (x_ch, y_ch), h=ry * 0.25, fill=col,
                        alpha=alpha, split=split_dist, kt_glow=kt_glow)

    for px, py in poles:
        c.glow((px, py), 16.0, GREEN, alpha * 0.95)


# ---------------------------------------------------------------------------
# CONTINUOUS 8-ACT VISUAL STORYBOARD (0s - 180s)
# ---------------------------------------------------------------------------

def act1_and_2_checkpoint_to_genetics(c: Canvas, t: float):
    """Act I (0-19s): Mitotic spindle & checkpoint.
       Transition (15-20s): Central chromatid uncoils directly into the BUB1B gene tracks of Act II (19-39s)."""
    if t > 40.5:
        return

    # 1. Mitotic Spindle (fades as chromatin uncoils at t=15..19.5)
    spindle_alpha = visible(t, -1.0, 19.2, 1.2, 2.5)
    attach_p = phase(t, 6.5, 11.5)
    if spindle_alpha > 0.002:
        draw_spindle_rig(c, t, center=(960.0, 485.0), rx=560.0, ry=265.0,
                         alpha=spindle_alpha, unattached_idx=1, attach_progress=attach_p)

        # Dynamic BUBR1 checkpoint signal & APC/C inhibition bar
        wait_signal = 1.0 - 0.65 * attach_p
        kt_unattached = (960.0 - 560.0 * 0.24 * (1.0 - attach_p), 485.0 - 132.0 - 18.0 * (1.0 - attach_p))
        c.text('BUBR1', (kt_unattached[0] - 88, kt_unattached[1] - 28), 32, YELLOW, spindle_alpha)
        c.line([(kt_unattached[0] - 42, kt_unattached[1] - 12),
                (kt_unattached[0] - 12, kt_unattached[1] - 2)], YELLOW, 2.0, spindle_alpha * 0.7)

        # APC/C brake schematic at bottom of spindle
        apc_y = 815.0
        c.rounded_rect((960.0, apc_y), 190, 48, r=12, fill=DARK_PANEL,
                       stroke=BLUE if attach_p > 0.85 else RED, width=2.2, alpha=spindle_alpha)
        c.text('APC/C', (960.0, apc_y), 27, WHITE, spindle_alpha)
        # Inhibitory T-bar from BUBR1 to APC/C
        tbar_alpha = spindle_alpha * wait_signal
        c.line([(810.0, apc_y), (852.0, apc_y)], RED, 3.2, tbar_alpha)
        c.line([(852.0, apc_y - 14), (852.0, apc_y + 14)], RED, 3.6, tbar_alpha)
        c.text('Wait signal', (730.0, apc_y), 26, RED, tbar_alpha, anchor='rm')

    # 2. Seamless Morph: Central Chromatid (t=14.5) -> Dual Horizontal Gene Tracks (t=20.0)
    if 14.5 <= t <= 40.5:
        u_morph = phase(t, 17.0, 20.0)
        u_exit = phase(t, 37.0, 39.5)
        act2_alpha = (1.0 - u_exit) * phase(t, 14.5, 16.5)

        chrom_arm_1 = resample_curve(chromatid_arm_curve((960.0, 485.0), h=68.0, side=-1), 240)
        chrom_arm_2 = resample_curve(chromatid_arm_curve((960.0, 485.0), h=68.0, side=1), 240)

        xs = np.linspace(230.0, 1690.0, 240)
        # Zoom into residue 1002 at end of Act II (35.5s -> 39.5s)
        zoom_center = np.array([230.0 + 1460.0 * (1002.0 / 1050.0), 600.0])

        tracks_y = [395.0, 600.0]
        for row, (arm_pts, base_y) in enumerate(zip([chrom_arm_1, chrom_arm_2], tracks_y)):
            wave1 = np.c_[xs, base_y + 11.0 * np.sin( np.linspace(0, TAU * 10, 240) + t * 0.25)]
            wave2 = np.c_[xs, base_y + 22.0 + 11.0 * np.cos(np.linspace(0, TAU * 10, 240) + t * 0.25)]

            pts1 = mix(arm_pts, wave1, u_morph)
            pts2 = mix(arm_pts, wave2, u_morph)

            if u_exit > 0.001:
                pts1 = (pts1 - zoom_center) * (1.0 + 3.5 * u_exit) + np.array([760.0, 480.0]) * u_exit + zoom_center * (1.0 - u_exit)
                pts2 = (pts2 - zoom_center) * (1.0 + 3.5 * u_exit) + np.array([760.0, 480.0]) * u_exit + zoom_center * (1.0 - u_exit)

            row_fade = act2_alpha * (1.0 - u_exit if row == 0 else 1.0)
            c.line(pts1, BLUE, width=3.2, alpha=row_fade * 0.88)
            c.line(pts2, PURPLE, width=2.0, alpha=row_fade * 0.45)

            # Exon rung ticks along the double helix
            if u_morph > 0.35 and u_exit < 0.7:
                rung_alpha = row_fade * phase(t, 18.0, 21.0) * (1.0 - u_exit * 1.4)
                for k in range(8, 232, 10):
                    c.line([pts1[k], pts2[k]], GRAY, width=1.4, alpha=rung_alpha * 0.45)

        # Variant markers & cis/trans phase swap animation (t=27..33s)
        if t >= 19.0:
            v_alpha = visible(t, 19.5, 37.5, 1.5, 1.5)
            swap = smooth_pulse(t, 28.0, 34.5)

            x_737 = 230.0 + 1460.0 * (737.0 / 1050.0)
            x_1002 = 230.0 + 1460.0 * (1002.0 / 1050.0)
            y_737 = tracks_y[0] + 11.0
            # Asn1002Lys smoothly arcs between Track 2 (trans) and Track 1 (cis) to show phase ambiguity
            y_1002 = mix(tracks_y[1] + 11.0, tracks_y[0] + 11.0, swap)

            # Premature truncation bar at 737
            stop_rev = phase(t, 21.5, 25.5)
            c.line([(x_737, y_737 - 26), (x_737, y_737 + 26)], RED, width=4.5, alpha=v_alpha * stop_rev)
            c.dashed((x_737 + 8, y_737), (1690.0, y_737), RED, width=2.8, alpha=v_alpha * stop_rev * 0.65)
            c.glow((x_737, y_737), 18.0, RED, v_alpha)
            c.text('p.Leu737Ter', (x_737, y_737 - 48), 34, RED, v_alpha)

            # Missense node at 1002
            c.glow((x_1002, y_1002), 20.0, YELLOW, v_alpha)
            c.text('p.Asn1002Lys', (x_1002 - 15, y_1002 + 58), 34, YELLOW, v_alpha, anchor='rm')

            # Connecting phase bracket for cis vs. trans ambiguity
            amb_alpha = v_alpha * phase(t, 26.5, 29.0)
            arc_pts = bezier_curve((x_737, y_737 + 28), (x_737 + 80, 505.0),
                                   (x_1002 - 80, 505.0), (x_1002, y_1002 - 18), 45)
            c.dashed(arc_pts[0], arc_pts[-1], MUTED, width=2.0, alpha=amb_alpha * 0.65)
            c.rounded_rect((960.0, 502.0), 235, 42, r=10, fill=DARK_PANEL, stroke=YELLOW,
                           width=1.6, alpha=amb_alpha * 0.9)
            c.text('cis vs. trans ?', (960.0, 502.0), 27, YELLOW, amb_alpha)


def act3_atomic_substitution(c: Canvas, t: float):
    """Act III (38-59s): Codon AAT -> AAG and true ball-and-stick side-chain morphing (Asn -> Lys)."""
    a = visible(t, 37.8, 59.2, 1.6, 1.6)
    if a < 0.002:
        return

    change = phase(t, 43.5, 47.5)
    fold_into_3d = phase(t, 56.0, 59.0)
    content_alpha = a * (1.0 - fold_into_3d)

    # Left Panel: Codon Ladder (AAT -> AAG)
    c.text('c.3006T > G', (510.0, 290.0), 34, MUTED, content_alpha)
    c.line([(330.0, 350.0), (690.0, 350.0)], BLUE, width=3.5, alpha=content_alpha * 0.7)

    bases = [('A', BLUE, 'A', BLUE), ('A', BLUE, 'A', BLUE), ('T', BLUE, 'G', YELLOW)]
    for i, (b_wt, col_wt, b_mut, col_mut) in enumerate(bases):
        bx = 390.0 + i * 120.0
        c.line([(bx, 350.0), (bx, 415.0)], GRAY, width=3.0, alpha=content_alpha * 0.6)
        c.rounded_rect((bx, 460.0), 86, 86, r=16, fill=DARK_PANEL,
                       stroke=col_mut if (i == 2 and change > 0.5) else col_wt,
                       width=2.8, alpha=content_alpha)
        if i < 2:
            c.text(b_wt, (bx, 460.0), 54, col_wt, content_alpha)
        else:
            c.text(b_wt, (bx, 460.0 - 22.0 * change), 54, col_wt, content_alpha * (1.0 - change))
            c.text(b_mut, (bx, 460.0 + 22.0 * (1.0 - change)), 54, col_mut, content_alpha * change)

    # Central transition arrow
    c.arrow((740.0, 460.0), (930.0, 460.0), WHITE, width=3.0, alpha=content_alpha)

    # Right Side: Ball-and-Stick Amino Acid Side-Chain Geometry (Asn1002 -> Lys1002)
    # Anchor C-alpha moves smoothly toward the Act IV 3D N1002 position during [55..59s]
    pts_3d_target, _ = project_protein_3d(t, center=(680.0, 530.0), scale=385.0)
    n1002_target = pts_3d_target[N_INDEX]
    ca_pos = mix((1060.0, 520.0), n1002_target, fold_into_3d)

    # Backbone ribbon passing through C-alpha
    bb_pts = bezier_curve((ca_pos[0] - 95, ca_pos[1] + 55), (ca_pos[0] - 35, ca_pos[1] + 10),
                          (ca_pos[0] + 35, ca_pos[1] - 10), (ca_pos[0] + 95, ca_pos[1] + 45), 32)
    c.line(bb_pts, GRAY, width=5.0, alpha=content_alpha * 0.7)

    # Asn (N) atoms: CB, CG, OD1, ND2  ->  Morphing into extended Lys (K) chain: CB, CG, CD, CE, NZ(+)
    cb = ca_pos + np.array([58.0, -52.0]) * (1.0 - 0.7 * fold_into_3d)
    cg = cb + np.array([66.0, -18.0]) * (1.0 - 0.7 * fold_into_3d)

    # Branch 1 (Carbonyl O in Asn -> folds into aliphatic chain in Lys)
    od1_asn = cg + np.array([28.0, -64.0])
    cd_lys = cg + np.array([62.0, -48.0])
    ce_lys = cd_lys + np.array([64.0, -14.0])
    nz_lys = ce_lys + np.array([58.0, -46.0])

    nd2_asn = cg + np.array([68.0, 26.0])

    p_od1_or_cd = mix(od1_asn, cd_lys, change)
    p_nd2_or_ce = mix(nd2_asn, ce_lys, change)
    p_tip = mix(nd2_asn, nz_lys, change)

    if content_alpha > 0.01:
        # Electrostatic / Steric Footprint Envelope
        env_center = mix(cg + np.array([35.0, -15.0]), ce_lys, change)
        env_rx = mix(82.0, 138.0, change)
        env_ry = mix(68.0, 96.0, change)
        env_col = YELLOW if change > 0.5 else BLUE
        c.ellipse(env_center, env_rx, env_ry, fill=env_col, stroke=env_col,
                  width=1.8, alpha=content_alpha * 0.45, fill_alpha=content_alpha * 0.08)

        # Covalent bonds
        c.line([ca_pos, cb, cg], WHITE, width=4.5, alpha=content_alpha * 0.9)
        c.line([cg, p_od1_or_cd], WHITE, width=4.0, alpha=content_alpha * 0.9)
        c.line([cg, p_nd2_or_ce], WHITE, width=4.0, alpha=content_alpha * (1.0 - change * 0.85))
        if change > 0.02:
            c.line([p_od1_or_cd, p_nd2_or_ce, p_tip], YELLOW, width=4.2, alpha=content_alpha * change)

        c.line([cg+np.array([-6,-3]), p_od1_or_cd+np.array([-6,-3])], WHITE,
               width=2.0, alpha=content_alpha*(1-change))
        c.circle(p_nd2_or_ce, 10, MUTED, WHITE, width=1.8, alpha=content_alpha*change)
        # Atomic nodes
        c.circle(ca_pos, 13.0, fill=BLUE, stroke=WHITE, width=2.2, alpha=a)
        c.circle(cb, 10.0, fill=MUTED, stroke=WHITE, width=1.8, alpha=content_alpha)
        c.circle(cg, 10.0, fill=MUTED, stroke=WHITE, width=1.8, alpha=content_alpha)
        c.circle(p_od1_or_cd, 11.0, fill=RED if change < 0.5 else MUTED,
                 stroke=WHITE, width=1.8, alpha=content_alpha)
        c.circle(p_tip, mix(11.0, 15.0, change), fill=BLUE if change < 0.5 else YELLOW,
                 stroke=WHITE, width=2.2, alpha=content_alpha)

        if change > 0.35:
            c.glow(p_tip, 22.0, YELLOW, content_alpha * change)
            c.text('+', (p_tip[0] + 28, p_tip[1] - 18), 42, YELLOW, content_alpha * change)

        # Clean comparative label
        c.text('Asn1002 (neutral polar)', (1230.0, 675.0), 35, BLUE, content_alpha * (1.0 - change))
        c.text('Lys1002 (+ charged, longer)', (1230.0, 675.0), 35, YELLOW, content_alpha * change)


def act4_structural_context(c: Canvas, t: float):
    """Act IV (57-83s): 3D depth-sorted C-alpha backbone (`bubr1_ca.json`) + visual metric gauges."""
    a = visible(t, 56.5, 83.0, 1.8, 1.8)
    if a < 0.002:
        return

    # Unfold goes 0.85 -> 0.0 as the 3D backbone folds around N1002 at t=56.5..62.0
    unfold_in = 0.85 * (1.0 - phase(t, 56.5, 62.0))
    # Transition to Act V (78.5..83s): Protein shrinks and glides to the left BUBR1 pool
    to_act5 = phase(t, 80.0, 83.0)
    center = mix((680.0, 520.0), (355.0, 425.0), to_act5)
    scale = mix(385.0, 135.0, to_act5)

    pts_2d, _ = draw_protein_3d(c, t, center=center, scale=scale, alpha=a, unfold=unfold_in)
    q_n1002 = pts_2d[N_INDEX]

    panel_alpha = a * (1.0 - to_act5 * 1.3)
    if panel_alpha > 0.005:
        # Actual atom-to-atom contacts, projected using the same protein rotation.
        contact_p = phase(t, 64.0, 67.0)
        rot = protein_rotation(t)
        def atom_screen(key):
            q = ((np.array(POLAR_ATOMS[key])-CA_CENTER)/CA_RADIUS) @ rot.T
            return np.array(center) + np.array([q[0], -q[1]])*scale
        for k, (left, right) in enumerate(CONTACT_PAIRS):
            pa, pb = atom_screen(left), atom_screen(right)
            col = [PURPLE, GREEN, TEAL][k]
            c.dashed(pa, pb, col, width=2.8, alpha=panel_alpha*contact_p, dash=5)
            c.circle(pa, 4, col, alpha=panel_alpha*contact_p)
            c.circle(pb, 4, col, alpha=panel_alpha*contact_p)
        c.text('N1002', (q_n1002[0]+24, q_n1002[1]-24), 32, YELLOW, panel_alpha*(1-phase(t,65.5,67)), anchor='lm')
        # Measurements have units; no arbitrary bar percentages.
        metrics = [('pLDDT 91.1', BLUE, 60.5), ('SASA 27.5 Å²', GREEN, 63.0),
                   ('Polar contacts 2.83–2.95 Å', PURPLE, 65.5)]
        for i, (label, col, start) in enumerate(metrics):
            opacity = panel_alpha*phase(t, start, start+1.4)
            y = 365+i*120
            c.rounded_rect((1410, y), 520, 76, r=14, fill=DARK_PANEL,
                           stroke=col, width=2, alpha=opacity)
            c.text(label, (1410, y), 32, WHITE, opacity)
        # Magnified contact geometry, derived from model atomic coordinates.
        opacity = panel_alpha*contact_p
        origin = np.mean(list(POLAR_ATOMS.values()), axis=0)
        projected = {}
        for key, xyz in POLAR_ATOMS.items():
            q = (np.array(xyz)-origin) @ rot.T
            projected[key] = np.array([1410, 790])+np.array([q[0], -q[1]])*53
        for k, (left, right) in enumerate(CONTACT_PAIRS):
            c.dashed(projected[left], projected[right], [PURPLE,GREEN,TEAL][k],
                     width=2.2, alpha=opacity, dash=6)
        for key, xy in projected.items():
            col = RED if key.endswith('O') or key.endswith('OD1') else BLUE
            c.circle(xy, 7, col, WHITE, width=1.2, alpha=opacity)


def act5_checkpoint_failure(c: Canvas, t: float):
    """Act V (81-109s): Depletion of functional BUBR1 pool -> weakened MCC/PP2A signaling -> segregation error."""
    a = visible(t, 80.5, 109.5, 1.8, 1.8)
    if a < 0.002:
        return

    loss = phase(t, 86.5, 94.5)
    to_act6 = phase(t, 106.0, 109.0)
    scene_alpha = a * (1.0 - to_act6)

    # Left: Pool of 4 Mini-3D BUBR1 Proteins (3 of them destabilize/unfold as `loss` increases)
    pool_coords = [(275.0, 395.0), (435.0, 395.0), (275.0, 565.0), (435.0, 565.0)]
    for idx, (px, py) in enumerate(pool_coords):
        is_unstable = idx >= 1
        unfold_val = (0.72 * loss) if is_unstable else 0.0
        col = GRAY if (is_unstable and loss > 0.45) else BLUE
        p_alpha = a * (1.0 - 0.45 * loss if is_unstable else 1.0)
        # During transition to Act VI, the central unstable proteins slide toward x=960
        pos = mix((px, py), (820.0 + (idx - 1) * 140.0, 510.0), to_act6)
        draw_protein_3d(c, t + idx * 1.7, center=pos, scale=mix(92.0, 125.0, to_act6),
                        alpha=p_alpha, unfold=unfold_val, base_color=col, highlight_n1002=True)

    c.text('Functional BUBR1 ↓', (355.0, 285.0), 34, YELLOW, scene_alpha*(1-phase(t,89,92)))

    # Center: Bifurcated Signaling Pathways (MCC & PP2A-B56) weakening with BUBR1 loss
    sig_strength = 1.0 - 0.68 * loss
    for branch_y, label, col in [(425.0, 'MCC / APC/C', BLUE), (545.0, 'PP2A-B56', PURPLE)]:
        signal_alpha = scene_alpha * (0.3 + 0.7 * sig_strength)
        if branch_y == 425.0:
            c.line([(535, 480), (775, branch_y)], col, 1.5 + 2.8*sig_strength, signal_alpha)
            c.line([(775, branch_y-16), (775, branch_y+16)], col, 3.5, signal_alpha)
        else:
            c.arrow((535, 480), (775, branch_y), col, 1.5 + 2.8*sig_strength, signal_alpha)
        c.text(label, (655.0, branch_y - 28), 26, col, scene_alpha * 0.9)

    # Right: Mitotic Spindle experiencing premature anaphase & Chromosome #3 mis-segregation
    spindle_split = 0.55 * phase(t, 92.0, 99.0)
    draw_spindle_rig(c, t, center=(1295.0, 495.0), rx=435.0, ry=235.0,
                     alpha=scene_alpha, lag_idx=2, lag_amount=loss, anaphase_split=spindle_split)

    if loss > 0.25:
        c.text('Segregation error', (1295.0, 785.0), 34, RED, scene_alpha * loss)


def act6_treatment_4pba(c: Canvas, t: float):
    """Act VI (108-141s): 4-PBA chemical chaperone refolds destabilized BUBR1 ribbons into native 3D fold."""
    a = visible(t, 107.5, 141.0, 1.8, 1.8)
    if a < 0.002:
        return

    rescue = phase(t, 115.5, 126.0)
    to_act7 = phase(t, 137.5, 140.5)
    left_alpha = a * (1.0 - to_act7)

    # Left: 4-PBA Molecular Structure Icon (Benzene ring + butyrate tail)
    mol_center = (310.0, 500.0)
    ring_angles = np.linspace(0, TAU, 7)[:-1]
    ring_pts = np.c_[mol_center[0] + 46.0 * np.cos(ring_angles),
                     mol_center[1] + 46.0 * np.sin(ring_angles)]
    c.polygon(ring_pts, fill=DARK_PANEL, stroke=BLUE, width=3.2, alpha=left_alpha)
    c.circle(mol_center, 24.0, fill=None, stroke=BLUE, width=1.8, alpha=left_alpha * 0.65)
    tail_pts = [(mol_center[0] + 46.0, mol_center[1]),
                (mol_center[0] + 82.0, mol_center[1] - 24.0),
                (mol_center[0] + 118.0, mol_center[1] + 4.0),
                (mol_center[0] + 154.0, mol_center[1] - 20.0),
                (mol_center[0] + 190.0, mol_center[1] + 4.0)]
    c.line(tail_pts, BLUE, width=3.2, alpha=left_alpha)
    end = np.array(tail_pts[-1])
    c.line([end, end+[30,-28]], RED, 3, left_alpha)
    c.line([end+[5,3], end+[35,-25]], RED, 2, left_alpha)
    c.line([end, end+[32,26]], RED, 3, left_alpha)
    c.circle(end+[36,-32], 7, RED, alpha=left_alpha)
    c.circle(end+[38,30], 7, RED, alpha=left_alpha)
    c.text('4-PBA', (mol_center[0] + 35, mol_center[1] + 92), 40, BLUE, left_alpha)

    # Propagating chaperone wave pulses from 4-PBA to the central folding chamber
    wave_on = phase(t, 112.0, 115.0) * (1.0 - to_act7)
    if wave_on > 0.01:
        for w_idx in range(4):
            u = ((motion_time(t) * 0.52 + w_idx * 0.25) % 1.0)
            wx = mix(495.0, 770.0, u)
            wy_span = 55.0 + 35.0 * u
            arc = bezier_curve((wx, 500.0 - wy_span), (wx + 28.0, 500.0 - wy_span * 0.4),
                               (wx + 28.0, 500.0 + wy_span * 0.4), (wx, 500.0 + wy_span), 28)
            c.line(arc, GREEN, width=2.6, alpha=wave_on * math.sin(math.pi * u) * 0.75)

    # Center: 3D BUBR1 Folding Chamber (Unfolded ribon smoothly refolds as `rescue` -> 1.0)
    prot_center = mix((960.0, 500.0), (1490.0, 510.0), to_act7)
    prot_scale = mix(255.0, 195.0, to_act7)
    current_unfold = 0.68 * (1.0 - rescue)
    prot_col = BLUE if rescue > 0.45 else GRAY
    draw_protein_3d(c, t, center=prot_center, scale=prot_scale,
                    alpha=a, unfold=current_unfold, base_color=prot_col, highlight_n1002=True)

    c.text('Predicted response', (960.0, 265.0), 35, GREEN, left_alpha * phase(t, 114.0, 118.0)*(1-phase(t,125,129)))

    # Right: Bifurcated Functional Verification Gauge (Quantity vs. Quality)
    branch_alpha = left_alpha * phase(t, 125.0, 129.0)
    if branch_alpha > 0.01:
        c.arrow((1165.0, 485.0), (1375.0, 415.0), GREEN, width=3.0, alpha=branch_alpha)
        c.arrow((1165.0, 515.0), (1375.0, 585.0), YELLOW, width=2.6, alpha=branch_alpha)
        c.rounded_rect((1545.0, 415.0), 290, 58, r=12, fill=DARK_PANEL, stroke=GREEN, width=2.2, alpha=branch_alpha)
        c.text('Stable BUBR1', (1545.0, 415.0), 29, GREEN, branch_alpha)
        c.rounded_rect((1545.0, 585.0), 290, 58, r=12, fill=DARK_PANEL, stroke=YELLOW, width=1.8, alpha=branch_alpha)
        c.text('Segregation fidelity', (1545.0, 585.0), 28, YELLOW, branch_alpha)


def act7_alternative_probes(c: Canvas, t: float):
    """Act VII (140-163s): Three mechanistic probe tracks (NMN cycle, TUDCA shield, Amlexanox stop readthrough)."""
    a = visible(t, 139.5, 163.0, 1.6, 1.8)
    if a < 0.002:
        return

    to_act8 = phase(t, 158.5, 162.5)
    lanes_alpha = a * (1.0 - to_act8)

    # Target 3D BUBR1 on the right (persistent from Act VI, then morphs into Act VIII spindle at t=158.5..162.5)
    target_pos = mix((1490.0, 510.0), (620.0, 505.0), to_act8)
    draw_protein_3d(c, t, center=target_pos, scale=mix(195.0, 90.0, to_act8),
                    alpha=a * (1.0 - 0.6 * to_act8), unfold=0.0, base_color=BLUE)

    # --- LANE 1 (y=325): NMN -> NAD+ / SIRT2 enzymatic cycle wheel ---
    o1 = lanes_alpha * phase(t, 140.5, 143.0)
    if o1 > 0.01:
        y1 = 325.0
        c.text('NMN', (290.0, y1), 42, BLUE, o1, anchor='lm')
        wheel_c = (660.0, y1)
        c.circle(wheel_c, 42.0, fill=DARK_PANEL, stroke=BLUE, width=2.5, alpha=o1)
        for k in range(3):
            ang = t * 1.8 + k * (TAU / 3.0)
            dot_p = (wheel_c[0] + 42.0 * math.cos(ang), wheel_c[1] + 42.0 * math.sin(ang))
            c.circle(dot_p, 6.0, fill=YELLOW, stroke=None, alpha=o1)
        # Mechanism explained by the caption track.
        c.arrow((735.0, y1), (1290.0, 455.0), BLUE, width=2.8, alpha=o1)

    # --- LANE 2 (y=510): TUDCA -> Chemical chaperone protective envelope ---
    o2 = lanes_alpha * phase(t, 143.0, 145.5)
    if o2 > 0.01:
        y2 = 510.0
        c.text('TUDCA', (290.0, y2), 42, GREEN, o2, anchor='lm')
        shield_c = (660.0, y2)
        c.ellipse(shield_c, 68.0, 38.0, fill=GREEN, stroke=GREEN,
                  width=2.4, alpha=o2, fill_alpha=o2 * 0.14)
        # Mini folded wave inside shield
        s_xs = np.linspace(shield_c[0] - 42, shield_c[0] + 42, 40)
        s_ys = y2 + 14.0 * np.sin((s_xs - shield_c[0]) * 0.14 + t * 2.0)
        c.line(np.c_[s_xs, s_ys], GREEN, width=3.0, alpha=o2)
        # Mechanism explained by the caption track.
        c.arrow((755.0, y2), (1275.0, 510.0), GREEN, width=2.8, alpha=o2)

    # --- LANE 3 (y=705): Amlexanox -> Ribosome translating past the Leu737Ter premature stop codon ---
    o3 = lanes_alpha * phase(t, 146.5, 149.0)
    if o3 > 0.01:
        y3 = 705.0
        c.text('Amlexanox', (290.0, y3), 40, PURPLE, o3, anchor='lm')
        # mRNA track with stop codon at x=820
        mrna_x0, mrna_x1, stop_x = 560.0, 1180.0, 825.0
        c.line([(mrna_x0, y3), (mrna_x1, y3)], PURPLE, width=3.2, alpha=o3 * 0.8)
        c.line([(stop_x, y3 - 20), (stop_x, y3 + 20)], RED, width=4.0, alpha=o3)

        # Gliding ribosome dome riding *past* the stop codon (readthrough)
        rt_u = phase(t, 147.0, 158.3)
        ribo_x = mix(mrna_x0 + 35.0, mrna_x1 - 35.0, ease(rt_u))
        c.ellipse((ribo_x, y3 - 10.0), 34.0, 22.0, fill=PURPLE, stroke=WHITE,
                  width=2.0, alpha=o3, fill_alpha=o3 * 0.45)
        c.ellipse((ribo_x, y3 + 12.0), 26.0, 12.0, fill=PURPLE, stroke=WHITE,
                  width=1.6, alpha=o3, fill_alpha=o3 * 0.35)
        if ribo_x > stop_x:
            c.glow((stop_x, y3), 16.0, GREEN, o3 * 0.8)
        # Stop-allele readthrough is described in the subtitle.
        c.arrow((1205.0, y3), (1320.0, 575.0), PURPLE, width=2.6, alpha=o3)


def act8_functional_rescue(c: Canvas, t: float):
    """Act VIII (161-180s): Restored mitotic spindle achieves symmetric chromosome alignment & clean segregation."""
    a = visible(t, 160.5, 180.5, 1.8, 1.5)
    if a < 0.002:
        return

    # Lagging chromosome is captured and aligned (162..169s), then clean symmetric anaphase occurs (171..177s)
    align_rescue = phase(t, 162.5, 169.5)
    clean_anaphase = 0.48 * phase(t, 171.0, 177.0)

    draw_spindle_rig(c, t, center=(620.0, 505.0), rx=430.0, ry=245.0,
                     alpha=a, lag_idx=2, lag_amount=(1.0 - align_rescue) * 0.75,
                     anaphase_split=clean_anaphase)

    c.text('Success criteria', (1415, 250), 35, WHITE, a*(1-phase(t,169.6,171.8)))

    # Right Side: 3 Minimalist Endpoint Readout Cards with custom geometric icons
    endpoints = [
        ('Aligned segregation', GREEN, 164.0),
        ('Feasible exposure', BLUE, 166.8),
        ('Genomic stability', YELLOW, 169.6),
    ]
    for i, (label, col, t0) in enumerate(endpoints):
        cy = 365.0 + i * 140.0
        card_a = a * ease_out_back(phase(t, t0, t0 + 2.2))
        if card_a < 0.01:
            continue
        c.rounded_rect((1415.0, cy), 520, 92, r=16, fill=DARK_PANEL,
                       stroke=col, width=2.4, alpha=card_a, fill_alpha=card_a * 0.85)

        # Mini graphic icon on the left of each readout card
        ix = 1215.0
        if i == 0:
            # Paired symmetric chromatids icon
            c.line([(ix - 12, cy - 18), (ix - 12, cy + 18)], GREEN, width=4.0, alpha=card_a)
            c.line([(ix + 12, cy - 18), (ix + 12, cy + 18)], GREEN, width=4.0, alpha=card_a)
            c.glow((ix, cy), 10.0, GREEN, card_a)
        elif i == 1:
            # Therapeutic window bell curve icon
            xs = np.linspace(ix - 26, ix + 26, 30)
            ys = cy + 16.0 - 32.0 * np.exp(-((xs - ix) / 14.0) ** 2)
            c.line(np.c_[xs, ys], BLUE, width=3.2, alpha=card_a)
        else:
            # Hexagonal stability shield icon
            ang = np.linspace(0, TAU, 7)[:-1]
            hex_pts = np.c_[ix + 20.0 * np.cos(ang), cy + 20.0 * np.sin(ang)]
            c.polygon(hex_pts, fill=None, stroke=YELLOW, width=2.8, alpha=card_a)
            c.circle((ix, cy), 5.0, fill=YELLOW, stroke=None, alpha=card_a)

        c.text(label, (1270.0, cy), 34, WHITE, card_a, anchor='lm')


# ---------------------------------------------------------------------------
# VOICEOVER SUBTITLES & MASTER FRAME COMPOSITOR
# ---------------------------------------------------------------------------

CAPTIONS = [(0, 7, 'Can restoring functional BUBR1 improve chromosome segregation?'), (7, 14, 'BUBR1 helps restrain APC/C–CDC20 until chromosome attachments are ready.'), (14, 20, 'This checkpoint protects daughter cells from receiving incorrect chromosome numbers.'), (20, 27, 'The case contains two BUB1B variants: p.Leu737Ter and p.Asn1002Lys.'), (27, 34, 'The stop can reduce full-length protein; N1002K changes the C-terminal domain.'), (34, 40, 'Their phase is unresolved: both cis and trans configurations must be evaluated.'), (40, 47, 'AAT becomes AAG, replacing asparagine with lysine at residue 1002.'), (47, 54, 'The longer, positively charged side chain changes local interaction possibilities.'), (54, 60, 'This chemistry motivates a structural hypothesis; it does not establish dysfunction.'), (60, 67, 'The wild-type model places N1002 in a locally confident structural region.'), (67, 74, 'Calculated solvent exposure and short polar contacts define its local environment.'), (74, 80, 'We therefore test whether N1002K reduces the stable, functional protein pool.'), (80, 88, 'Our working mechanism is partial loss of function through altered stability or regulation.'), (88, 96, 'Reduced BUBR1 could weaken checkpoint control and PP2A-B56-dependent attachment regulation.'), (96, 105, 'The predicted consequence is more chromosome-segregation errors: our primary functional endpoint.'), (105, 113, 'We propose sodium phenylbutyrate, 4-PBA, as the lead repurposed candidate.'), (113, 121, 'The premise: N1002K retains useful activity, but instability limits protein availability.'), (121, 129, 'Improved proteostasis could restore the stable pool and recover BUBR1-dependent control.'), (129, 137, 'The predicted benefit is better chromosome segregation, beyond increased protein abundance.'), (137, 144, 'Rescue must occur at feasible exposure without expanding genomically unstable cells.'), (144, 150, 'These predictions make 4-PBA our priority for functional testing.'), (150, 157, 'NMN probes NAD+/SIRT2-dependent abundance; TUDCA offers another proteostasis hypothesis.'), (157, 165, 'Amlexanox separately tests readthrough of the p.Leu737Ter premature-stop allele.'), (165, 173, 'Test candidates separately in cells reproducing the confirmed genotype and allele phase.'), (173, 180, 'Advance the candidate that reproducibly restores segregation fidelity at non-toxic exposure.')]


def frame(t: float, width: int = 1280, supersample: float = 1.5) -> Image.Image:
    global ACTUAL_TIME, STORY_TIME
    ACTUAL_TIME = t
    STORY_TIME = story_clock(t)
    c = Canvas(width, supersample)

    # Subtle mathematical coordinate grid
    for x in range(160, 1920, 160):
        c.line([(x, 80), (x, 900)], GRAY, width=1.0, alpha=0.055)
    for y in range(140, 920, 140):
        c.line([(100, y), (1820, y)], GRAY, width=1.0, alpha=0.055)

    # Execute continuous overlapping storyboard acts
    act1_and_2_checkpoint_to_genetics(c, STORY_TIME)
    act3_atomic_substitution(c, STORY_TIME)
    act4_structural_context(c, STORY_TIME)
    act5_checkpoint_failure(c, STORY_TIME)
    act6_treatment_4pba(c, STORY_TIME)
    act7_alternative_probes(c, STORY_TIME)
    act8_functional_rescue(c, STORY_TIME)

    # Clean Voiceover Subtitle Bar & Progress Timeline
    for a, b, cap_text in CAPTIONS:
        o = visible(t, a, b, 0.55, 0.55)
        if o > 0.002:
            caption_size = min(31, 1650/max(1, c.font(31).getlength(cap_text)/c.scale)*31)
            c.text(cap_text, (960.0, 965.0), caption_size, WHITE, o)

    c.line([(120.0, 1020.0), (1800.0, 1020.0)], GRAY, width=1.5, alpha=0.30)
    c.line([(120.0, 1020.0), (120.0 + 1680.0 * clamp(t / DURATION), 1020.0)], BLUE, width=2.5, alpha=0.85)

    return c.finish()


# ---------------------------------------------------------------------------
# CLI & FFMPEG RENDER PIPELINE
# ---------------------------------------------------------------------------

def get_ffmpeg() -> str:
    binary = shutil.which('ffmpeg')
    if binary:
        return binary
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit('Install imageio-ffmpeg (pip install -r requirements.txt) or provide FFmpeg on PATH.')


def render(args):
    width, fps, ss = {
        'draft': (960, 30, 1.0),
        'preview': (1280, 30, 1.0),
        'final': (1920, 60, 1.0),
    }[args.quality]
    width = args.width or width
    fps = args.fps or fps
    if args.supersample is not None:
        ss = args.supersample
    if width % 2:
        raise SystemExit('--width must be even.')
    height = round(width * 9 / 16)
    if height % 2:
        raise SystemExit('Choose a width giving an even 16:9 height, such as 960, 1280 or 1920.')
    start = max(0.0, args.start)
    end = min(DURATION, args.end)
    if end <= start:
        raise SystemExit('--end must be later than --start.')

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    total = round((end - start) * fps)

    cmd = [
        get_ffmpeg(), '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}', '-pix_fmt', 'rgb24', '-r', str(fps), '-i', '-',
        '-an', '-c:v', 'libx264', '-preset', args.preset, '-crf', str(args.crf),
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    begun = time.perf_counter()
    backend_name = 'PyCairo Vector AA' if HAS_CAIRO else f'PIL Supersampled ({max(ss, 4.0):.2f}x)'
    print(f'Rendering with {backend_name} | {width}x{height} @ {fps}fps')

    try:
        for n in range(total):
            image = frame(start + n / fps, width, ss)
            p.stdin.write(image.tobytes())
            if n % (fps * 5) == 0:
                elapsed = time.perf_counter() - begun
                print(f'{100 * n / total:5.1f}% | t={start + n / fps:6.1f}s | {n / max(elapsed, .001):.1f} frames/s',
                      flush=True)
        p.stdin.close()
        code = p.wait()
        if code:
            raise SystemExit(f'FFmpeg returned {code}')
    except (BrokenPipeError, KeyboardInterrupt):
        p.kill()
        p.wait()
        raise SystemExit('Render interrupted. A partial MP4 may need to be deleted.')
    except BaseException:
        p.kill()
        p.wait()
        raise
    print(f'Saved {output.resolve()} | {total / fps:.3f}s | {width}x{height} | {fps} fps')


def stills(args):
    out = Path(args.stills_dir)
    out.mkdir(parents=True, exist_ok=True)
    times = [11, 29, 49, 70, 97, 125, 152, 174]
    for t in times:
        frame(t, 1280, 4.0).save(out / f'frame_{t:03}.png')
    sheet = Image.new('RGB', (1280, 1440), BG)
    for i, t in enumerate(times):
        im = Image.open(out / f'frame_{t:03}.png').resize((640, 360), Image.Resampling.LANCZOS)
        sheet.paste(im, ((i % 2) * 640, (i // 2) * 360))
    sheet.save(out / 'storyboard.png')
    print('Saved annotated stills and storyboard:', out.resolve())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--quality', choices=['draft', 'preview', 'final'], default='preview')
    p.add_argument('--width', type=int)
    p.add_argument('--fps', type=int)
    p.add_argument('--supersample', type=float)
    p.add_argument('--start', type=float, default=0.0)
    p.add_argument('--end', type=float, default=DURATION)
    p.add_argument('--output', default='renders/BUB1B_explainer.mp4')
    p.add_argument('--preset', default='medium', choices=['ultrafast', 'veryfast', 'fast', 'medium', 'slow'])
    p.add_argument('--crf', type=int, default=18)
    p.add_argument('--stills', action='store_true')
    p.add_argument('--stills-dir', default='renders/stills')
    args = p.parse_args()
    if args.width is not None and args.width < 320:
        p.error('--width must be at least 320')
    if args.fps is not None and args.fps <= 0:
        p.error('--fps must be positive')
    if args.supersample is not None and args.supersample < 1:
        p.error('--supersample must be >= 1')
    if args.stills:
        stills(args)
    else:
        render(args)


if __name__ == '__main__':
    main()