"""Recopie l'icône d'onglet du site officiel (www.greype-france.com) dans assets/.

Le site officiel est sur Framer : l'URL de son icône change à chaque nouvelle
version, et sa page n'autorise pas la lecture depuis un autre domaine (pas de
CORS). On ne peut donc ni pointer dessus en dur ni la lire au chargement de la
page : ce script relit le site et recopie l'icône si elle a changé.

Lancé chaque jour par .github/workflows/sync-favicon.yml (et à la main).
Ne modifie rien si l'icône est identique ou si le site ne répond pas.
"""
import io
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image

SITE = "https://www.greype-france.com/"
ASSETS = Path(__file__).resolve().parents[2] / "assets"
UA = {"User-Agent": "annuaire-greype-favicon-sync"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def main():
    html = get(SITE).decode("utf-8", "replace")
    links = re.findall(r'<link[^>]*rel="(?:shortcut )?icon"[^>]*>', html)
    hrefs = [re.search(r'href="([^"]+)"', l).group(1) for l in links if 'href="' in l]
    # Préférer la variante thème clair si le site en déclare plusieurs.
    light = [h for h, l in zip(hrefs, links) if "prefers-color-scheme: light" in l]
    if not hrefs:
        print("Aucune icône trouvée sur le site, rien à faire.")
        return 0
    url = urllib.request.urljoin(SITE, (light or hrefs)[0])
    icon = Image.open(io.BytesIO(get(url))).convert("RGBA")

    targets = {"favicon.png": 64, "apple-touch-icon.png": 180}
    changed = False
    for name, size in targets.items():
        buf = io.BytesIO()
        icon.resize((size, size), Image.LANCZOS).save(buf, "PNG", optimize=True)
        path = ASSETS / name
        if not path.exists() or path.read_bytes() != buf.getvalue():
            path.write_bytes(buf.getvalue())
            changed = True
            print(f"{name} mis à jour depuis {url}")
    if not changed:
        print("Icône inchangée.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
