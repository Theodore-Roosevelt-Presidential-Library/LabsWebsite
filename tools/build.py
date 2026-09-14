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
      <a href="{up}living-library.html">The Living Library</a>
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

<section class="featured">
  <div class="shell">
    <div class="feat-grid">
      <div>
        <p class="kicker">Published research &middot; Microsoft &amp; TRPL</p>
        <h2>The Living Library</h2>
        <p class="sub">Transforming Archival Collections into Conversational Knowledge Systems &mdash;
          Lessons from the Theodore Roosevelt Presidential Library</p>
        <p>Microsoft and the Library have published the blueprint behind Campfire, the Archivist App,
          and Talk to TR: a four-layer framework for turning a fragmented archive into a governed,
          searchable, conversational corpus &mdash; and a six-step process for doing it to a
          different collection. The conversational avatar is the optional last layer. The first
          three stand on their own.</p>
        <div class="p-actions">
          <a class="btn solid" href="living-library.html">Read the breakdown</a>
          <a class="btn" href="https://arxiv.org/abs/2609.09368" target="_blank" rel="noopener">
            Paper on arXiv {ICON_EXT}</a>
        </div>
      </div>
      <ul class="feat-stats">
        <li><b>4</b><span>Layers, the last one optional</span></li>
        <li><b>~300,000</b><span>Records in the governed corpus</span></li>
        <li><b>40+</b><span>Repositories reconciled</span></li>
        <li><b>2.80s</b><span>Mean time to first spoken word</span></li>
      </ul>
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


PAPER_URL = "https://arxiv.org/abs/2609.09368"
PAPER_PDF = "https://arxiv.org/pdf/2609.09368"
PAPER_HTML = "https://arxiv.org/html/2609.09368"
TRC_URL = "https://www.theodorerooseveltcenter.org/"
TRC_LIBRARY = "https://www.theodorerooseveltcenter.org/digital-library/"
TRC_STAFF = "https://www.theodorerooseveltcenter.org/about/staff/"


def build_living_library():
    """A plain-language read of arXiv:2609.09368, for institutions considering the same work.

    Every figure on this page comes from the paper. Nothing is estimated or rounded up.
    """
    desc = ("Microsoft and the Theodore Roosevelt Presidential Library published the four-layer "
            "framework behind Campfire, the Archivist App, and Talk to TR — and a six-step process "
            "for applying it to another institution's collection.")

    body = f"""
<div class="shell">
  <p class="crumbs"><a href="index.html">TRPL Labs</a> &nbsp;/&nbsp; Published research</p>
</div>

<header class="p-head">
  <div class="shell">
    <p class="cat">Published research &middot; arXiv:2609.09368 &middot; 8 September 2026</p>
    <h1>The Living Library</h1>
    <p class="tag">Transforming archival collections into conversational knowledge systems.
      The framework behind Campfire, the Archivist App, and Talk to TR &mdash; written down so
      another institution can do it too.</p>
    <div class="p-actions">
      <a class="btn solid" href="{PAPER_URL}" target="_blank" rel="noopener">Read on arXiv {ICON_EXT}</a>
      <a class="btn" href="{PAPER_PDF}" target="_blank" rel="noopener">PDF {ICON_EXT}</a>
      <a class="btn quiet" href="{PAPER_HTML}" target="_blank" rel="noopener">Full text in HTML {ICON_EXT}</a>
    </div>
  </div>
</header>

<div class="shell">
  <div class="p-layout">
    <div class="prose" id="main">

      <section class="partner">
        <p class="kicker">Start here</p>
        <h2>None of this exists without the Theodore Roosevelt Center</h2>
        <p>Before there was a corpus to search, a model to ground, or an avatar to talk to, there was
          the patient, unglamorous work of finding Roosevelt's record and cataloging it item by item.
          That work belongs to the
          <a href="{TRC_URL}" target="_blank" rel="noopener">Theodore Roosevelt Center at Dickinson
          State University</a>, and it has been going on since 2007.</p>
        <p>The Center sits on Dickinson State's historic hilltop campus, about an hour east of the
          Badlands, and its mission is to preserve and analyze the legacy of the twenty-sixth
          president. Its cornerstone is the
          <a href="{TRC_LIBRARY}" target="_blank" rel="noopener">Theodore Roosevelt Digital Library</a>
          &mdash; an effort to gather Roosevelt-related documents, photographs, and ephemera scattered
          across dozens of holding institutions and put them online in one organized, comprehensible
          place, free to anyone. Alongside it the Center runs an annual Theodore Roosevelt Symposium,
          educational programming built on primary sources, and a reference service that answers
          scholars and schoolchildren alike. Much of the cataloging has been done with student interns
          and volunteers working record by record.</p>
        <p>That is the thing worth being precise about, because it is easy to lose in a paper full of
          architecture diagrams: <strong>the hard part was done first, by people, over nearly two
          decades.</strong> A retrieval index is only as good as the collection beneath it, and the
          collection beneath this one was assembled by archivists and catalogers making thousands of
          individual judgment calls. The Living Library is what became possible on top of that. It is
          not a substitute for it, and it could not have been built without it.</p>
        <p>The partnership is ongoing and practical. Campfire was built together with the Center and
          Microsoft's AI for Good Lab, drawing on collections from eighteen institutions. The Library's
          own <a href="projects/trc-widget.html">TRC Search Widget</a> &mdash; open source, in the
          catalog on this site &mdash; exists purely to make the Center's digital library easier to
          search from anywhere. And the paper's authors single the Center out by name, thanking it and
          Dickinson State for &ldquo;preserving, curating, and providing access to the archival
          collections that served as the foundation for these experiences.&rdquo;</p>

        <h3 class="people-h">The people doing the work</h3>
        <ul class="people">
          <li><b>Michael Patrick Cullinane, PhD</b><span>Co-Director; Lowman Walton Chair of
            Theodore Roosevelt Studies</span></li>
          <li><b>Erik Johnson, MA, MLIS</b><span>Co-Director</span></li>
          <li><b>William J. Hansard, PhD</b><span>Public Historian</span></li>
          <li><b>Alexandra Hecht, MA, MLIS</b><span>Digital Collections Cataloger and Archivist</span></li>
          <li><b>Gemma Koontz, MS</b><span>Digital Collections Cataloger</span></li>
          <li><b>Rachel Lane, MA</b><span>Researcher</span></li>
          <li><b>Valerie Naylor, MS</b><span>National Parks Researcher</span></li>
        </ul>
        <p class="fine">Staff as listed by the Center. Roles change &mdash; the current roster is on
          <a href="{TRC_STAFF}" target="_blank" rel="noopener">their staff page</a>.</p>
      </section>

      <h2>The problem it starts from</h2>
      <p>Theodore Roosevelt's record does not live in one building. The Library's own holdings were
        assembled from more than forty repositories &mdash; correspondence, photographs, publications,
        and artifacts accumulated across libraries, historical societies, and private hands, reconciled
        only informally. That is not unusual. The paper is blunt that fragmentation is the default
        condition of an archive, not the exception.</p>
      <p>Digitization alone does not fix it. Item-level cataloging is manual and inconsistent across
        eras of practice, so backlogs grow alongside acquisition. And a scanned page behind a search
        box is still not the same thing as an accessible one: a visitor has to already know what to
        search for, in a vocabulary the archive happens to share, before the archive will answer.</p>
      <p>So the question the paper sets itself is narrow and testable: <em>how might institutions make
        vast, fragmented, and partially cataloged collections universally accessible, searchable, and
        interpretable &mdash; without sacrificing historical integrity?</em></p>

      <h2>The four layers</h2>
      <p>The answer is a stack. Each layer is useful on its own, and each one depends only on the layer
        beneath it. Read from the bottom up.</p>

      <ol class="layers">
        <li>
          <span class="n">1</span>
          <div>
            <h3>Digitization and corpus creation</h3>
            <p>Material is pulled from the Library's own systems into institution-controlled
              preservation storage, with source identifiers and rights status preserved. Downstream
              stages never depend on a fragile upstream path.</p>
          </div>
        </li>
        <li>
          <span class="n">2</span>
          <div>
            <h3>AI-powered processing</h3>
            <p>Page images go through OCR and structured metadata extraction. Original metadata stays
              immutable and separate from anything a model generated. Records are chunked, embedded,
              and published to a search index.</p>
          </div>
        </li>
        <li>
          <span class="n">3</span>
          <div>
            <h3>Retrieval and reasoning</h3>
            <p>A hybrid dense and semantic index over the governed corpus. Queries are interpreted,
              material is retrieved, and a model composes an answer that is attributable to real
              documents. <strong>This layer alone is Campfire.</strong></p>
          </div>
        </li>
        <li class="optional">
          <span class="n">4</span>
          <div>
            <h3>Embodied conversational interface <em>(optional)</em></h3>
            <p>Voice, avatar, and physical presence over the very same corpus. This is Talk to TR:
              a full-scale digital human on an LED wall inside a staged room, not a chatbot with a
              face attached.</p>
          </div>
        </li>
      </ol>

      <p>The paper is careful about that word <em>optional</em>, and it is the most useful thing in it
        for a museum weighing cost. Layers 1 through 3 already turn a fragmented collection into a
        unified, searchable, governed resource. An institution can stop there, get the whole research
        benefit, and add a conversational layer later against the same corpus &mdash; or never.</p>

      <h2>Three tools, one corpus</h2>
      <div class="cols3">
        <div>
          <h3>Campfire</h3>
          <p>The public, researcher-facing experience: a text conversation grounded in the Layer 3
            corpus, with no embodiment. It is Layers 1 to 3, exposed through a web interface.</p>
        </div>
        <div>
          <h3>The Archivist App</h3>
          <p>A curator-facing web application. Archivists open a record beside its source page image
            and correct the AI-generated transcription and metadata in place.</p>
        </div>
        <div>
          <h3>Talk to TR</h3>
          <p>The exhibit. A continuously operating physical-digital installation that answers visitors
            in the first person, in a curated room with its own lighting and spatial audio.</p>
        </div>
      </div>

      <h2>Review that does not become a bottleneck</h2>
      <p>This is the governance decision worth stealing. Most review workflows are admission gates:
        nothing reaches the index until a human has signed off, and with a 300,000-record backlog that
        means the collection stays dark for years.</p>
      <p>The Living Library inverts it. Processed records are published to the index <em>continuously</em>,
        carrying their review status and OCR confidence. Unreviewed material is not held back from
        retrieval. What the Archivist App adds is curatorial <em>control</em> over that index rather
        than a precondition for entering it &mdash; a curator can push a corrected record in or
        withdraw a problematic one at any time. Edits are non-destructive and versioned: the original
        model output is preserved, each correction is a new version with a side-by-side comparison and
        a full audit trail of who changed what and when. Hard metadata carried from the source system
        stays immutable, so human correction never overwrites the institutional system of record.</p>
      <p>The collection becomes searchable immediately; human review raises its quality over time
        instead of blocking it.</p>

      <h2>Cross-Era Analogical Grounding</h2>
      <p>Here is the paper's central technique, and the one most specific to historical work. A
        century-old archive cannot answer a question about social media or electric cars. Free
        generation would answer, but invites anachronism and fabrication. Refusing is accurate and
        deadening.</p>
      <p>Instead, a mid-tier model reframes the contemporary question as a retrieval for a
        <em>historically attested analog</em>. It picks an era-appropriate theme, selects a story from
        a resident catalog of 108 curated narratives, emits a retrieval query, and attaches a one-line
        rationale &mdash; a curator hint &mdash; explaining why that story is relevant. Real archive
        evidence comes back, and the speaking model answers the modern question <em>through</em> the
        analog, in period and in voice. Stories rotate, so no visitor hears the same one twice.</p>

      <figure class="worked">
        <figcaption>A worked example, reproduced from the paper</figcaption>
        <dl>
          <dt>Visitor asks</dt><dd>&ldquo;What do you think about social media?&rdquo;</dd>
          <dt>Theme chosen</dt><dd>Reaching the people directly, over the gatekeepers of the day</dd>
          <dt>Story selected</dt><dd><em>Words Sharper Than Swords</em> &mdash; how Roosevelt moved the
            public with his voice and pen</dd>
          <dt>Retrieval query</dt><dd>Roosevelt / the press / the &lsquo;bully pulpit&rsquo; /
            appealing directly to the people</dd>
          <dt>Evidence returned</dt><dd>Passages on Roosevelt's use of the presidency as a
            &ldquo;bully pulpit&rdquo; to reach citizens over the party bosses</dd>
        </dl>
        <p class="warn"><strong>What comes back is a generated response, not a historical quotation.</strong>
          The system composes a new sentence in Roosevelt's register, grounded in real retrieved
          passages, containing no reference postdating 1919. It is never presented as something
          Roosevelt said, and visitors are told the responses are AI-generated. The paper treats this
          gap &mdash; between a source-grounded analog and an utterance the man never spoke &mdash; as
          a real and unresolved concern, not a solved one.</p>
      </figure>

      <h2>What it takes to stay responsive</h2>
      <p>Grounding an avatar in an archive is only useful if it answers promptly. The measured figure,
        over one exhibition period, is the delay from a visitor releasing the push-to-talk button to
        the first synthesized word:</p>

      <table class="data">
        <caption>End-to-end first-token latency across 457 completed answers</caption>
        <tbody>
          <tr><th>Mean</th><td>2.80 s</td></tr>
          <tr><th>Median</th><td>2.55 s</td></tr>
          <tr><th>Maximum</th><td>7.14 s</td></tr>
          <tr><th>Under 5 seconds</th><td>97%</td></tr>
          <tr><th>Under 3 seconds</th><td>69%</td></tr>
        </tbody>
      </table>
      <p class="fine">Of 653 total push-to-talk releases, 457 ran to a completed answer; the rest were
        interruptions, repeat requests, or held-button timeouts.</p>

      <p>Three choices buy that. Speech recognition runs locally and incrementally while the visitor is
        still talking. Retrieval takes two paths at once &mdash; the speaking model decides for itself
        whether the current turn needs the knowledge base, while a second path prefetches evidence for
        the next turn in the background. And the entire chain streams: recognition into model into
        speech synthesis into avatar frames, each stage starting before the one before it finishes, so
        total latency approaches the slowest single stage rather than the sum of all of them.</p>
      <p>The finding underneath is worth noting for anyone sizing an index: the dominant cost is
        <em>whether</em> a turn retrieves synchronously at all, not how large the index is.</p>

      <h2>Safety that never stalls the exhibit</h2>
      <p>The kiosk is public and includes children, so it has to resist prompt injection and steer away
        from improper content. But it operates under one strict rule that inverts the usual design:
        <strong>a safety check must never make the avatar stall or fall silent.</strong> In a
        face-to-face museum setting, a guardrail that freezes the figure mid-sentence is a failure of
        the interaction, not a safeguard.</p>
      <p>So the stack is three layers, each heavier and later than the last, and none of them blocks the
        turn in flight. A fast regex screen runs on visitor input in roughly no time at all; on a hit it
        does not end the session but injects an in-character &ldquo;deflect and pivot&rdquo; instruction
        into the <em>next</em> turn. A small-model classifier runs asynchronously and fails open &mdash;
        if its verdict has not returned by the time the reply is ready, the reply plays and any hit is
        handled on the following turn. A mid-tier model reviews the avatar's own outgoing line in
        parallel with the stream, defaulting to observe rather than block.</p>
      <p>That design came from a real failure: an early substring-based threat filter matched
        &ldquo;kill&rdquo; inside the benign phrase &ldquo;killer view&rdquo; and terminated the session
        irrecoverably. The current version deflects in character and matches on word boundaries.</p>

      <h2>Running all day without a babysitter</h2>
      <p>The exhibit holds one long-lived session open throughout the day rather than rebuilding per
        visitor, so nobody pays a cold-start cost. Three mechanisms make that safe. A moving
        <strong>watermark</strong> means each visitor sees only history from after they arrived. A short
        bounded window of recent ambient content bleeds across, so someone arriving mid-story can refer
        to it. And a watchdog periodically discards raw transcript and transient state in place while
        preserving a running summary &mdash; without dismantling the session.</p>
      <p>Watchdogs cover every part likely to fail &mdash; avatar generation, the dialogue service, the
        network transport, the rendering stack &mdash; and escalate from the least disruptive recovery
        to the most: rebuild the avatar session first, restart the agent next, and only then restart the
        whole show. The exhibit engaged close to 5,000 visitors in its first two weeks of public
        operation in July 2026.</p>

      <h2>Five principles the authors think transfer</h2>
      <div class="cols2">
        <div><h3>Grounded in truth</h3><p>Every visitor-facing output must trace to a verified source.
          The persona is grounded non-parametrically in primary sources, not baked into model weights
          or a static biography.</p></div>
        <div><h3>Human in the loop</h3><p>Automation accelerates the pipeline; it does not replace
          curatorial judgment. Sign-off governs the corpus's quality over time, not what enters it.</p></div>
        <div><h3>Scalable by design</h3><p>Vendors and models are configuration, not foundation. The OCR
          stage is model-pluggable, services are independently restartable, and persona prompts are
          overridable at runtime without a redeployment.</p></div>
        <div><h3>Experience-first</h3><p>A grounded, fast answer is necessary but not sufficient.
          Immersion depended as much on avatar realism, lighting, audio, and staging as on the
          language model.</p></div>
        <div><h3>Ethically responsible</h3><p>Generating novel utterances for a real person risks
          attributing statements they never made. Historical attribution is treated as a first-class
          design constraint, and visitors are told the responses are AI-generated.</p></div>
      </div>

      <h2>The six-step process</h2>
      <p>This is the part written for other institutions. Steps 1 to 4 are the load-bearing,
        broadly transferable core &mdash; they need governance and engineering effort proportional to
        collection size, but no persona design and no real-time systems expertise.</p>
      <ol class="steps">
        <li><strong>Assess collection readiness.</strong> Inventory assets across your own fragmented
          repositories and identify digitization gaps. Policy and inventory work, not engineering &mdash;
          and its outcome determines the scope of everything after it.</li>
        <li><strong>Build the corpus.</strong> Digitize and aggregate into institution-controlled
          storage. Establish governance &mdash; source identifiers, rights status, and a schema that
          separates immutable hard metadata from later enrichment &mdash; <em>before</em> any AI
          processing begins.</li>
        <li><strong>Apply AI processing.</strong> Run OCR and metadata enrichment as a model-pluggable
          stage. Validate the model choice against a source-grounded evaluation on a stratified sample
          rather than by inspection, and plan for expert review.</li>
        <li><strong>Implement the retrieval system.</strong> Index for hybrid dense and semantic search
          and expose it through a governed contract. <strong>This step alone gives you a
          researcher-facing tool</strong>, whether or not a conversational layer ever follows.</li>
        <li><strong>Add a conversational layer.</strong> Integrate a model against the Layer 3 retrieval
          contract and define the interaction patterns: persona grounding, analogical reframing for
          out-of-scope questions, and a non-blocking safety stack.</li>
        <li><strong>Add an avatar experience &mdash; optional.</strong> Only where an institution wants
          embodied, real-time presence. Voice and visual rendering under the same real-time budget and
          autonomous-operation discipline as Talk to TR.</li>
      </ol>

      <h2>What the paper does not claim</h2>
      <p>The authors are unusually direct about this, and it is worth repeating rather than glossing.
        This is a deployment experience report, not a controlled evaluation. The evidence is largely
        observational &mdash; basic usage logging plus qualitative observation over two weeks of public
        operation.</p>
      <ul>
        <li>Three qualities central to this class of system remain <strong>open</strong>: whether
          grounding keeps synthesis faithful, how often the figure lapses into anachronism, and how
          strong the visitor's sense of presence actually is. The first two would need systematic
          annotation of responses against their sources; the last needs a dedicated visitor study.</li>
        <li>OCR errors are reduced by expert review but not eliminated, and residual errors can
          propagate into retrieval.</li>
        <li>A corpus centered on one figure's correspondence over-represents that figure's perspective.
          Curatorial review can mitigate that bias but not remove it.</li>
        <li>The boundary between inference and fabrication is inherently imperfect. Even a
          source-grounded analog remains a novel utterance the historical figure never spoke.</li>
        <li>The study covers a single figure and a single archive.</li>
      </ul>
      <p>For a presidential library, that candor is the point. A framework that overclaimed would be
        the wrong thing to hand another institution.</p>

      <h2>Privacy, as deployed</h2>
      <p>Talk to TR is built for anonymous, walk-up use. The vision subsystem estimates presence and
        interaction state but performs no identity or facial recognition &mdash; camera frames, images,
        face embeddings, and biometric templates are not retained, and the only identifier it emits is
        transient and non-biometric with roughly a 30-second lifetime. Microphone audio is processed as
        a transient stream and never retained as a recording. Spoken participation is opt-in through the
        push-to-talk control, on-site notice tells visitors they are interacting with an AI-generated
        persona, and operational logs are kept for up to 30 days and then deleted. The system does not
        maintain visitor-linked memory across separate visits.</p>

      <h2>Cite it</h2>
      <div class="codeblock"><button data-copy>Copy</button>Pengce Wang, Lucia Ronchi Darre, Matt Briney, Michaell Bakalars,
Dan Rutkowski, Ursula Hardy, David Wolf, Laura Hoffman, Allen Kim,
Shawn Wright, and Juan Lavista Ferres.
"The Living Library: Transforming Archival Collections into
Conversational Knowledge Systems -- Lessons from the Theodore
Roosevelt Presidential Library." arXiv:2609.09368, September 2026.</div>

      <p>Everything above is drawn from the paper. The full text adds the architecture diagrams, the
        OCR model evaluation, and the complete references &mdash;
        <a href="{PAPER_URL}" target="_blank" rel="noopener">read it on arXiv</a>.</p>
    </div>

    <aside class="side">
      <section>
        <h3>Authors</h3>
        <p class="meta">Pengce Wang, Lucia Ronchi Darre, <strong>Matt Briney</strong>, Michaell
          Bakalars, Dan Rutkowski, Ursula Hardy, David Wolf, Laura Hoffman, Allen Kim, Shawn Wright,
          and Juan Lavista Ferres.</p>
        <p class="meta">Microsoft, and the Theodore Roosevelt Presidential Library.</p>
      </section>
      <section>
        <h3>Built on</h3>
        <ul>
          <li><span class="tech">Azure Storage</span></li>
          <li><span class="tech">Azure AI Foundry</span></li>
          <li><span class="tech">Azure Cosmos DB</span></li>
          <li><span class="tech">Azure AI Search</span></li>
          <li><span class="tech">Azure Custom Voice</span></li>
          <li><span class="tech">Whisper large-v3</span></li>
          <li><span class="tech">LiveKit</span></li>
          <li><span class="tech">Unreal Engine</span></li>
        </ul>
      </section>
      <section>
        <h3>Read it</h3>
        <div class="links">
          <a href="{PAPER_URL}" target="_blank" rel="noopener">{ICON_EXT} Abstract<span>arXiv</span></a>
          <a href="{PAPER_HTML}" target="_blank" rel="noopener">{ICON_EXT} Full text<span>HTML</span></a>
          <a href="{PAPER_PDF}" target="_blank" rel="noopener">{ICON_EXT} Download<span>PDF</span></a>
          <a href="https://campfire.trlibrary.com" target="_blank" rel="noopener">{ICON_EXT} Try Campfire<span>Layer 3, live</span></a>
        </div>
      </section>
      <section>
        <h3>The collection</h3>
        <p class="meta">The archive underneath all of this is the work of the Theodore Roosevelt
          Center at Dickinson State University, cataloging Roosevelt's record since 2007.</p>
        <div class="links">
          <a href="{TRC_URL}" target="_blank" rel="noopener">{ICON_EXT} The TR Center<span>Dickinson State</span></a>
          <a href="{TRC_LIBRARY}" target="_blank" rel="noopener">{ICON_EXT} Digital Library<span>Search it</span></a>
        </div>
      </section>
      <section>
        <h3>See also</h3>
        <p class="meta">The projects in <a href="index.html">this catalog</a> are the Library's
          smaller, forkable tools. The Living Library is the architecture underneath the big ones.</p>
      </section>
    </aside>
  </div>
  <p style="height:40px"></p>
</div>
"""
    out = (
        head("The Living Library — TRPL Labs", desc, 0, f"{SITE}/living-library.html")
        + body
        + footer(0).replace("</body>", '<script src="assets/js/labs.js"></script>\n</body>')
    )
    (ROOT / "living-library.html").write_text(out, encoding="utf-8")


def build_sitemap():
    urls = ([f"{SITE}/", f"{SITE}/living-library.html"]
            + [f"{SITE}/projects/{p['slug']}.html" for p in PROJECTS])
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
    build_living_library()
    build_index()
    for i, p in enumerate(PROJECTS):
        build_project(p, PROJECTS[i - 1] if i else None,
                      PROJECTS[i + 1] if i + 1 < len(PROJECTS) else None)
    shots = sum(1 for p in PROJECTS if shot_path(p["slug"]))
    print(f"Built index.html + {len(PROJECTS)} project pages ({shots} screenshots found).")


if __name__ == "__main__":
    main()
