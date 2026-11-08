#!/usr/bin/env python3
"""
Пиксельный мультик-промо для Instagram Reels / Stories (1080x1920, 9:16).

Всё рисуется кодом на маленьком холсте 270x480 и масштабируется x4
без сглаживания — так получаются настоящие "пиксели".

Запуск:
    python3 make_promo.py            # -> out/promo.mp4 + out/cover.png
    python3 make_promo.py --preview  # -> out/preview_*.png (ключевые кадры)

Нужно: Python 3 + Pillow, ffmpeg, шрифт Press Start 2P (fonts/).
"""
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ НАСТРОЙКИ
APP_NAME = "LEVEL UP"                 # <- название приложения
APP_TAGLINE = "ПРИЛОЖЕНИЕ ДЛЯ САМОРАЗВИТИЯ"
HERO_NAME = "ИГРОК 1"
CTA = "ССЫЛКА В ПРОФИЛЕ"

W, H = 270, 480          # «пиксельный» холст
SCALE = 4                # 270x480 -> 1080x1920
FPS = 24

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "PressStart2P-Regular.ttf")
OUT = os.path.join(HERE, "out")

_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT_PATH, size)
    return _fonts[size]


# ------------------------------------------------------------------ ПАЛИТРА
C = {
    "night": (22, 14, 48), "night2": (40, 24, 78), "purple": (88, 52, 150),
    "pink": (255, 77, 141), "gold": (255, 204, 51), "orange": (255, 136, 34),
    "red": (232, 48, 64), "green": (74, 222, 128), "dgreen": (30, 140, 80),
    "cyan": (56, 225, 255), "blue": (40, 90, 200), "white": (245, 245, 255),
    "grey": (130, 130, 160), "dgrey": (60, 60, 84), "black": (10, 8, 16),
    "wall": (44, 38, 70), "wall2": (36, 30, 58), "floor": (70, 48, 50),
    "wood": (120, 72, 48), "wood2": (90, 52, 36),
}


def lerp(a, b, k):
    return a + (b - a) * k


def lerpc(c1, c2, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp01(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ------------------------------------------------------------------ ГЕРОЙ
# Пацан с фото: тёмные волосы, густые брови, борода, чёрный вязаный
# зип-свитер поверх чёрного поло, руки скрещены.
HERO_PAL = {
    "K": (18, 12, 14),    # контур
    "H": (38, 26, 22),    # волосы
    "h": (62, 44, 36),    # блик волос
    "S": (226, 172, 140), # кожа
    "s": (192, 134, 104), # тень кожи
    "B": (40, 28, 24),    # борода
    "b": (66, 46, 38),    # борода светлее
    "e": (20, 14, 14),    # глаза
    "w": (250, 246, 240), # белок
    "J": (38, 38, 46),    # свитер
    "j": (58, 58, 70),    # фактура вязки
    "Z": (190, 194, 206), # молния
    "P": (16, 16, 20),    # поло
    "D": (34, 46, 78),    # джинсы
    "d": (26, 34, 58),
    "O": (230, 230, 236), # кроссовки
    "o": (150, 150, 165),
    "F": (30, 30, 36),    # телефон
    "L": (120, 220, 255), # экран
    "G": (16, 16, 18),    # очки
    "g": (90, 90, 120),   # блик очков
}

HEAD = [
    "....KKKKKKKKKK....",
    "...KHHhHHHHHhHK...",
    "..KHHHHHhHHHHHHK..",
    "..KHHHHHHHHHHHHK..",
    "..KHHSHHHHHHHSHK..",
    "..KHSSSSSSSSSSHK..",
    ".KSSHHHSSSSHHHSSK.",
    ".KSSSweSSSSweSSSK.",
    ".KsSSSSSSsSSSSSsK.",
    "..KSSSSSSsSSSSSK..",
    "..KBSSSSssSSSSBK..",
    "..KBBBBBBBBBBBBK..",
    "..KBBbBsssSBbBBK..",
    "..KBBBBBBBBBBBBK..",
    "...KBBBbBBbBBBK...",
    "....KBBBBBBBBK....",
    ".....KKsSSsKK.....",
]
HEAD_DOWN = HEAD[:7] + [
    ".KSSSSSSSSSSSSSSK.",
    ".KsSSeeSSsSeeSSsK.",
] + HEAD[9:]

BODY_CROSSED = [
    "...KKKJPPPPJKKK...",
    "..KJJJJjPPjJJJJK..",
    ".KJJjJJJPZPJJjJJK.",
    ".KJJJJJJJZJJJJJJK.",
    "KJJjJJJJJZJJJjJJJK",
    "KJKKKKKKKKKKKKKSSK",
    "KSSJJjJJjJJjJJJSSK",
    "KSSJjJJjJJjJJjJJJK",
    "KKKKKKKKKKKKKKKKKK",
    ".KJJJjJJJZJJjJJJK.",
    ".KJJJJJJJZJJJJJJK.",
    ".KKKKKKKKKKKKKKKK.",
]
BODY_PHONE = [
    "...KKKJPPPPJKKK...",
    "..KJJJJjPPjJJJJK..",
    ".KJJjJJJPZPJJjJJK.",
    ".KJJJJJJJZJJJJJJK.",
    "KJJjJJKKKKKKjJJJJK",
    "KJJJJKFLLLLFKJJJJK",
    "KJJJJKFLLLLFKJJjJK",
    "KJjJKSFLLLLFSKJJJK",
    "KJJJKSFFFFFFSKJJJK",
    ".KJJJKKKKKKKKJJJK.",
    ".KJJJJJJJZJJJJJJK.",
    ".KKKKKKKKKKKKKKKK.",
]
BODY_CHEER = [
    "...KKKJPPPPJKKK.KSSK",
    "..KJJJJjPPjJJJJKSSSK",
    ".KJJjJJJPZPJJjJKJJK.",
    ".KJJJJJJJZJJJJKJJK..",
    "KJJjJJJJJZJJJKJJK...",
    "KJJKJJJJJZJJJJJK....",
    "KJJKJjJJJZJJjJJK....",
    "KSSKJJJJJZJJJJJK....",
    "KSSKJJjJJZJjJJJK....",
    ".KKKJJJJJZJJJJJK....",
    "...KJJJJJZJJJJJK....",
    "...KKKKKKKKKKKKK....",
]
LEGS = [
    "...KDDDDDDDDDDK...",
    "...KDDdDDKDDdDK...",
    "...KDDDDK.KDDDK...",
    "...KDDdDK.KDdDK...",
    "...KDDDDK.KDDDK...",
    "...KDDDDK.KDDDK...",
    "..KOOOOOK.KOOOOK..",
    "..KooooK...KoooK..",
]
LEGS_WALK = [
    "...KDDDDDDDDDDK...",
    "...KDDdDDKDDdDK...",
    "..KDDDDK..KDDDK...",
    "..KDDdK...KDdDK...",
    ".KDDDK.....KDDK...",
    ".KDDK......KDDDK..",
    "KOOOOK.....KOOOOK.",
    "KooooK......KoooK.",
]
SHADES = [  # «очки как в мемах» — для финала
    "..GGGGGGG.GGGGGGG.",
    "GGGgGGGGGGGgGGGGGG",
    "..GGGGGG...GGGGGG.",
    "...GGGG.....GGGG..",
]


def draw_sprite(img, rows, x, y, scale=1, pal=HERO_PAL, tint=None, tint_k=0.0):
    px = img.load()
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            col = pal[ch]
            if tint is not None:
                col = lerpc(col, tint, tint_k)
            for dy in range(scale):
                for dx in range(scale):
                    X, Y = x + i * scale + dx, y + j * scale + dy
                    if 0 <= X < W and 0 <= Y < H:
                        px[X, Y] = col


def draw_hero(img, x, y, pose="crossed", scale=2, walk=False, head_bob=0,
              shades_y=None, tint=None, tint_k=0.0):
    """x,y — верхний левый угол головы. Ширина 18*scale."""
    head = HEAD_DOWN if pose == "phone" else HEAD
    body = {"crossed": BODY_CROSSED, "phone": BODY_PHONE,
            "cheer": BODY_CHEER}[pose]
    legs = LEGS_WALK if walk else LEGS
    hy = y + head_bob * scale
    by = y + len(HEAD) * scale
    ly = by + len(body) * scale
    draw_sprite(img, legs, x, ly, scale, tint=tint, tint_k=tint_k)
    draw_sprite(img, body, x, by, scale, tint=tint, tint_k=tint_k)
    draw_sprite(img, head, x, hy, scale, tint=tint, tint_k=tint_k)
    if shades_y is not None:
        draw_sprite(img, SHADES, x, hy + int(shades_y) * scale, scale)
    return (len(HEAD) + len(body) + len(LEGS)) * scale  # высота


HERO_H_ROWS = len(HEAD) + len(BODY_CROSSED) + len(LEGS)

# ------------------------------------------------------------------ ИКОНКИ
ICON_PAL = {
    "K": C["black"], "Y": C["gold"], "y": C["orange"], "R": C["red"],
    "W": C["white"], "G": C["green"], "g": C["dgreen"], "P": C["pink"],
    "C": C["cyan"], "B": C["blue"], "D": C["dgrey"], "M": C["grey"],
}
FIRE = [
    ".....R......",
    "....RR...R..",
    "...RRR..RR..",
    "..RRyRRRRR..",
    "..RyyyRRyR..",
    ".RRyYyyyyRR.",
    ".RyyYYYyyyR.",
    ".RyYYWYYyyR.",
    ".RyYWWWYYyR.",
    "..RyYWWYyR..",
    "...RRyyRR...",
    "....RRRR....",
]
STAR = [
    ".....K.....",
    "....KYK....",
    "....KYK....",
    "KKKKYYYKKKK",
    ".KYYYWYYYK.",
    "..KYYYYYK..",
    "..KYYKYYK..",
    ".KYYK.KYYK.",
    ".KKK...KKK.",
]
HEART = [
    ".KK...KK.",
    "KPPK.KPPK",
    "KPWPKPPPK",
    "KPPPPPPPK",
    ".KPPPPPK.",
    "..KPPPK..",
    "...KPK...",
    "....K....",
]
COIN = [
    "..KKKK..",
    ".KYYYYK.",
    "KYYWYYyK",
    "KYWYYYyK",
    "KYYYYYyK",
    "KYYYYyyK",
    ".KyyyyK.",
    "..KKKK..",
]
BOLT = [
    "....KKK",
    "...KYYK",
    "..KYYK.",
    ".KYYKKK",
    "KYYYYYK",
    "KKKYYK.",
    "..KYK..",
    ".KYK...",
    ".KK....",
]
BRAIN = [
    "..KKKKK..",
    ".KPPWPPK.",
    "KPPKPPPPK",
    "KPWPPKPPK",
    "KPPKPPWPK",
    ".KPPPKPK.",
    "..KKPPK..",
    "....KK...",
]
CHECK = [
    "......KK",
    ".....KGK",
    "K...KGK.",
    "KGK.KGK.",
    ".KGKGK..",
    "..KGK...",
    "...K....",
]


def icon(img, rows, x, y, scale=1):
    draw_sprite(img, rows, x, y, scale, pal=ICON_PAL)


# ------------------------------------------------------------------ ТЕКСТ
def text(d, s, x, y, size=8, col=C["white"], shadow=C["black"], center=False,
         outline=False):
    f = font(size)
    if center:
        w = d.textlength(s, font=f)
        x = int(x - w / 2)
    if outline:
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, 1),
                       (1, -1), (-1, -1)):
            d.text((x + ox, y + oy), s, font=f, fill=shadow)
    elif shadow is not None:
        d.text((x + 1, y + 1), s, font=f, fill=shadow)
    d.text((x, y), s, font=f, fill=col)


def typed(s, t, cps=18):
    n = int(max(0, t) * cps)
    return s[:n]


def panel(d, x0, y0, x1, y1, fill=C["night"], border=C["white"], b2=None):
    d.rectangle([x0, y0, x1, y1], fill=border)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=b2 or C["black"])
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=fill)


def bubble(d, x0, y0, x1, y1, tail_x, down=True):
    panel(d, x0, y0, x1, y1, fill=C["white"], border=C["black"], b2=C["black"])
    if down:
        for i in range(6):
            d.line([tail_x - 5 + i, y1 + i, tail_x + 1, y1 + i], fill=C["black"])
            if i < 5:
                d.line([tail_x - 3 + i, y1 - 1 + i, tail_x, y1 - 1 + i],
                       fill=C["white"])


# ------------------------------------------------------------------ ФОНЫ
_rng = random.Random(7)
STARS = [(_rng.randrange(W), _rng.randrange(H), _rng.random() * 6.28,
          _rng.choice([1, 1, 1, 2])) for _ in range(90)]
BUILDINGS = []
_x = -4
while _x < W:
    bw = _rng.randrange(18, 40)
    bh = _rng.randrange(40, 130)
    wins = [(wx, wy, _rng.random()) for wx in range(4, bw - 4, 6)
            for wy in range(6, bh, 8)]
    BUILDINGS.append((_x, bw, bh, wins))
    _x += bw + _rng.randrange(0, 4)


def sky(img, d, t, top=C["night"], bottom=C["night2"]):
    for y in range(0, H, 4):
        d.rectangle([0, y, W, y + 3], fill=lerpc(top, bottom, y / H))
    px = img.load()
    for (sx, sy, ph, sz) in STARS:
        b = 0.5 + 0.5 * math.sin(t * 3 + ph)
        if b > 0.25:
            col = lerpc(C["purple"], C["white"], b)
            d.rectangle([sx, sy, sx + sz - 1, sy + sz - 1], fill=col)


def city(d, t, base=H, lit=0.35, col=(16, 10, 34)):
    for (bx, bw, bh, wins) in BUILDINGS:
        d.rectangle([bx, base - bh, bx + bw, base], fill=col)
        for (wx, wy, r) in wins:
            on = r < lit or (r < lit + 0.1 and math.sin(t * 2 + r * 40) > 0)
            if on:
                d.rectangle([bx + wx, base - bh + wy, bx + wx + 2,
                             base - bh + wy + 3], fill=C["gold"])


def synth_floor(d, t, horizon=330, col=C["pink"]):
    d.rectangle([0, horizon, W, H], fill=(18, 6, 34))
    # горизонтальные линии бегут к зрителю
    for i in range(14):
        k = ((i + (t * 1.5) % 1) / 14) ** 2
        y = int(horizon + k * (H - horizon))
        d.line([0, y, W, y], fill=lerpc((60, 20, 80), col, k + 0.2))
    for i in range(-10, 11):
        x0 = W / 2 + i * 8
        x1 = W / 2 + i * 70
        d.line([x0, horizon, x1, H], fill=(120, 40, 140))
    d.line([0, horizon, W, horizon], fill=col)


def sun(d, cx, cy, r):
    for y in range(-r, r + 1):
        if y > 0 and (y // 3) % 2 == 1:
            continue
        hw = int(math.sqrt(max(0, r * r - y * y)))
        col = lerpc(C["gold"], C["pink"], (y + r) / (2 * r))
        d.line([cx - hw, cy + y, cx + hw, cy + y], fill=col)


def room(d, t, glow=0.0):
    d.rectangle([0, 0, W, H], fill=C["wall"])
    for y in range(0, 300, 16):  # обои
        for x in range((y // 16) % 2 * 8, W, 16):
            d.rectangle([x, y + 6, x + 1, y + 7], fill=C["wall2"])
    # окно с луной
    d.rectangle([150, 70, 246, 170], fill=C["wood2"])
    d.rectangle([154, 74, 242, 166], fill=(14, 10, 36))
    d.ellipse([210, 84, 230, 104], fill=(240, 236, 200))
    d.ellipse([216, 82, 236, 102], fill=(14, 10, 36))
    for (sx, sy, ph, _) in STARS[:14]:
        X, Y = 156 + sx % 84, 76 + sy % 88
        if math.sin(t * 3 + ph) > 0:
            d.point((X, Y), fill=C["white"])
    d.line([198, 74, 198, 166], fill=C["wood2"], width=3)
    d.line([154, 120, 242, 120], fill=C["wood2"], width=3)
    # часы
    panel(d, 20, 70, 108, 104, fill=C["black"], border=C["dgrey"])
    blink = ":" if int(t * 2) % 2 == 0 else " "
    text(d, f"03{blink}47", 28, 80, 16, C["red"], shadow=None)
    # пол и кровать
    d.rectangle([0, 300, W, H], fill=C["floor"])
    for y in range(300, H, 12):
        d.line([0, y, W, y], fill=(58, 40, 44))
    d.rectangle([110, 270, 270, 330], fill=C["wood"])
    d.rectangle([110, 262, 270, 286], fill=(200, 200, 220))
    d.rectangle([116, 254, 160, 270], fill=(235, 235, 245))
    if glow > 0:
        # синее свечение экрана
        ov = Image.new("RGB", (W, H), (60, 140, 255))
        return ov
    return None


# ------------------------------------------------------------------ СЦЕНЫ
SCENES = []  # (длительность, функция)


def scene(dur):
    def deco(fn):
        SCENES.append((dur, fn))
        return fn
    return deco


@scene(4.5)
def s_intro(img, d, t):
    sky(img, d, t)
    city(d, t, lit=0.25)
    # заголовок
    k = ease_back(t / 0.6)
    y = int(lerp(-40, 70, k))
    text(d, "ЗНАКОМЬТЕСЬ", W // 2, y, 16, C["gold"], center=True, outline=True)
    # герой падает сверху и приземляется
    land = 1.0
    hy_end = 200
    if t < land:
        hy = int(lerp(-140, hy_end, ease_out(t / land) ** 2))
    else:
        bounce = max(0, 1 - (t - land) * 3)
        hy = hy_end - int(abs(math.sin((t - land) * 12)) * 10 * bounce)
    scale = 3
    hx = W // 2 - 9 * scale
    if t > land:  # пыль от приземления
        p = (t - land) * 2
        if p < 1:
            for i in range(6):
                ox = int((i - 2.5) * 18 * p)
                d.rectangle([W // 2 + ox - 2, hy_end + HERO_H_ROWS * scale - 4,
                             W // 2 + ox + 2, hy_end + HERO_H_ROWS * scale],
                            fill=lerpc(C["white"], C["night2"], p))
    draw_hero(img, hx, hy, "crossed", scale)
    # карточка игрока
    if t > 1.6:
        k = ease_back((t - 1.6) / 0.5)
        x0 = int(lerp(-200, 20, k))
        panel(d, x0, 110, x0 + 230, 180)
        text(d, HERO_NAME, x0 + 12, 120, 8, C["cyan"])
        text(d, "LVL 1", x0 + 160, 120, 8, C["gold"])
        rows = [("МОТИВАЦИЯ", 2, C["pink"]), ("ДИСЦИПЛИНА", 1, C["orange"]),
                ("ЭНЕРГИЯ", 3, C["green"])]
        for i, (name, v, col) in enumerate(rows):
            yy = 136 + i * 13
            text(d, name, x0 + 12, yy, 8, C["white"])
            for b in range(10):
                c = col if b < v else C["dgrey"]
                d.rectangle([x0 + 112 + b * 11, yy, x0 + 120 + b * 11, yy + 7],
                            fill=c)


@scene(5.0)
def s_problem(img, d, t):
    room(d, t)
    # герой сидит на кровати с телефоном
    scale = 3
    hx, hy = 150, 150
    draw_hero(img, hx, hy, "phone", scale,
              head_bob=1 if int(t * 1.5) % 2 else 0)
    # свечение экрана на лице
    ov = Image.new("RGB", (W, H), (40, 110, 255))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    flick = 34 + int(12 * math.sin(t * 9))
    md.ellipse([hx - 6, hy, hx + 60, hy + 80], fill=flick)
    img.paste(Image.composite(ov, img, mask))
    # затемнение комнаты
    dark = Image.new("RGB", (W, H), (6, 4, 16))
    img.paste(Image.blend(img, dark, 0.25))
    d = ImageDraw.Draw(img)
    # мысли
    lines = ["НАЧНУ С", "ПОНЕДЕЛЬНИКА..."]
    if t > 0.4:
        bubble(d, 14, 190, 150, 228, 120)
        tt = t - 0.4
        text(d, typed(lines[0], tt), 24, 200, 8, C["black"], shadow=None)
        text(d, typed(lines[1], tt - len(lines[0]) / 18), 24, 212, 8,
             C["black"], shadow=None)
    # «счётчики» плохих привычек
    stats = [("СКРОЛЛИНГ", "5 Ч", C["red"]), ("ЦЕЛИ", "0/10", C["red"]),
             ("СОН", "4 Ч", C["red"])]
    for i, (a, b, col) in enumerate(stats):
        st = 2.2 + i * 0.5
        if t > st:
            k = ease_back((t - st) / 0.35)
            x = int(lerp(-140, 14, k))
            y = 360 + i * 22
            panel(d, x, y, x + 150, y + 18, fill=C["black"], border=col)
            text(d, a, x + 8, y + 6, 8, C["white"], shadow=None)
            text(d, b, x + 104, y + 6, 8, col, shadow=None)
    # zzz
    for i in range(3):
        z = (t * 0.8 + i * 0.33) % 1
        text(d, "Z", 250 - int(z * 12), 150 - int(z * 40), 8 + i * 0, lerpc(
            C["white"], C["wall"], z), shadow=None)


@scene(4.0)
def s_reveal(img, d, t):
    # уведомление -> вспышка -> логотип
    if t < 1.2:
        sky(img, d, t, top=(6, 6, 20), bottom=(12, 10, 30))
        # большой телефон
        px, py = 75, 120
        pw, ph = 120, 220
        shake = int(math.sin(t * 60) * 2) if t > 0.3 else 0
        d.rectangle([px - 4 + shake, py - 4, px + pw + 4 + shake, py + ph + 4],
                    fill=C["dgrey"])
        d.rectangle([px + shake, py, px + pw + shake, py + ph], fill=(14, 20, 40))
        if t > 0.3:
            k = ease_back((t - 0.3) / 0.3)
            ny = int(lerp(py - 40, py + 20, k))
            d.rectangle([px + 6 + shake, ny, px + pw - 6 + shake, ny + 44],
                        fill=C["white"])
            icon(img, STAR, px + 12 + shake, ny + 10, 2)
            text(d, "НОВЫЙ", px + 40 + shake, ny + 10, 8, C["black"],
                 shadow=None)
            text(d, "КВЕСТ!", px + 40 + shake, ny + 24, 8, C["pink"],
                 shadow=None)
        if t > 0.9:  # нарастающая вспышка
            fl = Image.new("RGB", (W, H), C["white"])
            img.paste(Image.blend(img, fl, clamp01((t - 0.9) / 0.3)))
        return
    tt = t - 1.2
    sky(img, d, t, top=C["night"], bottom=(90, 30, 110))
    sun(d, W // 2, 330, 70)
    synth_floor(d, t)
    if tt < 0.3:
        fl = Image.new("RGB", (W, H), C["white"])
        img.paste(Image.blend(img, fl, 1 - tt / 0.3))
        d = ImageDraw.Draw(img)
    # монетки
    for i in range(8):
        a = i / 8 * 6.28 + t * 1.5
        r = 90 + 6 * math.sin(t * 5 + i)
        icon(img, COIN, int(W / 2 + math.cos(a) * r) - 4,
             int(160 + math.sin(a) * r * 0.4) - 4)
    # логотип
    k = ease_back(tt / 0.6)
    size = 24
    y = int(lerp(-60, 150, k))
    wob = int(math.sin(t * 4) * 2)
    for off, col in ((4, C["pink"]), (2, C["cyan"])):
        text(d, APP_NAME, W // 2 + off, y + off + wob, size, col, shadow=None,
             center=True)
    text(d, APP_NAME, W // 2, y + wob, size, C["gold"], center=True,
         outline=True)
    if tt > 0.6:
        text(d, typed(APP_TAGLINE, tt - 0.6, 30), W // 2, 200, 8,
             C["white"], center=True, outline=True)


QUESTS = [("ЗАРЯДКА 10 МИН", 50), ("ПРОЧИТАТЬ 20 СТР", 40),
          ("2 Ч БЕЗ СОЦСЕТЕЙ", 70), ("ВЫПИТЬ 2 Л ВОДЫ", 20)]


def feature_title(d, t, num, title, sub):
    text(d, f"0{num}", 18, 64, 8, C["pink"])
    k = ease_out(t / 0.4)
    x = int(lerp(-260, 18, k))
    text(d, title, x, 78, 16, C["gold"], outline=True)
    text(d, typed(sub, t - 0.3, 30), 18, 102, 8, C["white"], outline=True)


@scene(3.6)
def s_quests(img, d, t):
    sky(img, d, t)
    city(d, t, lit=0.5)
    feature_title(d, t, 1, "КВЕСТЫ", "ПРИВЫЧКИ ПРЕВРАЩАЮТСЯ В ИГРУ")
    panel(d, 14, 128, 256, 290)
    text(d, "СЕГОДНЯ", 26, 138, 8, C["cyan"])
    for i, (q, xp) in enumerate(QUESTS):
        y = 158 + i * 32
        d.rectangle([26, y, 40, y + 14], fill=C["white"])
        d.rectangle([28, y + 2, 38, y + 12], fill=C["black"])
        text(d, q, 48, y + 4, 8, C["white"])
        done_t = 0.7 + i * 0.55
        if t > done_t:
            icon(img, CHECK, 29, y + 3, 2 if False else 1)
            d.line([48, y + 8, 48 + len(q) * 8 * min(1, (t - done_t) * 4), y + 8],
                   fill=C["green"])
            p = (t - done_t)
            if p < 0.8:
                text(d, f"+{xp} XP", 200, int(y - p * 24), 8,
                     lerpc(C["gold"], C["night"], p / 0.8), outline=True)
    # маленький герой рядом — радуется
    pose = "cheer" if int(t * 4) % 2 and t > 0.7 else "crossed"
    draw_hero(img, 160, 306, pose, 2)


@scene(3.6)
def s_levels(img, d, t):
    sky(img, d, t, top=(20, 10, 50), bottom=(60, 20, 90))
    synth_floor(d, t, horizon=360)
    feature_title(d, t, 2, "ОПЫТ И LVL", "КАЖДЫЙ ШАГ ДАЁТ XP")
    lvl = 1 + int(clamp01((t - 0.4) / 2.6) * 9)
    fill = ((t - 0.4) * 3.5) % 1 if t > 0.4 and t < 3.0 else (1 if t >= 3 else 0)
    # шкала XP
    panel(d, 20, 140, 250, 176)
    text(d, f"LVL {lvl}", 30, 152, 8, C["gold"])
    d.rectangle([90, 150, 238, 164], fill=C["dgrey"])
    d.rectangle([90, 150, 90 + int(148 * fill), 164], fill=C["green"])
    for x in range(90, 238, 8):
        d.line([x, 150, x, 164], fill=C["dgreen"])
    # LEVEL UP! вспышки на каждом переходе
    phase = ((t - 0.4) * 3.5) % 1 if t > 0.4 else 1
    if t > 0.4 and phase < 0.35 and t < 3.1:
        s = 16
        text(d, "LEVEL UP!", W // 2, 200 - int(phase * 20), s,
             C["pink"] if int(t * 10) % 2 else C["gold"], center=True,
             outline=True)
    scale = 3
    hx = W // 2 - 27
    tint_k = 0.5 if (t > 0.4 and phase < 0.15) else 0
    draw_hero(img, hx, 236, "crossed", scale, tint=C["gold"], tint_k=tint_k)
    # искры вокруг
    for i in range(10):
        a = i / 10 * 6.28 + t * 3
        r = 50 + 8 * math.sin(t * 6 + i)
        x = int(W / 2 + math.cos(a) * r)
        y = int(320 + math.sin(a) * r)
        d.rectangle([x, y, x + 1, y + 1], fill=C["gold"])


@scene(3.6)
def s_streak(img, d, t):
    sky(img, d, t, top=(40, 8, 20), bottom=(90, 30, 30))
    city(d, t, lit=0.3, col=(30, 8, 20))
    feature_title(d, t, 3, "СТРИКИ", "НЕ ПРЕРЫВАЙ СЕРИЮ")
    days = int(ease_out((t - 0.3) / 2.4) * 30) if t > 0.3 else 0
    pulse = 1 + (0.15 if int(t * 6) % 2 else 0)
    sc = int(6 * pulse)
    fx = W // 2 - 6 * sc
    fy = 140 - (sc - 6) * 6
    icon(img, FIRE, fx, fy + int(math.sin(t * 10) * 2), sc)
    text(d, str(days), W // 2, 222, 24, C["gold"], center=True, outline=True)
    text(d, "ДНЕЙ ПОДРЯД", W // 2, 254, 8, C["white"], center=True,
         outline=True)
    # календарь-сетка
    for i in range(30):
        x = 30 + (i % 10) * 22
        y = 280 + (i // 10) * 22
        col = C["orange"] if i < days else C["dgrey"]
        d.rectangle([x, y, x + 16, y + 16], fill=col)
        if i < days:
            d.rectangle([x + 2, y + 2, x + 5, y + 5], fill=C["gold"])
    if days >= 30:
        text(d, "ЛЕГЕНДА!", W // 2, 352, 16, C["pink"], center=True,
             outline=True)


@scene(3.6)
def s_stats(img, d, t):
    sky(img, d, t)
    feature_title(d, t, 4, "ПРОГРЕСС", "ВИДИШЬ, КАК РАСТЁШЬ")
    panel(d, 14, 128, 256, 380)
    bars = [("СИЛА", BOLT, C["gold"], 0.85), ("ФОКУС", BRAIN, C["pink"], 0.95),
            ("ЗДОРОВЬЕ", HEART, C["red"], 0.75), ("ЭНЕРГИЯ", STAR, C["cyan"],
                                                  0.9)]
    base = 340
    for i, (name, ic, col, v) in enumerate(bars):
        x = 34 + i * 56
        k = ease_back((t - 0.4 - i * 0.2) / 0.8)
        h = int(max(0, k) * v * 170)
        d.rectangle([x, base - h, x + 32, base], fill=col)
        d.rectangle([x, base - h, x + 32, base - h + 3], fill=C["white"])
        d.rectangle([x + 28, base - h, x + 32, base], fill=lerpc(col, C["black"],
                                                                 0.4))
        icon(img, ic, x + 8, base - h - 16)
        text(d, name[:5], x + 16, base + 8, 8, C["white"], center=True)
        if k > 0.95:
            text(d, f"+{int(v * 100)}%", x + 16, base - h + 8, 8, C["black"],
                 shadow=None, center=True)
    # мини-график линией
    pts = []
    for i in range(12):
        xx = 30 + i * 19
        yy = 180 - int((i / 11) ** 1.4 * 40 + math.sin(i) * 4)
        pts.append((xx, yy))
    n = int(clamp01((t - 0.3) / 1.6) * len(pts))
    if n > 1:
        d.line(pts[:n], fill=C["green"], width=2)
        x, y = pts[n - 1]
        d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=C["white"])


@scene(4.2)
def s_transform(img, d, t):
    sky(img, d, t, top=(40, 20, 80), bottom=(120, 40, 120))
    sun(d, W // 2, 330, 80)
    synth_floor(d, t, horizon=360)
    # лучи
    cx, cy = W // 2, 290
    if t > 0.6:
        for i in range(16):
            a = i / 16 * 6.28 + t * 0.8
            d.polygon([(cx, cy), (cx + math.cos(a) * 400, cy + math.sin(a) * 400),
                       (cx + math.cos(a + 0.12) * 400,
                        cy + math.sin(a + 0.12) * 400)],
                      fill=lerpc((120, 40, 120), C["gold"], 0.35))
    text(d, "ПРОКАЧКА", W // 2, 70, 16, C["gold"], center=True, outline=True)
    text(d, "ЗАВЕРШЕНА", W // 2, 92, 16, C["gold"], center=True, outline=True)
    scale = 3
    hx = W // 2 - 27
    flash = clamp01(1 - abs(t - 0.6) * 4)
    pose = "cheer" if t > 0.8 else "crossed"
    jump = int(abs(math.sin(t * 6)) * 10) if t > 0.8 and t < 2.4 else 0
    draw_hero(img, hx, 210 - jump, pose, scale, tint=C["white"], tint_k=flash)
    # новая карточка
    if t > 1.4:
        k = ease_back((t - 1.4) / 0.5)
        x0 = int(lerp(300, 20, k))
        panel(d, x0, 118, x0 + 230, 190, border=C["gold"])
        text(d, HERO_NAME, x0 + 12, 128, 8, C["cyan"])
        text(d, "LVL 30", x0 + 156, 128, 8, C["gold"])
        rows = [("МОТИВАЦИЯ", 10, C["pink"]), ("ДИСЦИПЛИНА", 9, C["orange"]),
                ("ЭНЕРГИЯ", 10, C["green"])]
        for i, (name, v, col) in enumerate(rows):
            yy = 146 + i * 13
            text(d, name, x0 + 12, yy, 8, C["white"])
            vv = min(v, int((t - 1.6) * 12))
            for b in range(10):
                c = col if b < vv else C["dgrey"]
                d.rectangle([x0 + 112 + b * 11, yy, x0 + 120 + b * 11, yy + 7],
                            fill=c)
    # конфетти
    rr = random.Random(int(t * FPS) // 2)
    if t > 0.8:
        for _ in range(30):
            x = rr.randrange(W)
            y = rr.randrange(60, 420)
            d.rectangle([x, y, x + 2, y + 2],
                        fill=rr.choice([C["gold"], C["pink"], C["cyan"],
                                        C["green"]]))


@scene(5.5)
def s_final(img, d, t):
    sky(img, d, t)
    sun(d, W // 2, 300, 64)
    synth_floor(d, t, horizon=330)
    scale = 3
    hx = W // 2 - 27
    hy = 190
    # очки падают сверху
    sh_end = 6
    if t < 0.4:
        sy = None
    elif t < 1.2:
        sy = lerp(-60, sh_end, ease_out((t - 0.4) / 0.8))
    else:
        sy = sh_end
    draw_hero(img, hx, hy, "crossed", scale, shades_y=sy)
    if t > 1.2 and t < 1.6:  # блик
        x = hx + 6 * scale
        d.rectangle([x, hy + 7 * scale, x + 2, hy + 7 * scale + 2],
                    fill=C["white"])
    k = ease_back((t - 0.2) / 0.6)
    text(d, "ПРОКАЧАЙ", W // 2, int(lerp(-30, 66, k)), 16, C["white"],
         center=True, outline=True)
    text(d, "СЕБЯ В", W // 2, int(lerp(-30, 88, k)), 16, C["white"],
         center=True, outline=True)
    text(d, "РЕАЛЬНОЙ ЖИЗНИ", W // 2, int(lerp(-30, 110, k)), 16, C["gold"],
         center=True, outline=True)
    if t > 1.4:
        wob = int(math.sin(t * 4) * 2)
        y = 146 + wob
        for off, col in ((3, C["pink"]), (1, C["cyan"])):
            text(d, APP_NAME, W // 2 + off, y + off, 24, col, shadow=None,
                 center=True)
        text(d, APP_NAME, W // 2, y, 24, C["gold"], center=True, outline=True)
    if t > 2.0:
        if int(t * 2.5) % 2 == 0:
            panel(d, 40, 394, 230, 416, fill=C["pink"], border=C["white"])
            text(d, CTA, W // 2, 402, 8, C["white"], center=True)
        # стрелка вверх (на профиль)
        ax, ay = W // 2, 380 - int(abs(math.sin(t * 5)) * 4)
        for i in range(5):
            d.line([ax - i, ay + i, ax + i, ay + i], fill=C["white"])
        text(d, "PRESS START", W // 2, 432, 8,
             C["gold"] if int(t * 4) % 2 else C["white"], center=True,
             outline=True)


# ------------------------------------------------------------------ СБОРКА
TRANS = 0.35  # пиксельный переход между сценами
TOTAL = sum(dd for dd, _ in SCENES)
_block_rng = random.Random(3)
BLOCK = 15
BLOCK_ORDER = [_block_rng.random() for _ in range((W // BLOCK + 1) *
                                                  (H // BLOCK + 1))]


def render_scene(i, lt):
    img = Image.new("RGB", (W, H), C["black"])
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    SCENES[i][1](img, d, lt)
    return img


def frame(t):
    acc = 0
    for i, (dur, fn) in enumerate(SCENES):
        if t < acc + dur or i == len(SCENES) - 1:
            lt = t - acc
            img = render_scene(i, lt)
            # переход «пиксельными блоками» в начале сцены
            if i > 0 and lt < TRANS:
                prev = render_scene(i - 1, SCENES[i - 1][0] + lt)
                k = lt / TRANS
                cols = W // BLOCK + 1
                for idx, r in enumerate(BLOCK_ORDER):
                    if r > k:
                        bx, by = (idx % cols) * BLOCK, (idx // cols) * BLOCK
                        box = (bx, by, min(W, bx + BLOCK), min(H, by + BLOCK))
                        img.paste(prev.crop(box), box)
            # Затемнение в начале и в конце ролика
            if t < 0.3 or t > TOTAL - 0.4:
                k = clamp01(t / 0.3) if t < 0.3 else clamp01((TOTAL - t) / 0.4)
                img = Image.blend(Image.new("RGB", (W, H), C["black"]), img, k)
            return img
        acc += dur


def scanlines(big):
    # лёгкий ретро-эффект ЭЛТ: каждая 4-я строка чуть темнее
    ov = Image.new("RGB", big.size, (0, 0, 0))
    mask = Image.new("L", big.size, 0)
    md = ImageDraw.Draw(mask)
    for y in range(SCALE - 1, big.size[1], SCALE):
        md.line([0, y, big.size[0], y], fill=40)
    return Image.composite(ov, big, mask)


def upscale(img):
    return scanlines(img.resize((W * SCALE, H * SCALE), Image.NEAREST))


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--preview" in sys.argv:
        acc = 0
        for i, (dur, fn) in enumerate(SCENES):
            for k in (0.5, 0.9):
                upscale(frame(acc + dur * k)).save(
                    os.path.join(OUT, f"preview_{i}_{int(k * 10)}.png"))
            acc += dur
        print("previews ->", OUT)
        return
    n = int(TOTAL * FPS)
    mp4 = os.path.join(OUT, "promo.mp4")
    music = os.path.join(OUT, "music.wav")
    make_chiptune(music, TOTAL)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{W * SCALE}x{H * SCALE}",
           "-r", str(FPS), "-i", "-", "-i", music,
           "-c:v", "libx264", "-preset", "slow", "-crf", "16",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n):
        p.stdin.write(upscale(frame(f / FPS)).tobytes())
        if f % 48 == 0:
            print(f"frame {f}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    # обложка для Reels
    acc = sum(dd for dd, _ in SCENES[:-1])
    upscale(frame(acc + 3.5)).save(os.path.join(OUT, "cover.png"))
    print("done ->", mp4)


# ------------------------------------------------------------------ МУЗЫКА
def make_chiptune(path, seconds, sr=22050):
    """Простенький 8-битный трек (квадратная волна + бас + хэт)."""
    import struct
    import wave
    bpm = 132
    beat = 60 / bpm
    # A-минор -> F -> C -> G, мелодия по 8-м
    prog = [(57, [69, 72, 76, 72, 74, 72, 69, 67]),
            (53, [65, 69, 72, 69, 72, 74, 72, 69]),
            (48, [67, 72, 76, 79, 76, 72, 76, 79]),
            (55, [71, 74, 79, 74, 76, 74, 71, 74])]

    def freq(m):
        return 440 * 2 ** ((m - 69) / 12)

    n = int(seconds * sr)
    buf = bytearray()
    noise = random.Random(1)
    for i in range(n):
        t = i / sr
        bar = int(t / (beat * 4)) % 4
        bass_n, mel = prog[bar]
        e = int(t / (beat / 2)) % 8
        te = t % (beat / 2)
        # первые 4.5с (интро) и сцена проблемы — тише и без мелодии
        quiet = t < 9.5
        v = 0.0
        if not quiet or e % 2 == 0:
            fm = freq(mel[e] + (0 if not quiet else -12))
            env = max(0, 1 - te / (beat / 2) * 0.9)
            duty = 0.25
            v += (0.12 if not quiet else 0.05) * env * (
                1 if (t * fm) % 1 < duty else -1)
        fb = freq(bass_n - 12)
        tb = t % (beat)
        v += 0.10 * max(0, 1 - tb / beat) * (2 * abs(2 * ((t * fb) % 1) - 1) - 1)
        if not quiet:
            th = t % (beat / 2)
            if th < 0.03:
                v += 0.05 * (noise.random() * 2 - 1) * (1 - th / 0.03)
            tk = t % beat
            if tk < 0.08:  # бочка
                v += 0.25 * math.sin(2 * math.pi * (60 + 120 * (1 - tk / 0.08))
                                     * tk) * (1 - tk / 0.08)
        # затухание в конце
        if t > seconds - 1.0:
            v *= max(0, (seconds - t) / 1.0)
        s = int(max(-1, min(1, v)) * 32000)
        buf += struct.pack("<h", s)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(buf))


if __name__ == "__main__":
    main()
