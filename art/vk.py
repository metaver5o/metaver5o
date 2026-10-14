"""Voight-Kampff panel for the metaver5o GitHub profile: terminal + android, one SVG.

The Q&A prints in a VT323 terminal; under it a long SHA3-512 chain of the
answers runs down to the android's feet in lolcat colours (a diagonal rainbow
whose hues cycle), then the verdict. The android (android.svg) is inlined with
its ids, classes and keyframes prefixed so the two stylesheets cannot collide.

Two layouts, so the README can pick by viewport with <picture>:
  wide   : terminal left, android right (desktop)
  stacked: terminal on top, android below (phones; text keeps full width)

Usage: python3 vk.py android.svg VT323-Regular.ttf out-wide.svg out-stacked.svg
(needs fontTools + brotli for the font subset)
"""
import base64
import colorsys
import hashlib
import io
import re
import sys
from html import escape

from fontTools import subset
from fontTools.ttLib import TTFont

FS, CW, CH, PAD = 20, 8.0, 18.0, 16
ANDROID_W, ANDROID_H = 394, 618
ROWS = int((ANDROID_H - 2 * PAD) // CH)          # terminal rows that fit beside the android
COLS = 54
TW = COLS * CW + 2 * PAD                         # terminal panel width

AMBER, WHITE, SOFT, DOTS, GREEN, CYAN, PINK = "#ffb000", "#e6e2ff", "#9a90d8", "#4a4088", "#39ff9f", "#4fd6ff", "#ff2e88"

QA = [
    ("A private key, lying in the sand.", "I don't touch it. I build a vault."),
    ("An agent wants signing authority.", "Granted. It signs nothing."),
    ("3 a.m. Who's on call?", "Agents. They wake a human first."),
    ("Your work. One word each.", "Keys. Thresholds. Proofs. Rain."),
]

lines = []                                       # list of rows; row = list of (text, colour)
lines.append([("metaver5o@criptografia", GREEN), (":", WHITE), ("~", CYAN), ("$ ", WHITE), ("vk --subject metaver5o.eth", WHITE)])
lines.append([])
for q, a in QA:
    lines.append([("Q  ", AMBER), (q, AMBER)])
    lines.append([("A  ", PINK), (a, WHITE)])
    lines.append([])
lines.append([("── RESPONSE DIGEST ", SOFT), ("sha3-512 chain", DOTS)])

verdict = [[("── RESULT: ", SOFT), ("inconclusive.", AMBER)], [("   More human than human.", WHITE)]]
hash_rows = ROWS - len(lines) - 1 - len(verdict)  # leave one blank row before the verdict

# a real SHA3-512 chain over the answers, 40 hex digits per row in groups of 4
seed = "\n".join(f"{q}\n{a}" for q, a in QA).encode()
hexstream, h = "", seed
while len(hexstream) < hash_rows * 40:
    h = hashlib.sha3_512(h).digest()
    hexstream += h.hex()
HASH = [" ".join(hexstream[r * 40 + k * 4: r * 40 + k * 4 + 4] for k in range(10)) for r in range(hash_rows)]
hash_top = len(lines)
lines += [[] for _ in HASH] + [[]] + verdict


def lolcat(c, r):
    hue = ((c * 0.018 + r * 0.05) % 1.0)
    rr, gg, bb = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
    return f"#{int(rr * 255):02x}{int(gg * 255):02x}{int(bb * 255):02x}"


def text_rows(x0, y0):
    out, hashes = [], []
    for r, segs in enumerate(lines):
        y = y0 + r * CH + CH * 0.78
        if hash_top <= r < hash_top + len(HASH):
            s = HASH[r - hash_top]
            spans = "".join(f'<tspan x="{x0 + c * CW:.1f}" fill="{lolcat(c, r)}">{ch}</tspan>'
                            for c, ch in enumerate(s) if ch != " ")
            hashes.append(f'<text y="{y:.1f}">{spans}</text>')
            continue
        c, spans = 0, []
        for t, col in segs:
            xs = " ".join(f"{x0 + (c + i) * CW:.1f}" for i in range(len(t)))
            spans.append(f'<tspan x="{xs}" fill="{col}">{escape(t)}</tspan>')
            c += len(t)
        if spans:
            out.append(f'<text y="{y:.1f}">{"".join(spans)}</text>')
    return "\n".join(out), "\n".join(hashes)


def font_b64(path):
    used = set("".join(t for row in lines for t, _ in row) + "".join(HASH) + "█")
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []
    opts.name_IDs = ["*"]                         # keep the OFL notice
    font = TTFont(path)
    sub = subset.Subsetter(options=opts)
    sub.populate(text="".join(sorted(used)))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def android_inline(path):
    """android.svg -> (css, body) with ids, classes and keyframes prefixed 'a-'."""
    src = open(path).read()
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    body = re.sub(r"^.*?</style>", "", re.sub(r"</svg>\s*$", "", src), flags=re.S)
    for name in ("bg", "beam", "glow", "soft"):
        body = body.replace(f'id="{name}"', f'id="a-{name}"').replace(f"url(#{name})", f"url(#a-{name})")
        css = css.replace(f"url(#{name})", f"url(#a-{name})")
    for cls in ("eyes", "ret", "scan", "verdict", "head"):
        body = body.replace(f'class="{cls}"', f'class="a-{cls}"')
        css = re.sub(rf"\.{cls}\b", f".a-{cls}", css)
    for kf in ("pulse", "lock", "scan", "hum"):
        css = re.sub(rf"\b{kf}\b(?= \d|\s*\{{)", f"a-{kf}", css)
    css = re.sub(r"(^|\n)text \{", r"\1.andr text {", css)
    css = re.sub(r"@media \(prefers-reduced-motion: reduce\) \{.*?\}\s*\}", "", css, flags=re.S)
    return css, body


def build(layout, android_css, android_body, fb64):
    if layout == "wide":
        W, H = TW + 20 + ANDROID_W, ANDROID_H
        tx, ty, ax, ay = 0, 0, TW + 20, 0
    else:
        aw_s = TW * 0.78
        W, H = TW, ANDROID_H + 16 + ANDROID_H * aw_s / ANDROID_W
        tx, ty, ax, ay = 0, 0, (TW - aw_s) / 2, ANDROID_H + 16
    aw = ANDROID_W if layout == "wide" else aw_s
    ah = ANDROID_H if layout == "wide" else ANDROID_H * aw_s / ANDROID_W
    hash_y0 = ty + PAD + hash_top * CH
    css = f"""
@font-face {{ font-family: 'VT323'; src: url(data:font/woff2;base64,{fb64}) format('woff2'); }}
.vk text {{ font-family: 'VT323', 'Courier New', Courier, monospace; font-size: {FS}px; white-space: pre; }}
.vk-glow {{ filter: url(#vk-phos); }}
.vk-rainbow {{ animation: vk-hue 6s linear infinite; }}
@keyframes vk-hue {{ from {{ filter: hue-rotate(0deg); }} to {{ filter: hue-rotate(360deg); }} }}
.vk-sweep {{ animation: vk-sweep 3.2s linear infinite; }}
@keyframes vk-sweep {{ from {{ transform: translate(0, {hash_y0 - CH:.0f}px); }} to {{ transform: translate(0, {hash_y0 + len(HASH) * CH:.0f}px); }} }}
.vk-cursor {{ animation: vk-blink 1.1s steps(1) infinite; }}
@keyframes vk-blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
{android_css}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""
    plain, hashes = text_rows(tx + PAD, ty + PAD)
    cur_row = len(lines) - 1
    cur_x = tx + PAD + (len("   More human than human.") + 1) * CW
    terminal = (f'<rect x="{tx}" y="{ty}" width="{TW:.0f}" height="{ANDROID_H}" rx="10" fill="url(#vk-bg)"/>'
                f'<rect x="{tx + 6}" y="{ty + 6}" width="{TW - 12:.0f}" height="{ANDROID_H - 12}" rx="6" fill="none" stroke="#00eaff" stroke-opacity=".45"/>'
                f'<g class="vk"><g class="vk-glow">'
                f'{plain}<g class="vk-rainbow">{hashes}</g></g></g>'
                f'<g clip-path="url(#vk-clip)"><g class="vk-sweep"><rect x="{tx + PAD - 4}" y="0" width="{TW - 2 * PAD + 8:.0f}" height="{CH:.0f}" fill="#ffffff" opacity=".10"/></g></g>'
                f'<rect class="vk-cursor" x="{cur_x:.1f}" y="{ty + PAD + cur_row * CH + 2:.1f}" width="{CW:.0f}" height="{CH - 3:.0f}" fill="{GREEN}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Voight-Kampff test. Q: A private key, lying in the sand. A: I don't touch it. I build a vault. Q: An agent wants signing authority. A: Granted. It signs nothing. Q: 3 a.m. Who's on call? A: Agents. They wake a human first. Q: Your work, one word each. A: Keys. Thresholds. Proofs. Rain. Result: inconclusive. More human than human.">
<style>{css}</style>
<defs>
<radialGradient id="vk-bg" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#0d0c24"/><stop offset="1" stop-color="#04030b"/></radialGradient>
<filter id="vk-phos" x="-2%" y="-2%" width="104%" height="104%"><feGaussianBlur stdDeviation="1.1" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="vk-clip"><rect x="{tx}" y="{hash_y0:.0f}" width="{TW:.0f}" height="{len(HASH) * CH:.0f}"/></clipPath>
</defs>
{terminal}
<svg x="{ax:.0f}" y="{ay:.0f}" width="{aw:.0f}" height="{ah:.0f}" viewBox="0 0 {ANDROID_W} {ANDROID_H}"><g class="andr">{android_body}</g></svg>
</svg>"""


if __name__ == "__main__":
    a_css, a_body = android_inline(sys.argv[1])
    fb = font_b64(sys.argv[2])
    for layout, out in (("wide", sys.argv[3]), ("stacked", sys.argv[4])):
        open(out, "w").write(build(layout, a_css, a_body, fb))
    print(f"rows={ROWS} hash_rows={len(HASH)} TW={TW:.0f}")
