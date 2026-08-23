"""Regenerate og-image.png (1200x630) -- fifth pass, 2026-08-23.

User feedback on v4 (real WhatsApp preview, confirmed the cache-busting
?v= trick worked and the new image WAS showing): logo still too small,
the "Real, evidence-based gaps..." subtitle text too small -- "trabaja
en el preview haciendo la mayor cantidad de ajustes y agregando
cualquier cosa que se pueda" (make as many adjustments as reasonable,
add anything that can be added).

Changes this round:
- Logo: 132px -> 168px. Wordmark: 44px -> 52px.
- Subtitle: 20px -> 26px, moved down to clear the now-taller headline.
- New bottom-left trust-mark row (mono/instrumentation style, matches
  the real site's .tele-row language) -- ONLY verifiable, atemporal
  facts this time (no repeat of the earlier 'MIT LICENSED' mistake
  with no LICENSE file backing it): "8 CATEGORIES" (matches the live
  CATEGORIES array, minus 'other' which is genuinely empty),
  "JETBRAINS MARKETPLACE", "OPEN SOURCE ON GITHUB". No download/plugin
  COUNT baked in (still deliberately atemporal, per the original
  2026-08-21 design decision -- those numbers move twice a day).
- Small "GHL" corner wordmark added top-right of the diagram panel for
  extra brand presence in the open space there.
- Headline sizes bumped slightly too (54 -> 58) so the whole left
  column reads as more confidently sized together, not just the two
  specific lines called out.

Still deliberately atemporal: no live catalog numbers baked in.
"""
from PIL import Image, ImageDraw, ImageFont
import math

LOGO_SRC = Image.open('apple-touch-icon.png').convert('RGBA')

W, H = 1200, 630
BG = (9, 13, 22)
TEXT = (230, 234, 242)
TEXT_DIM = (165, 174, 196)
TEXT_FAINT = (120, 132, 158)
ACCENT = (63, 162, 255)   # #3FA2FF -- real CATEGORIES.api color
TEAL = (52, 213, 199)

# Real CATEGORIES palette + order from index.html:3115-3125, exactly as
# buildHuntingSvg() actually renders them: deg = i * (360/8), and
# polar() treats 0deg as STRAIGHT UP (deg-90 before cos/sin), going
# clockwise -- so API sits at 12 o'clock, DevOps at 1:30, etc. 'other'
# is excluded (0 real plugins in it after this session's
# NICHE_TO_CATEGORY fix, same drop condition activeCategories() itself
# uses).
CATS = [
    ('API',          (63, 162, 255),  0),    # #3FA2FF
    ('DevOps',       (2, 241, 114),   45),   # #02F172
    ('Security',     (255, 110, 122), 90),   # #FF6E7A
    ('Data',         (185, 140, 255), 135),  # #B98CFF
    ('Code Quality', (255, 176, 32),  180),  # #FFB020
    ('Codegen',      (1, 179, 253),   225),  # #01B3FD
    ('Testing',      (52, 213, 199),  270),  # #34D5C7
    ('Editor',       (141, 172, 224), 315),  # #8DACE0
]

def polar(cx, cy, r, deg):
    """Matches the real site's polar() in index.html exactly: 0deg is
    straight up, angle increases clockwise."""
    rad = math.radians(deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')

FONTS = 'C:/Windows/Fonts/'
def font(path, size): return ImageFont.truetype(FONTS + path, size)

f_brand = font('segoeuib.ttf', 52)
f_h1 = font('segoeuib.ttf', 58)
f_sub = font('segoeui.ttf', 26)
f_node = font('consolab.ttf', 12)
f_mono = font('consolab.ttf', 14)
f_corner = font('consolab.ttf', 13)

# ---- background dot-grid texture (matches .hero-dotgrid on the real site) ----
step = 26
for gx in range(0, W, step):
    for gy in range(0, H, step):
        d.ellipse([gx-1, gy-1, gx+1, gy+1], fill=(255,255,255,10))

# ---- corner-frame marks (matches .corner-frame device) ----
def corner(x, y, dx, dy, size=26, color=(70,82,110,255)):
    d.line([x, y, x + dx*size, y], fill=color, width=1)
    d.line([x, y, x, y + dy*size], fill=color, width=1)

corner(40, 40, 1, 1)
corner(W-40, H-40, -1, -1)

# ---- logo mark: paste the REAL rasterized brand mark, resized -- bigger AGAIN per explicit user feedback ----
def draw_logo(cx, cy, s):
    size = int(s)
    resized = LOGO_SRC.resize((size, size), Image.LANCZOS)
    img.paste(resized, (int(cx - size/2), int(cy - size/2)), resized)

draw_logo(126, 150, 168)
d.text((222, 118), 'Gap Hunter Labs', font=f_brand, fill=TEXT)

# ---- headline ----
d.text((90, 262), 'Plugin Intelligence', font=f_h1, fill=TEXT)
d.text((90, 328), 'Catalog Report', font=f_h1, fill=ACCENT)

# ---- subtitle, bigger per explicit user feedback ----
sub_lines = [
    'Real, evidence-based gaps in developer tooling —',
    'every plugin exists because of one, not a guess.',
]
sy = 412
for line in sub_lines:
    d.text((90, sy), line, font=f_sub, fill=TEXT_DIM)
    sy += 35

# ---- bottom-left trust-mark row: only verifiable, atemporal facts,
# no repeat of the earlier "MIT LICENSED / no LICENSE file" mistake ----
trust_y = 560
trust_items = ['8 CATEGORIES', 'JETBRAINS MARKETPLACE', 'OPEN SOURCE ON GITHUB']
tx = 90
for item in trust_items:
    d.ellipse([tx, trust_y+5, tx+5, trust_y+10], fill=TEAL)
    d.text((tx+12, trust_y-2), item, font=f_mono, fill=TEXT_FAINT)
    bbox = d.textbbox((tx+12, trust_y-2), item, font=f_mono)
    tx = bbox[2] + 28

# =====================================================================
# Right panel: the real Hunting Field radial diagram -- all 8 category
# nodes at the SAME angles the live SVG actually computes (polar(),
# defined above, copied verbatim from index.html), same order/palette
# as CATEGORIES.
# =====================================================================
hub_x, hub_y = 890, 345
orbit_r = 155
node_r = 27

# small corner wordmark above the diagram, extra brand presence in the
# open space there per "agregando cualquier cosa que se pueda"
d.text((hub_x - 46, 60), 'HUNTING FIELD', font=f_corner, fill=TEXT_FAINT)
d.line([hub_x - 46, 82, hub_x + 138, 82], fill=(70,82,110,255), width=1)

for label, color, angle_deg in CATS:
    nx, ny = polar(hub_x, hub_y, orbit_r, angle_deg)
    d.line([hub_x, hub_y, nx, ny], fill=color + (100,), width=2)

# hub: ring + small accent core (echoes .hub-group's ring, not a blurry
# tiny copy of the full logo)
d.ellipse([hub_x-38, hub_y-38, hub_x+38, hub_y+38], outline=(70,82,110,255), width=1)
d.ellipse([hub_x-26, hub_y-26, hub_x+26, hub_y+26], fill=(16,21,34,255), outline=(90,105,140,255), width=1)
d.ellipse([hub_x-8, hub_y-8, hub_x+8, hub_y+8], fill=ACCENT)

for label, color, angle_deg in CATS:
    nx, ny = polar(hub_x, hub_y, orbit_r, angle_deg)
    # outer halo ring (matches .dot-ring)
    d.ellipse([nx-node_r-5, ny-node_r-5, nx+node_r+5, ny+node_r+5], outline=color+(80,), width=1)
    # sphere fill with a lighter highlight ellipse for a glossy read
    d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r], fill=color+(235,))
    d.ellipse([nx-node_r*0.5, ny-node_r*0.65, nx-node_r*0.05, ny-node_r*0.25], fill=(255,255,255,90))
    d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r], outline=(230,234,242,140), width=1)
    # label tag, contiguous stub like the real site's tag-stub.
    bbox = d.textbbox((0,0), label, font=f_node)
    tw = bbox[2]-bbox[0]
    stub_y = ny + node_r
    tag_y = stub_y + 6
    d.line([nx, stub_y, nx, tag_y], fill=color+(180,), width=2)
    d.rounded_rectangle([nx-tw/2-8, tag_y, nx+tw/2+8, tag_y+20], radius=5, fill=(16,21,34,235), outline=color+(150,), width=1)
    d.text((nx-tw/2, tag_y+3), label, font=f_node, fill=TEXT)

out_path = 'og-image.png'
img.save(out_path, 'PNG', optimize=True)
print('saved', out_path, img.size)
