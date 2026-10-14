"""The NEXUS-6 replicant record for the metaver5o GitHub profile, as a VT100 terminal SVG.

Text is set in VT323 (a VT320-style font, SIL OFL), subset to the glyphs the
card uses and embedded as base64, since an SVG shown through <img> cannot
fetch fonts. The frame and barcode are vector shapes, so they stay crisp in
any browser. A shell prompt cats the record, a cursor blinks at the next prompt, and a
CRT scanline overlay sits on top.

Usage: python3 card.py out.svg path/to/VT323-Regular.ttf
(needs fontTools + brotli for the subset)
"""
import base64
import io
import random
import sys
from html import escape

from fontTools import subset
from fontTools.ttLib import TTFont

random.seed(6)

COLS, ROWS = 92, 24
FS = 20
CW = FS * 0.4                      # VT323 advance is 400/1000 em
CH = 18.0
PAD = 16
W, H = COLS * CW + 2 * PAD, ROWS * CH + 2 * PAD

FRAME, HEAD, LABEL, VALUE, DOTS, ACCENT, PINK, SOFT = "#00eaff", "#ffb000", "#ffb000", "#e6e2ff", "#4a4088", "#b967ff", "#ff2e88", "#9a90d8"
PROMPT_USER, PROMPT_PATH, GREEN = "#39ff9f", "#4fd6ff", "#39ff9f"

RECORD = [
    ("DESIGNATION", [("metaver5o.eth", PINK)]),
    ("MODEL", [("Founder · CTO & CAIO, CRIPTOGRAFIA.app", VALUE)]),
    ("FUNCTION", [("keys · chains · agents", VALUE)]),
    ("", [("and the systems that are not allowed to fail", SOFT)]),
    None,
    ("PRIOR DUTY", [("QuickNode", ACCENT), (": 250+ chains carried through hard forks", VALUE)]),
    ("", [("Pixel Vault", ACCENT), (": KMS signing ceremonies, $50M+, 0 breaches", VALUE)]),
    ("", [("Google Cloud", ACCENT), (": Click-to-Deploy across 1,000+ envs", VALUE)]),
    None,
    ("IMPLANTS", [("M.Sc. Digital Currency", VALUE), (", University of Nicosia", SOFT)]),
    ("", [("M.Sc. Computer Security", VALUE), (", University of Liverpool", SOFT)]),
    ("", [("B.Sc. Computer Science", VALUE), (", Mackenzie, São Paulo", SOFT)]),
    None,
    ("LIFESPAN", [("indefinite, uploading to the matrix", GREEN)]),
]

lines = {}                        # row -> {(c, r): (glyph, color)}


def line(r):
    return lines.setdefault(r, {})


def put(target, c, r, s, col):
    for i, ch in enumerate(s):
        if ch != " ":
            target[(c + i, r)] = (ch, col)


put(line(1), 3, 1, "CRIPTOGRAFIA", HEAD)
put(line(1), 16, 1, "//", DOTS)
put(line(1), 19, 1, "NEXUS-6 REPLICANT RECORD", VALUE)
put(line(1), COLS - 23, 1, "CLASS: N6-MAA-0x5AFE", SOFT)


def prompt(r, cmd):
    L = line(r)
    put(L, 3, r, "metaver5o@criptografia", PROMPT_USER)
    put(L, 25, r, ":", VALUE)
    put(L, 26, r, "~", PROMPT_PATH)
    put(L, 27, r, "$", VALUE)
    put(L, 29, r, cmd, VALUE)
    return 29 + len(cmd)


prompt(4, "cat nexus6.record")

r, LAB_W = 6, 16
for row in RECORD:
    if row is None:
        r += 1
        continue
    label, segs = row
    L = line(r)
    if label:
        put(L, 3, r, label, LABEL)
        put(L, 3 + len(label) + 1, r, "." * (LAB_W - len(label) - 1), DOTS)
    c = 3 + LAB_W + 1
    for text, col in segs:
        put(L, c, r, text, col)
        c += len(text)
    r += 1
final_row = r + 1
cursor_col = prompt(final_row, "")

BX = COLS - 14
put(line(18), BX - 1, 18, "N6MAA10816", "#7f74c9")
put(line(19), BX - 1, 19, "INCEPT ????", "#7f74c9")


def runs(cm, x0, y0):
    out, rows = [], {}
    for (c, rr), (g, col) in cm.items():
        rows.setdefault(rr, []).append((c, g, col))
    for rr in sorted(rows):
        spans, cur = [], None
        for c, g, col in sorted(rows[rr]):
            if cur and cur[0] == col and cur[1][-1] == c - 1:
                cur[1].append(c); cur[2].append(g)
            else:
                cur = [col, [c], [g]]; spans.append(cur)
        y = y0 + rr * CH + CH * 0.78
        out.append(f'<text y="{y:.1f}">' + "".join(
            f'<tspan x="{" ".join(f"{x0 + c * CW:.1f}" for c in cs)}" fill="{col}">{escape("".join(gs))}</tspan>'
            for col, cs, gs in spans) + "</text>")
    return "\n".join(out)


# ---------------------------------------------------------------- font subset
used = {g for L in lines.values() for (g, _) in L.values()}
opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = []
opts.name_IDs = ["*"]             # keep the OFL copyright and license names
font = TTFont(sys.argv[2])
sub = subset.Subsetter(options=opts)
sub.populate(text="".join(sorted(used)))
sub.subset(font)
buf = io.BytesIO()
font.flavor = "woff2"
font.save(buf)
FONT_B64 = base64.b64encode(buf.getvalue()).decode()

# ---------------------------------------------------------------- vector frame + barcode
fx0, fy0, fx1, fy1 = PAD + CW / 2, PAD + CH / 2, W - PAD - CW / 2, H - PAD - CH / 2
sep_y = PAD + 2.5 * CH
frame = (f'<rect x="{fx0:.1f}" y="{fy0:.1f}" width="{fx1 - fx0:.1f}" height="{fy1 - fy0:.1f}" fill="none" stroke="{FRAME}" stroke-width="1.2"/>'
         f'<rect x="{fx0 + 4:.1f}" y="{fy0 + 4:.1f}" width="{fx1 - fx0 - 8:.1f}" height="{fy1 - fy0 - 8:.1f}" fill="none" stroke="{FRAME}" stroke-width="1.2"/>'
         f'<line x1="{fx0 + 4:.1f}" y1="{sep_y:.1f}" x2="{fx1 - 4:.1f}" y2="{sep_y:.1f}" stroke="#1f6f80" stroke-width="1"/>')
bars, x = [], PAD + BX * CW
for k in range(21):
    w = random.choice([1.5, 1.5, 3, 4]) if 0 < k < 20 else 3
    if k % 2 == 0:
        bars.append(f'<rect x="{x:.1f}" y="{PAD + 7 * CH:.1f}" width="{w}" height="{10 * CH:.1f}" fill="{"#4fd6ff" if k % 3 else "#2a8fb0"}"/>')
    x += w + 1.2
barcode = "".join(bars)

printed = [f'<g class="ln">{runs(lines[rr], PAD, PAD)}</g>' for rr in sorted(lines)]

css = f"""
@font-face {{ font-family: 'VT323'; src: url(data:font/woff2;base64,{FONT_B64}) format('woff2'); }}
text {{ font-family: 'VT323', 'Courier New', Courier, monospace; font-size: {FS}px; white-space: pre; }}
.frame {{ filter: url(#glow); }}
.ln, .bars {{ filter: url(#phosphor); }}
.cursor {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
.scan {{ animation: scan 6s linear infinite; }}
@keyframes scan {{ from {{ transform: translate(0, {PAD:.0f}px); }} to {{ transform: translate(0, {H - PAD:.0f}px); }} }}
.flicker {{ animation: flick 7s infinite; }}
@keyframes flick {{ 0%,96%,100% {{ opacity: .05; }} 97% {{ opacity: .12; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .scan {{ display: none; }} }}
"""
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="VT100 terminal printing the NEXUS-6 replicant record for metaver5o.eth: Founder, CTO and CAIO of CRIPTOGRAFIA.app; prior duty at QuickNode, Pixel Vault and Google Cloud; M.Sc. Digital Currency (Nicosia), M.Sc. Computer Security (Liverpool), B.Sc. Computer Science (Mackenzie); lifespan: indefinite, uploading to the matrix">
<style>{css}</style>
<defs>
<radialGradient id="bg" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#0d0c24"/><stop offset="1" stop-color="#04030b"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00eaff" stop-opacity="0"/><stop offset="1" stop-color="#00eaff" stop-opacity=".12"/></linearGradient>
<pattern id="lines" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000"/></pattern>
<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="phosphor" x="-2%" y="-5%" width="104%" height="110%"><feGaussianBlur stdDeviation="1.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="clip"><rect width="{W:.0f}" height="{H:.0f}" rx="10"/></clipPath>
</defs>
<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="url(#bg)"/>
<g clip-path="url(#clip)"><g class="scan"><rect x="0" y="-40" width="{W:.0f}" height="40" fill="url(#beam)"/></g></g>
<g class="frame">{frame}</g>
<g class="body">{"".join(printed)}<g class="bars">{barcode}</g></g>
<rect class="cursor" x="{PAD + cursor_col * CW:.1f}" y="{PAD + final_row * CH + 2:.1f}" width="{CW:.1f}" height="{CH - 3:.1f}" fill="#39ff9f"/>
<g clip-path="url(#clip)"><rect width="{W:.0f}" height="{H:.0f}" fill="url(#lines)" opacity=".3"/><rect class="flicker" width="{W:.0f}" height="{H:.0f}" fill="#9fdcff" opacity=".05"/></g>
</svg>"""
open(sys.argv[1], "w").write(svg)
print(f"{W:.0f}x{H:.0f}", len(svg) // 1024, "KB, font", len(FONT_B64) // 1024, "KB,", len(used), "glyphs")
