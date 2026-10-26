#!/usr/bin/env python3
"""Write the machine-readable copies of the site before `zola build` (standard library only, Python 3.11+).

- static/llms.txt: the site in one Markdown index (llmstxt.org): what it is, then every page and project, one line each.
- static/llms-full.txt: the same, with every page's full Markdown body.
- static/<path>.md: a Markdown copy of every page, next to its HTML URL (/articles/x/ -> /articles/x.md).

All three are gitignored: they are generated from content/ and data/ on every build, never edited.
"""
import pathlib
import re
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
config = tomllib.loads((ROOT / "config.toml").read_text())
kinds = tomllib.loads((ROOT / "data/kinds.toml").read_text())["kinds"]
base = config["base_url"].rstrip("/")
static = ROOT / "static"


def pages(register):
    for md in sorted((ROOT / register).glob("*.md"), reverse=True):
        if md.name.startswith("_index"):
            continue
        m = re.match(r"\+\+\+\n(.*?)\n\+\+\+\n?(.*)", md.read_text(), re.S)
        fm, body = tomllib.loads(m.group(1)), m.group(2).strip()
        if fm.get("draft"):
            continue
        path = register.removeprefix("content/") + md.stem   # articles/why-this-site-is-static
        yield fm, body, path


index = [f"# {config['title']}", "", f"> {config['description']}", "",
         "Every page has a Markdown copy at its URL with `.md` instead of the trailing slash.", ""]
full = list(index)
for name, spec in kinds.items():
    if not spec["register"].startswith("content/"):
        continue
    section = spec["register"].removeprefix("content/").strip("/").capitalize()
    index += [f"## {section}", ""]
    for fm, body, path in pages(spec["register"]):
        url = f"{base}/{path}.md"
        index.append(f"- [{fm['title']}]({url}): {fm['description']}")
        full += [f"## {fm['title']}", "", f"Source: {base}/{path}/", "", body, ""]
        copy = static / f"{path}.md"
        copy.parent.mkdir(parents=True, exist_ok=True)
        meta = f"---\ntitle: {fm['title']}\ndate: {fm['date']}\nurl: {base}/{path}/\ndescription: {fm['description']}\n---\n\n"
        copy.write_text(meta + f"# {fm['title']}\n\n" + body + "\n")
    index.append("")

index += ["## Projects", ""]
for p in tomllib.loads((ROOT / "data/projects.toml").read_text()).get("projects", []):
    index.append(f"- [{p['title']}]({p['url']}): {p['description']}")
index += ["", "## For agents", "", f"- [Atom feed]({base}/atom.xml)", f"- [Full text]({base}/llms-full.txt)",
          f"- [API catalog]({base}/.well-known/api-catalog)", f"- [Authentication: none]({base}/.well-known/auth.md)", ""]

(static / "llms.txt").write_text("\n".join(index))
(static / "llms-full.txt").write_text("\n".join(full))
print(f"llms: {sum(1 for l in index if l.startswith('- ['))} entries")
