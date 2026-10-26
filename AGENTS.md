# AGENTS.md

This repository is a static website: Zola renders it at commit time, Cloudflare Pages serves the files, and one
small Worker handles the only thing a file cannot (reader feedback). There is no server, no database, and no
runtime to patch. This file is the contract for working on it, for agents (Claude Code, Codex, Cursor) and people.

The short version: **every kind of content is declared in `data/kinds.toml` and registered once, in one source
file. Everything else (pages, feeds, JSON-LD, llms.txt, Markdown copies, the sitemap) is generated.** If something
does not show up where it should, fix the source or the generator, never the output.

## Stack

| Layer | What | Where |
|---|---|---|
| Static site generator | Zola, pinned in `mise.toml` (never a bare `zola`, it may be another version) | `config.toml` |
| Theme | `themes/blueprint`, meant to live in its own repo as a git submodule | `themes/blueprint/` |
| Content | Markdown with TOML front matter, meant to live in its own repo as a submodule | `content/` |
| Data | TOML registers: the ontology, topics, projects | `data/` |
| Hosting | Cloudflare Pages, built from `main` by the GitHub integration | `static/_headers`, `static/_redirects` |
| Edge logic | One Worker: reader feedback becomes a GitHub issue | `worker/` |
| Tooling | mise for tools and tasks; validators use only the Python standard library | `mise.toml`, `scripts/` |

## The ontology

`data/kinds.toml` declares every kind of resource the site knows: where it is registered, which fields it must
have, which values a field may take, and what it becomes for machines (its JSON-LD type). `scripts/check_content.py`
enforces it, and CI runs it on every pull request. A new kind of content starts with a new entry there, not with a
new folder.

Current kinds: **article** (`content/articles/`), **note** (`content/notes/`), **project** (`data/projects.toml`),
**topic** (`data/topics.toml`).

## Registers and sinks

| Kind | Register | Reaches |
|---|---|---|
| Article | `content/articles/<slug>.md` | its page, the articles list, the feed, JSON-LD BlogPosting, llms.txt, `/<path>.md` |
| Note | `content/notes/<slug>.md` | its page, the notes list, the feed, JSON-LD Article, llms.txt, `/<path>.md` |
| Project | an entry in `data/projects.toml` | the projects page, JSON-LD SoftwareApplication, llms.txt |
| Topic | `data/topics.toml` | the topic pages, every page's keywords, llms.txt |

## Recipes

- **New article or note:** create `content/<section>/<slug>.md` with `title`, `date`, `description` (under 160
  characters) and `[taxonomies] topics = [...]` from `data/topics.toml`. Start with `draft = true`. Run `mise run check`.
- **New topic:** add it to `data/topics.toml` first (name, description), then use it.
- **New project:** add a `[[projects]]` entry to `data/projects.toml` with the fields `data/kinds.toml` requires.
- **New kind:** declare it in `data/kinds.toml`, teach `scripts/check_content.py` and `scripts/llms.py` about it, add
  its templates and JSON-LD, and update the tables above.

## Verify before reporting done

```sh
mise run check      # ontology, front matter, topics, then zola check
mise run build      # llms.txt and Markdown copies, then zola build into public/
mise run dev        # http://127.0.0.1:1111
```

Then look at the result: the page, its JSON-LD, its line in `/llms.txt`, its `.md` copy.

## Rules that hold

- No external requests from pages: no CDN scripts, no web fonts from third parties, no analytics. The CSP in
  `static/_headers` forbids them and inline scripts; keep it that way.
- No secrets in the repository or the client. The Worker's token lives in Cloudflare (`wrangler secret put`).
- Generated files are gitignored (`static/llms*.txt`, `static/**/*.md` copies, `public/`). Never edit them.
- Theme changes go to the theme repo first, then the submodule is bumped here.
- Commit and push only when asked.
