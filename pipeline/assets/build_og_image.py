"""Regenerate og-image.png (1200x630) -- fourth pass, 2026-08-23.

User feedback on v3: remove the Matrix-style divider entirely ("muy
feo"), align the Hunting Field nodes faithfully to the REAL diagram
(the real page currently renders exactly 8 nodes -- 'other' dropped to
0 plugins after this session's NICHE_TO_CATEGORY fix -- at equal 45°
steps starting straight up, same order as CATEGORIES in index.html:
API, DevOps, Security, Data, Code Quality, Codegen, Testing, Editor),
and make the logo bigger again.

Still deliberately atemporal: no live catalog numbers baked in.
"""
from PIL import Image, ImageDraw, ImageFont
import math

LOGO_SRC = Image.open('apple-touch-icon.png').convert('RGBA')

W, H = 1200, 630
BG = (9, 13, 22)
TEXT = (230, 234, 242)
TEXT_DIM = (150, 160, 180)
ACCENT = (63, 162, 255)   # #3FA2FF -- real CATEGORIES.api color

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

f_brand = font('segoeuib.ttf', 44)
f_h1 = font('segoeuib.ttf', 54)
f_sub = font('segoeui.ttf', 20)
f_node = font('consolab.ttf', 12)

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

# ---- logo mark: paste the REAL rasterized brand mark, resized -- bigger again per user feedback ----
def draw_logo(cx, cy, s):
    size = int(s)
    resized = LOGO_SRC.resize((size, size), Image.LANCZOS)
    img.paste(resized, (int(cx - size/2), int(cy - size/2)), resized)

draw_logo(112, 152, 132)
d.text((192, 122), 'Gap Hunter Labs', font=f_brand, fill=TEXT)

# ---- headline ----
d.text((90, 272), 'Plugin Intelligence', font=f_h1, fill=TEXT)
d.text((90, 336), 'Catalog Report', font=f_h1, fill=ACCENT)

# ---- subtitle ----
sub_lines = [
    'Real, evidence-based gaps in developer tooling —',
    'every plugin exists because of one, not a guess.',
]
sy = 428
for line in sub_lines:
    d.text((90, sy), line, font=f_sub, fill=TEXT_DIM)
    sy += 28

# =====================================================================
# Right panel: the real Hunting Field radial diagram -- all 8 category
# nodes at the SAME angles the live SVG actually computes (polar(),
# defined above, copied verbatim from index.html), same order/palette
# as CATEGORIES. No divider between the two halves anymore (user: "muy
# feo") -- the diagram just has its own open space on the page.
# =====================================================================
hub_x, hub_y = 890, 335
orbit_r = 155
node_r = 27

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
    # label tag, contiguous stub like the real site's tag-stub. Tag sits
    # BELOW the node for the bottom half of the circle (angle 45..315,
    # i.e. not the two side nodes) and stays below for side nodes too --
    # simplest layout that never overlaps the hub or another node at
    # this orbit radius/node spacing (verified by eye across all 8).
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
