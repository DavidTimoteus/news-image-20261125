#!/usr/bin/env python3
"""news-image-20261125 v1 — broadsheet front page, 100% code-drawn (Pillow).

Fresh renderer written for this bounty day; no file copied from earlier
sessions (authorship lesson). Style: editorial broadsheet (cream paper,
ink, one muted red) following the v4 broadsheet language of
news-image-20261124-v3. Deterministic: no timestamps, no randomness,
fixed font paths. 1024x1024, RGB, saved as entry.png next to this script.

Content: 38 stories, all happened or first reported Wednesday 25 Nov 2026
(UTC). See SOURCES.md for per-story verification.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28                      # margin
CW = W - 2 * M              # 968 content width
PAPER = (245, 240, 225)     # #F5F0E1
INK = (26, 26, 26)          # #1A1A1A
RED = (166, 25, 46)         # #A6192E
MUTED = (95, 89, 77)        # small-caps grey, ~5.9:1 on paper
FAINT = (120, 114, 100)
LAND = (227, 217, 190)      # map land beige
SEA = (214, 227, 231)       # map sea pale blue
BLUE = (47, 93, 107)        # muted blue accent (charts / sea lines)
GOLD = (146, 106, 0)        # dark amber, decorative only

FD = "/usr/share/fonts/truetype"
SERIF_BLACK = f"{FD}/noto/NotoSerif-Black.ttf"
SERIF_BOLD = f"{FD}/noto/NotoSerif-Bold.ttf"
SERIF = f"{FD}/noto/NotoSerif-Regular.ttf"
SERIF_IT = f"{FD}/noto/NotoSerif-Italic.ttf"
SANS = f"{FD}/dejavu/DejaVuSans.ttf"
SANS_B = f"{FD}/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy wrap; returns list of lines, each <= max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit(draw, text, fnt, max_w, max_lines, what):
    lines = wrap(draw, text, fnt, max_w)
    assert len(lines) <= max_lines, f"{what}: {len(lines)} lines > {max_lines}: {lines}"
    return lines


def rule(draw, x, y, w, fill=INK, width=1):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


def small_caps(draw, text, x, y, size=8, fill=MUTED, fnt=None):
    f = fnt or font(SANS_B, size)
    draw.text((x, y), text.upper(), font=f, fill=fill)
    return draw.textlength(text.upper(), font=f)


def trim_to(draw, text, fnt, max_w):
    """Shorten text with an ellipsis so it fits max_w."""
    t = text
    while d_textlen(draw, t, fnt) > max_w and len(t) > 4:
        t = t[:-1]
    if t != text:
        t = t.rstrip() + "\u2026"
    return t


def d_textlen(draw, text, fnt):
    return draw.textlength(text, font=fnt)


# ---------------------------------------------------------------- data
HEROES = [
    dict(num=1, kick="MIDDLE EAST  \u00b7  CONFIRMED",
         head="Tanker fire kills 31 on Cairo\u2019s Ring Road",
         body="A fuel tanker overturned on Tunnel 10 in Warraq at 16:08 UTC, "
              "setting 27 vehicles ablaze; 39 ambulances raced in.",
         src="CNN  \u00b7  AP", art="cairo"),
    dict(num=2, kick="NORTH AMERICA  \u00b7  CONFIRMED",
         head="Trump proposes new tariffs on 14 trading partners",
         body="USTR\u2019s 8-month Section 301 probe ends in proposed duties: "
              "China 20%, Vietnam 35%, India 25%, EU 15%.",
         src="REUTERS  \u00b7  LE MONDE", art="tariffs"),
    dict(num=3, kick="EAST ASIA  \u00b7  CONFIRMED",
         head="Shenzhou-24 carries first Pakistani into orbit",
         body="Long March-2F lifted off at 00:18 UTC and docked at 03:56; "
              "Muhammad Zeeshan Ali is the first Pakistani in orbit.",
         src="AP  \u00b7  NATURE", art="shenzhou"),
]

CARDS = [
    dict(num=4, kick="SAVASLEYKA  \u00b7  EUROPE  \u00b7  CLAIM",
         head="Ukraine says it hit Savasleyka air base; 5 jets damaged",
         body="Kyiv says 3 MiG-31s and 2 Su-34s were damaged; Moscow has not commented.",
         src="REUTERS", art="jet", banner="3 MiG-31 + 2 Su-34"),
    dict(num=5, kick="RAS TANURA  \u00b7  MIDDLE EAST  \u00b7  CLAIM",
         head="Houthis claim Ras Tanura refinery hit; Brent jumps 3.5%",
         body="Coalition says 4 drones were intercepted; NASA imagery shows thick smoke.",
         src="REUTERS", art="refinery", banner="550,000 BPD REFINERY"),
    dict(num=6, kick="CARTAGENA \u00b7 LAT. AMERICA \u00b7 CONFIRMED",
         head="76 hostages freed as police storm Cartagena supermarket",
         body="The 17-hour siege ended at 06:30 UTC; one gunman killed, four arrested.",
         src="REUTERS  \u00b7  AFP", art="store", banner="76 FREED  \u00b7  1 KILLED"),
    dict(num=7, kick="ENUGU  \u00b7  AFRICA  \u00b7  CONFIRMED",
         head="Nigeria seizes $227m of meth; five Mexicans arrested",
         body="An industrial lab in Enugu held 1,512 kg of meth; a 7-month probe spanned 4 countries.",
         src="REUTERS  \u00b7  BBC", art="flask", banner="$227M  \u00b7  1,512 KG"),
    dict(num=8, kick="CAPE TOWN  \u00b7  AFRICA  \u00b7  OFFICIAL",
         head="Court voids Phala Phala report; Ramaphosa wins",
         body="The High Court voided the 2022 panel report; the impeachment process falls away.",
         src="SOWETAN  \u00b7  BLOOMBERG", art="court", banner="IMPEACHMENT DEAD"),
    dict(num=9, kick="DHAKA  \u00b7  S. ASIA  \u00b7  CONFIRMED",
         head="Bangladesh raises garment wage 36% after protests",
         body="Minimum pay rises 12,500 to 17,000 taka from 1 Dec after weeks of factory protests.",
         src="AP  \u00b7  THE HINDU", art="shirt", banner="12,500 \u2192 17,000 TAKA"),
    dict(num=10, kick="PYONGYANG  \u00b7  E. ASIA  \u00b7  CONFIRMED",
         head="North Korea expels Swiss diplomat, shuts office",
         body="Envoy Sylvain Astier was given 48 hours to leave, weeks after the office reopened.",
         src="REUTERS", art="door", banner="48 HOURS TO LEAVE"),
    dict(num=11, kick="DAMAZIN  \u00b7  AFRICA  \u00b7  REPORTED",
         head="RSF drone strikes kill 19 in Sudan\u2019s Blue Nile",
         body="Reported Wednesday: Tuesday-night strikes killed 19, including six women.",
         src="REUTERS", art="drone", banner="19 KILLED  \u00b7  20 HURT"),
    dict(num=12, kick="GAZA CITY  \u00b7  MIDDLE EAST  \u00b7  CONFIRMED",
         head="Israeli strike kills Hamas security chief and family",
         body="Abuelouf, his wife and two daughters died in a dawn strike on Shati camp.",
         src="REUTERS  \u00b7  XINHUA", art="block", banner="2ND IN 24 HOURS"),
    dict(num=13, kick="WARSAW  \u00b7  EUROPE  \u00b7  OFFICIAL",
         head="Poland plans no-fly zone along Ukraine border",
         body="Tomczyk: the zone would run tens of km from the eastern border.",
         src="REUTERS", art="nofly", banner="TENS OF KM DEEP"),
]

ALSO = [
    (14, "Netanyahu judges urge dropping Case 4000 bribery", "REUTERS"),
    (15, "ISIL attack kills 2 security staff in Hasakah", "REUTERS"),
    (16, "Lebanon to open second airport next month", "REUTERS"),
    (17, "Australia signs A$740m security treaty with Solomons", "PM.GOV.AU"),
    (18, "US Q3 GDP revised to 4.3%; core PCE 3.3%", "IBD"),
    (19, "Wall Street plunges, then recovers; gold $3,446\u2192$3,574", "FINWIRE"),
    (20, "Australia CPI jumps 4.9%, highest since Oct 2023", "ABS"),
    (21, "Germany Q3 GDP revised down to +0.1%", "DESTATIS"),
    (22, "Malaysia sues Google for $146m over YouTube content", "REUTERS"),
    (23, "ESA\u2019s Hera sees stadium-sized crater on Dimorphos", "REUTERS"),
    (24, "FCC clears SpaceX plan for 1m orbital data satellites", "REUTERS"),
    (25, "Amodei: \u2018absurd\u2019 to say he wants AI to rule us", "TECHCRUNCH"),
    (26, "Deloitte WA suspended 3 months over AI-made report", "ABC"),
    (27, "Sporting 2\u20132 Man Utd; Fernandes scores twice", "REUTERS"),
    (28, "PSG 2\u20132 Roma; perfect UCL record ends", "AP"),
    (29, "Lille stun Bayern 2\u20131; first Bayern loss of season", "REUTERS"),
    (30, "Liverpool beat Club Brugge 3\u20130; Isak scores twice", "UEFA"),
    (31, "Barcelona rout Sabah 4\u20131; Gordon scores twice", "UEFA"),
    (32, "Inter beat Stuttgart 2\u20130; Lautaro scores on return", "UEFA"),
    (33, "Macy\u2019s 100th parade postponed to Saturday by storm", "REUTERS"),
    (34, "King tides collapse part of Pacifica Pier", "AP"),
    (35, "Jolie and Pitt settle Ch\u00e2teau Miraval winery suit", "PEOPLE"),
    (36, "Duran Duran\u2019s Andy Taylor dies, 65 \u2014 announced Wed", "REUTERS"),
    (37, "CDC: 9 US measles deaths in 2026; 6,039 cases", "REUTERS"),
    (38, "Army detonates 68 barrels of lead azide in Iowa", "REUTERS"),
]

NUMBERS = [
    ("31", "killed in the Cairo tanker fire"),
    ("14", "partners face proposed US tariffs"),
    ("$227m", "of meth seized in Enugu, Nigeria"),
    ("1,000,000", "satellites in SpaceX\u2019s Starmind plan"),
    ("4.3%", "US Q3 GDP, revised up from 3.4%"),
    ("76", "hostages freed in Cartagena"),
]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off from Jiuquan"),
    ("03:56", "Shenzhou-24 docks at Tiangong"),
    ("06:30", "Colombian forces free 76 hostages in Cartagena"),
    ("12:44", "Reuters: Nigeria announces $227m meth bust"),
    ("16:08", "Cairo tanker fire erupts in Warraq"),
]

# featured pin locations (lon, lat) + manual nudge (dx, dy) px.
# Cairo/Gaza/Warsaw nudged apart: true positions are ~9px apart.
PINS = [
    (1, 31.20, 30.08, -16, -10),   # Cairo / Warraq
    (2, -77.04, 38.90, 0, 0),      # Washington
    (3, 98.49, 39.74, 0, 0),       # Jiuquan
    (4, 43.32, 55.38, 0, 0),       # Savasleyka
    (5, 50.06, 26.64, 8, 4),       # Ras Tanura
    (6, -75.51, 10.40, -10, 10),   # Cartagena
    (7, 7.49, 6.52, 0, 0),         # Enugu
    (8, 18.42, -33.93, 0, 0),      # Cape Town
    (9, 90.41, 23.81, 0, 8),       # Dhaka
    (10, 125.75, 39.03, 0, 0),     # Pyongyang
    (11, 34.55, 11.77, 0, 0),      # Damazin, Blue Nile
    (12, 34.47, 31.50, -2, -12),   # Gaza City
    (13, 21.01, 52.23, -12, -6),   # Warsaw
]

# simplified continents (lon, lat) polygons, schematic
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-105, 72), (-90, 74), (-82, 73), (-76, 62),
     (-65, 60), (-60, 52), (-65, 45), (-70, 42), (-75, 35), (-81, 31), (-84, 30),
     (-90, 29), (-97, 26), (-97, 22), (-105, 20), (-95, 16), (-86, 13), (-83, 9),
     (-90, 14), (-97, 16), (-105, 20), (-110, 23), (-117, 33), (-124, 40),
     (-125, 49), (-135, 58), (-150, 60), (-165, 60), (-168, 66)],
    [(-80, 9), (-77, 7), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-70, -52),
     (-73, -44), (-73, -30), (-70, -18), (-77, -12), (-81, -6), (-80, 0), (-80, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 70), (40, 68),
     (45, 68), (50, 69), (55, 68), (60, 69), (68, 73), (75, 72), (80, 73),
     (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 70), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 59),
     (142, 55), (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
     (122, 28), (115, 22), (110, 20), (108, 12), (105, 9), (100, 7), (98, 12),
     (95, 16), (92, 21), (89, 22), (86, 20), (80, 13), (77, 8), (75, 15),
     (72, 20), (68, 23), (62, 25), (57, 26), (52, 28), (50, 30), (48, 30),
     (44, 29), (40, 32), (36, 36), (30, 36), (26, 38), (23, 36), (20, 40),
     (18, 42), (14, 45), (10, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 37), (-10, 36)],
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (39, 21),
     (43, 12), (48, 11), (51, 12), (44, 2), (41, -2), (40, -10), (40, -18),
     (36, -26), (32, -29), (28, -33), (20, -35), (18, -32), (15, -27),
     (12, -18), (13, -12), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
    [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
]


# ---------------------------------------------------------------- hero art
def art_cairo(d, x, y, w, h):
    """Schematic Greater Cairo: Mediterranean top, Nile, Warraq pin,
    Giza pyramids, Ring Road arc, callout with the death toll."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK, width=1)
    # Egypt landmass (schematic) — top edge low enough for a readable sea band
    land = [(0.04, 0.28), (0.30, 0.22), (0.55, 0.20), (0.82, 0.24), (0.98, 0.32),
            (0.98, 0.55), (0.90, 0.85), (0.70, 0.98), (0.45, 0.98), (0.25, 0.80),
            (0.10, 0.55), (0.04, 0.38)]
    d.polygon([(x + px * w, y + py * h) for px, py in land], fill=LAND, outline=INK)
    # Nile (vertical, slightly wavy)
    d.line([(x + 0.52 * w, y + 0.26 * h), (x + 0.50 * w, y + 0.55 * h),
            (x + 0.54 * w, y + h)], fill=BLUE, width=2)
    # Ring Road arc (dashed red) around the Warraq pin
    cx, cy = x + 0.55 * w, y + 0.42 * h
    for a in range(-70, 200, 12):
        import math
        a1 = math.radians(a)
        a2 = math.radians(a + 7)
        d.arc([cx - 34, cy - 20, cx + 34, cy + 20], a, a + 7, fill=RED, width=2)
    # Warraq pin + label
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED, outline=PAPER, width=1)
    d.text((cx + 8, cy - 4), "WARRAQ", font=font(SANS_B, 7), fill=INK)
    d.text((cx + 8, cy + 5), "RING ROAD", font=font(SANS_B, 7), fill=INK)
    # Giza pyramids (SW of Cairo)
    px, py = x + 0.30 * w, y + 0.62 * h
    for i, s in enumerate((9, 7, 5)):
        bx = px + i * 11
        d.polygon([(bx, py - s), (bx - s, py), (bx + s, py)], fill=GOLD, outline=INK)
    d.text((px - 6, py + 3), "GIZA", font=font(SANS_B, 7), fill=INK)
    d.text((x + 6, y + 3), "MEDITERRANEAN", font=font(SANS_B, 7), fill=BLUE)
    t16 = "16:08 UTC"
    d.text((x + w - 6 - d.textlength(t16, font=font(SANS_B, 7)), y + 3), t16,
           font=font(SANS_B, 7), fill=INK)
    # callout box bottom-left
    bx, by = x + 6, y + h - 22
    d.rectangle([bx, by, bx + 128, by + 17], fill=PAPER, outline=INK, width=1)
    d.text((bx + 5, by + 3), "31 DEAD  \u00b7  21 HURT", font=font(SANS_B, 8), fill=RED)


def art_tariffs(d, x, y, w, h):
    """Vertical bars: proposed max tariff % per partner. China carries a
    dashed extension to 40% (applies if the trade truce fails)."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    d.text((x + 8, y + 4), "PROPOSED TARIFFS \u2014 MAX %", font=font(SANS_B, 7), fill=MUTED)
    d.text((x + w - 74, y + 4), "14 PARTNERS", font=font(SANS_B, 8), fill=RED)
    bars = [("CHINA", 20, 40), ("VIETNAM", 35, None), ("INDIA", 25, None), ("EU", 15, None)]
    base = y + h - 16
    bw = 38
    gap = (w - 4 * bw - 24) / 5
    for i, (lab, v, ext) in enumerate(bars):
        bx = x + 12 + gap + i * (bw + gap)
        # scale 45 (not 40) so the extension stays below the header line
        bh = (h - 38) * v / 45.0
        d.rectangle([bx, base - bh, bx + bw, base], fill=RED if i == 0 else INK)
        if ext:
            eh = (h - 38) * ext / 45.0
            for yy in range(int(base - eh), int(base - bh), 4):
                d.line([(bx + 2, yy), (bx + bw - 2, yy)], fill=RED, width=2)
            # "40%*" sits in the gap right of the extension, clear of the
            # header above and of the Vietnam bar (gap is 27px at bw 38)
            d.text((bx + bw + 2, base - eh + 2), "40%*", font=font(SANS_B, 8), fill=RED)
        else:
            d.text((bx + 8, base - bh - 11), f"{v}%", font=font(SANS_B, 8), fill=INK)
        d.text((bx + 2, base + 3), lab, font=font(SANS_B, 7), fill=MUTED)
    d.line([(x + 8, base), (x + w - 8, base)], fill=INK, width=1)
    d.text((x + 8, y + h - 13), "", font=font(SANS_B, 7), fill=MUTED)


def art_shenzhou(d, x, y, w, h):
    """Launch arc: Jiuquan ground pad -> dashed ascent -> Tiangong station."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK, width=1)
    # stars
    for (sx, sy) in [(0.12, 0.18), (0.22, 0.10), (0.38, 0.14), (0.55, 0.08),
                     (0.70, 0.16), (0.86, 0.10), (0.94, 0.24), (0.30, 0.26)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                  fill=INK)
    # ground line + pad
    gy = y + h - 14
    d.line([(x + 6, gy), (x + w - 6, gy)], fill=INK, width=2)
    d.text((x + 8, gy + 3), "JIUQUAN", font=font(SANS_B, 7), fill=INK)
    # rocket on pad
    rx = x + 0.16 * w
    d.polygon([(rx, gy - 26), (rx - 5, gy - 14), (rx - 5, gy), (rx + 5, gy),
               (rx + 5, gy - 14)], fill=INK)
    d.polygon([(rx - 5, gy - 14), (rx, gy - 26), (rx + 5, gy - 14)], fill=RED)
    # dashed ascent arc to station
    import math
    sx, sy = rx, gy - 26
    tx, ty = x + 0.82 * w, y + 0.24 * h
    mx, my = (sx + tx) / 2 + 10, (sy + ty) / 2 - 22
    prev = None
    for j in range(25):
        t = j / 24
        px = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t ** 2 * tx
        py = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t ** 2 * ty
        if prev is not None and j % 2 == 0:
            d.line([prev, (px, py)], fill=RED, width=2)
        prev = (px, py)
    # Tiangong station: core + two solar panels
    d.rectangle([tx - 16, ty - 3, tx + 16, ty + 3], fill=INK)
    d.rectangle([tx - 34, ty - 7, tx - 18, ty + 7], fill=BLUE, outline=INK, width=1)
    d.rectangle([tx + 18, ty - 7, tx + 34, ty + 7], fill=BLUE, outline=INK, width=1)
    d.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=RED, outline=PAPER, width=1)
    d.text((tx - 26, ty + 10), "TIANGONG", font=font(SANS_B, 7), fill=INK)
    # times in the empty lower band: the dashed arc crosses the whole top
    # band, and the rocket occupies the bottom-left corner
    d.text((x + 70, y + 24), "00:18 \u2192 03:56 UTC", font=font(SANS_B, 8), fill=RED)
    # callout box bottom-right
    bx, by = x + w - 138, y + h - 22
    d.rectangle([bx, by, bx + 132, by + 17], fill=PAPER, outline=INK, width=1)
    d.text((bx + 5, by + 3), "CREW 3  \u00b7  1ST PAKISTANI", font=font(SANS_B, 8), fill=RED)


# ---------------------------------------------------------------- card art
def banner(d, x, y, w, h, text):
    bw = d.textlength(text, font=font(SANS_B, 8)) + 12
    bx, by = x + 6, y + h - 20
    d.rectangle([bx, by, bx + bw, by + 15], fill=INK)
    d.text((bx + 6, by + 3), text, font=font(SANS_B, 8), fill=PAPER)


def art_panel(d, x, y, w, h, kind, banner_text):
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    cx, cy = x + w / 2, y + h / 2
    if kind == "jet":
        # top-view jet on a runway
        d.line([(x + 10, y + 44), (x + w - 10, y + 44)], fill=INK, width=2)
        for i in range(5):
            d.line([(x + 20 + i * 30, y + 42), (x + 20 + i * 30, y + 46)],
                   fill=PAPER, width=1)
        d.polygon([(cx, y + 10), (cx - 6, y + 26), (cx - 6, y + 44), (cx + 6, y + 44),
                   (cx + 6, y + 26)], fill=INK)
        d.polygon([(cx - 6, y + 24), (cx - 34, y + 40), (cx - 6, y + 36)], fill=INK)
        d.polygon([(cx + 6, y + 24), (cx + 34, y + 40), (cx + 6, y + 36)], fill=INK)
        d.polygon([(cx - 8, y + 14), (cx - 16, y + 22), (cx - 6, y + 22)], fill=RED)
        d.polygon([(cx + 8, y + 14), (cx + 16, y + 22), (cx + 6, y + 22)], fill=RED)
    elif kind == "refinery":
        for i, (tx, th) in enumerate([(30, 30), (62, 40), (94, 26)]):
            d.rectangle([x + tx, y + 52 - th, x + tx + 18, y + 52], fill=LAND,
                        outline=INK, width=2)
            d.line([(x + tx + 4, y + 52 - th + 6), (x + tx + 14, y + 52 - th + 6)],
                   fill=INK, width=1)
        d.rectangle([x + 126, y + 34, x + 158, y + 52], fill=INK)
        # flame
        d.polygon([(x + 146, y + 12), (x + 138, y + 30), (x + 142, y + 34),
                   (x + 150, y + 34), (x + 154, y + 30)], fill=RED, outline=INK)
        d.line([(x + 10, y + 54), (x + w - 10, y + 54)], fill=INK, width=2)
    elif kind == "store":
        d.rectangle([x + 30, y + 18, x + w - 30, y + 52], fill=PAPER, outline=INK, width=2)
        for i in range(6):
            d.polygon([(x + 30 + i * 21, y + 18), (x + 30 + (i + 1) * 21, y + 18),
                       (x + 30 + (i + 1) * 21, y + 28), (x + 30 + i * 21, y + 28)],
                      fill=RED if i % 2 == 0 else PAPER, outline=INK)
        d.rectangle([x + 76, y + 32, x + w - 76, y + 52], fill=INK)
        d.text((x + 84, y + 37), "76", font=font(SANS_B, 10), fill=PAPER)
        d.line([(x + 14, y + 54), (x + w - 14, y + 54)], fill=INK, width=2)
    elif kind == "flask":
        # flask kept small so the banner (bottom 15px) does not swallow it
        d.polygon([(cx - 6, y + 6), (cx + 6, y + 6), (cx + 6, y + 16),
                   (cx + 26, y + 34), (cx - 26, y + 34), (cx - 6, y + 16)],
                  fill=PAPER, outline=INK, width=2)
        d.polygon([(cx - 19, y + 25), (cx + 19, y + 25), (cx + 26, y + 34),
                   (cx - 26, y + 34)], fill=BLUE)
        d.ellipse([cx - 13, y + 19, cx - 7, y + 25], outline=INK, width=1)
        d.ellipse([cx + 7, y + 27, cx + 13, y + 33], outline=INK, width=1)
        d.text((cx - 4, y + 24), "$", font=font(SANS_B, 10), fill=INK)
        d.line([(x + 14, y + 40), (x + w - 14, y + 40)], fill=INK, width=2)
    elif kind == "court":
        # courthouse compressed into the strip above the banner (banner
        # occupies the bottom 15px of the panel)
        d.polygon([(cx - 56, y + 4), (cx + 56, y + 4), (cx, y + 14)], fill=LAND,
                  outline=INK, width=2)
        for i in range(3):
            d.rectangle([x + 34 + i * 44, y + 16, x + 44 + i * 44, y + 28], fill=INK)
        d.rectangle([x + 24, y + 28, x + w - 24, y + 31], fill=INK)
        # gavel, small, bottom right above the banner
        d.rectangle([x + 132, y + 16, x + 152, y + 21], fill=RED, outline=INK, width=1)
        d.line([(x + 142, y + 21), (x + 142, y + 29)], fill=INK, width=3)
    elif kind == "shirt":
        d.polygon([(cx - 14, y + 12), (cx + 14, y + 12), (cx + 34, y + 20),
                   (cx + 26, y + 34), (cx + 18, y + 30), (cx + 18, y + 52),
                   (cx - 18, y + 52), (cx - 18, y + 30), (cx - 26, y + 34),
                   (cx - 34, y + 20)], fill=PAPER, outline=INK, width=2)
        d.line([(cx - 14, y + 12), (cx, y + 22), (cx + 14, y + 12)], fill=INK, width=1)
        # no in-shirt text: the banner already carries the wage numbers,
        # and any text here is cut by the banner's top edge
    elif kind == "door":
        d.rectangle([x + 62, y + 10, x + w - 62, y + 54], fill=LAND, outline=INK, width=2)
        d.line([(x + w / 2, y + 10), (x + w / 2, y + 54)], fill=INK, width=2)
        d.ellipse([x + 84, y + 32, x + 88, y + 36], fill=INK)
        d.ellipse([x + 96, y + 32, x + 100, y + 36], fill=INK)
        # small Swiss flag on a pole
        d.line([(x + 150, y + 12), (x + 150, y + 44)], fill=INK, width=2)
        d.rectangle([x + 150, y + 12, x + 168, y + 26], fill=RED, outline=INK, width=1)
        d.rectangle([x + 157, y + 15, x + 161, y + 23], fill=PAPER)
        d.rectangle([x + 153, y + 17, x + 165, y + 21], fill=PAPER)
    elif kind == "drone":
        d.line([(cx - 26, cy - 12), (cx + 26, cy + 12)], fill=INK, width=2)
        d.line([(cx - 26, cy + 12), (cx + 26, cy - 12)], fill=INK, width=2)
        for (rx, ry) in [(-26, -12), (26, 12), (-26, 12), (26, -12)]:
            d.ellipse([cx + rx - 9, cy + ry - 3, cx + rx + 9, cy + ry + 3],
                      outline=INK, width=2)
        d.rectangle([cx - 10, cy - 6, cx + 10, cy + 6], fill=RED, outline=INK, width=1)
    elif kind == "block":
        d.rectangle([x + 40, y + 12, x + w - 40, y + 54], fill=LAND, outline=INK, width=2)
        for r in range(3):
            for c in range(4):
                d.rectangle([x + 50 + c * 22, y + 18 + r * 12,
                             x + 58 + c * 22, y + 26 + r * 12], fill=INK)
        # strike burst top-right
        bx, by = x + w - 44, y + 10
        for (dx, dy) in [(0, -8), (6, -6), (8, 0), (6, 6), (0, 8), (-6, 6), (-8, 0), (-6, -6)]:
            d.line([(bx, by), (bx + dx, by + dy)], fill=RED, width=2)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)
    elif kind == "nofly":
        # plane silhouette inside a prohibition circle
        d.polygon([(cx - 30, cy - 2), (cx + 22, cy - 6), (cx + 36, cy), (cx + 22, cy + 6),
                   (cx - 30, cy + 2)], fill=INK)
        d.polygon([(cx + 6, cy - 6), (cx + 16, cy - 20), (cx + 20, cy - 6)], fill=INK)
        d.polygon([(cx - 6, cy + 4), (cx - 12, cy + 16), (cx - 2, cy + 6)], fill=INK)
        d.ellipse([cx - 40, cy - 26, cx + 40, cy + 26], outline=RED, width=3)
        d.line([(cx - 28, cy + 18), (cx + 28, cy - 18)], fill=RED, width=3)
    banner(d, x, y, w, h, banner_text)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # ---- top bar
    small_caps(d, "Wednesday 25 November 2026", M, 8, size=9, fill=INK)
    r = d.textlength("38 STORIES  \u00b7  10 REGIONS", font=font(SANS_B, 9))
    d.text((W - M - r, 8), "38 STORIES  \u00b7  10 REGIONS", font=font(SANS_B, 9), fill=INK)
    d.text((W / 2 - 4, 7), "\u25c6", font=font(SANS_B, 9), fill=RED)
    rule(d, M, 26, CW, width=2)
    # ---- masthead
    mf = font(SERIF_BLACK, 50)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(t, font=mf)) / 2, 30), t, font=mf, fill=INK)
    # ---- eyebrow row
    small_caps(d, "From Cairo to Canberra", M, 84, size=9)
    small_caps(d, "All times UTC unless stated", W - M - 196, 84, size=9)
    d.text((W / 2 - 4, 83), "\u25c6", font=font(SANS_B, 9), fill=RED)
    rule(d, M, 100, CW, width=1)
    # ---- sub-headline
    sf = font(SERIF_IT, 15)
    sub = ("A tanker fire kills 31 in Cairo, Trump proposes tariffs on 14 partners \u2014 "
           "and a Pakistani astronaut reaches Tiangong.")
    d.text(((W - d.textlength(sub, font=sf)) / 2, 106), sub, font=sf, fill=INK)
    rule(d, M, 128, CW, width=1)

    # ---- Day in Numbers
    small_caps(d, "The day in numbers", M, 134, size=9, fill=RED)
    colw = CW / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + i * colw
        nf = font(SERIF_BOLD, 26)
        d.text((cx, 146), num, font=nf, fill=INK)
        d.text((cx, 178), lab, font=font(SANS, 8), fill=MUTED)
        if i:
            d.line([(cx - 8, 148), (cx - 8, 186)], fill=FAINT, width=1)
    rule(d, M, 190, CW, width=1)

    # ---- Timeline
    small_caps(d, "Timeline \u2014 UTC", M, 196, size=9, fill=RED)
    tw = (CW - 120) / 5
    for i, (tm, txt) in enumerate(TIMELINE):
        tx = M + 120 + i * tw
        d.text((tx, 196), tm, font=font(SANS_B, 9), fill=RED)
        lines = fit(d, txt, font(SANS, 8), tw - 8, 2, f"timeline {tm}")
        draw_lines(d, lines, tx, 208, font(SANS, 8), INK, 10)
    rule(d, M, 232, CW, width=1)

    # ---- Heroes
    hy, hh = 240, 146
    hw = (CW - 2 * 16) / 3
    for i, hro in enumerate(HEROES):
        hx = M + i * (hw + 16)
        d.text((hx, hy), str(hro["num"]), font=font(SERIF_BOLD, 13), fill=RED)
        small_caps(d, hro["kick"], hx + 16, hy + 3, size=8)
        lines = fit(d, hro["head"], font(SERIF_BOLD, 16), hw, 2, f"hero {hro['num']}")
        draw_lines(d, lines, hx, hy + 16, font(SERIF_BOLD, 16), INK, 19)
        ay = hy + 16 + len(lines) * 19 + 4
        ah = 52
        if hro["art"] == "cairo":
            art_cairo(d, hx, ay, hw, ah)
        elif hro["art"] == "tariffs":
            art_tariffs(d, hx, ay, hw, ah)
        else:
            art_shenzhou(d, hx, ay, hw, ah)
        by = ay + ah + 4
        blines = fit(d, hro["body"], font(SANS, 9), hw, 2, f"hero body {hro['num']}")
        draw_lines(d, blines, hx, by, font(SANS, 9), INK, 10)
        small_caps(d, hro["src"], hx, by + len(blines) * 10 + 2, size=7)
        assert by + len(blines) * 10 + 10 <= hy + hh, f"hero {hro['num']} overflows"
    rule(d, M, hy + hh + 6, CW, width=1)

    # ---- Cards (2 rows x 5)
    cw = (CW - 4 * 12) / 5
    ch = 136
    for row in range(2):
        cy0 = 400 + row * (ch + 6)
        for col in range(5):
            c = CARDS[row * 5 + col]
            cx = M + col * (cw + 12)
            rule(d, cx, cy0, cw, fill=INK, width=2)
            d.text((cx, cy0 + 5), str(c["num"]), font=font(SERIF_BOLD, 11), fill=RED)
            kick = trim_to(d, c["kick"].upper(), font(SANS_B, 7), cw - 16)
            small_caps(d, kick, cx + 14, cy0 + 7, size=7)
            lines = fit(d, c["head"], font(SERIF_BOLD, 12), cw, 2, f"card {c['num']}")
            draw_lines(d, lines, cx, cy0 + 20, font(SERIF_BOLD, 12), INK, 14)
            ay = cy0 + 20 + len(lines) * 14 + 4
            ah = 50
            art_panel(d, cx, ay, cw, ah, c["art"], c["banner"])
            by = ay + ah + 4
            blines = fit(d, c["body"], font(SANS, 8), cw, 2, f"card body {c['num']}")
            draw_lines(d, blines, cx, by, font(SANS, 8), INK, 10)
            small_caps(d, c["src"], cx, cy0 + ch - 9, size=7)
    rule(d, M, 682, CW, width=1)

    # ---- World map (taller than v1-26Nov: 80px so Eurasia is not a thin strip)
    my = 688
    small_caps(d, "Where it happened", M, my, size=9, fill=RED)
    small_caps(d, "13 featured stories  \u00b7  numbered pins  \u00b7  schematic map, not to scale",
               M + 150, my, size=8)
    map_top, map_h = my + 14, 80
    mx0, mx1 = M, W - M
    lon2x = lambda lon: mx0 + (lon + 170) / 360 * (mx1 - mx0)
    lat2y = lambda lat: map_top + (78 - lat) / 136 * map_h
    for poly in CONTINENTS:
        d.polygon([(lon2x(lo), lat2y(la)) for lo, la in poly], fill=LAND, outline=INK)
    for (lab, lo, la) in [("ATLANTIC", -30, -25), ("PACIFIC", -150, -25),
                          ("INDIAN", 90, -30)]:
        tx = lon2x(lo) - d.textlength(lab, font=font(SANS_B, 7)) / 2
        d.text((tx, lat2y(la)), lab, font=font(SANS_B, 7), fill=BLUE)
    for (n, lo, la, dx, dy) in PINS:
        px, py = lon2x(lo) + dx, lat2y(la) + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=PAPER, width=1)
        tw_ = d.textlength(str(n), font=font(SANS_B, 7))
        d.text((px - tw_ / 2, py - 5), str(n), font=font(SANS_B, 7), fill=PAPER)
    # region counts line
    ry = map_top + map_h + 4
    small_caps(d, "Middle East 6  \u00b7  Europe 10  \u00b7  East Asia 2  \u00b7  South Asia 1  "
                  "\u00b7  SE Asia 1  \u00b7  Africa 3  \u00b7  North America 9  \u00b7  "
                  "Latin America 1  \u00b7  Oceania 3  \u00b7  Global 1  \u00b7  EU\u2013N. America 1",
               M, ry, size=8)
    rule(d, M, ry + 14, CW, width=1)

    # ---- Also on
    ay0 = ry + 22
    small_caps(d, "Also on Wednesday 25 November", M, ay0, size=9, fill=RED)
    colw2 = CW / 2
    for i, (n, head, src) in enumerate(ALSO):
        col, r = divmod(i, 13)
        ax = M + col * colw2
        ay = ay0 + 14 + r * 9
        d.text((ax, ay), str(n), font=font(SANS_B, 8), fill=RED)
        hf = font(SANS, 8)
        srcw = d.textlength("  " + src, font=font(SANS_B, 7))
        max_hw = colw2 - 22 - srcw
        hh_ = head
        while d.textlength(hh_, font=hf) > max_hw and len(hh_) > 10:
            hh_ = hh_[:-1]
        if hh_ != head:
            hh_ = hh_.rstrip() + "\u2026"
        d.text((ax + 16, ay), hh_, font=hf, fill=INK)
        d.text((ax + 16 + d.textlength(hh_, font=hf) + 4, ay), src,
               font=font(SANS_B, 7), fill=MUTED)
    rule(d, M, ay0 + 14 + 13 * 9 + 4, CW, width=1)

    # ---- DATE CHECK
    dy = ay0 + 14 + 13 * 9 + 10
    small_caps(d, "Date check \u2014 left out on purpose", M, dy, size=9, fill=RED)
    dc = ("LEFT OUT \u2014 24 Nov: PIF Tower strike \u00b7 Chen Jining probe \u00b7 "
          "Huawei guilty 10/12 \u00b7 Zaporizhzhia raid \u00b7 Sanofi $41bn deal \u00b7 "
          "AFCON to Senegal \u00b7 Serang toll 26 \u00b7 Hanoi gas blast \u00b7 "
          "Nepal quake 5.6 \u00b7 UAE bus crash \u00b7 Dow >50,000 \u00b7 Ariane 6, 36 sats \u00b7 "
          "Hormuz: 3 ships hit.  "
          "26 Nov: Sanaa blast & Riyadh intercepts \u00b7 Kim nuclear order (KCNA) \u00b7 "
          "Asia markets rebound \u00b7 FedEx Miami overrun \u00b7 Rams beat Packers \u00b7 "
          "UK\u2013EU treaty \u00b7 NZ quakes M5.2/M5.0 \u00b7 NSW Falcon raids.  "
          "NOT YET \u2014 Macy\u2019s Sat 28 Nov \u00b7 Thanksgiving 26 Nov \u00b7 "
          "Swiss 48 hrs end 27 Nov \u00b7 OPEC+ 29 Nov \u00b7 Spain vote 29 Nov \u00b7 "
          "USTR comments 5 Jan 2027.")
    dlines = fit(d, dc, font(SANS, 8), CW, 3, "date check")
    draw_lines(d, dlines, M, dy + 12, font(SANS, 8), INK, 10)
    rule(d, M, dy + 12 + len(dlines) * 10 + 4, CW, width=1)

    # ---- Footer
    fy = dy + 12 + len(dlines) * 10 + 10
    foot = ("HOW SURE:  CONFIRMED = verified by a named outlet  \u00b7  OFFICIAL = government / "
            "court / statistics office  \u00b7  REPORTED = reported, not officially confirmed  "
            "\u00b7  CLAIM = one side\u2019s claim  \u00b7  ONGOING = still developing.")
    flines = fit(d, foot, font(SANS, 7), CW, 1, "footer")
    draw_lines(d, flines, M, fy, font(SANS, 7), MUTED, 9)
    assert fy + len(flines) * 9 <= H - 6, f"footer overflows: {fy}"
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    data = open(out, "rb").read()
    print(out, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    print("size", img.size, img.mode)


if __name__ == "__main__":
    main()
