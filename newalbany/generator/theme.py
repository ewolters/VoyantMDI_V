# MDI theme: the ONLY place brand lives.
# Every generator writes through write_themed(), which maps the Voyant base tokens to the active theme.
# Pick a theme with the environment variable MDI_THEME (default "voyant"); override the site label with MDI_SITE.
#
# Signal colors (green / amber / red), grays and whites are NOT brand. They mean the same thing in every
# theme and are never remapped.
import os, re

THEMES = {
    "voyant": {  # Voyant Brand Guidelines v2.0
        "brand": "voyant", "site": "NEW ALBANY",
        "font_heading": "Georgia", "font_body": "Arial",
        "dark": "#07272D", "primary": "#004851", "accent": "#00B2A9", "soft": "#B0E3E4", "tint": "#E5F3F3", "tint_svg": "#EEF6F6",
    },
    "svend": {   # TODO: replace with the real SVEND palette + font before first use
        "brand": "SVEND", "site": "MDI",
        "font_heading": "Segoe UI", "font_body": "Segoe UI",
        "dark": "#111827", "primary": "#1F3A5F", "accent": "#2F80ED", "soft": "#C9DDF7", "tint": "#EAF2FC", "tint_svg": "#F1F6FD",
    },
    "neutral": { # unbranded
        "brand": "MDI", "site": "PLANT",
        "font_heading": "Segoe UI", "font_body": "Segoe UI",
        "dark": "#1F2933", "primary": "#334E68", "accent": "#486581", "soft": "#BCCCDC", "tint": "#E9EEF3", "tint_svg": "#F0F4F8",
    },
}
_BASE = THEMES["voyant"]
_FONT_ENUM = {"Georgia": "Font.Georgia", "Arial": "Font.Arial", "Segoe UI": "Font.'Segoe UI'", "Verdana": "Font.Verdana",
              "Lato": "Font.Lato", "Open Sans": "Font.'Open Sans'", "Courier New": "Font.'Courier New'"}

def _rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def theme_map(name=None):
    """List of (from, to) string replacements turning Voyant tokens into the named theme."""
    t = THEMES[name or os.environ.get("MDI_THEME", "voyant")]
    site = os.environ.get("MDI_SITE", t["site"])
    pairs = []
    for key in ("dark", "primary", "accent", "soft", "tint", "tint_svg"):
        a, b = _BASE[key], t[key]
        if a.upper() == b.upper(): continue
        pairs.append(("RGBA_" + key, _rgb(a), _rgb(b)))            # Power Fx RGBA(...) incl. any alpha
        pairs.append((a.upper(), b.upper())); pairs.append((a.lower(), b.lower()))   # SVG hex
        pairs.append(("%23" + a.upper().lstrip("#"), "%23" + b.upper().lstrip("#")))  # URL-encoded SVG hex
    out = []
    for p in pairs:
        out.append(p)
    text = [('"' + _BASE["brand"] + '"', '"' + t["brand"] + '"'),
            ('"' + _BASE["site"] + '"', '"' + site + '"'),
            ("Font." + _BASE["font_heading"], _FONT_ENUM.get(t["font_heading"], "Font." + t["font_heading"])),
            ("Font." + _BASE["font_body"], _FONT_ENUM.get(t["font_body"], "Font." + t["font_body"])),
            ("font-family='" + _BASE["font_body"] + "'", "font-family='" + t["font_body"] + "'"),
            ("font-family%3D%27" + _BASE["font_body"] + "%27", "font-family%3D%27" + t["font_body"].replace(" ", "%20") + "%27")]
    if site != _BASE["site"] and t["site"] == _BASE["site"]:
        pass
    for a, b in text:
        if a != b: out.append((a, b))
    return out

def apply_theme(text, name=None):
    for p in theme_map(name):
        if p[0].startswith("RGBA_"):
            (r1, g1, b1), (r2, g2, b2) = p[1], p[2]
            text = re.sub(rf"RGBA\({r1}, {g1}, {b1}, ([0-9.]+)\)", lambda m: f"RGBA({r2}, {g2}, {b2}, {m.group(1)})", text)
        else:
            text = text.replace(p[0], p[1])
    return text

exec(open(__import__("os").environ["MDI_GEN"]+"/fx_compat.py").read())
def write_themed(path, text):
    if os.environ.get("MDI_OUTDIR"): path = os.path.join(os.environ["MDI_OUTDIR"], os.path.basename(path))
    open(path, "w").write(photo_b64(fix_iferror(apply_theme(text))))
