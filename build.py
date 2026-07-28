#!/usr/bin/env python3
"""Static build for arunviswanathan.com.

Single sources of truth:
  - Posts:    writing/content/*.md   (Markdown, one per post)
  - Projects: data/projects.yaml

Running `python3 build.py` regenerates everything derived from them:
  - writing/<slug>.html            (article pages)
  - the post list on writing.html  (between the POSTS markers)
  - search-index.json              (post search)
  - the project sections on projects.html   (PROJECTS markers)
  - the home page's "Selected projects" (FEATURED markers) and
    "Recent writing" (RECENT markers)

The pages are still served as plain static files; this build runs locally.
Needs:  pip install markdown pyyaml
"""

import os
import re
import json
import glob
import datetime
import markdown
import yaml

CONTENT_DIR = "writing/content"
OUT_DIR = "writing"
DATA_DIR = "data"
WRITING_PAGE = "writing.html"
PROJECTS_PAGE = "projects.html"
HOME_PAGE = "index.html"
INDEX_FILE = "search-index.json"
RECENT_ON_HOME = 3

ARTICLE_TEMPLATE = """<!DOCTYPE html>
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


# ---------------------------------------------------------------- helpers

def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def format_date(iso):
    d = datetime.date.fromisoformat(iso)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def replace_region(text, start, end, inner):
    """Replace whatever sits between the two marker comments with `inner`,
    keeping the markers. Assumes the END marker is indented 12 spaces."""
    pattern = re.escape(start) + r".*?" + re.escape(end)
    repl = start + "\n" + inner + "\n            " + end
    new, n = re.subn(pattern, lambda m: repl, text, flags=re.DOTALL)
    if n == 0:
        raise SystemExit("Marker %s not found — did the page lose it?" % start)
    return new


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


# ---------------------------------------------------------------- posts

def build_posts():
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

        page = (ARTICLE_TEMPLATE
                .replace("%%TITLE%%", html_escape(title))
                .replace("%%DESC%%", html_escape(desc))
                .replace("%%DATE_ISO%%", iso)
                .replace("%%DATE_DISPLAY%%", format_date(iso))
                .replace("%%BODY%%", body_html))
        open(os.path.join(OUT_DIR, slug + ".html"), "w", encoding="utf-8").write(page)

        posts.append({"title": title, "url": "writing/%s.html" % slug,
                      "date": iso, "text": plain})

    posts.sort(key=lambda p: p["date"], reverse=True)
    json.dump(posts, open(INDEX_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return posts


def post_list_items(posts, indent):
    pad = " " * indent
    return "\n".join(
        '%s<li>\n'
        '%s    <time datetime="%s">%s</time>\n'
        '%s    <a href="%s">%s</a>\n'
        '%s</li>' % (pad, pad, p["date"], p["date"], pad, p["url"],
                     html_escape(p["title"]), pad)
        for p in posts)


def build_writing_page(posts):
    inner = ('                <ul class="post-list" id="posts">\n'
             + post_list_items(posts, 20) + '\n'
             '                </ul>')
    text = open(WRITING_PAGE, encoding="utf-8").read()
    text = replace_region(text, "<!-- POSTS:START -->", "<!-- POSTS:END -->", inner)
    open(WRITING_PAGE, "w", encoding="utf-8").write(text)


# ---------------------------------------------------------------- projects

def card_html(p, meta_key="meta", desc_key="description"):
    meta = p.get(meta_key) or p.get("meta") or ""
    desc = p.get(desc_key) or p.get("description") or ""
    return ('                <a class="card" href="%s">\n'
            '                    <h2>%s</h2>\n'
            '                    <div class="meta">%s</div>\n'
            '                    <p>%s</p>\n'
            '                </a>' % (html_escape(p["url"]), html_escape(p["title"]),
                                      html_escape(meta), html_escape(" ".join(desc.split()))))


def load_projects():
    return yaml.safe_load(open(os.path.join(DATA_DIR, "projects.yaml"), encoding="utf-8"))


def build_projects_page(data):
    blocks = []
    for section in data["sections"]:
        cards = "\n\n".join(card_html(p) for p in section["projects"])
        blocks.append(
            '            <div class="section-head">\n'
            '                <h2>%s</h2>\n'
            '            </div>\n'
            '            <div class="cards duo">\n'
            '%s\n'
            '            </div>' % (html_escape(section["name"]), cards))
    inner = "\n\n".join(blocks)
    text = open(PROJECTS_PAGE, encoding="utf-8").read()
    text = replace_region(text, "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->", inner)
    open(PROJECTS_PAGE, "w", encoding="utf-8").write(text)


def build_home(data, posts):
    featured = [p for s in data["sections"] for p in s["projects"] if p.get("featured")]
    cards = "\n".join(card_html(p, "home_meta", "summary") for p in featured)
    featured_inner = ('            <div class="cards duo">\n'
                      + cards + '\n'
                      '            </div>')
    recent_inner = ('            <ul class="post-list">\n'
                    + post_list_items(posts[:RECENT_ON_HOME], 16) + '\n'
                    '            </ul>')
    text = open(HOME_PAGE, encoding="utf-8").read()
    text = replace_region(text, "<!-- FEATURED:START -->", "<!-- FEATURED:END -->", featured_inner)
    text = replace_region(text, "<!-- RECENT:START -->", "<!-- RECENT:END -->", recent_inner)
    open(HOME_PAGE, "w", encoding="utf-8").write(text)


# ---------------------------------------------------------------- main

def main():
    posts = build_posts()
    build_writing_page(posts)
    data = load_projects()
    build_projects_page(data)
    build_home(data, posts)
    nproj = sum(len(s["projects"]) for s in data["sections"])
    print("Built %d post(s) and %d project(s)." % (len(posts), nproj))


if __name__ == "__main__":
    main()
