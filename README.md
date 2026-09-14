# LabsWebsite

The source for **[labs.trlibrary.com](https://labs.trlibrary.com)** — a catalog of the
Theodore Roosevelt Presidential Library's public open source projects, built so that other
museums and nonprofits can find them, see them running, and fork them.

Static HTML with no build dependencies. GitHub Pages serves it from `main` at the root.

---

## How it works

Every page on the site is generated from a single file, `data/projects.json`. Nothing is
hand-edited in `index.html` or `projects/`.

```
data/projects.json     ← the only file you edit for content
tools/build.py         ← regenerates index.html, projects/*.html, sitemap.xml
index.html             ← generated
living-library.html    ← generated; prose lives in build_living_library()
projects/<slug>.html   ← generated, one per project
assets/css/labs.css    ← the design system
assets/js/labs.js      ← search, filtering, live previews
assets/shots/<slug>.png ← screenshots, captured weekly in CI
```

To add, remove, or reword a project:

```bash
# edit data/projects.json, then
python3 tools/build.py
git add -A && git commit -m "Add Foo to the catalog" && git push
```

No dependencies. Python 3 standard library only.

### Fields in `projects.json`

| Field | Notes |
|---|---|
| `slug` | Filename and URL. Never change it once published. |
| `repo` | Repository name in the org. Drives every GitHub link. |
| `name` / `tagline` | What the card shows. Keep the tagline under about 18 words. |
| `category` | Must match one of the categories in `CATEGORY_ORDER` in `tools/build.py`. |
| `description` | Array of paragraphs for the detail page. |
| `capabilities` | Array of bullets. Inline HTML (`<code>`) is allowed. |
| `stack` | Array. The first four appear as chips on the card. |
| `demo` | Live URL, or omit. |
| `embeddable` | `true` if the demo can be iframed. Controls the live-preview button. |
| `demoNote` | Optional caveat shown under the demo panel. |
| `demoAlt` | Optional second link, `{label, url}`. |
| `setup` | Array of numbered fork-and-adapt steps. Inline HTML allowed. |

### The Living Library page

`living-library.html` is not a catalog entry — it is a plain-language read of
[arXiv:2609.09368](https://arxiv.org/abs/2609.09368), the Microsoft/TRPL paper describing the
framework behind Campfire, the Archivist App, and Talk to TR. It is also the featured band at
the top of the homepage.

Its prose lives in `build_living_library()` in `tools/build.py`, not in `projects.json`, because
it is a one-off editorial page rather than a repeatable record.

**Every figure on that page comes from the paper.** If you edit it, keep it that way — the page
ends by telling the reader that where it differs from the paper, the paper is right. Two things
in particular were handled deliberately and should not be softened:

- The worked Cross-Era Analogical Grounding example carries an explicit warning that the response
  is **generated, not a historical quotation**. A TR-voiced sentence on a Library page must never
  read as something Roosevelt actually said.
- The "What the paper does not claim" section is not hedging. The authors flag faithfulness,
  anachronism, and experiential presence as open questions, and the page says so.

---

## Screenshots

`.github/workflows/screenshots.yml` runs weekly, opens every project's live demo in headless
Chromium, and commits the results to `assets/shots/`. It then reruns `tools/build.py` so the
cards pick the images up.

**Run this workflow once after the first deploy.** Until it does, every card falls back to a
branded Night Sky tile with the project's name — correct, but monotonous across 21 cards.

Cards are screenshots only. Live demos are embedded on the project detail pages instead, one
per page and loaded on click — several of these projects pull a 3D model or a star catalog on
start, which is fine once and unreasonable twenty-one times.

Run it by hand:

```bash
npm install --no-save playwright && npx playwright install chromium
node tools/shoot.mjs             # everything
node tools/shoot.mjs stargazer   # one project
python3 tools/build.py
```

---

## Brand

Type and color follow the TRPL Visual Identity System v0.1.

- **Display** — Dharma Gothic E, all caps, tight leading. Falls back to Impact, then Arial Narrow.
- **Body** — ITC Clearface. Falls back to Georgia.
- **UI** — Frutiger. Falls back to the system sans stack.
- **Color** — white ground, Dark Gray text, Night Sky for masthead, hero, and footer,
  Deep Orange for action. Two color families, per the identity system's restraint rule.

### One thing to finish: self-hosted fonts

`assets/css/labs.css` resolves each face from `assets/fonts/` **first**, and falls back to
the copy on `trlibrary.com` if the local file is missing. Right now `assets/fonts/` is empty,
so the site is loading fonts from trlibrary.com.

To make it fully self-contained, drop these eight files into `assets/fonts/`:

```
dharma_type-dharmagothice-bold.woff2
dharma_type-dharmagothice-exbold.woff2
clearfacestd-regular.woff2
clearfacestd-regularitalic.woff2
clearfacestd-bold.woff2
frutigerltstd-light.woff2
frutigerltstd-regular.woff2
frutigerltstd-bold.woff2
```

They are the same files already served from
`https://www.trlibrary.com/themes/custom/trpl/css/`. No CSS change is needed — the local
copies take priority automatically. **Check the license before committing them**, since this
repository is public and several of the Library's other repos deliberately avoid bundling
these faces for that reason.

### Accessibility note

Deep Orange (`#E7805D`) does not clear WCAG AA as text on white — the identity system says
as much. The site uses the real Deep Orange only where it carries no text (rules, dots,
headline numerals on Night Sky) and a darkened tint of the same hue, `#B4522F`, wherever text
or a button label is involved. All body and label text meets AA.

---

## URLs

The site uses extensionless URLs — `/about`, `/living-library`,
`/projects/stargazer`. The files on disk keep their `.html` names; GitHub Pages
resolves a request for `/about` to `about.html` on its own, with no redirect.

Two consequences worth knowing:

- **Old `.html` URLs still work.** `/living-library.html` serves the same page, so
  anything already shared or indexed keeps resolving.
- **No trailing slashes.** GitHub Pages does *not* serve `/about/` — that 404s.
  `tools/build.py` strips `.html` from every internal link at write time
  (`prettify()`), so don't hand-write links with extensions or trailing slashes.

## Local preview

`open index.html` and `python3 -m http.server` both break on extensionless links,
because neither adds the `.html`. Use the included server instead — it applies the
same rule GitHub Pages does:

```bash
python3 tools/serve.py          # http://localhost:8000
python3 tools/serve.py 8080     # a different port
```

It deliberately mirrors two Pages behaviours so mistakes surface locally: a
trailing slash on a page URL 404s, and a directory without an `index.html` 404s
rather than showing a listing.

---

## License

The site itself is MIT, and so is every project it lists.
