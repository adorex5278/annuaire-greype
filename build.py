#!/usr/bin/env python3
"""
Régénère les cartes de l'équipe dans index.html à partir de team.json.

    python3 build.py

Le script remplace tout ce qui se trouve entre les marqueurs
<!-- TEAM:START --> et <!-- TEAM:END --> dans index.html.
Ne rien écrire à la main entre ces deux lignes : ce sera écrasé.

Pour modifier l'équipe : éditer team.json, relancer le script, committer
team.json ET index.html.
"""

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
TEAM = ROOT / "team.json"
PAGE = ROOT / "index.html"

START = "<!-- TEAM:START -->"
END = "<!-- TEAM:END -->"


def initials(name):
    return "".join(w[0] for w in re.split(r"[ -]", name) if w)[:3]


def card(m):
    e = html.escape
    name = e(m["name"])
    phone = e(m["phone"])
    actions = []

    if m.get("whatsapp"):
        actions.append(
            f'<a class="btn whatsapp" href="https://wa.me/{phone}" target="_blank" '
            f'rel="noopener noreferrer" title="WhatsApp {name}" aria-label="WhatsApp {name}">'
            f'<svg class="ico"><use href="#ico-wa"></use></svg></a>'
        )
    if m.get("sms"):
        actions.append(
            f'<a class="btn sms" href="sms:+{phone}" title="SMS {name}" '
            f'aria-label="Envoyer un SMS à {name}">💬</a>'
        )
    if m.get("linkedin"):
        actions.append(
            f'<a class="btn linkedin" href="{e(m["linkedin"])}" target="_blank" '
            f'rel="noopener noreferrer" title="LinkedIn {name}" aria-label="LinkedIn {name}">'
            f'<svg class="ico"><use href="#ico-li"></use></svg></a>'
        )
    if m.get("pappers"):
        actions.append(
            f'<a class="btn pappers" href="{e(m["pappers"])}" target="_blank" '
            f'rel="noopener noreferrer" title="Fiche Pappers {name}" '
            f'aria-label="Fiche Pappers {name}">📄</a>'
        )

    acts = "\n          ".join(actions)
    return f"""      <div class="card">
        <div class="card-top"></div>
        <div class="card-content">
          <div class="avatar" aria-hidden="true">{e(initials(m["name"]))}</div>
          <div class="name">{name}</div>
          <div class="role">{e(m["role"])}</div>
          <a class="phone" href="tel:+{phone}">📞 {e(m["display"])}</a>
          <div class="actions">
          {acts}
          </div>
        </div>
      </div>"""


def main():
    team = json.loads(TEAM.read_text(encoding="utf-8"))

    # Garde-fous : une coquille ici se retrouve sur une page publique.
    seen = set()
    for m in team:
        for key in ("name", "role", "phone", "display"):
            if not m.get(key):
                sys.exit(f"ERREUR : champ '{key}' manquant pour {m.get('name', '?')}")
        if not m["phone"].isdigit():
            sys.exit(f"ERREUR : téléphone non numérique pour {m['name']} ({m['phone']})")
        if m["phone"].replace(" ", "") != m["display"].replace(" ", "").lstrip("+"):
            sys.exit(f"ERREUR : 'phone' et 'display' divergent pour {m['name']}")
        if m["phone"] in seen:
            print(f"  attention : numéro en double -> {m['name']} ({m['display']})")
        seen.add(m["phone"])

    page = PAGE.read_text(encoding="utf-8")
    if START not in page or END not in page:
        sys.exit(f"ERREUR : marqueurs {START} / {END} introuvables dans index.html")

    cards = "\n".join(card(m) for m in team)
    page = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        f"{START}\n{cards}\n      {END}",
        page,
        flags=re.S,
    )
    PAGE.write_text(page, encoding="utf-8")
    print(f"OK : {len(team)} cartes régénérées dans index.html")


if __name__ == "__main__":
    main()
