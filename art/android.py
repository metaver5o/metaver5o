"""A raymarched ASCII android head under a Voight-Kampff scan, as an animated SVG.

The head is a signed-distance model (skull, jaw, eye sockets, ear plates, neck
cables, shoulders), lit by a cyan key light and a pink rim light, and every
cell's brightness picks a character from a density ramp.

Usage: python3 android.py out.svg
"""
import math
import sys
from html import escape

COLS, ROWS = 52, 46
CW, CH, FS = 7.2, 13.0, 12
PAD = 10
SCALE = 185.0                       # pixels per model unit
RAMP = " .`:-=+*cox#%@"

PINK, CYAN, AMBER, VIOLET = (255, 46, 136), (0, 234, 255), (255, 176, 0), (185, 103, 255)


# ---------------------------------------------------------------- SDF helpers
def length(x, y, z):
    return math.sqrt(x * x + y * y + z * z)


def sd_ellipsoid(p, r):
    x, y, z = p[0] / r[0], p[1] / r[1], p[2] / r[2]
    k0 = length(x, y, z)
    k1 = length(x / r[0], y / r[1], z / r[2])
    return k0 * (k0 - 1.0) / max(k1, 1e-6)


def sd_round_box(p, b, rad):
    q = [abs(p[i]) - b[i] for i in range(3)]
    return length(*(max(v, 0.0) for v in q)) + min(max(q[0], max(q[1], q[2])), 0.0) - rad


def sd_sphere(p, c, r):
    return length(p[0] - c[0], p[1] - c[1], p[2] - c[2]) - r


def sd_cyl_y(p, c, r, y0, y1):
    d = math.hypot(p[0] - c[0], p[2] - c[2]) - r
    return max(d, y0 - p[1], p[1] - y1)


def sd_cyl_x(p, c, r, h):
    d = math.hypot(p[1] - c[1], p[2] - c[2]) - r
    return max(d, abs(p[0] - c[0]) - h)


def smin(a, b, k):
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h * h * k * 0.25


def smax(a, b, k):
    return -smin(-a, -b, k)


EYES = [(-0.2, 0.3, 0.5), (0.2, 0.3, 0.5)]


def scene(p):
    """Returns (distance, material). Material 1 = shell, 2 = eye."""
    x, y, z = p
    skull = sd_ellipsoid((x, y - 0.38, z), (0.52, 0.64, 0.58))
    jaw = sd_round_box((x, y + 0.2, z - 0.06), (0.3, 0.2, 0.34), 0.14)
    head = smin(skull, jaw, 0.25)
    # brow ridge and a seam across the face plate
    head = smin(head, sd_round_box((x, y - 0.47, z - 0.42), (0.36, 0.03, 0.08), 0.03), 0.08)
    head = smax(head, -sd_round_box((x, y - 0.06, z - 0.5), (0.4, 0.008, 0.2), 0.0), 0.02)
    for e in EYES:
        head = smax(head, -sd_sphere(p, (e[0], e[1], e[2] + 0.06), 0.13), 0.04)
    # ear plates
    for s in (-1, 1):
        head = smin(head, sd_cyl_x(p, (0.53 * s, 0.3, 0.0), 0.15, 0.06), 0.04)
    # mouth grille: three shallow slots
    for k in range(3):
        head = smax(head, -sd_round_box((x, y + 0.2 + k * 0.07, z - 0.42), (0.13, 0.012, 0.1), 0.0), 0.01)
    neck = sd_cyl_y(p, (0, 0, -0.02), 0.16, -0.95, -0.3)
    for s in (-1, 1):
        neck = min(neck, sd_cyl_y(p, (0.14 * s, 0, 0.05), 0.045, -0.95, -0.25))
    body = sd_ellipsoid((x, y + 1.18, z), (0.86, 0.32, 0.44))
    d = min(smin(head, neck, 0.06), smin(body, neck, 0.1))
    de = min(sd_sphere(p, e, 0.085) for e in EYES)
    return (de, 2) if de < d else (d, 1)


def normal(p):
    e = 1e-3
    d = lambda q: scene(q)[0]
    nx = d((p[0] + e, p[1], p[2])) - d((p[0] - e, p[1], p[2]))
    ny = d((p[0], p[1] + e, p[2])) - d((p[0], p[1] - e, p[2]))
    nz = d((p[0], p[1], p[2] + e)) - d((p[0], p[1], p[2] - e))
    n = length(nx, ny, nz)
    return nx / n, ny / n, nz / n


def norm3(v):
    n = length(*v)
    return v[0] / n, v[1] / n, v[2] / n


KEY = norm3((-0.9, 0.5, 0.8))
RIM = norm3((1.0, 0.15, -0.5))
TOP = norm3((0.0, 1.0, 0.2))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hexc(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, v)) for v in c)


# ---------------------------------------------------------------- render
cells, eyes = {}, {}
OX, OY = COLS / 2, ROWS / 2 - 3.5
for r in range(ROWS):
    for c in range(COLS):
        x = (c + 0.5 - OX) * CW / SCALE
        y = -(r + 0.5 - OY) * CH / SCALE
        p, t, hit = (x, y, 3.0), 0.0, None
        for _ in range(90):
            q = (x, y, 3.0 - t)
            d, m = scene(q)
            if d < 1e-3:
                hit = (q, m)
                break
            t += d
            if t > 6:
                break
        if not hit:
            continue
        q, m = hit
        if m == 2:
            eyes[(c, r)] = "@"
            continue
        n = normal(q)
        key = max(0.0, n[0] * KEY[0] + n[1] * KEY[1] + n[2] * KEY[2])
        rim = max(0.0, 1.0 - n[2]) ** 2.2 * max(0.0, n[0] * RIM[0] + n[1] * RIM[1] + n[2] * RIM[2] + 0.35)
        top = max(0.0, n[1] * TOP[1] + n[2] * TOP[2]) * 0.25
        lum = min(1.0, (0.03 + key * 0.62 + rim * 0.95 + top * 0.7) ** 1.15)
        g = RAMP[min(len(RAMP) - 1, int(lum * (len(RAMP) - 1) + 0.5))]
        if g == " ":
            g = "."
        base = PINK if rim * 1.1 > key * 0.85 else CYAN
        col = mix((22, 18, 48), base, min(1.0, 0.25 + lum))
        cells[(c, r)] = (g, hexc(col))

# ---------------------------------------------------------------- VK overlay
hud = {}


def hud_text(c, r, s, col):
    for i, ch in enumerate(s):
        if ch != " ":
            hud[(c + i, r)] = (ch, col)


DIM = "#6f63b8"
hud_text(0, 0, "┌─ VOIGHT-KAMPFF ─────────────────────┐", DIM)
hud_text(0, 1, "│ SUBJECT  metaver5o.eth   NEXUS-6    │", "#a99bff")
hud_text(0, 2, "└─────────────────────────────────────┘", DIM)
for c0, r0, s in ((0, 4, "┌"), (COLS - 1, 4, "┐"), (0, ROWS - 1, "└"), (COLS - 1, ROWS - 1, "┘")):
    hud[(c0, r0)] = (s, DIM)
hud_text(1, ROWS - 4, "IRIS FLUCTUATION .... 0.83", "#a99bff")
hud_text(1, ROWS - 3, "EMPATHIC RESPONSE ... ▮▮▮▮▮▮▮▯", "#a99bff")
hud_text(1, ROWS - 2, "VERDICT ............. MORE HUMAN THAN HUMAN", "#ff8fc0")

# reticle around the left eye
left_eye = [(c, r) for (c, r) in eyes if c < COLS / 2]
ex = round(sum(c for c, r in left_eye) / len(left_eye))
ey = round(sum(r for c, r in left_eye) / len(left_eye))
ret = {}
for (dc, dr, ch) in ((-3, -2, "┌"), (3, -2, "┐"), (-3, 2, "└"), (3, 2, "┘"), (-4, 0, "─"), (4, 0, "─"), (0, -3, "│"), (0, 3, "│")):
    ret[(ex + dc, ey + dr)] = (ch, AMBER and "#ffb000")
ret_label = {}
for i, ch in enumerate("LOCK"):
    ret_label[(ex - 12 + i, ey - 2)] = (ch, "#ffb000")


def runs(cm, x0=0.0, y0=0.0):
    out, rows = [], {}
    for (c, r), (g, col) in cm.items():
        rows.setdefault(r, []).append((c, g, col))
    for r in sorted(rows):
        spans, cur = [], None
        for c, g, col in sorted(rows[r]):
            if cur and cur[0] == col and cur[1][-1] == c - 1:
                cur[1].append(c); cur[2].append(g)
            else:
                cur = [col, [c], [g]]; spans.append(cur)
        y = y0 + r * CH + CH * 0.8
        out.append(f'<text y="{y:.1f}">' + "".join(
            f'<tspan x="{" ".join(f"{x0 + c * CW:.1f}" for c in cs)}" fill="{col}">{escape("".join(gs))}</tspan>'
            for col, cs, gs in spans) + "</text>")
    return "\n".join(out)


W, H = COLS * CW + 2 * PAD, ROWS * CH + 2 * PAD
eye_cells = {k: (v, "#ff5a1f") for k, v in eyes.items()}
css = f"""
text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace; font-size: {FS}px; white-space: pre; }}
.eyes {{ filter: url(#glow); animation: pulse 2.4s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .55; }} }}
.ret {{ animation: lock 3s steps(1) infinite; }}
@keyframes lock {{ 0%,70% {{ opacity: 1; }} 75% {{ opacity: 0; }} 80% {{ opacity: 1; }} 85% {{ opacity: 0; }} 90% {{ opacity: 1; }} }}
.scan {{ animation: scan 4.5s linear infinite; }}
@keyframes scan {{ from {{ transform: translate(0, {PAD + 3 * CH:.0f}px); }} to {{ transform: translate(0, {PAD + (ROWS - 5) * CH:.0f}px); }} }}
.verdict {{ animation: hum 4s infinite; }}
@keyframes hum {{ 0%,88%,92%,100% {{ opacity: 1; }} 90% {{ opacity: .3; }} }}
.head {{ filter: url(#soft); }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""
verdict = {k: v for k, v in hud.items() if k[1] == ROWS - 2}
hud_rest = {k: v for k, v in hud.items() if k[1] != ROWS - 2}
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="ASCII android head under a Voight-Kampff scan, glowing eyes, verdict: more human than human">
<style>{css}</style>
<defs>
<radialGradient id="bg" cx=".5" cy=".42" r=".65"><stop offset="0" stop-color="#1a1238"/><stop offset="1" stop-color="#05040d"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00eaff" stop-opacity="0"/><stop offset=".85" stop-color="#00eaff" stop-opacity=".18"/><stop offset="1" stop-color="#00eaff" stop-opacity=".7"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation=".7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="url(#bg)"/>
<g class="head">{runs(cells, PAD, PAD)}</g>
<g class="eyes">{runs(eye_cells, PAD, PAD)}</g>
<g>{runs(hud_rest, PAD, PAD)}</g>
<g class="verdict">{runs(verdict, PAD, PAD)}</g>
<g class="ret">{runs(ret, PAD, PAD)}{runs(ret_label, PAD, PAD)}</g>
<g class="scan"><rect x="{PAD}" y="-26" width="{COLS * CW:.0f}" height="26" fill="url(#beam)"/><rect x="{PAD}" y="-1" width="{COLS * CW:.0f}" height="1.2" fill="#9ff6ff"/></g>
</svg>"""
open(sys.argv[1], "w").write(svg)
print(f"{W:.0f}x{H:.0f}", len(svg) // 1024, "KB", len(cells), "shell cells,", len(eyes), "eye cells")
