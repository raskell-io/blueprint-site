+++
title = "Why This Site Is Static"
date = 2026-10-26
description = "Rendering at commit time removes the runtime an attacker needs. What is left is files, a CDN, and one small Worker."

[taxonomies]
topics = ["static-sites", "security", "edge"]
+++

Most websites run code for every request: an interpreter reads a template, asks a database, and assembles a page
that is almost always the same page it assembled a second ago. Every one of those requests is a chance for a bug in
that code, or in the interpreter beneath it, to run something it should not.

This site does the assembling once, when a change is merged. What reaches the CDN is files. A request for a page
reads a file; it cannot reach a template engine, a database, or a language runtime, because none of them are
running.

## What is left

Three things still run:

- **The CDN**, which serves files and applies the headers in `static/_headers`.
- **The build**, on every merge to `main`, in a throwaway container.
- **One Worker**, which accepts reader feedback and files it as a GitHub issue. It holds one secret, a token that can
  open issues in one repository, and nothing else.

That is the whole attack surface. The [first note](@/notes/a-page-is-a-file.md) has the short version.
