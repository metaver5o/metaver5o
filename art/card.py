"""The NEXUS-6 replicant record card for the metaver5o GitHub profile, as an SVG.

Usage: python3 card.py out.svg
"""
import random
import sys
from html import escape

random.seed(6)

COLS, ROWS = 92, 21
CW, CH, FS = 7.8, 16.0, 13
PAD = 14
W, H = COLS * CW + 2 * PAD, ROWS * CH + 2 * PAD

FRAME, HEAD, LABEL, VALUE, DOTS, ACCENT, PINK = "#00eaff", "#ffb000", "#ffb000", "#e6e2ff", "#3d3470", "#b967ff", "#ff2e88"

ROWS_DATA = [
    ("DESIGNATION", [("metaver5o.eth", PINK)]),
    ("MODEL", [("Founder · CTO & CAIO, CRIPTOGRAFIA.app", VALUE)]),
    ("FUNCTION", [("keys · chains · agents", VALUE)]),
    ("", [("and the systems that are not allowed to fail", "#9a90d8")]),
    None,
    ("PRIOR DUTY", [("QuickNode", ACCENT), (": 250+ chains carried through hard forks", VALUE)]),
    ("", [("Pixel Vault", ACCENT), (": KMS signing ceremonies, $50M+, 0 breaches", VALUE)]),
    ("", [("Google Cloud", ACCENT), (": Click-to-Deploy across 1,000+ envs", VALUE)]),
    None,
    ("IMPLANTS", [("M.Sc. Digital Currency", VALUE), (", University of Nicosia", "#9a90d8")]),
    ("", [("M.Sc. Computer Security", VALUE), (", University of Liverpool", "#9a90d8")]),
    ("", [("B.Sc. Computer Science", VALUE), (", Mackenzie, São Paulo", "#9a90d8")]),
    None,
    ("LIFESPAN", [("indefinite, if properly backed up", "#39ff9f")]),
]

cells = {}


def put(c, r, s, col):
    for i, ch in enumerate(s):
        if ch != " ":
            cells[(c + i, r)] = (ch, col)


# frame
put(0, 0, "╔" + "═" * (COLS - 2) + "╗", FRAME)
for r in range(1, ROWS - 1):
    put(0, r, "║", FRAME); put(COLS - 1, r, "║", FRAME)
put(0, ROWS - 1, "╚" + "═" * (COLS - 2) + "╝", FRAME)
put(0, 2, "╟" + "─" * (COLS - 2) + "╢", "#1f6f80")
put(3, 1, "TYRELL CORP", HEAD)
put(16, 1, "//", DOTS)
put(19, 1, "NEXUS-6 REPLICANT RECORD", VALUE)
put(COLS - 22, 1, "CLASS: N6-MAA-0x5AFE", "#9a90d8")

r = 4
LAB_W = 16
for row in ROWS_DATA:
    if row is None:
        r += 1
        continue
    label, segs = row
    if label:
        put(3, r, label, LABEL)
        put(3 + len(label) + 1, r, "." * (LAB_W - len(label) - 1), DOTS)
    c = 3 + LAB_W + 1
    for text, col in segs:
        put(c, r, text, col)
        c += len(text)
    r += 1
cursor_cell = (3 + LAB_W + 1 + len("indefinite, if properly backed up") + 1, r - 1)

# barcode + serial on the right
bx = COLS - 13
for k in range(10):
    bar = "█" if k in (0, 9) else random.choice("█▌▐▍▎ ")
    for rr in range(5, 15):
        if bar != " ":
            cells[(bx + k, rr)] = (bar, "#4fd6ff" if k % 3 else "#2a8fb0")
put(bx - 1, 16, "N6MAA10816", "#7f74c9")
put(bx - 1, 17, "INCEPT ????", "#7f74c9")


def runs(cm, x0, y0):
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
        y = y0 + r * CH + CH * 0.75
        out.append(f'<text y="{y:.1f}">' + "".join(
            f'<tspan x="{" ".join(f"{x0 + c * CW:.1f}" for c in cs)}" fill="{col}">{escape("".join(gs))}</tspan>'
            for col, cs, gs in spans) + "</text>")
    return "\n".join(out)


frame = {k: v for k, v in cells.items() if v[1] in (FRAME, "#1f6f80")}
body = {k: v for k, v in cells.items() if k not in frame}
cx, cy = cursor_cell
css = f"""
text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace; font-size: {FS}px; white-space: pre; }}
.frame {{ filter: url(#glow); }}
.cursor {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.scan {{ animation: scan 6s linear infinite; }}
@keyframes scan {{ from {{ transform: translate(0, {PAD:.0f}px); }} to {{ transform: translate(0, {H - PAD:.0f}px); }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .scan {{ display: none; }} }}
"""
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="NEXUS-6 replicant record for metaver5o.eth: Founder, CTO and CAIO of CRIPTOGRAFIA.app; prior duty at QuickNode, Pixel Vault and Google Cloud; M.Sc. Digital Currency (Nicosia), M.Sc. Computer Security (Liverpool), B.Sc. Computer Science (Mackenzie)">
<style>{css}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0a1f"/><stop offset="1" stop-color="#05040d"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00eaff" stop-opacity="0"/><stop offset="1" stop-color="#00eaff" stop-opacity=".12"/></linearGradient>
<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="clip"><rect width="{W:.0f}" height="{H:.0f}" rx="10"/></clipPath>
</defs>
<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="url(#bg)"/>
<g clip-path="url(#clip)"><g class="scan"><rect x="0" y="-40" width="{W:.0f}" height="40" fill="url(#beam)"/></g></g>
<g class="frame">{runs(frame, PAD, PAD)}</g>
<g>{runs(body, PAD, PAD)}</g>
<rect class="cursor" x="{PAD + cx * CW:.1f}" y="{PAD + cy * CH + 2:.1f}" width="{CW:.1f}" height="{CH - 3:.1f}" fill="#39ff9f"/>
</svg>"""
open(sys.argv[1], "w").write(svg)
print(f"{W:.0f}x{H:.0f}", len(svg) // 1024, "KB")
