#!/usr/bin/env python3
"""Static site generator for hackinghat.com.

Reads Markdown posts (with YAML frontmatter) from posts/, renders them and
navigation pages (index, archive, per-tag) into docs/, which GitHub Pages
serves. Run this before committing and pushing.

    pip install -r requirements.txt
    python build.py
"""

import re
import shutil
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
DOCS_DIR = ROOT / "docs"

# Leading "YYYY-MM-DD-" on a post filename is a convention; stripped for the slug.
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_posts():
    md = markdown.Markdown(extensions=["fenced_code", "tables", "smarty"])
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        fm = frontmatter.loads(path.read_text(encoding="utf-8"))
        slug = DATE_PREFIX.sub("", path.stem)
        tags = [{"name": t, "slug": slugify(t)} for t in fm.get("tags", [])]
        html = md.reset().convert(fm.content)
        posts.append({
            "slug": slug,
            "title": fm.get("title", slug),
            "date": str(fm.get("date", "")),
            "tags": tags,
            "summary": fm.get("summary", ""),
            "html": html,
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def build_tags(posts):
    counts = {}
    name_by_slug = {}
    for p in posts:
        for t in p["tags"]:
            counts[t["slug"]] = counts.get(t["slug"], 0) + 1
            name_by_slug[t["slug"]] = t["name"]
    return [
        {"slug": s, "name": name_by_slug[s], "count": c}
        for s, c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    ]


def build_archive(posts):
    by_year = {}
    for p in posts:
        by_year.setdefault(p["date"][:4], []).append(p)
    return sorted(by_year.items(), key=lambda kv: kv[0], reverse=True)


def clean_docs():
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True)
    (DOCS_DIR / ".nojekyll").write_text("")
    (DOCS_DIR / "CNAME").write_text("hackinghat.com\n")


def main():
    posts = load_posts()
    tags = build_tags(posts)
    archive = build_archive(posts)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    clean_docs()
    shutil.copytree(ASSETS_DIR, DOCS_DIR / "assets")

    def render(template, dest, context, root):
        ctx = {"root": root, "tags": tags, **context}
        out = DOCS_DIR / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(env.get_template(template).render(**ctx), encoding="utf-8")

    render("index.html", "index.html", {"posts": posts}, root="")
    render("archive.html", "archive.html", {"archive": archive}, root="")
    render("tags_index.html", "tags/index.html", {}, root="../")

    for p in posts:
        render("post.html", f"posts/{p['slug']}.html", {"post": p}, root="../")

    for t in tags:
        tag_posts = [p for p in posts if any(pt["slug"] == t["slug"] for pt in p["tags"])]
        render("tag.html", f"tags/{t['slug']}.html", {"posts": tag_posts, "tag": t}, root="../")

    print(f"Built {len(posts)} post(s), {len(tags)} tag(s) into docs/")


if __name__ == "__main__":
    main()
