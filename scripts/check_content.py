#!/usr/bin/env python3
"""Enforce the ontology in data/kinds.toml on every page and data entry. Standard library only (Python 3.11+).

Checks: required fields present, no unknown fields (typos fail loudly), enum values allowed, description length,
topic count, every topic defined in data/topics.toml, `broader` topics defined, slugs that match file names.
Exits 1 with one line per problem, so CI and agents can act on the output.
"""
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
kinds = tomllib.loads((ROOT / "data/kinds.toml").read_text())
rules = kinds["rules"]
topics = tomllib.loads((ROOT / "data/topics.toml").read_text())
problems = []


def flat(d, prefix=""):
    """{'a': {'b': 1}} -> {'a.b': 1}, so dotted names in kinds.toml match nested front matter."""
    out = {}
    for k, v in d.items():
        key = prefix + k
        if isinstance(v, dict) and key in ("taxonomies", "extra"):
            out.update(flat(v, key + "."))
        else:
            out[key] = v
    return out


def check(where, kind_name, fields, topic_list):
    spec = kinds["kinds"][kind_name]
    allowed = set(spec["required"]) | set(spec.get("optional", []))
    for f in spec["required"]:
        if f not in fields:
            problems.append(f"{where}: missing required field `{f}` for a {kind_name}")
    for f in fields:
        if f not in allowed and not f.startswith("extra."):
            problems.append(f"{where}: unknown field `{f}` (a {kind_name} has {', '.join(sorted(allowed))})")
    for f, values in spec.get("enum", {}).items():
        if f in fields and fields[f] not in values:
            problems.append(f"{where}: `{f}` is {fields[f]!r}, expected one of {values}")
    desc = fields.get("description", "")
    if len(desc) > rules["description_max"]:
        problems.append(f"{where}: description is {len(desc)} characters, the limit is {rules['description_max']}")
    if topic_list is not None:
        if not rules["topics_min"] <= len(topic_list) <= rules["topics_max"]:
            problems.append(f"{where}: {len(topic_list)} topics, expected {rules['topics_min']} to {rules['topics_max']}")
        for t in topic_list:
            if t not in topics:
                problems.append(f"{where}: topic `{t}` is not defined in data/topics.toml")


# Pages: every kind whose register is a content section.
for name, spec in kinds["kinds"].items():
    reg = spec["register"]
    if not reg.startswith("content/"):
        continue
    for md in sorted((ROOT / reg).glob("*.md")):
        if md.name.startswith("_index"):
            continue
        rel = md.relative_to(ROOT)
        m = re.match(r"\+\+\+\n(.*?)\n\+\+\+", md.read_text(), re.S)
        if not m:
            problems.append(f"{rel}: no TOML front matter")
            continue
        try:
            fm = tomllib.loads(m.group(1))
        except tomllib.TOMLDecodeError as err:
            problems.append(f"{rel}: front matter is not valid TOML ({err})")
            continue
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", md.stem):
            problems.append(f"{rel}: file name must be a lowercase slug with hyphens")
        check(rel, name, flat(fm), fm.get("taxonomies", {}).get("topics", []))

# Projects: entries in data/projects.toml.
for i, p in enumerate(tomllib.loads((ROOT / "data/projects.toml").read_text()).get("projects", [])):
    check(f"data/projects.toml [[projects]] #{i + 1} ({p.get('slug', '?')})", "project", p, p.get("topics", []))

# Topics: the vocabulary itself.
for slug, t in topics.items():
    check(f"data/topics.toml [{slug}]", "topic", t, None)
    for b in t.get("broader", []):
        if b not in topics:
            problems.append(f"data/topics.toml [{slug}]: broader topic `{b}` is not defined")

for p in problems:
    print(p)
print(f"check_content: {len(problems)} problem(s)" if problems else "check_content: ontology holds")
sys.exit(1 if problems else 0)
