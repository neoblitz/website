# arunviswanathan.com

My personal website — plain HTML and CSS, hosted on GitHub Pages. Articles are
written in Markdown and turned into pages by a small local build script; the
site itself is served as static files (no build on the server).

## Structure

- `index.html` — home / about me
- `projects.html` — projects
- `writing.html` — writing (post list + search, and links to work published elsewhere)
- `publications.html` — publications
- `talks.html` — talks and presentations
- `writing/content/*.md` — **article sources** (Markdown, one per post)
- `writing/*.html` — **generated** article pages (do not edit by hand)
- `build.py` — converts the Markdown into pages, rebuilds the post list, and
  writes the search index
- `search-index.json` — **generated** index used by the Writing page's search
- `search.js` — client-side search behavior
- `theme.js` — light/dark toggle behavior
- `assets/portrait.png` — the circular hero portrait shown on the home page
- `style.css` — the single shared stylesheet
- `404.html` — not-found page
- `CNAME` — custom domain for GitHub Pages
- `.nojekyll` — tells GitHub Pages to serve files as-is (no Jekyll build)

## Writing a new article

1. Create `writing/content/<slug>.md` and write your post in Markdown.
   Optionally add front matter at the top to set the title and date:

   ```markdown
   ---
   title: Why I Started Writing
   date: 2026-07-28
   ---

   Your first paragraph…
   ```

   Without front matter, the title is taken from the first `# heading` and the
   date from the file's modified time.

2. Run the build (needs Python + the `markdown` package — `pip install markdown`):

   ```bash
   python3 build.py
   ```

   This regenerates the article page, the post list on `writing.html`, and the
   search index.

3. Commit and push — GitHub Pages publishes automatically.

Or just hand the Markdown (or even the plain text) to Claude and it will run the
build and publish for you.
