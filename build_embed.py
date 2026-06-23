# -*- coding: utf-8 -*-
"""Embed images as base64 data URIs into index.html by token replacement.
Keeps base64 off the editing context (operates on disk)."""
import base64, io, os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, "index.html")
SRC  = os.path.join(ROOT, "assets_src")

# token -> (source path, max_width, quality)
JOBS = {
    "__HERO__":     (os.path.join(SRC, "portrait.jpg"), 1100, 80),
    "__ABOUT__":    (os.path.join(SRC, "about.jpg"),    1500, 82),
    "__UNIVERSE__": (os.path.join(SRC, "universe.jpg"), 1280, 80),
    "__AFIRME__":   (os.path.join(SRC, "afirme.jpg"),   1280, 80),
}

def encode(path, max_w, q):
    im = Image.open(path)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if im.width > max_w:
        h = round(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=q, optimize=True, progressive=True)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:image/jpeg;base64," + data, len(buf.getvalue())

with open(HTML, "r", encoding="utf-8") as f:
    html = f.read()

total = 0
for token, (path, max_w, q) in JOBS.items():
    if token not in html:
        print("WARN token not found:", token); continue
    uri, nbytes = encode(path, max_w, q)
    html = html.replace(token, uri)
    total += nbytes
    print(f"{token:12s} <- {os.path.basename(path):24s} {nbytes/1024:7.1f} KB")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nEmbedded raw image bytes: {total/1024:.1f} KB")
print(f"index.html size: {os.path.getsize(HTML)/1024:.1f} KB")
remaining = [t for t in JOBS if t in html]
print("Remaining tokens:", remaining if remaining else "none")
