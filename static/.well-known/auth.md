# Authentication

Nothing on this site needs authentication. Every page, its Markdown copy (`<url>.md`), `/llms.txt`,
`/llms-full.txt` and `/atom.xml` is public and read-only. A 401 or 403 from this site is a fault, not a policy.

The only endpoint that accepts input is `POST /api/feedback`, which files a reader's message as a GitHub issue.
