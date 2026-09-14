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
      <a href="{up}about.html">About</a>
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
      <p style="margin:0"><a href="mailto:hello@trlibrary.com">hello@trlibrary.com</a></p>
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
        <p class="kicker">The Library's AI work, published in full</p>
        <h2>The Living Library</h2>
        <p class="sub">Transforming Archival Collections into Conversational Knowledge Systems &mdash;
          Lessons from the Theodore Roosevelt Presidential Library</p>
        <p>Every museum and library is being asked what it is doing about AI. This is the Library's
          answer, written down with <strong>Microsoft's AI for Good Lab</strong> and published for
          anyone to copy: how roughly 300,000 archival records became something a visitor can
          question in plain language, powering Campfire, the Archivist App, and the Talk to TR
          exhibit.</p>
        <p>It is four layers, and <strong>the AI avatar is only the last one &mdash; and it is
          optional.</strong> The first three are the part most institutions actually need. It also
          states plainly what the authors could not resolve, which is rarer than it should be.</p>
        <div class="p-actions">
          <a class="btn solid" href="living-library.html">Read the breakdown</a>
          <a class="btn" href="https://arxiv.org/abs/2609.09368" target="_blank" rel="noopener">
            Paper on arXiv {ICON_EXT}</a>
        </div>
      </div>
      <ul class="feat-stats">
        <li><b>4</b><span>Layers &mdash; only the last is an avatar</span></li>
        <li><b>~300,000</b><span>Archival records, made askable</span></li>
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
          framework. Each project page lists exactly which files to change.</p>
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
          attribution and without asking. Open an issue if something is broken or unclear &mdash;
          that feedback makes the next fork easier for somebody else.</p>
      </div>
    </div>
    <p class="lede" style="margin-top:30px">Worth saying plainly: these are not products. There is no
      support contract and no roadmap, they were built for one institution's circumstances, and a few
      are prototypes that say so on their own page. Licensed fonts and collection photography are not
      the Library's to redistribute, so every project falls back to open substitutes.</p>
    <p style="margin-top:24px"><a class="btn" href="about.html">About the Library</a></p>
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
MS_SIGNAL = "https://news.microsoft.com/signal/articles/ai-theodore-roosevelt-presidential-library/"
MS_AIFG = "https://www.microsoft.com/en-us/research/group/ai-for-good-research-lab/"
MS_AIFG_OSS = "https://microsoft.github.io/aiforgoodlab/"
GEEKWIRE = ("https://www.geekwire.com/2026/archives-to-avatars-microsoft-ai-powers-"
            "the-interactive-president-at-new-theodore-roosevelt-library/")
UKUVULA = "https://github.com/microsoft/ukuvula"
TRC_URL = "https://www.theodorerooseveltcenter.org/"
TRC_LIBRARY = "https://www.theodorerooseveltcenter.org/digital-library/"
TRC_STAFF = "https://www.theodorerooseveltcenter.org/about/staff/"


def trc_collection_chart(top=12):
    """Render the TRC digital library's holdings as a ranked bar chart.

    Bars are linear against the largest collection, deliberately. The Library of
    Congress Manuscript Division really is ~86% of the whole thing, and a log
    scale would flatter the smaller collections by hiding that.
    """
    src = json.loads((ROOT / "data" / "trc-collections.json").read_text(encoding="utf-8"))
    # One listed collection currently holds zero records; excluding it keeps the
    # caption's arithmetic honest against the "and N more" line below.
    items = [i for i in src["items"] if i["count"] > 0]
    total, n = src["records"], len(items)
    head, tail = items[:top], items[top:]
    biggest = head[0]["count"]

    rows = []
    for i in head:
        pct = i["count"] / total * 100
        width = max(i["count"] / biggest * 100, 0.45)   # keep a sliver visible
        mine = " own" if "Presidential Library" in i["name"] else ""
        rows.append(
            f'<li class="bar{mine}">'
            f'<span class="bl">{esc(i["name"])}</span>'
            f'<span class="bt"><span class="bf" style="width:{width:.3f}%"></span></span>'
            f'<span class="bv">{i["count"]:,}<em>{pct:.1f}%</em></span></li>'
        )

    rest = sum(i["count"] for i in tail)
    date = src["harvested"][:10]
    dt = f"{date[8:10]} {['January','February','March','April','May','June','July','August','September','October','November','December'][int(date[5:7]) - 1]} {date[:4]}".lstrip("0")

    chart = (
        '<figure class="chart">\n'
        f'  <figcaption>{total:,} records across {n} collections &mdash; '
        'the top twelve holders</figcaption>\n'
        f'  <ul>\n    ' + "\n    ".join(rows) + "\n  </ul>\n"
        f'  <p class="rest">&hellip;and {len(tail)} more collections, {rest:,} records between them '
        '&mdash; state historical societies, national parks and monuments, university libraries, '
        'and private collections given or loaned for digitization.</p>\n'
        "</figure>"
    )
    return chart, dt


def build_living_library():
    """A plain-language read of arXiv:2609.09368, for institutions weighing the same work.

    Three parts: what it is, how it works, how you would do it. Every figure
    comes from the paper. Nothing is estimated or rounded up.
    """
    CHART, CHART_DATE = trc_collection_chart()

    # The Campfire screenshot is captured in CI like every other shot. If it has
    # not run yet, the figure is omitted rather than rendering a broken image.
    CAMPFIRE = ""
    if (ROOT / "assets" / "shots" / "campfire.png").exists():
        CAMPFIRE = (
            '<figure class="shot">\n'
            '        <a href="https://campfire.trlibrary.com" target="_blank" rel="noopener">'
            '<img src="assets/shots/campfire.png" loading="lazy" width="1280" height="800" '
            'alt="The Campfire research interface, answering a question with citations to '
            'archival documents"></a>\n'
            '        <figcaption><strong>Campfire</strong> is layers one to three with nothing '
            'bolted on top &mdash; a text interface, free, open to anyone. '
            f'<a href="https://campfire.trlibrary.com" target="_blank" rel="noopener">Try it '
            f'yourself {ICON_EXT}</a></figcaption>\n'
            "      </figure>"
        )

    desc = ("Microsoft's AI for Good Lab and the Theodore Roosevelt Presidential Library published "
            "the framework behind Campfire, the Archivist App, and Talk to TR - and a six-step "
            "process for applying it to another institution's collection.")

    body = f"""
<div class="shell">
  <p class="crumbs"><a href="index.html">TRPL Labs</a> &nbsp;/&nbsp; Published research</p>
</div>

<header class="p-head">
  <div class="shell">
    <p class="cat">Published research &middot; arXiv:2609.09368 &middot; 8 September 2026</p>
    <h1>The Living Library</h1>
    <p class="tag">What one institution learned putting AI in front of its archive &mdash; and in
      front of the public. The framework behind Campfire, the Archivist App, and Talk to TR,
      written down so another institution can do it too.</p>
    <div class="p-actions">
      <a class="btn solid" href="{PAPER_URL}" target="_blank" rel="noopener">Read on arXiv {ICON_EXT}</a>
      <a class="btn" href="{PAPER_PDF}" target="_blank" rel="noopener">PDF {ICON_EXT}</a>
      <a class="btn quiet" href="{PAPER_HTML}" target="_blank" rel="noopener">Full text in HTML {ICON_EXT}</a>
    </div>
  </div>
</header>

<div class="shell">
  <section class="exec">
    <p class="kicker">If your board is asking what you are doing about AI</p>
    <p class="lede">Nearly every museum, library, and historical society is being asked that question
      right now &mdash; by trustees, by funders, and by vendors with a polished demo. Very little of
      the available guidance comes from anyone who has actually put one of these in front of the
      public and then measured what happened. <strong>This is a record of one institution that did,
      including the parts it could not resolve.</strong></p>
    <dl>
      <div>
        <dt>What it actually does</dt>
        <dd>It lets someone ask your collection a question in plain language and get real documents
          back &mdash; instead of requiring them to already know the right search term.</dd>
      </div>
      <div>
        <dt>Why that matters to you</dt>
        <dd>Most collections are functionally invisible. They are catalogued for people who already
          know what they are looking for, which is a small and shrinking audience.</dd>
      </div>
      <div>
        <dt>The one decision that matters</dt>
        <dd>It is four layers, and <strong>you can stop after three.</strong> Three gives you a
          searchable collection and a public research tool. Four is the talking avatar &mdash; a
          different kind of project, and optional.</dd>
      </div>
      <div>
        <dt>What it will cost you</dt>
        <dd>The paper gives no dollar figures and it would be irresponsible to invent them. It does
          say the first four steps need governance and engineering proportional to your collection,
          but <em>no</em> specialist AI staff. The honest caveat: Microsoft donated much of this
          work. Budget accordingly.</dd>
      </div>
      <div>
        <dt>The risk to take seriously</dt>
        <dd>Not the technology. Putting words in a real person's mouth. Everything expensive in the
          design exists to manage that one problem, and the authors still list it as unresolved.</dd>
      </div>
      <div>
        <dt>Your first step is not technical</dt>
        <dd>It is an inventory: what you hold, where it actually lives, what is not digitized. That
          is policy and staff work, it needs no vendor, and it scopes everything after it.</dd>
      </div>
    </dl>
    <p class="onward">What this is not: a benchmark, a product pitch, or a claim that this is right
      for every collection. It is one deployment, described honestly, by people still arguing with
      parts of it.</p>
  </section>
</div>

<div class="shell">
  <div class="p-layout">
    <div class="prose" id="main">

      <p class="part"><span>Part one</span> What it is</p>

      <section class="credit">
        <h2>The collection is not the Library's</h2>
        <p>Worth establishing before anything else, because the framework gets the attention and the
          collection is the part that took twenty years. Roosevelt's record is held by dozens of
          separate institutions &mdash; the Library of Congress, Harvard, national parks, state
          historical societies, private collectors. Very little of it belongs to any one place.</p>
        <p>Gathering it, cataloguing it item by item, and putting it online is the work of the
          <a href="{TRC_URL}" target="_blank" rel="noopener">Theodore Roosevelt Center at Dickinson
          State University</a>, going on since 2007, much of it done by archivists, student interns,
          and volunteers working one record at a time. A retrieval index is only as good as the
          collection beneath it, and this one was built by people, by hand, first.
          <a href="#collection">The breakdown of who actually holds what is further down.</a></p>
      </section>

      <h2>What it looks like in use</h2>
      <p>Before the architecture, the thing itself. Here the historian Doris Kearns Goodwin puts
        questions to the Talk to TR avatar in the Library's exhibit space, alongside Microsoft vice
        chair and president Brad Smith.</p>
      <figure class="media">
        <div class="ratio">
          <iframe src="https://www.youtube-nocookie.com/embed/MJu_-hiK_qk" loading="lazy"
            title="Doris Kearns Goodwin in conversation with the Talk to TR avatar"
            allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
        </div>
        <figcaption>Video: Microsoft. The exhibit is a full-scale digital human on an LED wall in a
          staged room &mdash; not a screen the visitor holds.</figcaption>
      </figure>

      <h2>The problem it starts from</h2>
      <p>Roosevelt's record does not live in one building, and digitization alone does not fix that.
        Item-level cataloguing is manual and inconsistent across eras of practice, so backlogs grow
        alongside acquisition. And a scanned page behind a search box is still not an accessible one:
        a visitor has to already know what to search for, in a vocabulary the archive happens to
        share, before the archive will answer.</p>
      <p>So the paper sets itself a narrow, testable question: <em>how might institutions make vast,
        fragmented, and partially catalogued collections universally accessible, searchable, and
        interpretable &mdash; without sacrificing historical integrity?</em></p>

      <h2>Four layers, three tools, one corpus</h2>
      <p>The answer is a stack. Each layer is useful on its own and depends only on the one beneath
        it. Read from the bottom up.</p>

      <ol class="layers">
        <li>
          <span class="n">1</span>
          <div>
            <h3>Digitization and corpus creation</h3>
            <p>Material moves into institution-controlled preservation storage with source
              identifiers and rights status preserved, so later stages never depend on a fragile
              upstream path.</p>
          </div>
        </li>
        <li>
          <span class="n">2</span>
          <div>
            <h3>AI-powered processing</h3>
            <p>OCR and metadata extraction. Original metadata stays immutable and separate from
              anything a model generated. <strong>This layer produces the Archivist App</strong>,
              where curators correct what the model got wrong.</p>
          </div>
        </li>
        <li>
          <span class="n">3</span>
          <div>
            <h3>Retrieval and reasoning</h3>
            <p>A hybrid index over the governed corpus. Questions are interpreted, real material is
              retrieved, and a model composes an answer attributable to actual documents.
              <strong>This layer alone is Campfire.</strong></p>
          </div>
        </li>
        <li class="optional">
          <span class="n">4</span>
          <div>
            <h3>Embodied conversational interface <em>(optional)</em></h3>
            <p>Voice, avatar, and physical presence over the very same corpus. <strong>This layer is
              Talk to TR</strong> &mdash; and the paper is deliberate about calling it optional.</p>
          </div>
        </li>
      </ol>

      <p>That last word is the most useful thing on this page for anyone weighing cost. Layers one
        through three already turn a fragmented collection into a unified, governed, searchable
        resource. An institution can stop there, take the entire research benefit, and decide about a
        conversational layer later &mdash; or never.</p>

      {CAMPFIRE}

      <h2>Review that does not become a bottleneck</h2>
      <p>This is the governance decision most worth stealing. Most review workflows are admission
        gates: nothing reaches the index until a human signs off, which with a 300,000-record backlog
        means the collection stays dark for years.</p>
      <p>The Living Library inverts it. Processed records publish to the index <em>continuously</em>,
        carrying their review status and OCR confidence. What the Archivist App adds is curatorial
        <em>control</em> over that index rather than a precondition for entering it &mdash; a curator
        can push a corrected record in or withdraw a problematic one at any time. Edits are
        non-destructive and versioned, the original model output is preserved, and hard metadata from
        the source system stays immutable, so human correction never overwrites the institutional
        record. The collection becomes searchable immediately; review raises its quality over time
        instead of blocking it.</p>

      <p class="part"><span>Part two</span> How it works</p>
      <p class="part-note">The engineering half. If you came for the decision rather than the
        machinery, skip to <a href="#doing">part three</a> &mdash; nothing below changes the answer,
        it only explains what the answer costs.</p>

      <h2>Answering questions the archive never anticipated</h2>
      <p class="gloss">In plain terms: when a visitor asks about something that did not exist in your
        subject's lifetime, the system finds the closest thing that <em>did</em>, and answers through
        that instead of guessing.</p>
      <p>A century-old archive cannot answer a question about social media. Unconstrained generation
        would answer, but invites anachronism and fabrication. Refusing is accurate and deadening.
        The paper's central technique, <em>Cross-Era Analogical Grounding</em>, takes a third path:
        it reframes the contemporary question as a retrieval for a <strong>historically attested
        analog</strong>.</p>
      <p>A mid-tier model picks an era-appropriate theme, selects a story from a resident catalog of
        108 curated narratives, emits a retrieval query, and attaches a one-line rationale &mdash; a
        curator hint &mdash; explaining why that story fits. Real archive evidence comes back, and
        the speaking model answers the modern question <em>through</em> the analog, in period and in
        voice. Stories rotate, so no visitor hears the same one twice.</p>

      <figure class="worked">
        <figcaption>A worked example, reproduced from the paper</figcaption>
        <dl>
          <div><dt>Visitor asks</dt><dd>&ldquo;What do you think about social media?&rdquo;</dd></div>
          <div><dt>Theme chosen</dt><dd>Reaching the people directly, over the gatekeepers of the day</dd></div>
          <div><dt>Story selected</dt><dd><em>Words Sharper Than Swords</em> &mdash; how Roosevelt
            moved the public with his voice and pen</dd></div>
          <div><dt>Retrieval query</dt><dd>Roosevelt / the press / the &lsquo;bully pulpit&rsquo; /
            appealing directly to the people</dd></div>
          <div><dt>Evidence returned</dt><dd>Passages on Roosevelt's use of the presidency as a
            &ldquo;bully pulpit&rdquo; to reach citizens over the party bosses</dd></div>
        </dl>
        <p class="warn"><strong>What comes back is a generated response, not a historical
          quotation.</strong> The system composes a new sentence in Roosevelt's register, grounded in
          real retrieved passages, containing no reference postdating 1919. It is never presented as
          something Roosevelt said, and visitors are told the responses are AI-generated. The paper
          treats that gap &mdash; between a source-grounded analog and an utterance the man never
          spoke &mdash; as a real and unresolved concern.</p>
      </figure>

      <h2>Staying fast enough to feel like conversation</h2>
      <p class="gloss">In plain terms: a visitor will forgive a slightly worse answer, but not a long
        silence.</p>
      <p>The measured figure is the delay from a visitor releasing the push-to-talk button to the
        first synthesized word, across one exhibition period:</p>

      <table class="data">
        <caption>End-to-end first-token latency, 457 completed answers</caption>
        <tbody>
          <tr><th>Mean</th><td>2.80 s</td></tr>
          <tr><th>Median</th><td>2.55 s</td></tr>
          <tr><th>Maximum</th><td>7.14 s</td></tr>
          <tr><th>Under 5 seconds</th><td>97%</td></tr>
          <tr><th>Under 3 seconds</th><td>69%</td></tr>
        </tbody>
      </table>
      <p class="fine">Of 653 total push-to-talk releases, 457 ran to a completed answer; the rest
        were interruptions, repeat requests, or held-button timeouts.</p>

      <p>Three choices buy that. Speech recognition runs locally and incrementally while the visitor
        is still talking. Retrieval takes two paths at once &mdash; the speaking model decides for
        itself whether the current turn needs the knowledge base, while a second path prefetches
        evidence for the next turn. And the whole chain streams: recognition into model into speech
        synthesis into avatar frames, each stage starting before the previous finishes, so total
        latency approaches the slowest single stage rather than the sum of all of them.</p>
      <p>The finding underneath is worth noting for anyone sizing an index: the dominant cost is
        <em>whether</em> a turn retrieves synchronously at all, not how large the index is.</p>

      <h2>Safety that never stalls the exhibit</h2>
      <p class="gloss">In plain terms: children will try to make the exhibit say something awful, and
        an avatar that freezes mid-sentence in front of a crowd is its own kind of failure.</p>
      <p>The kiosk is public and includes children, so it has to resist prompt injection and steer
        away from improper content &mdash; under one strict rule that inverts the usual design:
        <strong>a safety check must never make the avatar stall or fall silent.</strong></p>
      <p>So the stack is three layers, each heavier and later than the last, none blocking the turn
        in flight. A fast pattern screen runs on visitor input almost instantly; on a hit it does not
        end the session but injects an in-character deflection into the <em>next</em> turn. A
        small-model classifier runs asynchronously and fails open. A mid-tier model reviews the
        avatar's own outgoing line in parallel with the stream, defaulting to observe rather than
        block.</p>
      <p>That design came from a real failure: an early substring filter matched &ldquo;kill&rdquo;
        inside the benign phrase &ldquo;killer view&rdquo; and terminated the session irrecoverably.
        The current version deflects in character and matches on word boundaries.</p>

      <h2>Running all day without a babysitter</h2>
      <p class="gloss">In plain terms: it has to open at nine and still work at five without staff
        restarting it, and no visitor should see the previous visitor's conversation.</p>
      <p>The exhibit holds one long-lived session open all day rather than rebuilding per visitor, so
        nobody pays a cold-start cost. A moving <strong>watermark</strong> means each visitor sees
        only history from after they arrived; a short bounded window of recent ambient content bleeds
        across so someone arriving mid-story can refer to it; and a watchdog periodically discards raw
        transcript and transient state while preserving a running summary.</p>
      <p>Watchdogs cover every part likely to fail &mdash; avatar generation, dialogue, transport,
        rendering &mdash; and escalate from the least disruptive recovery to the most: rebuild the
        avatar session, restart the agent, and only then restart the whole show. The exhibit engaged
        close to 5,000 visitors in its first two weeks of public operation in July 2026.</p>

      <p class="part" id="doing"><span>Part three</span> Doing it yourself</p>

      <h2>The six-step process</h2>
      <p>Steps one to four are the load-bearing, broadly transferable core. They need governance and
        engineering effort proportional to collection size, but no persona design and no real-time
        systems expertise.</p>
      <ol class="steps">
        <li><strong>Assess collection readiness.</strong> Inventory assets across your own fragmented
          repositories and identify digitization gaps. Policy and inventory work, not engineering
          &mdash; and its outcome scopes everything after it.</li>
        <li><strong>Build the corpus.</strong> Digitize and aggregate into institution-controlled
          storage. Establish governance &mdash; source identifiers, rights status, and a schema
          separating immutable metadata from later enrichment &mdash; <em>before</em> any AI
          processing begins.</li>
        <li><strong>Apply AI processing.</strong> Run OCR and metadata enrichment as a
          model-pluggable stage. Validate the model choice against a source-grounded evaluation on a
          stratified sample rather than by inspection, and plan for expert review.</li>
        <li><strong>Implement retrieval.</strong> Index for hybrid search and expose it through a
          governed contract. <strong>This step alone gives you a researcher-facing tool</strong>,
          whether or not a conversational layer ever follows.</li>
        <li><strong>Add a conversational layer.</strong> Integrate a model against that retrieval
          contract and define the interaction patterns: persona grounding, analogical reframing, and
          a non-blocking safety stack.</li>
        <li><strong>Add an avatar &mdash; optional.</strong> Only where an institution wants embodied,
          real-time presence, under the same latency and autonomous-operation discipline.</li>
      </ol>

      <h2>Five principles the authors think transfer</h2>
      <div class="cols2">
        <div><h3>Grounded in truth</h3><p>Every visitor-facing output traces to a verified source.
          The persona is grounded in primary sources, not baked into model weights.</p></div>
        <div><h3>Human in the loop</h3><p>Automation accelerates the pipeline; it does not replace
          curatorial judgment. Sign-off governs quality over time, not entry.</p></div>
        <div><h3>Scalable by design</h3><p>Vendors and models are configuration, not foundation. The
          OCR stage is pluggable and persona prompts are overridable without redeployment.</p></div>
        <div><h3>Experience-first</h3><p>A grounded, fast answer is necessary but not sufficient.
          Immersion depended as much on lighting, audio, and staging as on the model.</p></div>
        <div><h3>Ethically responsible</h3><p>Generating novel utterances for a real person risks
          attributing statements they never made. Attribution is a first-class design constraint.</p></div>
      </div>

      <h2>What the paper does not claim</h2>
      <p>The authors are unusually direct about this, and it is worth repeating rather than glossing.
        This is a deployment experience report, not a controlled evaluation, and the evidence is
        largely observational over two weeks of public operation.</p>
      <ul>
        <li>Three qualities central to this class of system remain <strong>open</strong>: whether
          grounding keeps synthesis faithful, how often the figure lapses into anachronism, and how
          strong the visitor's sense of presence actually is.</li>
        <li>OCR errors are reduced by expert review but not eliminated, and residual errors can
          propagate into retrieval.</li>
        <li>A corpus centred on one figure's correspondence over-represents that figure's
          perspective. Curatorial review can mitigate that bias but not remove it.</li>
        <li>The boundary between inference and fabrication is inherently imperfect. Even a
          source-grounded analog remains a novel utterance the historical figure never spoke.</li>
        <li>The study covers a single figure and a single archive.</li>
      </ul>
      <p>For a presidential library, that candour is the point. A framework that overclaimed would be
        the wrong thing to hand another institution.</p>

      <h2>Privacy, as deployed</h2>
      <p>Talk to TR is built for anonymous, walk-up use. The vision subsystem estimates presence but
        performs no identity or facial recognition &mdash; camera frames, images, face embeddings and
        biometric templates are not retained, and the only identifier it emits is transient and
        non-biometric with roughly a 30-second lifetime. Microphone audio is processed as a transient
        stream, never retained as a recording. Spoken participation is opt-in through the
        push-to-talk control, on-site notice tells visitors they are interacting with an AI-generated
        persona, and operational logs are kept for up to 30 days. No visitor-linked memory persists
        across visits.</p>

      <section id="collection">
        <h2>The collection, in detail</h2>
        <p>Back to where this started. Here is the Theodore Roosevelt Center's digital library broken
          out by the institution that actually holds the material &mdash; the clearest available
          picture of how distributed a presidential record really is.</p>
{CHART}
        <p class="fine"><strong>Read this chart for one thing only: who holds what.</strong> It is a
          snapshot of the Center's collection facet, harvested {CHART_DATE} by the Library's own
          <a href="projects/trc-widget.html">TRC Search Widget</a>, and counts move as cataloguing
          continues. It is <em>not</em> a measure of any institution's holdings &mdash; each figure
          counts only what that institution has catalogued into this particular index. The Library's
          own Roosevelt material is substantially larger than its line here suggests and is mostly
          catalogued elsewhere, and the roughly 300,000-record corpus the paper describes is broader
          still than this digital library.</p>

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

      <h2>Where this sits in the Lab's work</h2>
      <p>The paper is a Microsoft AI for Good Lab publication &mdash; ten of its eleven authors are
        Microsoft, among them the Lab's senior director, Laura Hoffman, and its director and
        co-founder, Juan Lavista Ferres. When the Library opened in July 2026,
        <a href="{MS_SIGNAL}" target="_blank" rel="noopener">Microsoft said it planned to publish a
        paper documenting how the technology works and to open source the software</a>. This paper is
        the first half of that; <a href="index.html">the catalog on this site</a> is the second.</p>
      <p>It is also not the Lab's only run at this problem. Its closest sibling is
        <a href="{UKUVULA}" target="_blank" rel="noopener">Ukuvula</a>, built with the Nelson Mandela
        Foundation &mdash; a pipeline making large oral-history archives searchable, generating
        transcripts, named entities, and summaries from liberation-era recordings. Different medium,
        different continent, same shape of problem: a collection that exists but cannot be asked a
        question.</p>

      <h2>The short of it</h2>
      <p>An archive that cannot be questioned is, for most people, an archive that does not exist.
        The Living Library is one worked answer to that &mdash; not the only one, and not a finished
        one. Its most transferable parts are the least glamorous: publish records continuously and
        let curators correct them in place, keep every claim traceable to a real document, and decide
        honestly whether you need the avatar at all.</p>
      <p>If your institution is somewhere in this, the Library would like to hear about it.
        <a href="mailto:hello@trlibrary.com">hello@trlibrary.com</a> reaches a person.</p>

      <div class="codeblock"><button data-copy>Copy</button><span class="cm"># citation</span>
Pengce Wang, Lucia Ronchi Darre, Matt Briney, Michaell Bakalars,
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
        <h3>On this page</h3>
        <div class="links toc">
          <a href="#main">One &mdash; What it is</a>
          <a href="#doing">Three &mdash; Doing it yourself</a>
          <a href="#collection">The collection, in detail</a>
        </div>
      </section>
      <section>
        <h3>Read the paper</h3>
        <div class="links">
          <a href="{PAPER_URL}" target="_blank" rel="noopener">{ICON_EXT} Abstract<span>arXiv</span></a>
          <a href="{PAPER_HTML}" target="_blank" rel="noopener">{ICON_EXT} Full text<span>HTML</span></a>
          <a href="{PAPER_PDF}" target="_blank" rel="noopener">{ICON_EXT} Download<span>PDF</span></a>
        </div>
      </section>
      <section>
        <h3>Try the real thing</h3>
        <div class="links">
          <a href="https://campfire.trlibrary.com" target="_blank" rel="noopener">{ICON_EXT} Campfire<span>Layers 1&ndash;3, live</span></a>
          <a href="{TRC_LIBRARY}" target="_blank" rel="noopener">{ICON_EXT} Digital Library<span>The collection</span></a>
        </div>
      </section>
      <section>
        <h3>Authors</h3>
        <p class="meta">Pengce Wang, Lucia Ronchi Darre, <strong>Matt Briney</strong>, Michaell
          Bakalars, Dan Rutkowski, Ursula Hardy, David Wolf, Laura Hoffman, Allen Kim, Shawn Wright,
          and Juan Lavista Ferres &mdash; Microsoft, and the Theodore Roosevelt Presidential
          Library.</p>
      </section>
      <section>
        <h3>Press &amp; background</h3>
        <div class="links">
          <a href="{MS_SIGNAL}" target="_blank" rel="noopener">{ICON_EXT} Microsoft on the opening<span>Signal</span></a>
          <a href="{GEEKWIRE}" target="_blank" rel="noopener">{ICON_EXT} Archives to avatars<span>GeekWire</span></a>
          <a href="{MS_AIFG}" target="_blank" rel="noopener">{ICON_EXT} AI for Good Lab<span>The lab</span></a>
          <a href="{UKUVULA}" target="_blank" rel="noopener">{ICON_EXT} Ukuvula<span>Sibling project</span></a>
        </div>
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


def build_about():
    """About the Library itself — for the peer institution that arrived here via GitHub.

    Mission, vision, values and Foundation facts are quoted from trlibrary.com.
    """
    desc = ("The Theodore Roosevelt Presidential Library in Medora, North Dakota — its mission, "
            "the Badlands it sits in, the Foundation that runs it, and the collection behind "
            "these open source projects.")

    body = f"""
<div class="shell">
  <p class="crumbs"><a href="index.html">TRPL Labs</a> &nbsp;/&nbsp; About</p>
</div>

<header class="p-head">
  <div class="shell">
    <p class="cat">About</p>
    <h1>The Theodore Roosevelt Presidential Library</h1>
    <p class="tag">Theodore Roosevelt died on 6 January 1919. For more than a century he had no
      presidential library. Today he does, and it stands in Medora, North Dakota &mdash; in the
      Badlands country that made him.</p>
    <div class="p-actions">
      <a class="btn solid" href="https://www.trlibrary.com" target="_blank" rel="noopener">
        Visit trlibrary.com {ICON_EXT}</a>
      <a class="btn" href="https://www.trlibrary.com/visit" target="_blank" rel="noopener">
        Plan a visit {ICON_EXT}</a>
    </div>
  </div>
</header>

<div class="shell">
  <div class="p-layout">
    <div class="prose" id="main">

      <h2>Why the Badlands</h2>
      <p>Most presidential libraries stand where their president governed or was born. This one
        stands where a young man fell apart and put himself back together.</p>
      <p>Roosevelt came to the Dakota Territory in his twenties, and returned to it after losing his
        wife and his mother on the same day in the same house. He ranched, he froze, he rode for
        days, and he came back East a different person &mdash; the conservationist and the
        practitioner of the strenuous life that the country would later elect. He said the
        experience made him. The Library is built in that country, on purpose, because the landscape
        is not a backdrop to the story. It is the story.</p>

      <h2>Mission, vision, and values</h2>
      <p>The Library organizes its work around three pillar principles &mdash;
        <strong>Citizenship, Leadership, and Conservation</strong> &mdash; and states its purpose
        plainly:</p>
      <div class="cols2">
        <div>
          <h3>Mission</h3>
          <p>Explore T.R.'s life, legacy, and enduring relevance.</p>
        </div>
        <div>
          <h3>Vision</h3>
          <p>Inspire action and fearless participation in the arena.</p>
        </div>
      </div>
      <p>Its four values are <strong>Dare Greatly</strong>, <strong>Think Boldly</strong>,
        <strong>Live Passionately</strong>, and <strong>Care Deeply</strong>. They are worth reading
        as an explanation of why this site exists at all: an institution that tells visitors to get
        into the arena is poorly placed to keep its own working methods behind a wall.</p>

      <h2>The building and the land</h2>
      <p>The Library opened to the public on 4 July 2026. The building is covered in native grasses,
        with a planted roof visitors can walk across and skylights providing most of the interior
        light &mdash; an attempt to make a substantial public building sit inside the landscape
        rather than on top of it.</p>
      <p>The site is a 93-acre property being restored to its natural state, and the project pursues
        the Living Building Challenge alongside LEED and SITES certification. For an institution
        honoring the conservation president, the building is part of the argument, not just the
        container for it.</p>

      <h2>The collection, and what was done with it</h2>
      <p>Roosevelt left one of the richest written records of any American president, and for more
        than a century it sat scattered across dozens of separate institutions &mdash; readable in
        practice only by people who could travel to an archive and already knew where to look.</p>
      <p>Bringing that together is the Library's central digital project, built on decades of
        cataloging by the <a href="{TRC_URL}" target="_blank" rel="noopener">Theodore Roosevelt
        Center at Dickinson State University</a>. It produced three things: a research tool anyone
        can use from anywhere, a curator-facing application for correcting and verifying records,
        and an exhibit where a visitor can stand in a room and ask Roosevelt a question out loud.
        The method behind all three was published with Microsoft and is
        <a href="living-library.html">broken down here</a>.</p>

      <h2>The Foundation</h2>
      <p>The Theodore Roosevelt Presidential Library Foundation is the non-profit organization that
        operates the Library, governed by a board of trustees drawn from local and national
        leadership. It is not a federal institution and is not run by the National Archives.
        Audited financial statements, Form 990 filings, bylaws, and committee charters are
        <a href="https://www.trlibrary.com/the-foundation" target="_blank" rel="noopener">published
        openly</a>.</p>

      <h2>And this site</h2>
      <p>labs.trlibrary.com is where the Library publishes the software it builds for itself, so
        that other museums and non-profits can fork it rather than pay to have it rebuilt. Everything
        here is MIT licensed. The reasoning is
        <a href="index.html#about">on the homepage</a>, and the projects are
        <a href="index.html#projects">in the catalog</a>.</p>
    </div>

    <aside class="side">
      <section>
        <h3>Visit</h3>
        <p class="meta">Medora, North Dakota, in the Badlands of the state's western edge.</p>
        <div class="links">
          <a href="https://www.trlibrary.com/visit" target="_blank" rel="noopener">{ICON_EXT} Plan your visit<span>Hours, tickets</span></a>
          <a href="https://www.trlibrary.com/visit/directions" target="_blank" rel="noopener">{ICON_EXT} Directions<span>Getting there</span></a>
          <a href="https://www.trlibrary.com/visit/exhibits" target="_blank" rel="noopener">{ICON_EXT} Exhibits<span>What's inside</span></a>
        </div>
      </section>
      <section>
        <h3>Explore from anywhere</h3>
        <div class="links">
          <a href="https://campfire.trlibrary.com" target="_blank" rel="noopener">{ICON_EXT} Campfire<span>Ask the archive</span></a>
          <a href="https://www.trlibrary.com/tr" target="_blank" rel="noopener">{ICON_EXT} T.R.'s life<span>Free to read</span></a>
          <a href="https://www.trlibrary.com/podcast/good-citizen" target="_blank" rel="noopener">{ICON_EXT} Good Citizen<span>Podcast</span></a>
        </div>
      </section>
      <section>
        <h3>The organization</h3>
        <div class="links">
          <a href="https://www.trlibrary.com/the-foundation" target="_blank" rel="noopener">{ICON_EXT} The Foundation<span>Governance</span></a>
          <a href="https://www.trlibrary.com/board-members" target="_blank" rel="noopener">{ICON_EXT} Trustees<span>The board</span></a>
          <a href="https://www.trlibrary.com/support-trpl" target="_blank" rel="noopener">{ICON_EXT} Support the Library<span>Donate</span></a>
        </div>
      </section>
      <section>
        <h3>Get in touch</h3>
        <div class="links">
          <a href="mailto:hello@trlibrary.com">Email the Library<span>hello@trlibrary.com</span></a>
          <a href="{ORG_URL}" target="_blank" rel="noopener">{ICON_EXT} GitHub<span>All repositories</span></a>
        </div>
      </section>
    </aside>
  </div>
  <p style="height:40px"></p>
</div>
"""
    out = (
        head("About — TRPL Labs", desc, 0, f"{SITE}/about.html")
        + body
        + footer(0).replace("</body>", '<script src="assets/js/labs.js"></script>\n</body>')
    )
    (ROOT / "about.html").write_text(out, encoding="utf-8")


def build_sitemap():
    urls = ([f"{SITE}/", f"{SITE}/about.html", f"{SITE}/living-library.html"]
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
    build_about()
    build_living_library()
    build_index()
    for i, p in enumerate(PROJECTS):
        build_project(p, PROJECTS[i - 1] if i else None,
                      PROJECTS[i + 1] if i + 1 < len(PROJECTS) else None)
    shots = sum(1 for p in PROJECTS if shot_path(p["slug"]))
    print(f"Built index.html + {len(PROJECTS)} project pages ({shots} screenshots found).")


if __name__ == "__main__":
    main()
