"""Regenerate og-image.png (1200x630) -- third pass, 2026-08-23.

User feedback on the previous version (real WhatsApp preview): the
right-side radial diagram didn't read as the actual Gap Hunter Labs
Hunting Field (wrong palette/proportions vs. the real CATEGORIES array
in index.html), logo+wordmark should be bigger, drop the 4-item bottom
trust-mark row entirely, and add a Matrix/hacker/cybersecurity-style
vertical divider between the left (brand) and right (diagram) halves
to read as more polished/on-theme for a security-adjacent dev-tools
brand.

Still deliberately atemporal: no live catalog numbers baked in.
"""
from PIL import Image, ImageDraw, ImageFont
import math, random

random.seed(7)  # stable output across regenerations

LOGO_SRC = Image.open('apple-touch-icon.png').convert('RGBA')

W, H = 1200, 630
BG = (9, 13, 22)
TEXT = (230, 234, 242)
TEXT_DIM = (150, 160, 180)
ACCENT = (63, 162, 255)   # #3FA2FF -- real CATEGORIES.api color

# Real CATEGORIES palette from index.html:3115-3125, copied exactly so
# the diagram matches the actual site instead of an approximated look.
CATS = [
    ('API',          (63, 162, 255), -90),   # #3FA2FF
    ('DevOps',       (2, 241, 114),  -38),   # #02F172
    ('Security',     (255, 110, 122), 14),   # #FF6E7A
    ('Data',         (185, 140, 255), 66),   # #B98CFF
    ('Code Quality', (255, 176, 32), 118),   # #FFB020
    ('Testing',      (52, 213, 199), 154),   # #34D5C7
    ('Editor',       (141, 172, 224), -142), # #8DACE0
]

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')

FONTS = 'C:/Windows/Fonts/'
def font(path, size): return ImageFont.truetype(FONTS + path, size)

f_brand = font('segoeuib.ttf', 40)
f_h1 = font('segoeuib.ttf', 56)
f_sub = font('segoeui.ttf', 21)
f_node = font('consolab.ttf', 13)
f_matrix = font('consolab.ttf', 15)

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

# =====================================================================
# Matrix/hacker-style vertical divider -- columns of glyphs "falling,"
# brightest near the top of each column, fading to the divider's own
# faint base line. Reads as security/dev/hacking-culture without
# leaning on a cliche green-on-black wall (kept in the brand's own
# blue/cyan so it still feels like THIS site, not a generic Matrix
# meme image).
# =====================================================================
divider_x = 700
glyphs = list("01{}<>/#$%&*+=-_~^GHL01010101")
col_w = 16
row_h = 20
for cx in range(divider_x - 40, divider_x + 41, col_w):
    y = 40
    # dense continuous column, brightest streak near a random point,
    # fading both up and down from it -- a real "falling code" read
    # instead of sparse scattered glyphs.
    bright_at = random.randint(3, int((H - 80) / row_h) - 3)
    row = 0
    while y < H - 40:
        dist = abs(row - bright_at)
        if dist == 0:
            color = (215, 238, 255, 255)
        else:
            alpha = max(18, int(200 - dist * 22))
            color = (ACCENT[0], ACCENT[1], ACCENT[2], alpha)
        ch = random.choice(glyphs)
        d.text((cx, y), ch, font=f_matrix, fill=color)
        y += row_h
        row += 1
# faint vertical guide line under the glyph columns, full-bleed top-to-bottom
d.line([divider_x, 30, divider_x, H - 30], fill=(63, 162, 255, 55), width=1)

# ---- logo mark: paste the REAL rasterized brand mark, resized -- BIGGER now ----
def draw_logo(cx, cy, s):
    size = int(s)
    resized = LOGO_SRC.resize((size, size), Image.LANCZOS)
    img.paste(resized, (int(cx - size/2), int(cy - size/2)), resized)

draw_logo(108, 150, 116)
d.text((180, 118), 'Gap Hunter Labs', font=f_brand, fill=TEXT)

# ---- headline ----
d.text((90, 270), 'Plugin Intelligence', font=f_h1, fill=TEXT)
d.text((90, 336), 'Catalog Report', font=f_h1, fill=ACCENT)

# ---- subtitle ----
sub_lines = [
    'Real, evidence-based gaps in developer tooling —',
    'every plugin exists because of one, not a guess.',
]
sy = 430
for line in sub_lines:
    d.text((90, sy), line, font=f_sub, fill=TEXT_DIM)
    sy += 30

# =====================================================================
# Right panel: the real Hunting Field radial diagram -- 7 category
# nodes at the site's own real angles/palette (matches CATEGORIES in
# index.html exactly), hub + spokes + orbital rings, styled to match
# the live SVG's own glossy-sphere + halo-ring language as closely as
# a static raster can.
# =====================================================================
hub_x, hub_y = 945, 340
orbit_r = 150
node_r = 30

for label, color, angle_deg in CATS:
    a = math.radians(angle_deg)
    nx = hub_x + orbit_r * math.cos(a)
    ny = hub_y + orbit_r * math.sin(a)
    d.line([hub_x, hub_y, nx, ny], fill=color + (100,), width=2)

# hub: ring + small accent core (echoes .hub-group's ring, not a blurry
# tiny copy of the full logo)
d.ellipse([hub_x-40, hub_y-40, hub_x+40, hub_y+40], outline=(70,82,110,255), width=1)
d.ellipse([hub_x-27, hub_y-27, hub_x+27, hub_y+27], fill=(16,21,34,255), outline=(90,105,140,255), width=1)
d.ellipse([hub_x-8, hub_y-8, hub_x+8, hub_y+8], fill=ACCENT)

for label, color, angle_deg in CATS:
    a = math.radians(angle_deg)
    nx = hub_x + orbit_r * math.cos(a)
    ny = hub_y + orbit_r * math.sin(a)
    # outer halo ring (matches .dot-ring)
    d.ellipse([nx-node_r-5, ny-node_r-5, nx+node_r+5, ny+node_r+5], outline=color+(80,), width=1)
    # sphere fill with a lighter highlight ellipse for a glossy read
    d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r], fill=color+(235,))
    d.ellipse([nx-node_r*0.5, ny-node_r*0.65, nx-node_r*0.05, ny-node_r*0.25], fill=(255,255,255,90))
    d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r], outline=(230,234,242,140), width=1)
    # label tag below node, contiguous stub like the real site's tag-stub
    bbox = d.textbbox((0,0), label, font=f_node)
    tw = bbox[2]-bbox[0]
    stub_y = ny + node_r
    tag_y = stub_y + 7
    d.line([nx, stub_y, nx, tag_y], fill=color+(180,), width=2)
    d.rounded_rectangle([nx-tw/2-9, tag_y, nx+tw/2+9, tag_y+22], radius=5, fill=(16,21,34,235), outline=color+(150,), width=1)
    d.text((nx-tw/2, tag_y+4), label, font=f_node, fill=TEXT)

out_path = 'og-image.png'
img.save(out_path, 'PNG', optimize=True)
print('saved', out_path, img.size)
