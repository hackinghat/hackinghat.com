# hackinghat.com

A static blog served from GitHub Pages. Posts are Markdown files with YAML
frontmatter; a small Python script renders them and generates navigation
(by date and by tag) into `docs/`, which GitHub Pages serves.

## Write a post

Create `posts/YYYY-MM-DD-slug.md`:

```markdown
---
title: My Post
date: 2026-10-04
tags: [math, python]
summary: One-line description for the index and archive.
---
Body in **Markdown**. Inline math $x^2$; display math $$\int_0^1 x\,dx$$.
```

- `date` is the creation date used for the archive. The filename date is a
  convention only (stripped to form the URL slug).
- `tags` is a list; each tag gets its own page and a nav link.
- Images live in `assets/images/` and are referenced relative to the
  *generated* post location: `![](../assets/images/foo.png)`.

## Build

```sh
pip install -r requirements.txt
python build.py        # writes everything into docs/
```

Preview locally:

```sh
python -m http.server -d docs 8000
# open http://localhost:8000
```

## Publish

1. `git add docs/` (the generated output is committed) and push to `main`.
2. In the repo: Settings → Pages → Deploy from branch → `main` → `/docs`.
3. The `docs/CNAME` makes the apex domain `hackinghat.com` work once DNS
   (Route53) points at GitHub Pages — that's configured separately, not here.
