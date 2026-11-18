#!/usr/bin/env python3
"""Sum up 17 November's world news in one image.

make.fun bounty: https://make.fun/bounty/news-image-20261117
Entry: a program that writes one image to /output/entry.png.

Stdlib only, no network, deterministic.  The front page is *drawn* by
this program, pixel by pixel: a tiny 3x5 bitmap font, a small canvas
library (rectangles, lines, circles, triangles), a pure-Python PNG
encoder (zlib + CRC32, filter 0), and the researched news of Tuesday
17 November 2026 laid out as a newspaper front page, "THE WORLD TODAY",
dated 17 November 2026, No. 17, Page 1.  Running it twice produces
identical bytes.

Stories, in weighted order:
  1. U.S. strikes on Iran / tanker attacks in the Strait of Hormuz
  2. Ukraine strikes the Crimean Bridge; Russia hits Kyiv's bridges
  3. Trump, Xi and Putin to meet in Shenzhen
  4. Winter rains flood Gaza shelters; aid call
  5. U.S. loses measles elimination status
  6. Wall Street falls; Nvidia jumps after results
  7. Depardieu admits assault and drops appeal
  8. Japan scrambles jets; Houthi forces advance
  9. RAYE leads Grammy nominations with 11; Dubai airport traffic
Every story has its own drawn illustration.  No other date, no ads,
no unrelated images.
"""

import math
import os
import struct
import sys
import zlib
from pathlib import Path

# ---------------------------------------------------------------- PNG -----

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(width, height, rgb):
    """Encode an RGB bytearray as a PNG (filter 0 on every scanline)."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


# ------------------------------------------------------------- Canvas -----

class Canvas:
    """A plain RGB canvas, origin top-left."""

    def __init__(self, width, height, paper):
        self.width = width
        self.height = height
        self.pixels = bytearray(paper * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.width), min(y + h, self.height)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                self.pixels[base + (xx - x0) * 3:base + (xx - x0) * 3 + 3] = color

    def rect(self, x, y, w, h, color, thick=1):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, filled=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                elif abs(d2 - r * r) <= r:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle by scanline fill."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            t1 = (y - ay) / (cy - ay) if cy != ay else 0
            xa = ax + (cx - ax) * t1
            if y < by:
                t2 = (y - ay) / (by - ay) if by != ay else 0
                xb = ax + (bx - ax) * t2
            else:
                t2 = (y - by) / (cy - by) if cy != by else 0
                xb = bx + (cx - bx) * t2
            for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
                self.set(x, y, color)

# --------------------------------------------------------------- Font -----

# A 3x5 bitmap font.  Each glyph is 5 rows of 3 cells, '1' = ink.
FONT = {
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("011", "100", "100", "100", "011"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("011", "100", "101", "101", "011"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "010"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("110", "101", "101", "101", "101"),
    "O": ("010", "101", "101", "101", "010"),
    "P": ("110", "101", "110", "100", "100"),
    "Q": ("010", "101", "101", "110", "011"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
    "0": ("011", "101", "101", "101", "110"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("110", "001", "010", "100", "111"),
    "3": ("110", "001", "010", "001", "110"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "110", "001", "110"),
    "6": ("011", "100", "110", "101", "010"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("010", "101", "010", "101", "010"),
    "9": ("010", "101", "011", "001", "110"),
    " ": ("000", "000", "000", "000", "000"),
    ".": ("000", "000", "000", "000", "010"),
    ",": ("000", "000", "000", "010", "100"),
    ":": ("000", "010", "000", "010", "000"),
    ";": ("000", "010", "000", "010", "100"),
    "'": ("010", "010", "000", "000", "000"),
    "-": ("000", "000", "111", "000", "000"),
    "!": ("010", "010", "010", "000", "010"),
    "?": ("110", "001", "010", "000", "010"),
    "%": ("101", "001", "010", "100", "101"),
    "$": ("010", "111", "010", "111", "010"),
    "/": ("001", "001", "010", "100", "100"),
    "(": ("001", "010", "010", "010", "001"),
    ")": ("100", "010", "010", "010", "100"),
    "&": ("011", "101", "010", "101", "011"),
    "+": ("000", "010", "111", "010", "000"),
    "=": ("000", "111", "000", "111", "000"),
    '"': ("101", "101", "000", "000", "000"),
    "#": ("101", "111", "101", "111", "101"),
}


def text_width(text, scale):
    return len(text) * 4 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw upper-cased text at (x, y); returns the x after the text."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(5):
            for col in range(3):
                if glyph[row][col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 4 * scale
    return cx


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= max_chars:
                line += " " + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_block(cv, x, y, width, lines, scale, color, leading=2):
    """Draw wrapped lines; returns the y below the block."""
    for line in lines:
        draw_text(cv, x, y, line, scale, color)
        y += 5 * scale + leading
    return y

# ------------------------------------------------------------ Stories -----

PAPER = bytes([247, 242, 231])
INK = bytes([17, 17, 17])
RED = bytes([178, 34, 34])
BLUE = bytes([31, 82, 143])
SEA = bytes([52, 120, 168])
SKY = bytes([214, 231, 240])
SAND = bytes([222, 196, 150])
GREY = bytes([120, 120, 120])
GREEN = bytes([46, 125, 50])
GOLD = bytes([201, 162, 39])
ORANGE = bytes([230, 126, 34])
DARK = bytes([44, 62, 80])

# (kicker, headline, body, illustration kind)
STORIES = [
    (
        "LEAD - MIDDLE EAST",
        "U.S. STRIKES IRAN AS TANKER IS HIT IN THE STRAIT OF HORMUZ",
        "The United States struck a missile site on Qeshm Island and a "
        "tanker was hit seven nautical miles north of Khasab, in a sharp "
        "escalation in the Strait of Hormuz. Twenty-four seafarers were "
        "evacuated from the tanker Tara Gas. Reports in Washington spoke "
        "of an alleged Iranian dirty-bomb plot, and President Trump warned "
        "Tehran of a severe response if shipping is attacked again.",
        "tanker",
    ),
    (
        "UKRAINE",
        "UKRAINE STRIKES CRIMEAN BRIDGE AS RUSSIA HITS KYIV BRIDGES",
        "Ukrainian forces struck the Crimean Bridge in a long-range attack, "
        "while Russian missiles hit bridges in Kyiv. President Zelenskyy "
        "called the bridge strike unprecedented as both sides pressed "
        "attacks on the transport links that supply their armies.",
        "bridge",
    ),
    (
        "DIPLOMACY",
        "TRUMP, XI AND PUTIN TO MEET IN SHENZHEN",
        "The leaders of the United States, China and Russia are to meet in "
        "Shenzhen, in a summit that will test whether the three powers can "
        "ease tensions over trade, Ukraine and the Middle East.",
        "summit",
    ),
    (
        "GAZA",
        "WINTER RAINS FLOOD GAZA SHELTERS AS AID GROUPS PLEAD FOR HELP",
        "Heavy winter rain flooded tents sheltering displaced families in "
        "Gaza, soaking bedding and food. Aid agencies warned of cold and "
        "disease as winter sets in and called for shelter materials to be "
        "allowed in at once.",
        "tents",
    ),
    (
        "HEALTH",
        "U.S. LOSES MEASLES ELIMINATION STATUS",
        "The United States has lost its measles elimination status after "
        "sustained outbreaks, health officials confirmed. The Pan American "
        "Health Organization reported thousands of cases this year as "
        "vaccination rates fell in parts of the country.",
        "virus",
    ),
    (
        "MARKETS",
        "WALL STREET FALLS AS NVIDIA JUMPS AFTER RESULTS",
        "Stocks fell on Wall Street, with the S and P 500 down 1 percent, "
        "the Dow down 1.6 percent and the Nasdaq down 0.7 percent. Nvidia "
        "rose about 4 percent after its results and a 130 billion dollar "
        "forecast, cushioning the wider sell-off.",
        "chart",
    ),
    (
        "FRANCE",
        "DEPARDIEU ADMITS ASSAULT AND DROPS APPEAL",
        "Actor Gerard Depardieu admitted assault and dropped his appeal, "
        "closing a long-running case that has divided French cinema and "
        "reopened debate over abuse in the film industry.",
        "court",
    ),
    (
        "ASIA",
        "JAPAN SCRAMBLES JETS AS HOUTHI FORCES ADVANCE",
        "Japan scrambled fighter jets in response to flights near its "
        "airspace, while Houthi forces advanced on the ground in Yemen, "
        "in a day of rising military tension across Asia and the Red Sea.",
        "jets",
    ),
    (
        "CULTURE",
        "RAYE LEADS GRAMMY NOMINATIONS AS DUBAI TRAFFIC FALLS",
        "RAYE leads the Grammy nominations with 11, ahead of ROSALIA with "
        "9. Dubai airport traffic fell 28.1 percent to 50.4 million "
        "passengers as regional travel stayed weak.",
        "stage",
    ),
]

# ------------------------------------------------------- Illustrations -----

def draw_illustration(cv, x, y, w, h, kind):
    """A small flat scene for one story, drawn inside (x, y, w, h)."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.rect(x, y, w, h, INK)
    if kind == "tanker":
        cv.fill_rect(x, y + h * 3 // 5, w, h * 2 // 5, SEA)
        cv.fill_rect(x + w // 8, y + h // 3, w * 3 // 4, h // 4, DARK)
        cv.fill_rect(x + w // 2, y + h // 6, w // 10, h // 6, RED)
        for i in range(5):
            cv.line(x + w // 2 + i * 3, y + h // 6, x + w // 2 + 12 + i * 3, y, ORANGE)
        cv.line(x + 4, y + h * 3 // 5, x + w - 4, y + h * 3 // 5, INK)
    elif kind == "bridge":
        cv.fill_rect(x, y + h * 2 // 3, w, h // 3, SEA)
        cv.line(x + 4, y + h // 2, x + w // 3, y + h // 4, INK)
        cv.line(x + w // 3, y + h // 4, x + w * 2 // 3, y + h // 2, INK)
        cv.line(x + w * 2 // 3, y + h // 2, x + w - 4, y + h // 4, INK)
        cv.fill_rect(x + w // 3 - 2, y + h // 4, 4, h // 2, INK)
        cv.fill_rect(x + w * 2 // 3 - 2, y + h // 2, 4, h // 4, INK)
        for i in range(4):
            cv.line(x + w // 6 + i * 8, y + h * 3 // 4, x + w // 6 + i * 8, y + h - 4, SEA)
    elif kind == "summit":
        cv.fill_rect(x, y + h * 2 // 3, w, h // 3, SAND)
        cv.fill_rect(x + w // 8, y + h // 5, w // 5, h // 2, RED)
        cv.fill_rect(x + w // 2 - w // 10, y + h // 5, w // 5, h // 2, GOLD)
        cv.fill_rect(x + w * 7 // 10, y + h // 5, w // 5, h // 2, BLUE)
        cv.fill_rect(x + w // 8, y + h // 2, w * 3 // 4, h // 8, DARK)
    elif kind == "tents":
        cv.fill_rect(x, y + h * 2 // 3, w, h // 3, SAND)
        for i, tx in enumerate((w // 8, w // 3, w * 5 // 8)):
            cv.triangle(x + tx, y + h * 2 // 3, x + tx + w // 5, y + h // 4,
                        x + tx + w * 2 // 5, y + h * 2 // 3, BLUE if i % 2 else RED)
        for i in range(6):
            cv.line(x + 6 + i * 14, y + 4, x + 2 + i * 14, y + h // 3, BLUE)
    elif kind == "virus":
        cv.circle(x + w // 2, y + h // 2, h // 4, RED, filled=True)
        for i in range(8):
            ang = i * 0.785
            dx = int(14 * math.cos(ang))
            dy = int(14 * math.sin(ang))
            cv.line(x + w // 2, y + h // 2, x + w // 2 + dx, y + h // 2 + dy, RED)
        cv.circle(x + w // 2 - 5, y + h // 2 - 4, 3, PAPER, filled=True)
        cv.circle(x + w // 2 + 6, y + h // 2 + 3, 2, PAPER, filled=True)
    elif kind == "chart":
        bars = [30, 55, 40, 70, 50, 85]
        bw = w // 8
        for i, bh in enumerate(bars):
            col = GREEN if i == len(bars) - 1 else (RED if i % 2 else BLUE)
            cv.fill_rect(x + 8 + i * bw, y + h - 6 - bh * h // 110, bw - 6, bh * h // 110, col)
        cv.line(x + 4, y + h - 6, x + w - 4, y + h - 6, INK)
    elif kind == "court":
        cv.fill_rect(x, y + h * 3 // 4, w, h // 4, SAND)
        for i in range(4):
            cx = x + w // 8 + i * w // 4
            cv.fill_rect(cx, y + h // 4, 8, h // 2, DARK)
        cv.triangle(x + w // 10, y + h // 4, x + w // 2, y + 4, x + w * 9 // 10, y + h // 4, RED)
        cv.fill_rect(x + w // 10, y + h // 4, w * 4 // 5, 4, DARK)
    elif kind == "jets":
        cv.circle(x + w * 4 // 5, y + h // 4, h // 5, RED, filled=True)
        for jx, jy in ((w // 4, h // 2), (w // 2, h * 2 // 3)):
            cv.triangle(x + jx, y + jy, x + jx + 34, y + jy - 6, x + jx + 34, y + jy + 6, DARK)
            cv.triangle(x + jx + 8, y + jy - 4, x + jx + 18, y + jy - 16, x + jx + 22, y + jy - 2, DARK)
        cv.line(x + 6, y + h - 8, x + w - 6, y + h - 8, INK)
    elif kind == "stage":
        cv.circle(x + w // 2, y + h // 3, h // 5, GOLD, filled=True)
        for i in range(5):
            cv.line(x + w // 2, y + h // 3, x + w // 2 - 18 + i * 9, y + h * 3 // 4, GOLD)
        cv.fill_rect(x + w // 6, y + h * 3 // 4, w * 2 // 3, 6, DARK)
        cv.fill_rect(x + w // 6, y + h * 3 // 4 + 8, w * 2 // 3, 4, RED)


# ------------------------------------------------------------- Layout -----

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 36


def render_page():
    cv = Canvas(PAGE_W, PAGE_H, PAPER)
    # Masthead.
    draw_text_centered(cv, PAGE_W // 2, 30, "THE WORLD TODAY", 6, INK)
    cv.fill_rect(MARGIN, 78, PAGE_W - 2 * MARGIN, 3, INK)
    draw_text_centered(
        cv, PAGE_W // 2, 90,
        "TUESDAY, 17 NOVEMBER 2026  |  NO. 17  |  PAGE 1", 2, INK)
    cv.fill_rect(MARGIN, 116, PAGE_W - 2 * MARGIN, 2, INK)

    # Lead story.
    kicker, headline, body, kind = STORIES[0]
    draw_text(cv, MARGIN, 134, kicker, 2, RED)
    y = 158
    for line in wrap_text(headline, 48):
        draw_text(cv, MARGIN, y, line, 3, INK)
        y += 22
    draw_illustration(cv, 660, 134, 328, 130, kind)
    y = 232
    y = draw_block(cv, MARGIN, y, 600, wrap_text(body, 70), 2, INK)
    cv.fill_rect(MARGIN, 372, PAGE_W - 2 * MARGIN, 2, INK)

    # The other eight stories, two columns by four rows.
    col_w = (PAGE_W - 2 * MARGIN - 24) // 2
    row_h = 148
    for idx, (kicker, headline, body, kind) in enumerate(STORIES[1:]):
        col = idx % 2
        row = idx // 2
        x = MARGIN + col * (col_w + 24)
        y0 = 392 + row * row_h
        draw_illustration(cv, x, y0, col_w, 34, kind)
        draw_text(cv, x, y0 + 42, kicker, 1, RED)
        hy = y0 + 56
        for line in wrap_text(headline, col_w // 8)[:2]:
            draw_text(cv, x, hy, line, 2, INK)
            hy += 14
        draw_block(cv, x, hy + 2, col_w, wrap_text(body, 110)[:3], 1, INK)
        if col == 0:
            cv.line(x + col_w + 12, y0, x + col_w + 12, y0 + row_h - 16, GREY)
    cv.fill_rect(MARGIN, 984, PAGE_W - 2 * MARGIN, 2, INK)
    draw_text_centered(cv, PAGE_W // 2, 996, "THE WORLD TODAY - 17 NOVEMBER 2026", 1, GREY)
    return cv


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    page = render_page()
    png = encode_png(PAGE_W, PAGE_H, page.pixels)
    (out_dir / "entry.png").write_bytes(png)
    return 0


if __name__ == "__main__":
    sys.exit(main())

