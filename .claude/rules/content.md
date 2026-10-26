# Content rules

Applies when writing or editing anything in `content/` or `data/`.

- Every page is one kind from `data/kinds.toml`. Fill the required fields; the validator rejects missing ones.
- `description` is one or two concrete sentences, under 160 characters. It becomes the meta description, the
  social card text, and the line in llms.txt, so it has to stand on its own.
- Topics come from `data/topics.toml` only. Use the most specific two to five that apply. Add a topic there first
  when one is missing, with a one-sentence description.
- Link related pages in the text with `@/` paths (`[the note](@/notes/first-note.md)`); Zola checks them at build
  time, so a broken internal link fails the build instead of reaching readers.
- Images: AVIF in `static/images/`, with alt text that says what the image shows.
- Facts about the outside world (dates, versions, numbers) come from a source you checked, and the source goes
  into the page under a `## References` heading.
- New pages start with `draft = true`. Remove the line to publish; do not set it to false.
