"""Regenerate og-image.png (1200x630) with the empty bottom-right space
filled -- 2026-08-23, explicit user request from a real WhatsApp preview
screenshot showing the card mostly empty on the right/bottom half.

Design choices (deliberately atemporal, same discipline as the original
2026-08-21 image -- no live catalog numbers baked in, so it never goes
stale and the twice-daily catalog cron never needs to touch it):
- Right side: a simplified echo of the site's own signature visual (the
  "Hunting Field" radial diagram) -- a hub + 6 category nodes on spokes,
  same palette as the real site. Reads as "this brand" instantly to
  anyone who's already seen the real page, and fills the dead space with
  something that belongs to this product instead of generic decoration.
- Bottom: a thin instrumentation-style trust-mark row (JetBrains
  Marketplace / GitHub / category count) in the mono face, echoing the
  site's own .tele-row/topbar language -- no specific numbers, just
  category COUNT (9) which is structural, not a moving stat.
- Corner-frame marks (top-left, bottom-right) matching the site's own
  .corner-frame device.
"""
from PIL import Image, ImageDraw, ImageFont
import math

# Real brand mark, rasterized correctly in an earlier round (matches
# the site's own SVG logo geometry) -- reused here via resize/paste
# instead of hand-redrawing polygons, which produced a distorted
# diamond-ish shape rather than the real hexagon G on the first pass.
LOGO_SRC = Image.open('apple-touch-icon.png').convert('RGBA')

W, H = 1200, 630
BG = (9, 13, 22)
BORDER = (30, 38, 54)
TEXT = (230, 234, 242)
TEXT_DIM = (150, 160, 180)
TEXT_FAINT = (110, 122, 148)
ACCENT = (63, 162, 255)
GREEN = (2, 241, 114)
CYAN = (1, 179, 253)
PURPLE = (185, 140, 255)
RED = (255, 110, 122)
AMBER = (255, 176, 32)
TEAL = (52, 213, 199)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')

FONTS = 'C:/Windows/Fonts/'
def font(path, size): return ImageFont.truetype(FONTS + path, size)

f_brand = font('segoeuib.ttf', 30)
f_h1 = font('segoeuib.ttf', 52)
f_h1b = font('segoeuib.ttf', 52)
f_sub = font('segoeui.ttf', 21)
f_mono_sm = font('consolab.ttf', 15)
f_mono_xs = font('consola.ttf', 13)
f_node = font('consolab.ttf', 13)

# ---- background dot-grid texture (matches .hero-dotgrid on the real site) ----
step = 26
for gx in range(0, W, step):
    for gy in range(0, H, step):
        d.ellipse([gx-1, gy-1, gx+1, gy+1], fill=(255,255,255,10))

# ---- corner-frame marks ----
def corner(x, y, dx, dy, size=26, color=(70,82,110,255)):
    d.line([x, y, x + dx*size, y], fill=color, width=1)
    d.line([x, y, x, y + dy*size], fill=color, width=1)

corner(40, 40, 1, 1)
corner(W-40, H-40, -1, -1)

# ---- logo mark: paste the REAL rasterized brand mark, resized ----
def draw_logo(cx, cy, s):
    size = int(s)
    resized = LOGO_SRC.resize((size, size), Image.LANCZOS)
    img.paste(resized, (int(cx - size/2), int(cy - size/2)), resized)

draw_logo(96, 130, 84)
d.text((150, 108), 'Gap Hunter Labs', font=f_brand, fill=TEXT)

# ---- headline ----
d.text((90, 250), 'Plugin Intelligence', font=f_h1, fill=TEXT)
d.text((90, 312), 'Catalog Report', font=f_h1b, fill=ACCENT)

# ---- subtitle ----
sub_lines = [
    'Real, evidence-based gaps in developer tooling —',
    'every plugin exists because of one, not a guess.',
]
sy = 400
for line in sub_lines:
    d.text((90, sy), line, font=f_sub, fill=TEXT_DIM)
    sy += 30

# ---- bottom trust-mark row (mono, instrumentation style) ----
trust_y = 560
trust_items = ['JETBRAINS MARKETPLACE', 'GITHUB', '9 CATEGORIES', 'MIT LICENSED']
tx = 90
for i, item in enumerate(trust_items):
    d.ellipse([tx, trust_y+5, tx+5, trust_y+10], fill=TEAL)
    d.text((tx+12, trust_y-2), item, font=f_mono_xs, fill=TEXT_FAINT)
    bbox = d.textbbox((tx+12, trust_y-2), item, font=f_mono_xs)
    tx = bbox[2] + 26

# =====================================================================
# Right panel: simplified Hunting Field radial diagram -- echoes the
# real site's signature interactive element so the preview card reads
# as unmistakably THIS product's brand, not generic dev-tool stock art.
# =====================================================================
hub_x, hub_y = 935, 330
categories = [
    ('API', ACCENT, -90),
    ('DevOps', GREEN, -38),
    ('Security', RED, 14),
    ('Data', PURPLE, 66),
    ('Testing', TEAL, 130),
    ('Editor', (141,172,224), -142),
]
orbit_r = 148
node_r = 30

# spokes first (under nodes)
for label, color, angle_deg in categories:
    a = math.radians(angle_deg)
    nx = hub_x + orbit_r * math.cos(a)
    ny = hub_y + orbit_r * math.sin(a)
    d.line([hub_x, hub_y, nx, ny], fill=color + (90,), width=2)

# hub -- small mark, NOT the full raster logo (that already appears at
# full detail top-left; repeating it at 44px would just look blurry).
# A simple ring + solid accent dot reads as "this is the origin point"
# without competing with the real logo.
d.ellipse([hub_x-38, hub_y-38, hub_x+38, hub_y+38], outline=(70,82,110,255), width=1)
d.ellipse([hub_x-26, hub_y-26, hub_x+26, hub_y+26], fill=(20,26,40,255), outline=(70,82,110,255), width=1)
d.ellipse([hub_x-7, hub_y-7, hub_x+7, hub_y+7], fill=ACCENT)

# nodes
for label, color, angle_deg in categories:
    a = math.radians(angle_deg)
    nx = hub_x + orbit_r * math.cos(a)
    ny = hub_y + orbit_r * math.sin(a)
    # outer ring
    d.ellipse([nx-node_r-4, ny-node_r-4, nx+node_r+4, ny+node_r+4], outline=color+(70,), width=1)
    # sphere fill (simple radial-ish via 2 ellipses)
    d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r], fill=color+(230,))
    d.ellipse([nx-node_r, ny-node_r, nx+node_r, ny+node_r], outline=(230,234,242,120), width=1)
    # label tag below node
    bbox = d.textbbox((0,0), label, font=f_node)
    tw = bbox[2]-bbox[0]
    ty = ny + node_r + 10
    d.rounded_rectangle([nx-tw/2-8, ty, nx+tw/2+8, ty+22], radius=5, fill=(20,26,40,235), outline=color+(140,), width=1)
    d.text((nx-tw/2, ty+4), label, font=f_node, fill=TEXT)

out_path = 'og-image.png'
img.save(out_path, 'PNG', optimize=True)
print('saved', out_path, img.size)
