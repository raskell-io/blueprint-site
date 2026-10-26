---
name: add-content
description: Add or change an article, note, project, or topic on this site end to end, from the register through validation to a visual check. Use whenever content is added, renamed, retagged, or published.
---

# Add content

1. **Pick the kind.** Read `data/kinds.toml`. If the content fits no kind, stop and propose a new kind to the user
   instead of bending an existing one.
2. **Register it once.** Articles and notes are `content/<section>/<slug>.md`; projects are
   entries in `data/projects.toml`; topics are entries in `data/topics.toml`. The slug is the file name, lowercase, with
   hyphens.
3. **Fill the required fields** listed for the kind. Topics must already exist in `data/topics.toml`.
4. **Link it.** Add `@/` links from and to related pages, so the new page is not an orphan.
5. **Validate:** `mise run check`. Fix every error it reports; do not loosen the validator to make it pass.
6. **Build and look:** `mise run build`, then open the page with `mise run dev`. Check its JSON-LD in the page
   source, its entry in `/llms.txt`, and its Markdown copy at `/<path>.md`.
7. **Report** what was added, where it shows up, and what you checked. Do not commit unless asked.
