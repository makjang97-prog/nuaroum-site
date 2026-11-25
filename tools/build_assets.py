#!/usr/bin/env python3
"""Build static assets for the NOUAROUM site: product photos, fonts, map, OG image, icons."""
import math
import pathlib
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PRODUCTS = ASSETS / "products"
FONTS = ASSETS / "fonts"
CACHE = pathlib.Path("/workspace/tmp/osm-tiles")
for p in (ASSETS, PRODUCTS, FONTS, CACHE):
    p.mkdir(parents=True, exist_ok=True)

SRC_FONTS = {
    "Cormorant-300.ttf": pathlib.Path("/workspace/documents/jewde-counseling-sheet/fonts/Cormorant-300.ttf"),
    "Cormorant-400.ttf": pathlib.Path("/workspace/documents/jewde-counseling-sheet/fonts/Cormorant-400.ttf"),
    "NotoSerifKR-300.ttf": pathlib.Path("/workspace/documents/jewde-counseling-sheet/fonts/NotoSerifKR-300.ttf"),
    "NotoSerifKR-400.ttf": pathlib.Path("/workspace/documents/jewde-counseling-sheet/fonts/NotoSerifKR-400.ttf"),
    "NotoSansKR-Medium.ttf": pathlib.Path("/workspace/documents/maisonyoung/_build/fonts/NotoSansKR-Medium.ttf"),
}

# ---------------------------------------------------------------- fonts
from fontTools import subset
from fontTools.ttLib import TTFont


def text_corpus():
    txt = []
    for f in ("index.html", "script.js", "products.json"):
        p = ROOT / f
        if p.exists():
            txt.append(p.read_text(encoding="utf-8"))
    extra = "가나다라마바사아자차카타파하0123456789·—’“”…~!?%×+.,()[]&/’"
    return "".join(txt) + extra


def build_fonts():
    corpus = text_corpus()
    keep = sorted({ord(c) for c in corpus if ord(c) > 31})
    for name, src in SRC_FONTS.items():
        if not src.exists():
            print("missing font", src)
            continue
        out_name = name.replace(".ttf", ".woff2").lower()
        dest = FONTS / out_name
        if name.startswith("Noto"):
            sub = subset.Subsetter(subset.Options(drop_tables=["DSIG", "GSUB", "GPOS"]))
            font = TTFont(str(src))
            sub.populate(unicodes=keep)
            sub.subset(font)
            font.flavor = "woff2"
            font.save(str(dest))
        else:
            font = TTFont(str(src))
            font.flavor = "woff2"
            font.save(str(dest))
        print("font", dest.name, dest.stat().st_size)


# ---------------------------------------------------------------- photos
def build_photos():
    pairs = [
        ("/workspace/documents/nuaroum-product-test/ring_front_studio.png", PRODUCTS / "nr-eg-001-01.jpg"),
        ("/workspace/documents/nuaroum-product-test/ring_top_studio.png", PRODUCTS / "nr-eg-001-02.jpg"),
    ]
    for src, dest in pairs:
        im = Image.open(src).convert("RGB")
        # 사진 여백이 넓어 링이 작게 보인다 → 중심 72%로 크롭해 프레임을 채운다
        w, h = im.size
        cw, ch = int(w * 0.78), int(h * 0.78)
        left, top = (w - cw) // 2, (h - ch) // 2
        im = im.crop((left, top, left + cw, top + ch)).resize((w, h), Image.LANCZOS)
        im.save(dest, quality=92, optimize=True, progressive=True)
        print("photo", dest.name, im.size, dest.stat().st_size)

    # OG image 1200x630: white studio panel + romanced lockup
    og = Image.new("RGB", (1200, 630), "#F9F9F9")
    ring = Image.open(pairs[0][0]).convert("RGB")
    h = 590
    w = int(ring.width * h / ring.height)
    ring = ring.resize((w, h), Image.LANCZOS)
    og.paste(ring, (1200 - w - 40, (630 - h) // 2))

    d = ImageDraw.Draw(og)
    c300 = ImageFont.truetype(str(SRC_FONTS["Cormorant-300.ttf"]), 72)
    kr = ImageFont.truetype(str(SRC_FONTS["NotoSerifKR-300.ttf"]), 26)
    small = ImageFont.truetype(str(SRC_FONTS["NotoSansKR-Medium.ttf"]), 13)

    def track(draw, xy, text, font, fill, spacing):
        x, y = xy
        for ch in text:
            draw.text((x, y), ch, font=font, fill=fill)
            x += draw.textlength(ch, font=font) + spacing
        return x

    track(d, (90, 176), "NOUAROUM", c300, "#141110", 6)
    d.text((92, 268), "누아로움", font=kr, fill="#4A4642")
    d.line([(92, 330), (392, 330)], fill="#DEDAD3", width=1)
    track(d, (92, 356), "HERITAGE FINE JEWELRY", small, "#8C857D", 3.4)
    d.text((92, 410), "인천의 주얼리 아틀리에", font=kr, fill="#141110") if False else None
    d.text((92, 400), "빛을 담아, 오래도록", font=ImageFont.truetype(str(SRC_FONTS["NotoSerifKR-300.ttf"]), 30), fill="#141110")
    track(d, (92, 500), "WEDDING BAND · ENGAGEMENT · SOLITAIRE · COUPLE RING", small, "#9A8F84", 2.2)
    og.save(ASSETS / "og-image.jpg", quality=90, optimize=True)
    print("og", (ASSETS / "og-image.jpg").stat().st_size)

    # apple touch icon
    icon = Image.new("RGB", (180, 180), "#FFFFFF")
    dd = ImageDraw.Draw(icon)
    dd.ellipse((30, 30, 150, 150), outline="#141110", width=2)
    f = ImageFont.truetype(str(SRC_FONTS["Cormorant-300.ttf"]), 92)
    tw = dd.textlength("N", font=f)
    dd.text(((180 - tw) / 2, 40), "N", font=f, fill="#141110")
    icon.save(ASSETS / "apple-touch-icon.png")
    print("icon ok")


# ---------------------------------------------------------------- map
LAT, LON = 37.440672, 126.7086357
ZOOM = 16
OUT_W, OUT_H = 720, 600
TILE = 256
UA = "NouaroumSite/1.0 (showroom map; nuaroum.com)"


def deg2num(lat, lon, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def fetch(z, x, y):
    path = CACHE / f"{z}_{x}_{y}.png"
    if not path.exists():
        url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as res:
            path.write_bytes(res.read())
    return Image.open(path).convert("RGB")


def build_map():
    try:
        fx, fy = deg2num(LAT, LON, ZOOM)
        tx, ty = int(fx), int(fy)
        x0, y0 = tx - 2, ty - 2
        mosaic = Image.new("RGB", (5 * TILE, 5 * TILE), "white")
        for dx in range(5):
            for dy in range(5):
                mosaic.paste(fetch(ZOOM, x0 + dx, y0 + dy), (dx * TILE, dy * TILE))
        px, py = (fx - x0) * TILE, (fy - y0) * TILE
        left, top = int(px - OUT_W / 2), int(py - OUT_H / 2)
        crop = mosaic.crop((left, top, left + OUT_W, top + OUT_H))

        # calm, bright treatment: desaturate and lift so the map sits behind the copy
        grey = crop.convert("L").convert("RGB")
        crop = Image.blend(crop, grey, 0.62)
        white = Image.new("RGB", crop.size, "#ffffff")
        crop = Image.blend(crop, white, 0.22)

        d = ImageDraw.Draw(crop)
        cx, cy = OUT_W / 2, OUT_H / 2
        for r, color, wd in ((26, "#FFFFFF", 5), (26, "#141110", 2), (5, "#141110", 0)):
            if wd:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=wd)
            else:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
        crop.save(ASSETS / "map.jpg", quality=88, optimize=True)
        print("map", (ASSETS / "map.jpg").stat().st_size)
    except Exception as exc:  # network/tile service issue — site works without it
        print("map failed:", exc)


# ---------------------------------------------------------------- favicon
def build_favicon():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="#ffffff"/>
  <circle cx="32" cy="32" r="22" fill="none" stroke="#141110" stroke-width="1.2"/>
  <path d="M24 42V22l16 20V22" fill="none" stroke="#141110" stroke-width="1.6" stroke-linejoin="round"/>
</svg>
"""
    (ASSETS / "favicon.svg").write_text(svg, encoding="utf-8")
    print("favicon ok")


if __name__ == "__main__":
    build_photos()
    build_favicon()
    build_map()
    build_fonts()
