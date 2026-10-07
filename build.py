#!/usr/bin/env python3
"""Static site generator for christopherhuang.dev.

Single source of truth is src/content.json. Running this script regenerates
every HTML page in site/ from that data. Assets under site/assets/ are never
touched. No dependencies beyond the Python standard library.

Usage:
    python3 build.py            # build
    python3 build.py --serve    # build, then serve site/ on :8000
"""

import html
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "site")
ASSETS = os.path.join(OUT, "assets")

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")


def e(text):
    """Escape a value for use in HTML text or an attribute."""
    return html.escape(str(text), quote=True)


def gallery_files(rel_dir):
    """List image paths (relative to site/) inside an assets subdirectory.

    `rel_dir` is relative to site/assets, e.g. "img/big-hands". Returns [] when
    the directory is absent so a project with no photos still builds.
    """
    if not rel_dir or not isinstance(rel_dir, str):
        return []
    abs_dir = os.path.join(ASSETS, rel_dir)
    if not os.path.isdir(abs_dir):
        return []
    names = sorted(n for n in os.listdir(abs_dir)
                   if n.lower().endswith(IMG_EXT) and not n.endswith(".thumb.jpg"))
    return [f"assets/{rel_dir}/{n}" for n in names]


def thumb_of(src):
    """Thumbnail path for a full-size image, falling back to the original."""
    cand = os.path.splitext(src)[0] + ".thumb.jpg"
    return cand if os.path.exists(os.path.join(OUT, cand)) else src


def page(title, body, person, active="", depth=0):
    """Wrap `body` in the shared document shell.

    `depth` is how many directories deep the page sits, so asset and nav URLs
    stay correct for pages written into subdirectories.
    """
    up = "../" * depth
    nav = [("Work", "projects.html"), ("Research", "research.html"),
           ("About", "about.html"), ("Photos", "photos.html")]
    links = "".join(
        f'<a href="{up}{href}"{" class=\'active\'" if active == href else ""}>{label}</a>'
        for label, href in nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(person['tagline'])}">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="site-head">
  <a class="brand" href="{up}index.html">{e(person['name'])}</a>
  <nav>{links}</nav>
</header>
<main>
{body}
</main>
<footer class="site-foot">
  <p>{e(person['name'])} &middot; {e(person['location'])} &middot;
     <a href="mailto:{e(person['email'])}">{e(person['email'])}</a></p>
</footer>
<script src="{up}assets/app.js"></script>
</body>
</html>
"""


def render_gallery(images, up=""):
    if not images:
        return ""
    items = "".join(
        f'<figure><img src="{up}{e(thumb_of(src))}" data-full="{up}{e(src)}"'
        f' alt="" loading="lazy"></figure>'
        for src in images
    )
    return f'<section class="gallery" data-lightbox>{items}</section>'


def render_files(files, up=""):
    if not files:
        return ""
    items = ""
    for f in files:
        href = f["href"]
        # external and mailto links pass through; local paths get the prefix
        prefix = "" if href.startswith(("http", "mailto:", "#")) else up
        items += f'<li><a href="{prefix}{e(href)}">{e(f["label"])}</a></li>'
    return f'<section class="files"><h3>Files &amp; links</h3><ul>{items}</ul></section>'


def todo(note):
    return f'<p class="todo">{e(note)}</p>' if note else ""


def card(item, href, kicker=""):
    """A project/paper card. With no image it degrades to a clean text card
    rather than reserving an empty placeholder block."""
    imgs = gallery_files(item.get("images"))
    lead = item.get("hero") or (imgs[0] if imgs else None)
    if lead:
        thumb = (f'<div class="card-thumb">'
                 f'<img src="{e(thumb_of(lead))}" alt="" loading="lazy"></div>')
        cls = "card"
    else:
        thumb = ""
        cls = "card card-textonly"
    sub = item.get("subtitle") or item.get("venue", "")
    return f"""<a class="{cls}" href="{e(href)}">
  {thumb}
  <div class="card-body">
    {f'<p class="kicker">{e(kicker)}</p>' if kicker else ''}
    <h3>{e(item['title'])}</h3>
    {f'<p class="sub">{e(sub)}</p>' if sub else ''}
    <p class="summary">{e(item.get('summary',''))}</p>
  </div>
</a>"""


# ---------------------------------------------------------------- page builders

def build_home(c):
    p = c["person"]
    featured = [x for x in c["projects"] if x.get("featured")]
    # show the ones with photos first so the grid never opens on an empty tile
    featured.sort(key=lambda x: not gallery_files(x.get("images")))
    cards = "".join(card(x, f"projects/{x['id']}.html") for x in featured)
    papers = "".join(
        f'<li><a href="research/{e(x["id"])}.html"><strong>{e(x["title"])}</strong></a>'
        f'<span class="sub">{e(x["venue"])} &middot; {e(x["status"])}</span></li>'
        for x in c["research"]
    )
    links = " ".join(
        f'<a class="btn" href="{e(l["href"])}">{e(l["label"])}</a>' for l in p["links"]
    )
    # headshot is optional: drop one at site/assets/img/headshot.jpg to use it
    shot = "assets/img/headshot.jpg"
    has_shot = os.path.exists(os.path.join(OUT, shot))
    hero_img = (f'<div class="hero-img"><img src="{e(shot)}" alt="{e(p["name"])}"></div>'
                if has_shot else "")
    body = f"""<section class="hero{'' if has_shot else ' hero-noimg'}">
  <div class="hero-text">
    <h1>{e(p['name'])}</h1>
    <p class="tagline">{e(p['tagline'])}</p>
    <p class="blurb">{e(p['blurb'])}</p>
    <p class="btn-row">{links}</p>
  </div>
  {hero_img}
</section>

<section class="band">
  <h2>Selected work</h2>
  <div class="card-grid">{cards}</div>
  <p class="more"><a href="projects.html">All projects &rarr;</a></p>
</section>

<section class="band">
  <h2>Research</h2>
  <ul class="paper-list">{papers}</ul>
  <p class="more"><a href="research.html">More on each paper &rarr;</a></p>
</section>
"""
    return page(p["name"], body, p, "index.html")


def build_projects(c):
    p = c["person"]
    cards = "".join(card(x, f"projects/{x['id']}.html") for x in c["projects"])
    body = f"""<h1>Work</h1>
<p class="lede">Engineering projects, competition entries, and the prosthetics chapter I run.</p>
<div class="card-grid">{cards}</div>
"""
    return page(f"Work — {p['name']}", body, p, "projects.html")


def build_research(c):
    p = c["person"]
    cards = "".join(card(x, f"research/{x['id']}.html", kicker=x["status"]) for x in c["research"])
    body = f"""<h1>Research</h1>
<p class="lede">Papers in additive manufacturing, sensor-integrated robotic hands,
prosthetic socket fitting, and one in computational social science.</p>
<div class="card-grid">{cards}</div>
"""
    return page(f"Research — {p['name']}", body, p, "research.html")


def build_project_page(item, p):
    imgs = gallery_files(item.get("images"))
    extra = gallery_files(item.get("extra_images"))
    sections = ""
    for heading, key in [("Outcome", "outcome"), ("Why", "motivation"),
                         ("My role", "role"), ("How it works", "detail")]:
        val = item.get(key)
        if val:
            sections += f"<h2>{heading}</h2><p>{e(val)}</p>"
    body = f"""<article class="detail">
  <p class="kicker"><a href="../projects.html">&larr; Work</a></p>
  <h1>{e(item['title'])}</h1>
  <p class="sub">{e(item.get('subtitle',''))}</p>
  <p class="lede">{e(item.get('summary',''))}</p>
  {todo(item.get('note'))}
  {render_gallery(imgs[:6], up="../")}
  {sections}
  {render_files(item.get('files'), up="../")}
  {f'<h2>From the presentation</h2>{render_gallery(extra, up="../")}' if extra else ''}
</article>
"""
    return page(f"{item['title']} — {p['name']}", body, p, "projects.html", depth=1)


def build_research_page(item, p):
    imgs = gallery_files(item.get("images"))
    sections = ""
    for heading, key in [("Outcome", "outcome"), ("Why", "motivation"),
                         ("Method", "method"), ("What it means", "findings")]:
        val = item.get(key)
        if val:
            sections += f"<h2>{heading}</h2><p>{e(val)}</p>"
    body = f"""<article class="detail">
  <p class="kicker"><a href="../research.html">&larr; Research</a></p>
  <h1>{e(item['title'])}</h1>
  <p class="sub">{e(item['venue'])} &middot; {e(item['status'])}<br>
     {e(item['role'])} &middot; {e(item['date'])}</p>
  <p class="lede">{e(item.get('summary',''))}</p>
  {todo(item.get('note'))}
  {render_gallery(imgs[:4], up="../")}
  {sections}
  {render_files(item.get('files'), up="../")}
</article>
"""
    return page(f"{item['title']} — {p['name']}", body, p, "research.html", depth=1)


def build_about(c):
    p = c["person"]
    lead = ""
    for role in c["leadership"]:
        pts = "".join(f"<li>{e(x)}</li>" for x in role["points"])
        lead += f"""<div class="role">
  <h3>{e(role['org'])}</h3>
  <p class="sub">{e(role['role'])} &middot; {e(role['date'])}</p>
  <ul>{pts}</ul>
</div>"""
    awards = "".join(f"<li>{e(a)}</li>" for a in c["awards"])
    skills = "".join(
        f'<div class="skill"><h3>{e(k)}</h3><p>{e(", ".join(v))}</p></div>'
        for k, v in c["skills"].items()
    )
    body = f"""<h1>About</h1>
<p class="lede">{e(p['blurb'])}</p>
<p class="btn-row"><a class="btn" href="assets/docs/christopher-huang-resume.pdf">Resume (PDF)</a>
   <a class="btn" href="mailto:{e(p['email'])}">Email me</a></p>

<section class="band"><h2>Leadership &amp; service</h2>{lead}</section>
<section class="band"><h2>Awards</h2><ul class="awards">{awards}</ul></section>
<section class="band"><h2>Skills</h2><div class="skill-grid">{skills}</div></section>
"""
    return page(f"About — {p['name']}", body, p, "about.html")


def build_photos(c):
    p = c["person"]
    blocks = ""
    for h in c["hobbies"]:
        imgs = gallery_files(h.get("images"))
        blocks += f"""<section class="band">
  <h2>{e(h['title'])}</h2>
  <p>{e(h['blurb'])}</p>
  {render_gallery(imgs)}
</section>"""
    body = f"""<h1>Photos &amp; side things</h1>
<p class="lede">Photography, drawing, and Minecraft builds — the things I make when
nothing has to work.</p>
{blocks}
"""
    return page(f"Photos — {p['name']}", body, p, "photos.html")


def main():
    c = json.load(open(os.path.join(SRC, "content.json")))
    p = c["person"]
    os.makedirs(os.path.join(OUT, "projects"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "research"), exist_ok=True)

    written = []

    def write(rel, text):
        path = os.path.join(OUT, rel)
        with open(path, "w") as fh:
            fh.write(text)
        written.append(rel)

    write("index.html", build_home(c))
    write("projects.html", build_projects(c))
    write("research.html", build_research(c))
    write("about.html", build_about(c))
    write("photos.html", build_photos(c))
    for item in c["projects"]:
        write(f"projects/{item['id']}.html", build_project_page(item, p))
    for item in c["research"]:
        write(f"research/{item['id']}.html", build_research_page(item, p))

    # copy static assets that live in src/
    for name in ("style.css", "app.js"):
        shutil.copy(os.path.join(SRC, name), os.path.join(ASSETS, name))

    print(f"built {len(written)} pages into site/")
    for rel in written:
        print("  ", rel)

    todos = [x["id"] for x in c["projects"] + c["research"] if x.get("note")]
    if todos:
        print("\nstill needs material:", ", ".join(todos))

    if "--serve" in sys.argv:
        import http.server, socketserver
        os.chdir(OUT)
        with socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler) as s:
            print("serving http://localhost:8000 (ctrl-c to stop)")
            s.serve_forever()


if __name__ == "__main__":
    main()
