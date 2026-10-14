"""Blade Runner skyline for the metaver5o GitHub profile, as an animated SVG.

Everything is drawn on a character grid, then emitted as positioned <text>
runs (one x per glyph, so columns hold even when a font's block glyphs differ
in width). Animated layers live in their own <g> with CSS keyframes, which
GitHub keeps when the SVG is shown through <img>.

Usage: python3 skyline.py out.svg
"""
import random
import sys
from html import escape

random.seed(2019)

COLS, ROWS = 140, 48
CW, CH, FS = 7.2, 13.0, 12          # cell width, cell height, font size (px)
PAD_TOP = 6
SCENE_H = ROWS * CH
W = COLS * CW
HORIZON = 41

# Palette
NIGHT = "#05040d"
MEGA, FAR, FAR_WIN = "#120f2b", "#1d1840", "#3d3470"
PYR_EDGE, PYR_BODY, PYR_LIT = "#d69a45", "#4a3016", "#ffb347"
MID = "#191433"
PINK, CYAN, AMBER, VIOLET, RED, GREEN = "#ff2e88", "#00eaff", "#ffb000", "#b967ff", "#ff3b3b", "#39ff9f"


class Layer:
    """A sparse grid of (char, color) cells."""

    def __init__(self):
        self.cells = {}

    def put(self, c, r, ch, color):
        if 0 <= c < COLS and 0 <= r < ROWS and ch != " ":
            self.cells[(c, r)] = (ch, color)

    def text(self, c, r, s, color):
        for i, ch in enumerate(s):
            self.put(c + i, r, ch, color)

    def vtext(self, c, r, s, color):
        for i, ch in enumerate(s):
            self.put(c, r + i, ch, color)


def runs(cells, x0=0.0, y0=0.0, cw=CW, ch=CH):
    """Emit <text> rows grouping consecutive same-color cells into tspans."""
    out, rows = [], {}
    for (c, r), (g, col) in cells.items():
        rows.setdefault(r, []).append((c, g, col))
    for r in sorted(rows):
        spans, cur = [], None
        for c, g, col in sorted(rows[r]):
            if cur and cur[0] == col and cur[1][-1] == c - 1:
                cur[1].append(c); cur[2].append(g)
            else:
                cur = [col, [c], [g]]; spans.append(cur)
        y = y0 + r * ch + ch * 0.8
        parts = []
        for col, cs, gs in spans:
            xs = " ".join(f"{x0 + c * cw:.1f}" for c in cs)
            parts.append(f'<tspan x="{xs}" fill="{col}">{escape("".join(gs))}</tspan>')
        out.append(f'<text y="{y:.1f}">{"".join(parts)}</text>')
    return "\n".join(out)


# ---------------------------------------------------------------- scene
sky, mega, far, pyr, mid, street, reflect = (Layer() for _ in range(7))
pyr_tw = [Layer() for _ in range(3)]
win_tw = [Layer() for _ in range(4)]
neon = {}

# Stars and smog specks
for _ in range(110):
    c, r = random.randrange(COLS), random.randrange(0, 16)
    sky.put(c, r, random.choice(".·.'`"), random.choice(["#2c2a55", "#3b3570", "#4b4590"]))

# Megastructures: a few huge, barely-there slabs behind everything
for x0, w, h in [(8, 14, 33), (52, 10, 30), (100, 16, 36), (124, 12, 31)]:
    for x in range(x0, x0 + w):
        for y in range(HORIZON - h, HORIZON):
            mega.put(x, y, "▒" if (x + y) % 7 else "░", MEGA)
    for y in range(HORIZON - h + 2, HORIZON, 3):
        mega.put(x0 + 2, y, "-", "#2b2358")
    mega.put(x0 + w // 2, HORIZON - h - 1, "'", RED)

# Far skyline: dense, dim, textured
c = 0
while c < COLS:
    w, h = random.randint(3, 9), random.randint(8, 25)
    top = HORIZON - h
    for x in range(c, min(COLS, c + w)):
        for y in range(top, HORIZON):
            far.put(x, y, "░", FAR)
            if random.random() < 0.07:
                far.put(x, y, "·", FAR_WIN)
    if random.random() < 0.35:
        far.put(c + w // 2, top - 1, "|", FAR)
        far.put(c + w // 2, top - 2, "'", RED)
    c += w + random.randint(0, 2)


# Back-street district on the far blocks: Neo Tokyo crossed with a future
# Chinatown. Kanji/kana neon plates, lantern strings and a pagoda crown, dimmed
# by haze so they sit behind the pyramids and the front neon. The plates are
# vector (a dark board with a neon tube border) so the CJK glyphs can be set
# larger than the grid allows.
BG_FS, BG_STEP = 15, 17
BG_SIGNS = [  # (class, col, row, text, colour, vertical)
    ("b1", 9, 9, "電脳街", "#ff4fd8", True),
    ("b2", 16, 8, "酒", AMBER, True),
    ("b8", 13, 14, "薬", GREEN, True),
    ("b3", 53, 12, "九龍城", RED, True),
    ("b4", 58, 13, "暗号", CYAN, True),
    ("b5", 100, 14, "ネオ東京", "#7ff6ff", False),
    ("b6", 103, 17, "未来", RED, False),
    ("b7", 126, 14, "龍門", "#ff6a3d", True),
    ("b8", 108, 20, "鍵", GREEN, True),
    ("b1", 120, 16, "夜", "#ff4fd8", True),
]


def bg_signs():
    out = []
    for cls, c, r, text, col, down in BG_SIGNS:
        x, y = c * CW, PAD_TOP + r * CH
        n = len(text)
        w, h = (BG_STEP + 6, n * BG_STEP + 6) if down else (n * BG_STEP + 8, BG_STEP + 6)
        rx = h / 2 if cls == "b6" else 2       # 未来 is a capsule
        glyphs = "".join(
            f'<text x="{x + w / 2 if down else x + 4 + (i + .5) * BG_STEP:.1f}" y="{y + 3 + (i + .82) * BG_STEP if down else y + 3 + .82 * BG_STEP:.1f}" '
            f'text-anchor="middle" fill="{col}">{ch}</text>' for i, ch in enumerate(text))
        out.append(f'<g class="{cls}"><rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="{rx}" fill="#0a0716" fill-opacity=".8" stroke="{col}" stroke-width="1.2"/>{glyphs}</g>')
    out.append(f'<text class="b5" x="{100 * CW + 4 * BG_STEP + 14:.1f}" y="{PAD_TOP + 14 * CH + 17:.1f}" fill="#7ff6ff" style="font-size:11px">2019</text>')
    return "".join(out)


def lantern_strings():
    out = []
    for k, (x0, x1, row, sag) in enumerate([(23, 36, 16, 12), (62, 72, 14, 9), (116, 125, 16, 7), (36, 50, 20, 10)]):
        X0, X1, Y = x0 * CW, x1 * CW, PAD_TOP + row * CH
        out.append(f'<path d="M{X0:.0f} {Y:.0f} Q{(X0 + X1) / 2:.0f} {Y + 2 * sag:.0f} {X1:.0f} {Y:.0f}" fill="none" stroke="#5a3a6a" stroke-width="1"/>')
        n = max(3, int((X1 - X0) // 12))
        for i in range(1, n):
            t = i / n
            lx = X0 + (X1 - X0) * t
            ly = Y + 2 * sag * 2 * t * (1 - t) + 1
            colr = [RED, "#ff6a3d", RED, AMBER][(i + k) % 4]
            out.append(f'<g class="lan{(i + k) % 2}"><circle cx="{lx:.1f}" cy="{ly + 2:.1f}" r="3.5" fill="{colr}" opacity=".2"/>'
                       f'<rect x="{lx - 1.5:.1f}" y="{ly:.1f}" width="3" height="4" rx="1.5" fill="{colr}"/></g>')
    return "".join(out)


# Pagoda tower on a far block between the pyramids
pagoda = Layer()
for x in range(63, 70):
    for y in range(24, HORIZON):
        far.put(x, y, "▒" if (x + y) % 5 else "░", "#16122f")
for row, half in [(18, 1), (20, 2), (22, 3), (24, 4)]:
    pagoda.text(66 - half - 1, row, "/" + "‾" * (2 * half + 1) + "\\", "#c8483a")
    if half > 1:
        pagoda.text(66 - half + 1, row + 1, "▪ " * half, "#ffb347")
pagoda.put(66, 17, "†", "#ffb347")
for y in range(26, 38, 2):
    pagoda.text(64, y, "▪ ▪", random.choice([AMBER, "#ff6a3d"]))

# Hologram koi swimming slowly across the upper sky
koi = Layer()
koi.text(0, 0, "  ,__", "#7ff6ff")
koi.text(0, 1, "><(((°>", "#ff8ad8")
koi.put(0, 1, ">", "#7ff6ff"); koi.put(1, 1, "<", "#7ff6ff")
koi.text(2, 2, "`‾‾", "#7ff6ff")

def pyramid(cx, apex, base, slope, tw_prob):
    for r in range(apex, base):
        hw = int((r - apex) * slope)
        for x in range(cx - hw, cx + hw + 1):
            pyr.put(x, r, ":" if (x + r) % 2 else ".", PYR_BODY)
            if (r - apex) % 3 == 1 and (x - cx) % 4 == 0 and random.random() < tw_prob:
                random.choice(pyr_tw).put(x, r, "▪", PYR_LIT)
        pyr.put(cx - hw - 1, r, "/", PYR_EDGE)
        pyr.put(cx + hw + 1, r, "\\", PYR_EDGE)
        if r % 4 == 0:  # terraces
            for x in range(cx - hw, cx + hw + 1):
                pyr.put(x, r, "_", PYR_EDGE)
    pyr.put(cx, apex - 1, "▲", PYR_LIT)


pyramid(44, 23, HORIZON, 1.3, 0.45)
pyramid(86, 12, HORIZON, 1.35, 0.55)

# Mid towers in front: stepped tops, windows, antenna beacons
towers = [(0, 9, 18), (11, 6, 11), (19, 8, 22), (61, 6, 8), (113, 8, 20), (123, 6, 13), (131, 9, 25)]
for x0, w, h in towers:
    top = HORIZON - h
    for x in range(x0, min(COLS, x0 + w)):
        for y in range(top, HORIZON):
            mid.put(x, y, "▓", MID)
    if w > 6:  # setback crown
        for x in range(x0 + 2, min(COLS, x0 + w - 2)):
            mid.put(x, top - 1, "▄", MID)
    for y in range(top + 1, HORIZON - 1, 2):
        for x in range(x0 + 1, min(COLS, x0 + w) - 1, 2):
            if random.random() < 0.4:
                random.choice(win_tw).put(x, y, "▪", random.choice([AMBER, AMBER, CYAN, "#ffd27a", PINK]))
    ax = x0 + w // 2
    for k in range(2, 5):
        mid.put(ax, top - k, "|", "#3a3366")
    mid.put(ax, top - 5, "*", RED)


def sign(cls, fn):
    fn(neon.setdefault(cls, Layer()))


sign("n1", lambda L: L.vtext(2, HORIZON - 15, "NEXUS-6", PINK))
sign("n2", lambda L: L.vtext(22, HORIZON - 19, "ENHANCE", CYAN))
sign("n3", lambda L: L.vtext(115, HORIZON - 17, "2-OF-3", AMBER))
sign("n4", lambda L: L.vtext(133, HORIZON - 22, "OFF-WORLD", VIOLET))
sign("n6", lambda L: L.text(124, HORIZON - 11, "PSBT", GREEN))
sign("n7", lambda L: L.vtext(13, HORIZON - 9, "0x5AFE", RED))

# Floating hologram billboard (drifts gently, flickers)
holo = Layer()
holo.text(0, 0, "┌──────────────────────────┐", "#7b5cff")
holo.text(0, 1, "│  support my open work at │", "#c9b8ff")
holo.text(0, 2, "│  ░░ metaver5o.eth ░░     │", CYAN)
holo.text(0, 3, "└──────────────────────────┘", "#7b5cff")
holo.put(4, 2, "░", "#2b4d6b"); holo.put(5, 2, "░", "#2b4d6b")
holo.put(20, 2, "░", "#2b4d6b"); holo.put(21, 2, "░", "#2b4d6b")
HOLO_S = 1.45
HOLO_X, HOLO_Y = 95 * CW, PAD_TOP + 6 * CH

# Flare stacks: two flame frames alternate
flame_a, flame_b = Layer(), Layer()
for fx in (31, 70, 104):
    for y in range(HORIZON - 6, HORIZON):
        mid.put(fx, y, "║", "#3a2f5e")
    mid.text(fx - 1, HORIZON - 6, "╔╩╗", "#3a2f5e")
    for L, shape in ((flame_a, [" ' ", " ^ ", "(^)", "/█\\"]), (flame_b, ["'  ", " ) ", "(▲)", "\\█/"])):
        for k, (row, col) in enumerate(zip(shape, ["#fff1a8", "#ffd000", "#ff8c00", "#ff4500"])):
            L.text(fx - 1, HORIZON - 10 + k, row, col)

# Street and neon bleeding into the wet asphalt
street.text(0, HORIZON, "▔" * COLS, "#2b2650")
for r in range(HORIZON + 1, ROWS):
    for x in range(COLS):
        if random.random() < 0.10:
            street.put(x, r, random.choice("_.-~"), "#1f1b3d")
for L in neon.values():
    for c, col in {c: col for (c, r), (g, col) in L.cells.items()}.items():
        for r in range(HORIZON + 1, ROWS):
            if random.random() < 0.75:
                reflect.put(c, r, random.choice("│¦:'"), col)
for t in win_tw:
    for (c, r), (g, col) in t.cells.items():
        if r > HORIZON - 6 and random.random() < 0.5:
            reflect.put(c, HORIZON + 1 + random.randint(0, 2), random.choice(":.'"), col)
for fx in (31, 70, 104):
    for r in range(HORIZON + 1, ROWS):
        if random.random() < 0.8:
            reflect.put(fx + random.randint(-1, 1), r, random.choice("¦:'~"), "#ff8c00")

# Splashes: little rings on the street, blinking at different rates
splash = [Layer() for _ in range(5)]
for _ in range(70):
    random.choice(splash).put(random.randrange(COLS), random.randrange(HORIZON + 1, ROWS), random.choice("o.°˙"), "#8fa3ff")


# Rain: vertical streaks, in three depths
def rain_tile(n, length, colors):
    L = Layer()
    for _ in range(n):
        c, r = random.randrange(COLS), random.randrange(ROWS)
        for k in range(length):
            L.put(c, r + k, "│" if k else "╵", colors[min(k, len(colors) - 1)])
    return L


rain_far = rain_tile(170, 1, ["#3a4a8a"])
rain_mid = rain_tile(120, 2, ["#4f64b8", "#6a80d6"])
rain_near = rain_tile(55, 3, ["#7f93ec", "#9db0ff", "#c4d0ff"])

# Spinner
spinner = Layer()
spinner.text(0, 0, "   _.--==--._", "#9aa4c8")
spinner.text(0, 1, " <[_oo_][_oo_]>", "#c9d1f0")
spinner.put(1, 1, "<", RED); spinner.put(14, 1, ">", CYAN)
spinner.text(3, 2, "'  ^^  ^^ '", "#4a5aa0")
spinner.text(15, 1, "≡≡≡", "#3d6bff")

# Walking robots: two leg poses each, sliding back and forth along the street.
# (frame A rows, frame B rows, body colour, eye colour, x from, x to, seconds)
BOTS = [
    ([" [o] ", "/|_|\\", " / \\ "], [" [o] ", "/|_|\\", " | | "], "#9aa4c8", CYAN, 12, 46, 23),
    ([" .-. ", "(o.o)", " |=| ", " / \\ "], [" .-. ", "(o.o)", " |=| ", " | | "], "#b9a7ff", PINK, 40, 70, 17),
    (["  O  ", " /|\\ ", " / \\ "], ["  O  ", " /|\\ ", " | | "], "#e6e2ff", AMBER, 58, 96, 29),
    (["  |  ", " [::]", " d  b"], ["  |  ", " [::]", "  db "], "#7fd6ff", RED, 78, 112, 21),
    (["_[]_ ", "(oooo)"], ["_[]_ ", "(OOOO)"], "#ffb000", GREEN, 92, 124, 26),
    ([" /\\_/\\ ", "/ (o) \\", " /\\ /\\ "], [" /\\_/\\ ", "/ (o) \\", " \\/ \\/ "], "#ff7ab8", CYAN, 22, 60, 33),
]
EYE_CHARS = set("o0O@")
BOT_NAMES = ["N3--8", "bN&&e", "0xR7", "Q5:k", "Z-9V3", "T4$$"]

# Speeder bike, low over the wet street, with an exhaust trail
speeder = Layer()
speeder.text(5, 0, "__o", "#e6e2ff")
speeder.text(0, 1, "≈≈≈<=[__/|_\\", "#9aa4c8")
speeder.text(0, 1, "≈≈≈", "#ff2e88")
speeder.put(4, 1, "=", CYAN)
speeder.text(5, 2, "'-------'", "#3d6bff")
SPEEDER_Y = PAD_TOP + (HORIZON + 2) * CH


def bot_layer(rows, body, eye):
    L = Layer()
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            L.put(c, r, ch, eye if ch in EYE_CHARS else body)
    return L


# ---------------------------------------------------------------- title
sys.path.insert(0, __import__("os").path.dirname(__file__))
from ansi_shadow import G, render
title = render("METAVER5O")
TCW, TCH, TT = 11.0, 13.0, 2.4      # title cell size, shadow stroke width
tw = max(len(l) for l in title) * TCW
tx0 = (W - tw) / 2
ty0 = PAD_TOP + SCENE_H + 24


def title_shapes():
    """Draw the figlet letters as rectangles, so no font can open gaps.

    Solid blocks become chrome cells; the box-drawing shadow becomes thin
    strokes through the cell centre."""
    start = sum(len(G[ch][0]) + 1 for ch in "METAVER")
    five = range(start, start + len(G["5"][0]))
    solid, shade, neon5 = [], [], []
    for r, line in enumerate(title):
        for c, g in enumerate(line):
            x, y = tx0 + c * TCW, ty0 + r * TCH
            mx, my, h = x + TCW / 2, y + TCH / 2, TT / 2
            if g == "█":
                (neon5 if c in five else solid).append((x, y, TCW + 0.4, TCH + 0.4))
            elif g == "═":
                shade.append((x, my - h, TCW + 0.4, TT))
            elif g == "║":
                shade.append((mx - h, y, TT, TCH + 0.4))
            elif g in "╗╝":
                shade.append((x, my - h, TCW / 2 + h, TT))
            elif g in "╔╚":
                shade.append((mx - h, my - h, TCW / 2 + h + 0.4, TT))
            if g in "╗╔":
                shade.append((mx - h, my - h, TT, TCH / 2 + h + 0.4))
            elif g in "╝╚":
                shade.append((mx - h, y, TT, TCH / 2 + h))
    rect = lambda b: f'<rect x="{b[0]:.1f}" y="{b[1]:.1f}" width="{b[2]:.1f}" height="{b[3]:.1f}"/>'
    return "".join(map(rect, solid)), "".join(map(rect, shade)), "".join(map(rect, neon5))


TITLE_SOLID, TITLE_SHADE, TITLE_FIVE = title_shapes()

sub = "S Ã O   P A U L O   ·   O F F - W O R L D   ·   O N - C H A I N"
sub_y = ty0 + len(title) * TCH + 30
H = sub_y + 24

# ---------------------------------------------------------------- CRIPTOGRAFIA sign
# The pyramid sign hashes itself into existence: every column rolls through hex
# digits, then the letters lock in left to right (white flash, then amber), the
# name holds, and it dissolves back into the hash. Each column's roll is a strip
# of digits stepped upward behind a one-line clip. Without animation (reduced
# motion) only the name shows.
BRAND = "CRIPTOGRAFIA"
BRAND_T, BRAND_K, BRAND_LH, BRAND_STAGGER = 11, 10, 22, 0.12
BRAND_ROLL = [0.55 + 0.07 * ((i * 5) % 7) for i in range(len(BRAND))]
BRAND_CX, BRAND_Y, BRAND_ADV = 86 * CW + CW / 2, PAD_TOP + 31 * CH + 11, 14.4


def brand_sign():
    x0 = BRAND_CX - (len(BRAND) - 1) * BRAND_ADV / 2
    clip = (f'<clipPath id="bclip"><rect x="{x0 - BRAND_ADV:.1f}" y="{BRAND_Y - 17:.1f}" '
            f'width="{(len(BRAND) + 1) * BRAND_ADV:.1f}" height="{BRAND_LH:.0f}"/></clipPath>')
    cols = []
    for i, letter in enumerate(BRAND):
        x = x0 + i * BRAND_ADV
        digits = [random.choice("0123456789abcdef") for _ in range(BRAND_K)]
        strip = "".join(f'<text x="{x:.1f}" y="{BRAND_Y + k * BRAND_LH:.1f}" text-anchor="middle">{d}</text>'
                        for k, d in enumerate(digits + digits[:1]))
        cols.append(f'<g class="bh c{i}"><g class="hs{i}">{strip}</g></g>'
                    f'<text class="bl c{i}" x="{x:.1f}" y="{BRAND_Y:.1f}" text-anchor="middle">{letter}</text>')
    return f'<g class="brand">{clip}<g clip-path="url(#bclip)">{"".join(cols)}</g></g>'


# ---------------------------------------------------------------- emit
css = f"""
text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace; font-size: {FS}px; white-space: pre; }}
.sub {{ font-size: 13px; fill: #8f86c9; }}
.rf {{ animation: fall 2.2s linear infinite; opacity: .45; }}
.rm {{ animation: fall 1.3s linear infinite; opacity: .6; }}
.rn {{ animation: fall .8s linear infinite; opacity: .8; }}
@keyframes fall {{ from {{ transform: translate(0, -{SCENE_H:.0f}px); }} to {{ transform: translate(0, 0); }} }}
.spinner {{ animation: fly 18s linear infinite -7s; }}
.bgneon {{ opacity: .7; filter: url(#glow); }}
.bgsign text {{ font-size: {BG_FS}px; font-weight: 700; }}
.b1 {{ animation: buzz 7s infinite 1.5s; }} .b3 {{ animation: buzz 9s infinite 3s; }} .b5 {{ animation: holoflick 3.4s infinite; }}
.b6 {{ animation: buzz 5s infinite .5s; }} .b7 {{ animation: buzz 12s infinite 6s; }} .b8 {{ animation: tw 6s infinite 2s; }} .b2 {{ animation: buzz 8s infinite 4s; }}
.lan0 {{ animation: tw 4s infinite; }} .lan1 {{ animation: tw 5.5s infinite 1.2s; }}
.koi {{ animation: swim 46s linear infinite -20s; }}
.koiflick {{ opacity: .55; filter: url(#glow); animation: holoflick 4s infinite; }}
@keyframes swim {{ 0% {{ transform: translate(-80px, {PAD_TOP + 3 * CH:.0f}px); }} 50% {{ transform: translate({W / 2:.0f}px, {PAD_TOP + 1 * CH:.0f}px); }} 100% {{ transform: translate({W + 40:.0f}px, {PAD_TOP + 3 * CH:.0f}px); }} }}
.gyro {{ opacity: 0; }}
.gr {{ animation: gyroR 18s linear infinite -7s; }} .gb {{ animation: gyroB 18s linear infinite -7s; }}
@keyframes gyroR {{ 0%,100% {{ opacity: 0; }} 44.0% {{ opacity: 0; }} 44.05%,44.70% {{ opacity: 1; }} 44.75% {{ opacity: 0; }} 45.8% {{ opacity: 0; }} 45.85%,46.50% {{ opacity: 1; }} 46.55% {{ opacity: 0; }} 47.6% {{ opacity: 0; }} 47.65%,48.30% {{ opacity: 1; }} 48.35% {{ opacity: 0; }} 49.4% {{ opacity: 0; }} 49.45%,50.10% {{ opacity: 1; }} 50.15% {{ opacity: 0; }} }}
@keyframes gyroB {{ 0%,100% {{ opacity: 0; }} 44.9% {{ opacity: 0; }} 44.95%,45.60% {{ opacity: 1; }} 45.65% {{ opacity: 0; }} 46.7% {{ opacity: 0; }} 46.75%,47.40% {{ opacity: 1; }} 47.45% {{ opacity: 0; }} 48.5% {{ opacity: 0; }} 48.55%,49.20% {{ opacity: 1; }} 49.25% {{ opacity: 0; }} 50.3% {{ opacity: 0; }} 50.35%,51.00% {{ opacity: 1; }} 51.05% {{ opacity: 0; }} }}
@keyframes fly {{ from {{ transform: translate(-150px, {PAD_TOP + 6 * CH:.0f}px); }} 50% {{ transform: translate({W / 2:.0f}px, {PAD_TOP + 9 * CH:.0f}px); }} to {{ transform: translate({W + 40:.0f}px, {PAD_TOP + 5 * CH:.0f}px); }} }}
.fa {{ animation: fa .5s steps(1) infinite; }} .fb {{ animation: fb .5s steps(1) infinite; }}
@keyframes fa {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
@keyframes fb {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
.tw0 {{ animation: tw 7s infinite; }} .tw1 {{ animation: tw 11s infinite 2s; }} .tw2 {{ animation: tw 5s infinite 1s; }} .tw3 {{ animation: tw 13s infinite 4s; }}
@keyframes tw {{ 0%,45%,55%,100% {{ opacity: 1; }} 50% {{ opacity: .15; }} }}
.sp0 {{ animation: sp 1.1s infinite; }} .sp1 {{ animation: sp 1.7s infinite .3s; }} .sp2 {{ animation: sp .9s infinite .6s; }} .sp3 {{ animation: sp 1.4s infinite .2s; }} .sp4 {{ animation: sp 2s infinite .8s; }}
@keyframes sp {{ 0%,60%,100% {{ opacity: 0; }} 70% {{ opacity: .9; }} 85% {{ opacity: .3; }} }}
.neon, .holo, .flame {{ filter: url(#glow); }}
.n2 {{ animation: buzz 6s infinite; }} .n4 {{ animation: buzz 4.5s infinite 1s; }} .n7 {{ animation: buzz 8s infinite 2s; }}
@keyframes buzz {{ 0%,91%,93%,96%,100% {{ opacity: 1; }} 92% {{ opacity: .2; }} 95% {{ opacity: .35; }} }}
.holo {{ animation: drift 9s ease-in-out infinite, holoflick 2.6s infinite; }}
@keyframes holoflick {{ 0%,100% {{ opacity: 1; }} 7% {{ opacity: .35; }} 8% {{ opacity: 1; }} 27% {{ opacity: .9; }} 28% {{ opacity: .15; }} 29% {{ opacity: .85; }} 30% {{ opacity: .25; }} 31% {{ opacity: 1; }} 55% {{ opacity: 1; }} 56% {{ opacity: .5; }} 57% {{ opacity: 1; }} 78% {{ opacity: .7; }} 79% {{ opacity: .05; }} 81% {{ opacity: 1; }} 90% {{ opacity: .6; }} 91% {{ opacity: 1; }} }}
@keyframes drift {{ 0%,100% {{ transform: translate({HOLO_X:.0f}px, {HOLO_Y:.0f}px); }} 50% {{ transform: translate({HOLO_X - 6:.0f}px, {HOLO_Y + 5:.0f}px); }} }}
.bolt {{ animation: bolt 11s infinite 4s; opacity: 0; }}
@keyframes bolt {{ 0%,90%,92.5%,100% {{ opacity: 0; }} 90.6% {{ opacity: .35; }} 91.2% {{ opacity: .05; }} 91.8% {{ opacity: .25; }} }}
.title {{ filter: url(#chromeglow); }}
.brand {{ filter: url(#glow); animation: buzz 10s infinite 5s; }}
.brand text {{ font-size: 19px; font-weight: 700; }}
.bl {{ fill: #ffb000; animation: lock {BRAND_T}s infinite both; }}
.bh {{ opacity: 0; fill: #00eaff; animation: hashv {BRAND_T}s infinite both; }}
@keyframes lock {{ 0%,19.9% {{ opacity: 0; fill: #ffffff; }} 20% {{ opacity: 1; fill: #ffffff; }} 23% {{ fill: #ffb000; }} 88% {{ opacity: 1; fill: #ffb000; }} 88.1%,100% {{ opacity: 0; }} }}
@keyframes hashv {{ 0%,19.9% {{ opacity: .95; }} 20%,88% {{ opacity: 0; }} 88.1%,100% {{ opacity: .95; }} }}
{"".join(f".hs{i} {{ animation: roll{i} {d:.2f}s steps({BRAND_K}) infinite; }}\n@keyframes roll{i} {{ from {{ transform: translate(0, 0); }} to {{ transform: translate(0, -{BRAND_K * BRAND_LH}px); }} }}\n" for i, d in enumerate(BRAND_ROLL))}
{"".join(f".c{i} {{ animation-delay: {i * BRAND_STAGGER:.2f}s; }}\n" for i in range(len(BRAND)))}
.shine {{ animation: shine 5s ease-in-out infinite 1s; }}
@keyframes shine {{ 0% {{ transform: translate({tx0 - 160:.0f}px, 0) skewX(-22deg); }} 55%,100% {{ transform: translate({tx0 + tw + 60:.0f}px, 0) skewX(-22deg); }} }}
.speeder {{ animation: ride 9s linear infinite -3s; }}
@keyframes ride {{ from {{ transform: translate({W + 40:.0f}px, {SPEEDER_Y:.0f}px) scaleX(-1); }} to {{ transform: translate(-160px, {SPEEDER_Y:.0f}px) scaleX(-1); }} }}
.tag {{ font-size: 9px; opacity: .85; letter-spacing: .5px; }}
.legA {{ animation: fa .45s steps(1) infinite; }} .legB {{ animation: fb .45s steps(1) infinite; }}
.bot {{ filter: url(#glow); }}
{"".join(f"@keyframes walk{i} {{ from {{ transform: translate({x0 * CW:.0f}px, {PAD_TOP + (HORIZON - len(a)) * CH:.0f}px); }} to {{ transform: translate({x1 * CW:.0f}px, {PAD_TOP + (HORIZON - len(a)) * CH:.0f}px); }} }}\n.w{i} {{ animation: walk{i} {t}s linear infinite alternate both {-((i * 3.7 + 2) % t):.1f}s; }}\n" for i, (a, b, body, eye, x0, x1, t) in enumerate(BOTS))}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .bolt, .gyro {{ opacity: 0; }} }}
"""

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Blade Runner style ASCII city at night: CRIPTOGRAFIA pyramids, neon signs, a Neo Tokyo Chinatown in kanji neon with lanterns and a hologram koi, falling rain, a flying spinner, and the name METAVER5O">',
    f"<style>{css}</style>",
    "<defs>",
    '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05040d"/><stop offset=".55" stop-color="#0c0820"/><stop offset=".86" stop-color="#2a0f2e"/><stop offset="1" stop-color="#3d1420"/></linearGradient>',
    f'<linearGradient id="chrome" gradientUnits="userSpaceOnUse" x1="0" y1="{ty0:.0f}" x2="0" y2="{ty0 + 6 * TCH:.0f}"><stop offset="0" stop-color="#ffffff"/><stop offset=".38" stop-color="#c3cbdc"/><stop offset=".5" stop-color="#5d6782"/><stop offset=".56" stop-color="#e9eef8"/><stop offset=".8" stop-color="#9aa3b9"/><stop offset="1" stop-color="#d7deeb"/></linearGradient>',
    f'<linearGradient id="neon5" gradientUnits="userSpaceOnUse" x1="0" y1="{ty0:.0f}" x2="0" y2="{ty0 + 6 * TCH:.0f}"><stop offset="0" stop-color="#ff2e88"/><stop offset="1" stop-color="#00eaff"/></linearGradient>',
    '<linearGradient id="band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
    f'<clipPath id="tclip">{TITLE_SOLID}</clipPath>',
    '<filter id="chromeglow" x="-5%" y="-40%" width="110%" height="180%"><feGaussianBlur in="SourceAlpha" stdDeviation="5" result="b"/><feFlood flood-color="#9fdcff" flood-opacity=".45"/><feComposite in2="b" operator="in" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    '<radialGradient id="haze" cx=".6" cy="1" r=".7"><stop offset="0" stop-color="#ff6a00" stop-opacity=".28"/><stop offset="1" stop-color="#ff6a00" stop-opacity="0"/></radialGradient>',
    '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    '<filter id="glow2" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    f'<clipPath id="scene"><rect x="0" y="{PAD_TOP}" width="{W:.0f}" height="{SCENE_H:.0f}"/></clipPath>',
    "</defs>",
    f'<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="{NIGHT}"/>',
    f'<rect x="0" y="{PAD_TOP}" width="{W:.0f}" height="{SCENE_H:.0f}" fill="url(#sky)"/>',
    f'<rect x="0" y="{PAD_TOP}" width="{W:.0f}" height="{SCENE_H:.0f}" fill="url(#haze)"/>',
    f'<rect class="bolt" x="0" y="{PAD_TOP}" width="{W:.0f}" height="{HORIZON * CH:.0f}" fill="#c9d4ff"/>',
    '<g clip-path="url(#scene)">',
]


def g(cls, layer):
    return f'<g class="{cls}">{runs(layer.cells, 0, PAD_TOP)}</g>'


parts += [g("sky", sky), g("mega", mega), g("far", far)]
parts += [f'<g class="bgneon">{g("pagoda", pagoda)}{lantern_strings()}<g class="bgsign">{bg_signs()}</g></g>']
parts += [f'<g class="koi"><g class="koiflick">{runs(koi.cells)}</g></g>']
parts += [g("pyr", pyr)]
parts += [g(f"tw{i}", L) for i, L in enumerate(pyr_tw)]
parts += [g("mid", mid)]
parts += [g(f"tw{i}", L) for i, L in enumerate(win_tw)]
parts += [g("flame fa", flame_a), g("flame fb", flame_b)]
parts += [g(f"neon {cls}", L) for cls, L in neon.items()]
parts += [brand_sign()]
parts += [f'<g class="holo"><g transform="scale({HOLO_S})">{runs(holo.cells)}</g></g>']
parts += [g("street", street), f'<g opacity=".45">{runs(reflect.cells, 0, PAD_TOP)}</g>']
parts += [g(f"sp{i}", L) for i, L in enumerate(splash)]
for i, (a, b, body, eye, x0, x1, t) in enumerate(BOTS):
    tag = f'<text class="tag" x="{len(a[0]) * CW / 2:.1f}" y="-4" text-anchor="middle" fill="{eye}">{escape(BOT_NAMES[i])}</text>'
    parts.append(f'<g class="w{i}">{tag}<g class="bot"><g class="legA">{runs(bot_layer(a, body, eye).cells)}</g>'
                 f'<g class="legB">{runs(bot_layer(b, body, eye).cells)}</g></g></g>')
parts.append(f'<g class="speeder"><g filter="url(#glow)">{runs(speeder.cells)}</g></g>')
# police light bar on the roof, above the "==": red and blue strobe once per pass
GYRO = "".join(
    f'<g class="gyro {cls}"><circle cx="{(c + .5) * CW:.1f}" cy="{CH * .45:.1f}" r="16" fill="{col}" opacity=".35" filter="url(#glow2)"/>'
    f'<rect x="{c * CW + 1:.1f}" y="{CH * .3:.1f}" width="{CW - 2:.1f}" height="4" rx="1.5" fill="#fff"/>'
    f'<rect x="{c * CW:.1f}" y="{CH * .3 - 1:.1f}" width="{CW:.1f}" height="6" rx="2" fill="{col}" opacity=".85" filter="url(#glow)"/></g>'
    for cls, c, col in (("gr", 7, "#ff1f3d"), ("gb", 8, "#2a6bff")))
parts += [f'<g class="spinner"><g filter="url(#glow)">{runs(spinner.cells)}</g>{GYRO}</g>']
for cls, L in (("rf", rain_far), ("rm", rain_mid), ("rn", rain_near)):
    body = runs(L.cells, 0, PAD_TOP)
    parts.append(f'<g class="{cls}">{body}<g transform="translate(0 {SCENE_H:.0f})">{body}</g></g>')
parts.append("</g>")
parts.append(f'<g class="title"><g fill="#4d5d7c">{TITLE_SHADE}</g><g fill="url(#chrome)">{TITLE_SOLID}</g><g fill="url(#neon5)" filter="url(#glow)">{TITLE_FIVE}</g>'
             f'<g clip-path="url(#tclip)"><rect class="shine" x="0" y="{ty0 - 10:.0f}" width="90" height="{6 * TCH + 20:.0f}" fill="url(#band)"/></g></g>')
parts.append(f'<text class="sub" x="{W / 2:.0f}" y="{sub_y:.0f}" text-anchor="middle">{escape(sub)}</text>')
parts.append("</svg>")

open(sys.argv[1], "w").write("\n".join(parts))
print(f"{W:.0f}x{H:.0f}", sum(len(p) for p in parts) // 1024, "KB")
