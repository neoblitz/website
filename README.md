# arunviswanathan.com

My personal website — plain HTML and CSS, no build step, hosted on GitHub Pages.

## Structure

- `index.html` — home / about me
- `projects.html` — projects
- `writing.html` — writing (on-site posts and links to work published elsewhere)
- `publications.html` — publications
- `talks.html` — talks and presentations
- `assets/portrait.png` — the circular hero portrait shown on the home page
- `assets/monogram.png` — the small "A" mark shown beside the name in every header
- `style.css` — the single shared stylesheet
- `404.html` — not-found page
- `CNAME` — custom domain for GitHub Pages
- `.nojekyll` — tells GitHub Pages to serve files as-is (no Jekyll build)

## Adding a post

1. Create `writing/<slug>.html`, reusing the header and footer markup from any
   existing page (adjust the relative paths — the file lives one level down, so
   use `../style.css`, `../assets/…`, `../index.html`, etc.).
2. Wrap the post body in an `<article>` and set the `<title>`, `<h1>`, and `<time>`.
3. Add a `<ul class="post-list">` entry to `writing.html` linking to it.
4. Commit and push — GitHub Pages publishes automatically.
