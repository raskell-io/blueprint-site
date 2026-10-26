#!/usr/bin/env python3
"""Write static/.well-known/security.txt (RFC 9116) with an Expires date one year out, so it never goes stale."""
import datetime
import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
config = tomllib.loads((ROOT / "config.toml").read_text())
base = config["base_url"].rstrip("/")
contact = config["extra"].get("security_contact", "mailto:security@example.org")
expires = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
out = ROOT / "static/.well-known/security.txt"
out.write_text(f"Contact: {contact}\nExpires: {expires}\nPreferred-Languages: en\nCanonical: {base}/.well-known/security.txt\n")
print(f"security.txt: expires {expires}")
