# arunviswanathan.com

My personal website — plain HTML and CSS, no build step, hosted on GitHub Pages.

## Structure

- `index.html` — home / about me
- `projects.html` — projects
- `writing.html` — writing (on-site posts and links to work published elsewhere)
- `publications.html` — publications
- `talks.html` — talks and presentations
- `writing/` — one HTML file per article; `writing/example-post.html` is the
  copy-me template
- `assets/portrait.png` — the circular hero portrait shown on the home page
- `style.css` — the single shared stylesheet
- `theme.js` — the light/dark toggle behavior (an inline snippet in each page's
  `<head>` applies the saved theme before paint)
- `404.html` — not-found page
- `CNAME` — custom domain for GitHub Pages
- `.nojekyll` — tells GitHub Pages to serve files as-is (no Jekyll build)

## Writing a new article

1. Copy `writing/example-post.html` to `writing/<slug>.html`
   (e.g. `writing/on-focus.html`).
2. Change the `<title>`, the `<h1>`, and the `<time>` (both the `datetime="…"`
   attribute and the visible date).
3. Replace everything inside `<div class="body"> … </div>` with your writing.
   Leave the header, footer, and paths alone — they're already correct.
4. Add a matching `<li>` to the `<ul class="post-list">` on `writing.html`:

   ```html
   <li>
       <time datetime="2026-08-01">2026-08-01</time>
       <a href="writing/on-focus.html">Your title</a>
   </li>
   ```

5. Commit and push — GitHub Pages publishes automatically. (Or just hand the
   text to Claude and it will do all of the above.)

Delete `writing/example-post.html` and its entry once you have real posts.
