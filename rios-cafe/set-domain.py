#!/usr/bin/env python3
"""
Point the whole site at a different web address, in one command.

The SEO tags (canonical, Open Graph, sitemap, structured data) have to contain
the FULL address of the site. That means if the address changes, they all have
to change together - and a canonical tag left pointing at a dead address is
worse than having none, because it tells Google the real page lives somewhere
that no longer exists.

Usage:
    python3 set-domain.py rioscafe.co.uk

Then check nothing was missed:
    grep -r "clonal.health" .
"""
import pathlib
import re
import sys

CURRENT = "rioscafe.clonal.health"
FILES = ["index.html", "menu.html", "sitemap.xml", "robots.txt"]

if len(sys.argv) != 2:
    sys.exit(__doc__)

new = sys.argv[1].strip().lower()
new = re.sub(r"^https?://", "", new).rstrip("/")

if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", new):
    sys.exit(f"That does not look like a domain: {new!r}")

here = pathlib.Path(__file__).parent
total = 0

for name in FILES:
    path = here / name
    if not path.exists():
        print(f"  skipped {name} (not found)")
        continue
    text = path.read_text(encoding="utf-8")
    count = text.count(CURRENT)
    if count:
        path.write_text(text.replace(CURRENT, new), encoding="utf-8")
        total += count
    print(f"  {name}: {count} changed")

print(f"\n{total} addresses updated: {CURRENT} -> {new}")
print(f"""
Still to do by hand:
  1. Edit CURRENT at the top of this script to "{new}", so the next move works.
  2. Regenerate qr-code.png / qr-code.svg for https://{new}
  3. GitHub > Settings > Pages > Custom domain -> {new}
  4. Add the DNS record for {new} BEFORE step 3.
  5. Only once the new address works: remove the old custom domain,
     then delete the old DNS record. Pointer first, house second.
""")
