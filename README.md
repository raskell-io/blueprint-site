# blueprint-site

A static website with no server to patch: Zola renders it when a change is merged, Cloudflare Pages serves the
files, and a single small Worker handles the one thing a file cannot. It is the site half of a blueprint; the app half
(Svelte, a service worker, Rust compiled to WebAssembly) is [blueprint-app](https://github.com/raskell-io/blueprint-app).

What you get out of the box:

- **An ontology.** `data/kinds.toml` declares every kind of content, its register, its required fields and its
  schema.org type. `scripts/check_content.py` enforces it on every pull request; typos and unknown topics fail.
- **Agent context first.** `AGENTS.md` (the contract), `CLAUDE.md`, `.claude/rules/` and a skill for adding content.
- **Pinned tools.** Zola, Python and Node are pinned in `mise.toml`; CI and the Cloudflare build use the same pins.
- **A strict CSP.** No inline scripts, no inline styles, no third-party requests (`static/_headers`).
- **Legible to machines.** `llms.txt`, `llms-full.txt`, a Markdown copy of every page at `<url>.md`, JSON-LD typed
  by the ontology, `robots.txt` with Content-Signal, `security.txt` (rolling expiry), an RFC 9727 API catalog and
  an `auth.md` that says nothing needs auth.
- **GitHub as the moderation layer.** CODEOWNERS, a content issue form, a pull-request checklist, and reader feedback
  that arrives as a GitHub issue through the Worker.
- **Accessible by default.** One `h1`, a skip link, visible focus, a form that works without JavaScript, light and dark.

## Run it

```sh
mise install          # zola, python, node at the pinned versions
mise run check        # the ontology holds, then zola check
mise run dev          # http://127.0.0.1:1111
mise run build        # public/, ready for any static host
mise run worker-test  # the feedback Worker, against a stubbed GitHub
```

## The repositories

The blueprint ships as one repository so that it runs on a fresh clone. In production it splits into an organisation
of small repositories, each with one job:

```
your-org/                 a GitHub organisation, not a personal account
├── .github               org profile, shared issue forms, SECURITY.md
├── .claude               org-wide agent context: rules, skills, decisions
├── theme                 the Zola theme         -> submodule at site/themes/blueprint
├── content               Markdown + data        -> submodule at site/content (and site/data)
├── site                  this repo: config, build, headers  -> Cloudflare Pages
└── worker                edge logic (or worker/ in the site repo)  -> Cloudflare Workers
```

To split the theme and content out of this repo once you have created the empty repositories:

```sh
git subtree split --prefix=themes/blueprint -b theme && git push git@github.com:your-org/theme.git theme:main
git subtree split --prefix=content -b content && git push git@github.com:your-org/content.git content:main
git rm -r themes/blueprint content && git commit -m "Theme and content move to their own repos"
git submodule add https://github.com/your-org/theme.git themes/blueprint
git submodule add https://github.com/your-org/content.git content
```

Use HTTPS URLs for submodules: the Cloudflare Pages build clones them without your SSH keys. Copy
`.github/content-repo-rebuild.yml` into the content repo so a merged content change rebuilds the site.

## Deploy

1. **Cloudflare Pages:** Workers & Pages > Create > Pages > Connect to Git, pick the site repo.
   Build command `bash scripts/cf-pages-build.sh`, output directory `public`. Every pull request gets a preview URL.
2. **Domain:** add the custom domain in the Pages project; Cloudflare creates the DNS record.
3. **Deploy hook:** Pages project > Settings > Builds > Deploy hooks. Store the URL as `CF_PAGES_DEPLOY_HOOK` in the
   content repo's Actions secrets.
4. **Worker:** in `worker/`, edit `wrangler.jsonc` (route, origin, repository), then
   `npx wrangler secret put GITHUB_TOKEN` (a fine-grained token: Issues read and write, on the content repo only) and
   `npx wrangler deploy`.
5. Replace `example.org`, `your-org` and `Your Name` everywhere (`grep -rn "example.org\|your-org\|Your Name"`).

## Licence

MIT. Copy it, change it, ship it.
