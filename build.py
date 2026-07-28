#!/usr/bin/env python3
"""Build writing/ HTML pages and the search index from Markdown.

Usage:  python3 build.py    (needs the `markdown` package: pip install markdown)

For each `writing/content/*.md` file it:
  - reads optional front matter (title, date),
  - converts the Markdown to HTML,
  - wraps it in the site's article template -> writing/<slug>.html,
  - rebuilds the Posts list in writing.html (between the POSTS markers),
  - writes search-index.json used by the Writing page's search box.

Front matter is optional. Example:

    ---
    title: Why I Started Writing
    date: 2026-07-28
    ---

If title/date are omitted, the title comes from the first `# ` heading and the
date from the file's modification time. Files whose names start with `_` are
skipped.
"""

import os
import re
import json
import glob
import datetime
import markdown

CONTENT_DIR = "writing/content"
OUT_DIR = "writing"
WRITING_PAGE = "writing.html"
INDEX_FILE = "search-index.json"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%%TITLE%% — Arun Viswanathan</title>
    <meta name="description" content="%%DESC%%">
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90' font-family='Georgia,serif' fill='%23b0522c'%3EA%3C/text%3E%3C/svg%3E">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700&family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../style.css">
    <script>(function(){try{var t=localStorage.getItem('theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
</head>
<body>
    <div class="page">
        <header class="site-header">
            <a class="identity" href="../index.html">
                <span class="site-name">Arun Viswanathan</span>
            </a>
            <nav class="site-nav">
                <a href="../index.html">About</a>
                <a href="../projects.html">Projects</a>
                <a href="../writing.html" aria-current="page">Writing</a>
                <a href="../publications.html">Publications</a>
                <a href="../talks.html">Talks</a>
                <button class="theme-toggle" type="button" aria-label="Switch to dark mode">
                    <svg class="icon-moon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg>
                    <svg class="icon-sun" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
                </button>
            </nav>
        </header>

        <main>
            <article>
                <header>
                    <h1>%%TITLE%%</h1>
                    <time datetime="%%DATE_ISO%%">%%DATE_DISPLAY%%</time>
                </header>

                <div class="body">
%%BODY%%
                </div>
            </article>

            <p class="muted"><a href="../writing.html">← Back to writing</a></p>
        </main>

        <footer class="site-footer">
            <span>© 2026 Arun Viswanathan</span>
            <span>
                <a href="https://github.com/neoblitz">GitHub</a> ·
                <a href="https://www.linkedin.com/in/arunaviswanathan/">LinkedIn</a>
            </span>
        </footer>
    </div>
    <script src="/theme.js"></script>
</body>
</html>
"""


def parse_front_matter(text):
    meta = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
        text = text[m.end():]
    return meta, text


def html_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def format_date(iso):
    d = datetime.date.fromisoformat(iso)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def build():
    posts = []
    for md_path in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.md"))):
        name = os.path.basename(md_path)
        if name.startswith("_"):
            continue
        slug = os.path.splitext(name)[0]
        raw = open(md_path, encoding="utf-8").read()
        meta, body_md = parse_front_matter(raw)

        title = meta.get("title")
        if not title:
            hm = re.search(r"^#\s+(.+)$", body_md, re.MULTILINE)
            title = hm.group(1).strip() if hm else slug.replace("-", " ").title()
            body_md = re.sub(r"^#\s+.+$", "", body_md, count=1, flags=re.MULTILINE)

        iso = meta.get("date") or datetime.date.fromtimestamp(
            os.path.getmtime(md_path)).isoformat()

        body_html = markdown.markdown(
            body_md.strip(), extensions=["extra", "sane_lists", "smarty"])

        plain = re.sub(r"<[^>]+>", " ", body_html)
        plain = re.sub(r"\s+", " ", plain).strip()
        desc = (plain[:157] + "…") if len(plain) > 158 else plain

        page = (TEMPLATE
                .replace("%%TITLE%%", html_escape(title))
                .replace("%%DESC%%", html_escape(desc))
                .replace("%%DATE_ISO%%", iso)
                .replace("%%DATE_DISPLAY%%", format_date(iso))
                .replace("%%BODY%%", body_html))
        out_path = os.path.join(OUT_DIR, slug + ".html")
        open(out_path, "w", encoding="utf-8").write(page)

        posts.append({"title": title, "url": "writing/%s.html" % slug,
                      "date": iso, "text": plain})

    posts.sort(key=lambda p: p["date"], reverse=True)

    # search index (title + full text; served from the site root)
    lite = [{"title": p["title"], "url": p["url"], "date": p["date"],
             "text": p["text"]} for p in posts]
    json.dump(lite, open(INDEX_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # rebuild the Posts list inside writing.html between the markers
    items = "\n".join(
        '                    <li>\n'
        '                        <time datetime="%s">%s</time>\n'
        '                        <a href="%s">%s</a>\n'
        '                    </li>' % (p["date"], p["date"], p["url"],
                                       html_escape(p["title"]))
        for p in posts)
    block = ('<!-- POSTS:START -->\n'
             '                <ul class="post-list" id="posts">\n'
             + items + '\n'
             '                </ul>\n'
             '                <!-- POSTS:END -->')
    page = open(WRITING_PAGE, encoding="utf-8").read()
    page = re.sub(r"<!-- POSTS:START -->.*?<!-- POSTS:END -->",
                  lambda m: block, page, flags=re.DOTALL)
    open(WRITING_PAGE, "w", encoding="utf-8").write(page)

    print("Built %d post(s): %s" % (len(posts),
          ", ".join(p["url"] for p in posts)))


if __name__ == "__main__":
    build()
