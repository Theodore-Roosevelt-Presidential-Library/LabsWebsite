#!/usr/bin/env python3
"""
Build labs.trlibrary.com from data/projects.json.

Everything on the site is generated from that one file. To add, remove, or
reword a project, edit the JSON and run:

    python3 tools/build.py

No dependencies. Output is plain static HTML committed to the repo, which is
what GitHub Pages serves from main / root.
"""

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
ORG_URL = DATA["meta"]["orgUrl"]
SITE = "https://labs.trlibrary.com"

CATEGORY_ORDER = [
    "Embeddable Widget",
    "Visitor Experience",
    "Interactive Media",
    "Dashboard",
    "Content Tool",
    "Data & Automation",
]

ICON_GITHUB = (
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 '
    '6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23'
    '-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66'
    '.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08'
    '-2.12 0 0 .67-.21 2.2.82a7.4 7.4 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82'
    '.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 '
    '1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
)
ICON_EXT = (
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M9 1v2h3.6L6.3 9.3l1.4 1.4L14 4.4V8h2V1H9z"/>'
    '<path d="M13 13H3V3h4V1H1v14h14V9h-2v4z"/></svg>'
)


def esc(s):
    return html.escape(str(s), quote=True)


def initials(name):
    words = [w for w in re.split(r"[\s-]+", name) if w]
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def shot_path(slug):
    """Return the screenshot's site-root path if the file exists, else None."""
    p = ROOT / "assets" / "shots" / f"{slug}.png"
    return f"assets/shots/{slug}.png" if p.exists() else None


def head(title, description, depth=0, canonical=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="TRPL Labs">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/css/labs.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{masthead(depth)}
"""


def masthead(depth=0):
    up = "../" * depth
    return f"""<header class="masthead">
  <div class="shell">
    <a class="brand" href="{up}index.html">
      <img src="{up}assets/img/trpl-wordmark-white.svg" alt="Theodore Roosevelt Presidential Library">
      <span class="labs">Labs</span>
    </a>
    <nav class="mast-nav" aria-label="Primary">
      <a href="{up}index.html#projects">Projects</a>
      <a href="{up}index.html#about">About</a>
      <a href="https://www.trlibrary.com">trlibrary.com</a>
      <a class="ghost" href="{ORG_URL}">GitHub</a>
    </nav>
  </div>
</header>
"""


def footer(depth=0):
    up = "../" * depth
    return f"""<footer class="footer">
  <div class="shell">
    <div>
      <img src="{up}assets/img/trpl-wordmark-white.svg" alt="Theodore Roosevelt Presidential Library">
      <p style="margin-top:14px">Medora, North Dakota</p>
      <p><a href="https://www.trlibrary.com">trlibrary.com</a> &nbsp;·&nbsp;
         <a href="{ORG_URL}">GitHub</a></p>
    </div>
    <div class="right">
      <p>Every project here is released under the MIT license. Fork it, rename it,
         and make it yours &mdash; no permission needed and no attribution required,
         though we would love to hear what you build.</p>
      <p style="margin:0"><a href="mailto:info@trlibrary.com">info@trlibrary.com</a></p>
    </div>
  </div>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- index page

def card(p):
    slug = p["slug"]
    shot = shot_path(slug)
    demo = p.get("demo")

    # Cards are screenshots only. Live demos live on the project pages, where
    # one iframe at a time is a reasonable thing to ask of a browser.
    if shot:
        media = (f'<img src="{shot}" alt="Screenshot of {esc(p["name"])}" '
                 f'loading="lazy" decoding="async" width="1280" height="800">')
    else:
        media = (
            f'<div class="fallback"><span class="glyph" aria-hidden="true">{esc(initials(p["name"]))}</span>'
            f'<span class="kicker">{esc(p["category"])}</span>'
            f'<span class="nm">{esc(p["name"])}</span></div>'
        )

    tech = "".join(f'<span class="tech">{esc(t)}</span>' for t in p["stack"][:4])

    demo_link = ""
    if demo:
        demo_link = (
            f'<a class="btn sm quiet" href="{esc(demo)}" target="_blank" rel="noopener">'
            f'Demo {ICON_EXT}</a>'
        )

    haystack = " ".join(
        [p["name"], p["repo"], p["tagline"], p["category"], " ".join(p["stack"]),
         re.sub(r"<[^>]+>", " ", " ".join(p["capabilities"]))]
    ).lower()

    return f"""    <li class="card" data-cat="{esc(p['category'])}" data-search="{esc(haystack)}">
      <div class="preview">{media}</div>
      <div class="card-body">
        <p class="cat">{esc(p['category'])}</p>
        <h2><a href="projects/{slug}.html">{esc(p['name'])}</a></h2>
        <p class="tag">{esc(p['tagline'])}</p>
      </div>
      <div class="stackline">{tech}</div>
      <div class="card-foot">
        <a class="btn sm" href="projects/{slug}.html">Details</a>
        {demo_link}
        <a class="btn sm quiet" href="{ORG_URL}/{esc(p['repo'])}" target="_blank" rel="noopener">
          {ICON_GITHUB} Code</a>
      </div>
    </li>"""


def build_index():
    cats = [c for c in CATEGORY_ORDER if any(p["category"] == c for p in PROJECTS)]
    chips = '<button class="chip" data-cat="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats
    )
    cards = "\n".join(card(p) for p in PROJECTS)
    embeds = sum(1 for p in PROJECTS if p.get("demo"))

    desc = ("Open source tools built by the Theodore Roosevelt Presidential Library and "
            "released for other museums and nonprofits to fork, rebrand, and run themselves.")

    body = f"""
<section class="hero">
  <div class="shell">
    <h1>Built here.<br>Yours to fork.</h1>
    <p class="lede">The Theodore Roosevelt Presidential Library builds a lot of its own software &mdash;
      ticketing widgets, embeddable timelines, a link checker, a 3D campus map, a night-sky
      explorer. <strong>All of it is public, all of it is MIT licensed, and most of it runs on
      nothing but GitHub Pages.</strong> A small museum with no engineering staff can fork any of
      these, swap one data file, and have it live on their own domain the same afternoon.</p>
    <div class="hero-stats">
      <div><b>{len(PROJECTS)}</b><span>Public projects</span></div>
      <div><b>{embeds}</b><span>Live demos</span></div>
      <div><b>MIT</b><span>Every repository</span></div>
      <div><b>$0</b><span>Hosting, in most cases</span></div>
    </div>
  </div>
</section>

<div class="toolbar">
  <div class="shell">
    <div class="search" id="searchWrap">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><line x1="16" y1="16" x2="21" y2="21"/></svg>
      <label for="q" class="skip">Search projects</label>
      <input id="q" type="search" placeholder="Search projects, capabilities, or tech&hellip;"
             autocomplete="off" spellcheck="false">
      <button class="clear" id="clearQ" aria-label="Clear search">&times;</button>
    </div>
    <div class="filters" role="group" aria-label="Filter by category">{chips}</div>
    <p class="count" id="count" aria-live="polite">{len(PROJECTS)} projects</p>
  </div>
</div>

<main id="main">
  <div class="shell" id="projects">
    <ul class="grid" id="grid">
{cards}
    </ul>
    <div class="empty" id="empty" hidden>
      <h2>Nothing matches that</h2>
      <p>Try a broader word &mdash; &ldquo;embed&rdquo;, &ldquo;dashboard&rdquo;, &ldquo;python&rdquo; &mdash;
         or clear the filters.</p>
    </div>
  </div>
</main>

<section class="band" id="about">
  <div class="shell">
    <h2>Why any of this is public</h2>
    <p class="lede">Museums and nonprofits keep solving the same problems separately and expensively.
      A timed-entry sell-out warning, a photo gallery that does not cost a monthly subscription,
      a way to get hours out of one CMS and onto another site &mdash; these are not competitive advantages.
      They are plumbing. Publishing the plumbing costs the Library nothing and saves somebody else a
      procurement cycle.</p>
    <div class="cols">
      <div>
        <h3>Built to be handed off</h3>
        <p>Nearly every project keeps its content in a plain JSON or Markdown file, separate from its
          code. Adapting one usually means rewriting data and swapping a logo, not learning a
          framework. Each project page here lists exactly which files to change.</p>
      </div>
      <div>
        <h3>Hosting is usually free</h3>
        <p>Most of these run entirely on GitHub Pages with a scheduled GitHub Action doing whatever
          work a server would normally do. No hosting bill, no database, no credentials sitting in a
          browser. Where an API key is needed, it lives in a repository secret.</p>
      </div>
      <div>
        <h3>Fork it, do not ask</h3>
        <p>MIT means you can use, change, and redistribute any of this commercially, without
          attribution and without asking. Open an issue on the repository if something is broken or
          unclear &mdash; that feedback makes the next fork easier for somebody else.</p>
      </div>
    </div>
  </div>
</section>
"""
    (ROOT / "index.html").write_text(
        head("TRPL Labs — Open source from the Theodore Roosevelt Presidential Library",
             desc, 0, SITE + "/")
        + body
        + footer(0).replace("</body>", '<script src="assets/js/labs.js"></script>\n</body>'),
        encoding="utf-8",
    )


# --------------------------------------------------------------- detail page

def build_project(p, prev, nxt):
    slug, repo, demo = p["slug"], p["repo"], p.get("demo")
    repo_url = f"{ORG_URL}/{repo}"
    shot = shot_path(slug)

    # Live demo panel -------------------------------------------------------
    demo_block = ""
    if demo and p.get("embeddable"):
        poster_media = (
            f'<img src="../{shot}" alt="Screenshot of {esc(p["name"])}" '
            f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top center">'
            if shot else ""
        )
        demo_block = f"""<div class="demo-frame" id="demoFrame">
  {poster_media}
  <div class="poster">
    <h3>Try it right here</h3>
    <p>This loads the live project from its own domain, exactly as a visitor would see it.</p>
    <button class="btn" id="loadDemo" data-src="{esc(demo)}">Launch live demo</button>
  </div>
</div>"""
    elif demo:
        demo_block = f"""<div class="demo-frame">
  <div class="poster">
    <h3>Open the live demo</h3>
    <p>{esc(p.get('demoNote', 'This one opens in its own tab.'))}</p>
    <a class="btn" href="{esc(demo)}" target="_blank" rel="noopener">Open demo {ICON_EXT}</a>
  </div>
</div>"""

    note = f'<p class="demo-note">{esc(p["demoNote"])}</p>' if p.get("demoNote") and p.get("embeddable") else ""

    paras = "\n".join(f"<p>{d}</p>" for d in p["description"])
    caps = "\n".join(f"<li>{c}</li>" for c in p["capabilities"])
    steps = "\n".join(f"<li>{s}</li>" for s in p["setup"])
    tech = "".join(f'<li><span class="tech">{esc(t)}</span></li>' for t in p["stack"])

    links = [(f'{ICON_GITHUB} View the repository', repo_url, "github.com")]
    if demo:
        links.append((f'{ICON_EXT} Open the live demo', demo, demo.split("//")[-1].split("/")[0]))
    if p.get("demoAlt"):
        links.append((f'{ICON_EXT} {esc(p["demoAlt"]["label"])}', p["demoAlt"]["url"],
                      p["demoAlt"]["url"].split("//")[-1].split("/")[0]))
    links.append(("Report an issue", f"{repo_url}/issues", "Issues"))
    links_html = "\n".join(
        f'<a href="{esc(u)}" target="_blank" rel="noopener">{lbl}<span>{esc(s)}</span></a>'
        for lbl, u, s in links
    )

    nav = []
    if prev:
        nav.append(f'<a href="{prev["slug"]}.html">&larr; Previous<b>{esc(prev["name"])}</b></a>')
    else:
        nav.append("<span></span>")
    if nxt:
        nav.append(f'<a href="{nxt["slug"]}.html" style="text-align:right">Next &rarr;<b>{esc(nxt["name"])}</b></a>')

    body = f"""
<div class="shell">
  <p class="crumbs"><a href="../index.html">TRPL Labs</a> &nbsp;/&nbsp; {esc(p['category'])}</p>
</div>

<header class="p-head">
  <div class="shell">
    <p class="cat">{esc(p['category'])}</p>
    <h1>{esc(p['name'])}</h1>
    <p class="tag">{esc(p['tagline'])}</p>
    <div class="p-actions">
      <a class="btn solid" href="{repo_url}" target="_blank" rel="noopener">{ICON_GITHUB} View on GitHub</a>
      {f'<a class="btn" href="{esc(demo)}" target="_blank" rel="noopener">Open live demo {ICON_EXT}</a>' if demo else ''}
      <a class="btn quiet" href="{repo_url}/fork" target="_blank" rel="noopener">Fork this repository</a>
    </div>
  </div>
</header>

<div class="shell">
  <div class="p-layout">
    <div class="prose" id="main">
      {demo_block}
      {note}

      <h2>What it does</h2>
      {paras}

      <h2>What it can do</h2>
      <ul>{caps}</ul>

      <h2>Make it your own</h2>
      <p>Start by forking the repository into your own organization. Everything below assumes
        you are working in your fork, not this one.</p>
      <div class="codeblock"><button data-copy>Copy</button><span class="cm"># clone your fork</span>
git clone https://github.com/YOUR-ORG/{esc(repo)}.git
cd {esc(repo)}</div>
      <ol class="steps">
{steps}
      </ol>
      <p>Stuck on a step? Open an issue on
        <a href="{repo_url}/issues" target="_blank" rel="noopener">the repository</a>.
        Questions from people adapting these for their own institution are the most useful
        feedback we get.</p>
    </div>

    <aside class="side">
      <section>
        <h3>Built with</h3>
        <ul>{tech}</ul>
      </section>
      <section>
        <h3>License</h3>
        <p class="meta">{esc(p['license'])} &mdash; free to use, change, and redistribute,
          commercially, without attribution.</p>
      </section>
      <section>
        <h3>Links</h3>
        <div class="links">{links_html}</div>
      </section>
    </aside>
  </div>

  <nav class="nextprev">{''.join(nav)}</nav>
  <p style="height:40px"></p>
</div>
"""
    desc = p["tagline"]
    out = (
        head(f"{p['name']} — TRPL Labs", desc, 1, f"{SITE}/projects/{slug}.html")
        + body
        + footer(1).replace("</body>", '<script src="../assets/js/labs.js"></script>\n</body>')
    )
    (ROOT / "projects" / f"{slug}.html").write_text(out, encoding="utf-8")


def build_favicon():
    """TR monogram on Night Sky, per the identity system's favicon rule."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#092A4D"/>
<text x="32" y="46" text-anchor="middle" fill="#FFFFFF"
      font-family="Impact,'Haettenschweiler','Arial Narrow',sans-serif"
      font-size="42" letter-spacing="1">TR</text>
</svg>
"""
    (ROOT / "assets" / "img" / "favicon.svg").write_text(svg, encoding="utf-8")


def build_sitemap():
    urls = [f"{SITE}/"] + [f"{SITE}/projects/{p['slug']}.html" for p in PROJECTS]
    body = "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8"
    )


def main():
    build_favicon()
    build_sitemap()
    build_index()
    for i, p in enumerate(PROJECTS):
        build_project(p, PROJECTS[i - 1] if i else None,
                      PROJECTS[i + 1] if i + 1 < len(PROJECTS) else None)
    shots = sum(1 for p in PROJECTS if shot_path(p["slug"]))
    print(f"Built index.html + {len(PROJECTS)} project pages ({shots} screenshots found).")


if __name__ == "__main__":
    main()
