#!/usr/bin/env python3
"""Render the 26 November 2026 one-page illustrated newspaper.

Layout (1024x1024, from Rifqi's 25 Nov concept): the date itself is the
giant serif masthead; a red italic strip carries three headlines; region
pills carry story counts; a timeline strip; three big leads with detailed
scene illustrations; ten small cards with mini illustrations; a bottom row
with a numbered world map, an ALSO ON list and THE DAY IN NUMBERS; a DATE
CHECK footer naming yesterday's stories that were deliberately left out.

Run: python3 render.py  ->  writes entry.png in this directory.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 252, 248)
INK = (17, 17, 17)
MUTED = (107, 114, 128)
RULE = (17, 17, 17)
RED = (185, 28, 28)
SKY = (219, 234, 254)
GOLD = (254, 243, 199)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif.ttf", s)  # no serif italic on this box; red serif carries the strip
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

TAG_STYLE = {
    "CONFIRMED": ((22, 101, 52), (220, 252, 231)),
    "REPORTED": ((29, 78, 216), (219, 234, 254)),
    "ONGOING": ((146, 64, 14), (254, 243, 199)),
    "AHEAD": ((107, 33, 168), (243, 232, 255)),
}

def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_tag(draw, x, y, status):
    fg, bg = TAG_STYLE[status]
    f = SANS_B(8)
    w = int(draw.textlength(status, font=f)) + 10
    draw.rounded_rectangle([x, y, x + w, y + 13], radius=3, fill=bg)
    draw.text((x + 5, y + 2), status, font=f, fill=fg)
    return w

def draw_num(draw, x, y, n):
    f = SANS_B(10)
    s = str(n)
    w = int(draw.textlength(s, font=f)) + 10
    draw.rounded_rectangle([x, y, x + w, y + 14], radius=7, fill=INK)
    draw.text((x + 5, y + 2), s, font=f, fill=(255, 255, 255))
    return w

def draw_pill(draw, x, y, label, count):
    f1, f2 = SANS_B(9), SANS_B(9)
    t = f"{label} {count}"
    w = int(draw.textlength(t, font=f1)) + 16
    draw.rounded_rectangle([x, y, x + w, y + 20], radius=10, outline=INK, width=1)
    draw.text((x + 8, y + 5), label, font=f1, fill=INK)
    tw = draw.textlength(label, font=f1)
    draw.text((x + 8 + tw + 4, y + 5), str(count), font=f2, fill=RED)
    return w

# ---------------------------------------------------------------- stories
LEADS = [
    dict(n=1, region="AMERICAS", kicker="WASHINGTON",
         headline="Trump's tariff wave hits 14 partners",
         deck="Taiwan faces up to 15% in a US overcapacity probe \u2014 the lowest tier, beside Japan, Korea and the EU. Markets slide as the list lands.",
         status="ONGOING", source="Reuters", scene="exchange"),
    dict(n=2, region="MIDDLE EAST", kicker="RIYADH",
         headline="Houthis claim Saudi refinery hit as Brent tops $94",
         deck="The claim lifts crude past $94 a barrel. Riyadh has not confirmed damage; shipping watches the Gulf.",
         status="REPORTED", source="AP", scene="refinery"),
    dict(n=3, region="EAST ASIA", kicker="JIUQUAN",
         headline="Shenzhou-24 carries the first foreign astronaut",
         deck="Pakistan's Muhammad Zeeshan Ali joins China's Tiangong station \u2014 the first non-Chinese crew member to fly there.",
         status="CONFIRMED", source="Xinhua", scene="rocket"),
]

CARDS = [
    dict(n=4, region="AMERICAS", kicker="NEW YORK",
         headline="Nasdaq falls nearly 4% as AI rout deepens",
         deck="All three US indexes drop in early trading as traders hunt for discounts.",
         status="ONGOING", source="Reuters", scene="chart"),
    dict(n=5, region="EAST ASIA", kicker="TAIPEI",
         headline="Taiwan stocks plunge 1,927 points",
         deck="The NT dollar weakens past 33 per US dollar as tariff fears weigh.",
         status="CONFIRMED", source="Nikkei Asia", scene="chart"),
    dict(n=6, region="AMERICAS", kicker="WASHINGTON",
         headline="Fed Beige Book: modest growth, sticky prices",
         deck="Wage gains continue and price pressure persists, the Fed survey finds.",
         status="REPORTED", source="AP", scene="bank"),
    dict(n=7, region="AFRICA", kicker="GIZA",
         headline="Tanker fire on ring road kills 30",
         deck="A fuel tanker crashes near the Warraq tunnel; 39 ambulances rush in.",
         status="CONFIRMED", source="AP", scene="fire"),
    dict(n=8, region="EUROPE", kicker="KYIV",
         headline="Ukraine downs 88 of 112 Russian drones",
         deck="Overnight defences hold; Poland asks NATO to intercept missiles over Ukraine.",
         status="REPORTED", source="Reuters", scene="drone"),
    dict(n=9, region="EUROPE", kicker="MOSCOW",
         headline="Russian refining hits a 20-year low",
         deck="Strikes on at least 18 refineries cut output to its lowest in two decades.",
         status="REPORTED", source="Reuters", scene="refinery2"),
    dict(n=10, region="EUROPE", kicker="MOSCOW",
         headline="Russia counts nearly 500,000 war dead",
         deck="Moscow's own figures put its military deaths in Ukraine near half a million.",
         status="REPORTED", source="The Guardian", scene="memorial"),
    dict(n=11, region="SOUTH ASIA", kicker="NEW DELHI",
         headline="India marks Constitution Day",
         deck="6,000 new IIT seats in robotics, AI and space; a \u20b915,000-crore Nepal package.",
         status="CONFIRMED", source="The Hindu", scene="parliament"),
    dict(n=12, region="SOUTH ASIA", kicker="DHAKA",
         headline="Bangladesh lifts garment wage 36%",
         deck="Entry-level pay rises as rioters burn at least 100 Grameen Bank branches.",
         status="REPORTED", source="AP", scene="factory"),
    dict(n=13, region="EAST ASIA", kicker="PYONGYANG",
         headline="North Korea expels Swiss diplomat",
         deck="Pyongyang orders Switzerland to close its new office in a sanctions row.",
         status="CONFIRMED", source="AP", scene="flag"),
]

ALSO_ON = [
    (14, "BOGOT\u00c1", "Colombia frees 20 hostages after a 17-hour siege."),
    (15, "CANBERRA", "Australia apologises to LGBTQ veterans."),
    (16, "TEHRAN", "Iran suspends executions of Armoon and Najjaran."),
    (17, "GENEVA", "Gukesh faces Sindarov for the world chess crown."),
    (18, "MUMBAI", "1,220 players register for the IPL 2027 auction."),
    (19, "BENGALURU", "Flipkart chief steps down in December."),
    (20, "LUXEMBOURG", "EU court rules on caged animals."),
    (21, "ABUJA", "ECOWAS approves its regional force roadmap."),
]

TIMELINE = [
    ("00:09", "Lukashenko offers Zelensky a Moscow flight"),
    ("00:33", "Giza tanker fire kills 30"),
    ("01:17", "EU briefing: Russia's military budget surges"),
    ("05:30", "Taiwan stocks close down 1,927"),
    ("14:30", "Nasdaq opens down nearly 4%"),
]

NUMBERS = [
    ("$94", "Brent crude, a barrel"),
    ("30", "killed in the Giza tanker fire"),
    ("1,927", "points lost by Taiwan stocks"),
    ("500,000", "Russian military deaths, Moscow's count"),
    ("15%", "top US tariff proposed on Taiwan goods"),
]

REGIONS = [("AMERICAS", 5), ("EUROPE", 5), ("SOUTH ASIA", 4),
           ("EAST ASIA", 3), ("MIDDLE EAST", 2), ("AFRICA", 2)]

# ------------------------------------------------------- scene illustrations
def scene_exchange(d, x, y, w, h):
    """Stock-exchange floor: columned facade, ticker tape, falling chart."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 41, 59))
    d.rectangle([x, y, x + w, y + 26], fill=(15, 23, 42))
    for i in range(6):
        cx = x + 14 + i * 50
        d.rectangle([cx, y + 30, cx + 22, y + h - 34], fill=(100, 116, 139))
        d.rectangle([cx - 3, y + 28, cx + 25, y + 33], fill=(148, 163, 184))
    d.rectangle([x, y + h - 34, x + w, y + h - 30], fill=(148, 163, 184))
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(185, 28, 28))
    tape = "NASDAQ -3.9%   S&P -2.1%   DOW -1.4%"
    d.text((x + 8, y + h - 24), tape, font=SANS_B(11), fill=(255, 255, 255))
    pts = [(x + 20, y + 78), (x + 70, y + 66), (x + 120, y + 74),
           (x + 175, y + 52), (x + 230, y + 62), (x + 290, y + 96)]
    d.line(pts, fill=(248, 113, 113), width=3)
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
              fill=(248, 113, 113))

def scene_refinery(d, x, y, w, h):
    """Oil refinery at dusk: towers, pipes, flare stack, orange sky."""
    for i in range(h):
        r = int(124 + (253 - 124) * i / h)
        g = int(45 + (148 - 45) * i / h)
        b = int(45 + (70 - 45) * i / h)
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    d.ellipse([x + w - 66, y + 12, x + w - 26, y + 52], fill=(254, 215, 130))
    d.rectangle([x + 30, y + 55, x + 58, y + h - 18], fill=(51, 65, 85))
    d.rectangle([x + 70, y + 40, x + 92, y + h - 18], fill=(71, 85, 105))
    d.rectangle([x + 104, y + 68, x + 150, y + h - 18], fill=(51, 65, 85))
    d.rectangle([x + 162, y + 50, x + 210, y + h - 18], fill=(30, 41, 59))
    for tx in (34, 74, 108, 166):
        d.rectangle([x + tx, y + 30, x + tx + 6, y + h - 18], fill=(100, 116, 139))
    d.rectangle([x + 226, y + 22, x + 234, y + h - 18], fill=(100, 116, 139))
    d.polygon([(x + 222, y + 22), (x + 238, y + 22), (x + 234, y + 6),
               (x + 226, y + 6)], fill=(249, 115, 22))
    d.ellipse([x + 224, y - 2, x + 236, y + 12], fill=(253, 224, 71))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(15, 23, 42))

def scene_rocket(d, x, y, w, h):
    """Rocket on the pad at night: gantry, plume, stars."""
    d.rectangle([x, y, x + w, y + h], fill=(15, 23, 42))
    import random
    rnd = random.Random(26)
    for _ in range(40):
        sx, sy = x + rnd.randint(4, w - 4), y + rnd.randint(4, h - 60)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(226, 232, 240))
    cx = x + w // 2
    d.rectangle([cx - 52, y + 20, cx - 44, y + h - 40], fill=(100, 116, 139))
    d.rectangle([cx + 44, y + 20, cx + 52, y + h - 40], fill=(100, 116, 139))
    d.line([(cx - 52, y + 34), (cx - 14, y + 34)], fill=(148, 163, 184), width=2)
    d.line([(cx + 14, y + 34), (cx + 52, y + 34)], fill=(148, 163, 184), width=2)
    d.polygon([(cx, y + 8), (cx - 13, y + 34), (cx + 13, y + 34)], fill=(185, 28, 28))
    d.rectangle([cx - 13, y + 34, cx + 13, y + 92], fill=(226, 232, 240))
    d.rectangle([cx - 13, y + 58, cx + 13, y + 66], fill=(185, 28, 28))
    d.polygon([(cx - 13, y + 92), (cx - 22, y + 104), (cx - 13, y + 104)], fill=(185, 28, 28))
    d.polygon([(cx + 13, y + 92), (cx + 22, y + 104), (cx + 13, y + 104)], fill=(185, 28, 28))
    d.polygon([(cx - 10, y + 104), (cx + 10, y + 104), (cx + 22, y + h - 8),
               (cx - 22, y + h - 8)], fill=(249, 115, 22))
    d.polygon([(cx - 5, y + 104), (cx + 5, y + 104), (cx + 10, y + h - 8),
               (cx - 10, y + h - 8)], fill=(253, 224, 71))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(51, 65, 85))

def scene_mini(d, x, y, w, h, key):
    """Small card illustration, one simple scene per story key."""
    sky = {"chart": (219, 234, 254), "bank": (226, 232, 240),
           "fire": (254, 215, 170), "drone": (186, 230, 253),
           "refinery2": (254, 215, 170), "memorial": (226, 232, 240),
           "parliament": (219, 234, 254), "factory": (254, 243, 199),
           "flag": (254, 226, 226)}.get(key, (226, 232, 240))
    d.rectangle([x, y, x + w, y + h], fill=sky)
    if key == "chart":
        pts = [(x + 10, y + h - 16), (x + 50, y + 26), (x + 90, y + 34),
               (x + 130, y + 16), (x + 175, y + h - 10)]
        d.line(pts, fill=(185, 28, 28), width=3)
        for px, py in pts:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(185, 28, 28))
    elif key == "bank":
        d.polygon([(x + w // 2, y + 8), (x + 18, y + 26), (x + w - 18, y + 26)],
                  fill=(51, 65, 85))
        for i in range(4):
            cx = x + 34 + i * 42
            d.rectangle([cx, y + 28, cx + 14, y + h - 10], fill=(100, 116, 139))
        d.rectangle([x + 14, y + h - 10, x + w - 14, y + h - 6], fill=(51, 65, 85))
    elif key == "fire":
        d.polygon([(x + w // 2, y + 6), (x + w // 2 - 26, y + h - 14),
                   (x + w // 2 + 26, y + h - 14)], fill=(249, 115, 22))
        d.polygon([(x + w // 2, y + 26), (x + w // 2 - 13, y + h - 14),
                   (x + w // 2 + 13, y + h - 14)], fill=(253, 224, 71))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(51, 65, 85))
    elif key == "drone":
        d.ellipse([x + w // 2 - 12, y + 22, x + w // 2 + 12, y + 40], fill=(51, 65, 85))
        for dx in (-34, 34):
            d.line([(x + w // 2 + dx - 16, y + 18), (x + w // 2 + dx + 16, y + 18)],
                   fill=(100, 116, 139), width=3)
            d.ellipse([x + w // 2 + dx - 4, y + 26, x + w // 2 + dx + 4, y + 34],
                      fill=(30, 41, 59))
        d.line([(x + w // 2, y + 40), (x + w // 2, y + h - 8)], fill=(100, 116, 139), width=2)
    elif key == "refinery2":
        d.rectangle([x + 24, y + 22, x + 52, y + h - 8], fill=(51, 65, 85))
        d.rectangle([x + 64, y + 12, x + 86, y + h - 8], fill=(71, 85, 105))
        d.rectangle([x + 98, y + 30, x + 140, y + h - 8], fill=(51, 65, 85))
        d.rectangle([x + 152, y + 8, x + 158, y + h - 8], fill=(100, 116, 139))
        d.ellipse([x + 148, y + 2, x + 162, y + 14], fill=(249, 115, 22))
    elif key == "memorial":
        for i in range(5):
            cx = x + 22 + i * 34
            d.rectangle([cx, y + h - 34, cx + 16, y + h - 8], fill=(100, 116, 139))
            d.ellipse([cx + 3, y + h - 44, cx + 13, y + h - 34], fill=(148, 163, 184))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(51, 65, 85))
    elif key == "parliament":
        d.polygon([(x + w // 2, y + 6), (x + 30, y + 28), (x + w - 30, y + 28)],
                  fill=(185, 28, 28))
        for i in range(5):
            cx = x + 30 + i * 30
            d.rectangle([cx, y + 30, cx + 12, y + h - 8], fill=(51, 65, 85))
        d.rectangle([x + 18, y + h - 8, x + w - 18, y + h - 4], fill=(51, 65, 85))
    elif key == "factory":
        d.rectangle([x + 20, y + 26, x + w - 20, y + h - 8], fill=(51, 65, 85))
        d.rectangle([x + 34, y + 10, x + 44, y + 26], fill=(100, 116, 139))
        d.rectangle([x + 54, y + 16, x + 62, y + 26], fill=(100, 116, 139))
        for i in range(3):
            d.rectangle([x + 36 + i * 44, y + 36, x + 58 + i * 44, y + 52],
                        fill=(254, 243, 199))
    elif key == "flag":
        d.rectangle([x + 30, y + 8, x + 36, y + h - 6], fill=(100, 116, 139))
        d.polygon([(x + 36, y + 8), (x + w - 30, y + 16), (x + 36, y + 28)],
                  fill=(185, 28, 28))
        d.ellipse([x + 52, y + 13, x + 62, y + 23], fill=(255, 255, 255))

LEAD_SCENES = {"exchange": scene_exchange, "refinery": scene_refinery,
               "rocket": scene_rocket}

# ------------------------------------------------------------------- layout
def fit_text(d, text, fnt_fn, size, max_w, start=15):
    size = start
    while size > 8:
        f = fnt_fn(size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return fnt_fn(8)

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(203, 213, 225))
    land = (226, 232, 240)
    polys = {
        "na": [(8, 14), (40, 8), (70, 14), (85, 10), (95, 22), (80, 30), (60, 28), (40, 34), (18, 30), (8, 22)],
        "sa": [(78, 44), (95, 42), (100, 58), (88, 72), (78, 58)],
        "eu": [(148, 8), (175, 6), (185, 14), (172, 20), (158, 22), (148, 16)],
        "af": [(150, 30), (180, 28), (195, 36), (185, 58), (165, 62), (152, 46)],
        "as": [(185, 8), (240, 4), (290, 10), (300, 22), (275, 30), (250, 26), (230, 34), (210, 30), (195, 20)],
        "au": [(268, 58), (296, 56), (300, 68), (272, 70)],
    }
    sx, sy = w / 312, h / 78
    for pts in polys.values():
        scaled = [(x + px * sx, y + py * sy) for px, py in pts]
        d.polygon(scaled, fill=land, outline=(148, 163, 184))
    pins = {1: (80, 22), 2: (188, 32), 3: (233, 21), 4: (83, 19), 5: (252, 30),
            6: (87, 27), 7: (174, 27), 8: (170, 16), 9: (182, 10), 10: (187, 16),
            11: (214, 28), 12: (225, 31), 13: (256, 22), 14: (83, 42),
            15: (276, 66), 16: (196, 22), 17: (152, 18), 18: (211, 34),
            19: (215, 38), 20: (157, 13), 21: (154, 40)}
    f = SANS_B(7)
    for n, (px, py) in pins.items():
        cx, cy = x + px * sx, y + py * sy
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED, outline=(255, 255, 255))
        t = str(n)
        tw = d.textlength(t, font=f)
        d.text((cx - tw / 2, cy - 4), t, font=f, fill=(255, 255, 255))

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 24
    CW = W - 2 * MX  # 976

    # top bar
    d.text((MX, 10), "THE WORLD IN ONE DAY", font=SANS_B(10), fill=INK)
    r = "21 STORIES \u00b7 6 REGIONS \u00b7 ONE DAY"
    d.text((W - MX - d.textlength(r, font=SANS_B(10)), 10), r, font=SANS_B(10), fill=INK)
    d.line([(MX, 30), (W - MX, 30)], fill=RULE, width=2)

    # masthead: the date itself
    date = "Thursday 26 November 2026"
    f = fit_text(d, date, SERIF_B, 54, CW, start=56)
    d.text(((W - d.textlength(date, font=f)) / 2, 36), date, font=f, fill=INK)

    # red italic headline strip
    strip = ("Trump hits 14 partners with new tariffs  /  Brent tops $94 after "
             "Houthi refinery claim  /  Shenzhou-24 carries first foreign astronaut")
    f = fit_text(d, strip, SERIF_I, 15, CW, start=15)
    d.text(((W - d.textlength(strip, font=f)) / 2, 102), strip, font=f, fill=RED)

    # region pills, centred
    widths = []
    for label, count in REGIONS:
        t = f"{label} {count}"
        widths.append(int(d.textlength(t, font=SANS_B(9))) + 16)
    total = sum(widths) + 8 * (len(widths) - 1)
    px = (W - total) / 2
    for (label, count), w in zip(REGIONS, widths):
        px += draw_pill(d, int(px), 128, label, count) + 8
    d.line([(MX, 156), (W - MX, 156)], fill=(203, 213, 225), width=1)

    # timeline strip
    tl = "TIMELINE  " + "  /  ".join(f"{t} {s}" for t, s in TIMELINE)
    f = fit_text(d, tl, SANS, 9, CW, start=10)
    d.text((MX, 164), tl, font=f, fill=MUTED)
    d.line([(MX, 186), (W - MX, 186)], fill=RULE, width=1)

    # three leads
    for i, lead in enumerate(LEADS):
        lx = MX + i * 332
        LEAD_SCENES[lead["scene"]](d, lx, 194, 312, 140)
        nw = draw_num(d, lx, 342, lead["n"])
        draw_tag(d, lx + nw + 6, 342, lead["status"])
        d.text((lx, 362), lead["kicker"], font=SANS_B(9), fill=RED)
        lines = wrap(d, lead["headline"], SERIF_B(17), 312)[:2]
        yy = 378
        for ln in lines:
            d.text((lx, yy), ln, font=SERIF_B(17), fill=INK)
            yy += 21
        deck_lines = wrap(d, lead["deck"], SANS(10), 312)[:3]
        yy = 424
        for ln in deck_lines:
            d.text((lx, yy), ln, font=SANS(10), fill=(55, 65, 81))
            yy += 14
        d.text((lx, 470), "Source: " + lead["source"], font=SANS(8), fill=MUTED)

    d.line([(MX, 492), (W - MX, 492)], fill=RULE, width=1)
    d.text((MX, 500), "MORE TODAY", font=SANS_B(10), fill=INK)

    # ten cards, 2 rows x 5
    for i, card in enumerate(CARDS):
        row, col = divmod(i, 5)
        cx = MX + col * 197
        cy = 520 + row * 132
        scene_mini(d, cx, cy, 187, 56, card["scene"])
        d.text((cx, cy + 62), card["kicker"], font=SANS_B(8), fill=RED)
        draw_tag(d, cx + 187 - 62, cy + 61, card["status"])
        lines = wrap(d, card["headline"], SERIF_B(11), 187)[:2]
        yy = cy + 78
        for ln in lines:
            d.text((cx, yy), ln, font=SERIF_B(11), fill=INK)
            yy += 13
        deck = wrap(d, card["deck"], SANS(9), 187)[:2]
        yy = cy + 106
        for ln in deck:
            d.text((cx, yy), ln, font=SANS(9), fill=(55, 65, 81))
            yy += 11
        d.text((cx, cy + 128), card["source"], font=SANS(7), fill=MUTED)

    d.line([(MX, 792), (W - MX, 792)], fill=RULE, width=1)

    # bottom row
    by = 800
    d.text((MX, by), "WHERE IT HAPPENED", font=SANS_B(10), fill=INK)
    draw_map(d, MX, by + 18, 312, 100)
    d.text((MX, by + 124), "Numbered pins match the stories above.",
           font=SANS(8), fill=MUTED)

    ax = MX + 332
    d.text((ax, by), "ALSO ON \u2014 8 MORE STORIES", font=SANS_B(10), fill=INK)
    yy = by + 18
    for n, place, text in ALSO_ON:
        line = f"{n}  {place} \u2014 {text}"
        lines = wrap(d, line, SANS(9), 312)[:1]
        d.text((ax, yy), lines[0], font=SANS(9), fill=INK)
        yy += 13

    nx = MX + 664
    d.text((nx, by), "THE DAY IN NUMBERS", font=SANS_B(10), fill=INK)
    yy = by + 20
    for num, label in NUMBERS:
        d.text((nx, yy), num, font=SERIF_B(17), fill=RED)
        nw = d.textlength(num, font=SERIF_B(17))
        d.text((nx + nw + 8, yy + 4), label, font=SANS(9), fill=INK)
        yy += 24

    # DATE CHECK footer
    dc = ("DATE CHECK \u2014 Left out on purpose: these happened on 25 November, "
          "not today: Nvidia's Jensen Huang returns as CEO, up 31.5% \u00b7 "
          "Ukraine sinks a Russian warship off Benghazi \u00b7 COP31 collapses in Antalya.")
    d.rectangle([MX, 946, W - MX, 978], fill=GOLD)
    d.rectangle([MX, 946, MX + 4, 978], fill=RED)
    lines = wrap(d, dc, SANS(9), CW - 24)[:2]
    yy = 950
    for ln in lines:
        d.text((MX + 12, yy), ln, font=SANS(9), fill=INK)
        yy += 11

    src = ("Sources: Reuters \u00b7 AP \u00b7 Yonhap \u00b7 Nikkei Asia \u00b7 ABC News \u00b7 "
           "The Hindu \u00b7 European Council \u00b7 UN \u00b7 SpaceQ \u00b7 All times UTC \u00b7 "
           "Every story dated Thursday 26 November 2026 (UTC) \u00b7 Illustrations are drawings")
    f = fit_text(d, src, SANS, 8, CW, start=9)
    d.text(((W - d.textlength(src, font=f)) / 2, 986), src, font=f, fill=MUTED)

    img.save("entry.png")
    print("saved entry.png", img.size)

if __name__ == "__main__":
    main()
