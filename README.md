# arunviswanathan.com

My personal website — plain HTML and CSS, hosted on GitHub Pages. Content lives
in two data sources (Markdown posts and a projects file); a small local build
script generates the pages from them. The site itself is served as static files
(no build on the server).

## Editing rule

You only ever edit **content sources**. Everything else with "generated" below
is rebuilt by `build.py` — don't hand-edit it, your changes will be overwritten.

Content sources:
- `writing/content/*.md` — one Markdown file per post
- `data/projects.yaml` — the list of projects
- prose on `index.html` (the intro / Background / Beyond work), `publications.html`,
  and `talks.html` is still edited directly

Everything derived from those (the article pages, the post list, the search
index, the project cards on `projects.html`, and the home page's "Selected
projects" and "Recent writing") is regenerated between `<!-- … -->` markers.

## Structure

- `index.html` — home / about (intro is hand-written; the two lists are generated)
- `projects.html` — projects (generated from `data/projects.yaml`)
- `writing.html` — writing (post list + search; generated post list)
- `publications.html`, `talks.html` — hand-written lists
- `writing/content/*.md` — **article sources**
- `writing/*.html` — **generated** article pages
- `data/projects.yaml` — **project source of truth**
- `build.py` — the generator
- `search-index.json` — **generated** search index · `search.js` — search UI
- `theme.js` — light/dark toggle · `style.css` — shared stylesheet
- `assets/portrait.png` — hero portrait
- `404.html` · `CNAME` · `.nojekyll`

## The build

```bash
pip install markdown pyyaml   # one-time
python3 build.py              # after editing any content source
```

## Adding a post

1. Create `writing/content/<slug>.md`. Optionally set title, date, and tags via
   front matter:

   ```markdown
   ---
   title: Why I Started Writing
   date: 2026-07-28
   tags: writing, reflection, personal
   ---

   Your first paragraph…
   ```

   Without front matter, the title comes from the first `# heading` and the date
   from the file's modified time. `tags` is a comma-separated list; it drives the
   Tags list in the Writing-page sidebar (the Archive is built automatically from
   dates), and the tags also appear on the article itself.

   `date` is the publish date and never changes on its own. A **"Updated …"**
   note appears next to it automatically once a post is changed after publishing
   — it's taken from git (the date the file was last committed, or today while
   the post has uncommitted edits). Set `updated: YYYY-MM-DD` in front matter to
   override it. It shows only when it differs from `date`.
2. Run `python3 build.py`, then commit and push.

### Drafts

Work in progress goes in `writing/drafts/`. That folder is **gitignored** — its
files are never compiled into pages, never committed, and never published (this
is a public repo, so drafts stay on your machine only). When a draft is ready,
move it to `writing/content/` and run the build.

## Adding or editing a project

1. Edit `data/projects.yaml` (add an entry under a section; set `featured: true`
   to also show it on the home page).
2. Run `python3 build.py`, then commit and push.

Or just hand the Markdown / project details to Claude and it will build and
publish for you.
