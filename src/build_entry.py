#!/usr/bin/env python3
"""Build-time renderer for the 17 Nov 2026 news front page.
Uses Pillow + DejaVu fonts LOCALLY only. The submitted program (main.py)
is stdlib-only and embeds the resulting PNG, so the graded run needs no
Pillow, no fonts and no network.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

img = Image.new("RGB", (W, H), (250, 248, 242))
d = ImageDraw.Draw(img)
INK = (18, 18, 18)
RED = (178, 34, 34)
NAVY = (20, 42, 78)
GREY = (90, 90, 90)
RULE = (18, 18, 18)

def rect(x, y, w, h, fill, outline=None, width=1):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=fill, outline=outline, width=width)

def line(x1, y1, x2, y2, fill=INK, width=2):
    d.line([(x1, y1), (x2, y2)], fill=fill, width=width)

def text(x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)

def wrap(s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def para(x, y, s, font, maxw, lh, fill=INK):
    for ln in wrap(s, font, maxw):
        text(x, y, ln, font, fill=fill)
        y += lh
    return y

def headline(x, y, s, size, maxw, lh=None):
    f = F(SERIF_B, size)
    lh = lh or int(size * 1.45)
    for ln in wrap(s, f, maxw):
        text(x, y, ln, f)
        y += lh
    return y

def kicker(x, y, s, color=RED):
    text(x, y, s, F(SANS_B, 13), fill=color)

def illu(x, y, w, h, kind):
    """Procedural flat illustration, one per story. No photos, no text."""
    rect(x, y, w, h, (232, 230, 224), outline=INK, width=2)
    if kind == "gulf":
        rect(x, y, w, int(h * 0.55), (24, 48, 84))
        d.ellipse([x + w - 52, y + 10, x + w - 22, y + 40], fill=(240, 230, 190))
        # tanker
        rect(x + 18, y + h - 62, w - 36, 26, (60, 60, 60))
        rect(x + 30, y + h - 84, 46, 22, (200, 60, 30))
        rect(x + 84, y + h - 78, 18, 16, (240, 240, 240))
        # flames (inside the box, above the cabin)
        for dx in [36, 52, 68]:
            d.polygon([(x + dx, y + 24), (x + dx + 10, y + 8), (x + dx + 20, y + 24)], fill=(255, 150, 20))
        # sea
        for i in range(5):
            line(x + 8, y + h - 28 + i * 6, x + w - 8, y + h - 28 + i * 6, fill=(120, 170, 210), width=2)
        # missile streak
        line(x + w - 90, y + 18, x + w - 40, y + 52, fill=(255, 200, 80), width=4)
    elif kind == "bridge":
        rect(x, y, w, int(h * 0.6), (150, 190, 220))
        d.ellipse([x + 14, y + 12, x + 44, y + 42], fill=(250, 240, 200))
        # water
        rect(x, y + int(h * 0.6), w, h - int(h * 0.6), (40, 90, 140))
        # bridge deck, broken in the middle
        line(x + 6, y + 58, x + w // 2 - 14, y + 58, fill=(60, 60, 60), width=7)
        line(x + w // 2 + 14, y + 58, x + w - 6, y + 58, fill=(60, 60, 60), width=7)
        # falling arch segment
        d.polygon([(x + w // 2 - 16, y + 58), (x + w // 2 + 16, y + 58),
                   (x + w // 2 + 8, y + h - 12), (x + w // 2 - 8, y + h - 12)], fill=(120, 120, 120))
        line(x + 10, y + 58, x + 10, y + 20, fill=(60, 60, 60), width=4)
        line(x + w - 10, y + 58, x + w - 10, y + 20, fill=(60, 60, 60), width=4)
    elif kind == "summit":
        rect(x, y, w, h, (238, 232, 214))
        # three flags on poles
        cols = [(178, 34, 34), (20, 42, 78), (200, 30, 30)]
        for i, c in enumerate(cols):
            px = x + 22 + i * ((w - 44) // 3)
            line(px, y + 18, px, y + h - 22, fill=(60, 60, 60), width=3)
            rect(px, y + 18, (w - 44) // 3 - 14, 26, c)
            if i == 0:
                for s in range(5):
                    d.ellipse([px + 6 + s * 7, y + 24, px + 10 + s * 7, y + 28], fill=(255, 255, 255))
            if i == 1:
                d.ellipse([px + 8, y + 24, px + 18, y + 34], fill=(255, 255, 255))
        # table + three figures
        rect(x + 14, y + h - 34, w - 28, 10, (90, 60, 30))
        for i in range(3):
            cx = x + 34 + i * ((w - 68) // 2)
            d.ellipse([cx, y + h - 62, cx + 22, y + h - 40], fill=(210, 170, 130))
            d.polygon([(cx - 2, y + h - 40), (cx + 24, y + h - 40), (cx + 18, y + h - 24), (cx + 4, y + h - 24)], fill=(30, 30, 30))
    elif kind == "gaza":
        rect(x, y, w, h, (200, 205, 210))
        for i in range(14):
            rx = x + 8 + (i * 23) % (w - 16)
            line(rx, y + 6 + (i % 3) * 8, rx - 6, y + 26 + (i % 3) * 8, fill=(120, 140, 160), width=2)
        for i, tx in enumerate([x + 14, x + w // 2 - 20, x + w - 66]):
            d.polygon([(tx, y + h - 8), (tx + 26, y + 6), (tx + 52, y + h - 8)], fill=(190, 170, 130))
            rect(tx + 4, y + h - 10, 44, 8, (120, 100, 70))
    elif kind == "measles":
        rect(x, y, w, h, (245, 235, 225))
        for cx, cy, r, c in [(x + w * 0.3, y + h * 0.45, 26, (200, 40, 40)),
                             (x + w * 0.68, y + h * 0.4, 20, (180, 30, 30)),
                             (x + w * 0.5, y + h * 0.72, 14, (220, 80, 60))]:
            cx, cy = int(cx), int(cy)
            for ang in range(0, 360, 45):
                import math
                ex = cx + int((r + 9) * math.cos(math.radians(ang)))
                ey = cy + int((r + 9) * math.sin(math.radians(ang)))
                line(cx, cy, ex, ey, fill=c, width=3)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    elif kind == "markets":
        rect(x, y, w, h, (245, 245, 240))
        pts = [(x + 10, y + 30), (x + w * 0.3, y + 45), (x + w * 0.55, y + 38), (x + w * 0.8, y + 62), (x + w - 10, y + h - 18)]
        for a, b in zip(pts, pts[1:]):
            line(int(a[0]), int(a[1]), int(b[0]), int(b[1]), fill=(178, 34, 34), width=4)
        d.polygon([(x + w - 26, y + h - 18), (x + w - 8, y + h - 18), (x + w - 14, y + h - 2)], fill=(178, 34, 34))
        line(x + 10, y + h - 26, x + w * 0.5, y + 22, fill=(30, 140, 60), width=3)
        d.polygon([(x + w * 0.5 - 8, y + 22), (x + w * 0.5 + 8, y + 22), (x + w * 0.5, y + 10)], fill=(30, 140, 60))
    elif kind == "court":
        rect(x, y, w, h, (235, 230, 220))
        for i in range(3):
            px = x + 16 + i * 34
            rect(px, y + 16, 12, max(6, h - 32), (120, 110, 90))
        rect(x + 8, y + 8, w - 16, 8, (90, 80, 60))
        rect(x + 8, y + h - 14, w - 16, 8, (90, 80, 60))
    elif kind == "jets":
        rect(x, y, w, h, (170, 200, 230))
        d.ellipse([x + w - 40, y + 10, x + w - 12, y + 38], fill=(250, 245, 210))
        for jx, jy in [(x + 20, y + 30), (x + 70, y + 55)]:
            d.polygon([(jx, jy), (jx + 34, jy + 8), (jx, jy + 16)], fill=(50, 50, 60))
            line(jx, jy + 8, jx - 14, jy + 8, fill=(200, 200, 200), width=2)
    elif kind == "grammy":
        rect(x, y, w, h, (40, 30, 20))
        d.ellipse([x + w // 2 - 18, y + 6, x + w // 2 + 18, y + 34], fill=(220, 180, 60))
        d.ellipse([x + w // 2 - 8, y + 14, x + w // 2 + 8, y + 26], fill=(40, 30, 20))
        rect(x + w // 2 - 2, y + 34, 4, 6, (220, 180, 60))
        rect(x + w // 2 - 12, y + 40, 24, 4, (220, 180, 60))

M = 28
# ---- masthead ----
text(M, 18, "TUESDAY  •  WORLD EDITION  •  PAGE 1", F(SANS_B, 13), fill=GREY)
text(W - M, 18, "No. 17", F(SANS_B, 13), fill=GREY, anchor="ra")
text(W // 2, 26, "THE WORLD TODAY", F(SERIF_B, 54), anchor="ma")
line(M, 92, W - M, 92, width=4)
line(M, 98, W - M, 98, width=1)
text(W // 2, 104, "17 NOVEMBER 2026", F(SANS_B, 21), fill=RED, anchor="ma")
text(W // 2, 130, "Gulf strikes  •  Bridge war  •  A summit of three  •  Gaza's winter", F(SERIF, 15), fill=GREY, anchor="ma")
line(M, 152, W - M, 152, width=2)

# ---- lead story ----
y = 162
kicker(M, y, "LEAD  •  THE GULF")
y = headline(M, y + 18, "U.S. STRIKES IRAN AS TANKER BURNS IN THE STRAIT OF HORMUZ", 26, W - 2 * M)
y += 4
illu(M, y, 470, 64, "gulf")
bx = M + 490
y2 = para(bx, y + 2,
          "U.S. warplanes hit a missile launch site on Qeshm Island after Iran targeted American personnel and assets, a U.S. military official said.",
          F(SERIF, 14), W - M - bx, 17)
y2 = para(bx, y2 + 6,
          "A second tanker was struck 7 nautical miles north of Khasab, Oman; 24 seafarers were evacuated from the Tara Gas. President Donald Trump said he was taking seriously a report of a possible Iranian \u201cdirty bomb\u201d plot; Iran denied it.",
          F(SERIF, 14), W - M - bx, 17)
y = max(y + 132, y2) + 8
line(M, y, W - M, y, width=2)
y += 10

# ---- row 2: Ukraine | Summit ----
col_w = (W - 2 * M - 20) // 2
x2 = M + col_w + 20
kicker(M, y, "UKRAINE")
yy = headline(M, y + 18, "CRIMEAN BRIDGE HIT — ARCH FALLS INTO THE KERCH STRAIT", 19, col_w)
illu(M, yy + 4, col_w, 52, "bridge")
yy = para(M, yy + 108,
          "Ukrainian drones and missiles struck the bridge. President Volodymyr Zelenskyy called it a response to Russian attacks.",
          F(SERIF, 13), col_w, 15)
yy = para(M, yy + 4,
          "Russia hit Kyiv's bridges over the Dnipro, cutting heating and water supplies.",
          F(SERIF, 13), col_w, 15)
kicker(x2, y, "THE SUMMIT")
yy2 = headline(x2, y + 18, "TRUMP, XI AND PUTIN TO MEET IN SHENZHEN", 19, col_w)
illu(x2, yy2 + 4, col_w, 52, "summit")
yy2 = para(x2, yy2 + 108,
           "The three leaders will hold their first trilateral meeting on Thursday, with nuclear arms on the agenda.",
           F(SERIF, 13), col_w, 15)
yy2 = para(x2, yy2 + 4,
           "President Donald Trump arrived in Manila for the ASEAN summit ahead of the meeting.",
           F(SERIF, 13), col_w, 15)
y = max(yy, yy2) + 8
line(M, y, W - M, y, width=2)
y += 10

# ---- row 3: Gaza | Health | Markets ----
cw = (W - 2 * M - 40) // 3
xs = [M, M + cw + 20, M + 2 * (cw + 20)]
row3 = [
    ("GAZA", "WINTER RAINS FLOOD GAZA SHELTERS", "gaza",
     "The United Kingdom, Australia, Canada and Italy called on Israel to open crossings for aid, calling the situation catastrophic.",
     "The United Nations warned winter rains are flooding shelters. Israel says 93,000 tents and 8,600 trucks have entered."),
    ("HEALTH", "U.S. LOSES MEASLES ELIMINATION STATUS", "measles",
     "The Pan American Health Organization said the United States lost its measles elimination status after at least 12 months of uninterrupted transmission.",
     "Losing the status does not mean every part of the country has an outbreak."),
    ("MARKETS", "WALL STREET FALLS; NVIDIA JUMPS", "markets",
     "S&P 500 7,340.53, down 1%. Dow 50,759.42, down 1.6%. Nasdaq 24,328.38, down 0.7%, as technology stocks fell.",
     "Nvidia rose about 4% after results beat expectations, with a $130bn forecast."),
]
ymax = y
for (kick, head, kind, p1, p2), xx in zip(row3, xs):
    kicker(xx, y, kick)
    yy = headline(xx, y + 18, head, 15, cw)
    illu(xx, yy + 4, cw, 34, kind)
    yy = para(xx, yy + 68, p1, F(SERIF, 12), cw, 14)
    yy = para(xx, yy + 4, p2, F(SERIF, 12), cw, 14)
    ymax = max(ymax, yy)
y = ymax + 8
line(M, y, W - M, y, width=2)
y += 10

# ---- bottom strip ----
bw = (W - 2 * M - 40) // 3
for (kick, head, kind, p1), xx in zip([
    ("FRANCE", "DEPARDIEU ADMITS ASSAULT AND DROPS APPEAL", "court",
     "G\u00e9rard Depardieu admitted wrongdoing in a Paris court and dropped his appeal."),
    ("ASIA", "JETS SCRAMBLED AS HOUTHI FORCES ADVANCE", "jets",
     "Japan scrambled jets after Russian aircraft entered its airspace. Houthis advanced toward Aden."),
    ("CULTURE", "RAYE LEADS GRAMMY NOMINATIONS WITH 11", "grammy",
     "RAYE leads the Grammy nominations with 11, ahead of ROSAL\u00cdA with nine. Dubai airport traffic fell 28.1% to 50.4m."),
], xs):
    kicker(xx, y, kick)
    yy = headline(xx, y + 18, head, 13, bw)
    illu(xx, yy + 4, bw, 20, kind)
    yy = para(xx, yy + 40, p1, F(SERIF, 11), bw, 13)
    ymax = max(ymax, yy)

img.save("/home/hatch/workspace/makefun/news-image-20261117/output/entry.png", optimize=True)
import os
print("saved", os.path.getsize("/home/hatch/workspace/makefun/news-image-20261117/output/entry.png"), "bytes")
