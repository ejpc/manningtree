#!/usr/bin/env python3
"""
Move a paid-for site out of the shared demo repo and into its own.

The demo repo holds every site in a subfolder, which is right for handing
out free previews - but a GitHub Pages site can carry only ONE custom
domain. Point a customer's domain at the shared repo and it would serve
every other business's site too, on their address. So a customer who pays
gets their own repo, with their site at the root.

Usage:
    python3 release.py rileys rileysmanningtree.co.uk
    python3 release.py rileys rileysmanningtree.co.uk --push

Without --push it prepares everything locally and prints the remaining
steps. With --push it also creates the GitHub repo and pushes (needs `gh`).
"""
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
OLD_HOST = "ejpc.github.io/manningtree"
GITHUB_PAGES_IPS = ["185.199.108.153", "185.199.109.153",
                    "185.199.110.153", "185.199.111.153"]

# Everything a standalone site needs. Anything not listed is deliberately
# left behind: build.py, the other businesses, and the prospect research.
WANTED = ["index.html", "menu.html", "services.html", "qr-card.html",
          "favicon.svg", "apple-touch-icon.png", "social-card.png",
          "qr-code.png", "qr-code.svg", "sitemap.xml", "robots.txt"]
WANTED_DIRS = ["photos", "art"]


def die(msg):
    sys.exit("error: " + msg)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    push = "--push" in sys.argv
    if len(args) != 2:
        sys.exit(__doc__)

    slug, domain = args[0].strip("/"), args[1].strip().lower()
    domain = re.sub(r"^https?://", "", domain).rstrip("/")
    if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", domain):
        die(f"that does not look like a domain: {domain!r}")

    src = HERE / slug
    if not (src / "index.html").exists():
        die(f"no site at {src}")

    out = HERE.parent / f"{slug}-live"
    if out.exists():
        die(f"{out} already exists - delete it or pick another slug")

    # ---- copy the site to the ROOT of the new repo ----
    out.mkdir()
    copied = []
    for name in WANTED:
        f = src / name
        if f.exists():
            shutil.copy2(f, out / name)
            copied.append(name)
    for d in WANTED_DIRS:
        if (src / d).is_dir():
            shutil.copytree(src / d, out / d)
            copied.append(d + "/")

    # ---- rewrite every address to the customer's own domain ----
    old = f"{OLD_HOST}/{slug}"
    changed = 0
    for f in out.rglob("*"):
        if f.suffix.lower() not in (".html", ".xml", ".txt", ".py"):
            continue
        text = f.read_text(encoding="utf-8")
        n = text.count(old)
        if n:
            f.write_text(text.replace(old, domain), encoding="utf-8")
            changed += n

    # a stray old address would tell Google the real page lives somewhere dead
    leftover = [f.name for f in out.rglob("*")
                if f.suffix.lower() in (".html", ".xml", ".txt")
                and OLD_HOST in f.read_text(encoding="utf-8")]
    if leftover:
        die(f"old address still present in: {', '.join(leftover)}")

    (out / "CNAME").write_text(domain + "\n", encoding="utf-8")

    # ---- the QR code must point at the new address, not the demo one ----
    qr_note = "no QR regenerated (segno not installed)"
    try:
        import segno
        qr = segno.make(f"https://{domain}/", error="h")
        dark = "#171514"
        m = re.search(r'name="theme-color" content="(#[0-9a-fA-F]{6})"',
                      (out / "index.html").read_text(encoding="utf-8"))
        if m:
            dark = m.group(1)
        for ext in ("png", "svg"):
            qr.save(out / f"qr-code.{ext}", scale=12, border=4,
                    dark=dark, light="#ffffff")
        qr_note = f"QR regenerated for https://{domain}/ (version {qr.version}-H)"
    except ImportError:
        pass

    # ---- a fresh set-domain.py, in case they ever move again ----
    sd = src / "set-domain.py"
    if sd.exists():
        (out / "set-domain.py").write_text(
            sd.read_text(encoding="utf-8").replace(old, domain), encoding="utf-8")

    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=out, check=True)

    # a fresh repo inherits no identity, so carry over whatever the demo repo uses
    for key in ("user.name", "user.email"):
        who = subprocess.run(["git", "config", key], cwd=HERE,
                             capture_output=True, text=True).stdout.strip()
        if not who:
            who = subprocess.run(["git", "config", "--global", key],
                                 capture_output=True, text=True).stdout.strip()
        if who:
            subprocess.run(["git", "config", key, who], cwd=out, check=True)

    subprocess.run(["git", "add", "-A"], cwd=out, check=True)
    subprocess.run(["git", "commit", "-q", "-m",
                    f"{slug} website, live on {domain}"], cwd=out, check=True)

    print(f"\nPrepared {out}")
    print(f"  copied      {', '.join(copied)}")
    print(f"  rewrote     {changed} addresses -> {domain}")
    print(f"  CNAME       {domain}")
    print(f"  {qr_note}")

    repo = f"{slug}-site"
    if push:
        subprocess.run(["gh", "repo", "create", repo, "--public",
                        "--source", str(out), "--push"], cwd=out, check=True)
        print(f"\n  pushed to GitHub as {repo}")

    print(f"""
NEXT, IN THIS ORDER - DNS first, GitHub second.

 1. At the customer's domain registrar, add these records for {domain}:
       A     @     {GITHUB_PAGES_IPS[0]}
       A     @     {GITHUB_PAGES_IPS[1]}
       A     @     {GITHUB_PAGES_IPS[2]}
       A     @     {GITHUB_PAGES_IPS[3]}
       CNAME www   ejpc.github.io
    (check GitHub's current docs - these IPs change occasionally)

 2. Wait for DNS to spread. Usually minutes, sometimes a few hours.
    Check with:  dig +short {domain}
""" + ("" if push else f""" 3. Create the repo and push:
       cd {out}
       gh repo create {repo} --public --source=. --push
""") + f"""
 {'3' if push else '4'}. In that repo: Settings > Pages > Custom domain -> {domain}
    Wait for the green tick, then tick "Enforce HTTPS".
    The certificate can take a few hours.

 {'4' if push else '5'}. Check https://{domain}/ serves the site, then reprint the QR
    code - qr-code.svg is the one for anything printed.

The demo at https://{OLD_HOST}/{slug}/ keeps working. Leave it up until
the real address is confirmed, then it can go.
""")


if __name__ == "__main__":
    main()
