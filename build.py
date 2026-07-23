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
import unicodedata

ROOT = pathlib.Path(__file__).parent
TEAM = ROOT / "team.json"
PAGE = ROOT / "index.html"
VCF = ROOT / "vcf"

START = "<!-- TEAM:START -->"
END = "<!-- TEAM:END -->"

ORG = "GREYPE FRANCE"
STANDARD = "+33468819725"
SITE = "https://adorex5278.github.io/annuaire-greype/index.html"


def initials(name):
    return "".join(w[0] for w in re.split(r"[ -]", name) if w)[:3]


# --------------------------------------------------------------------
# vCard 3.0
# --------------------------------------------------------------------

def slug(name):
    """Nom de fichier sûr : accents retirés, minuscules, tirets."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s


def split_name(full):
    """'Vanessa SAINT-DENIS' -> ('SAINT-DENIS', 'Vanessa').

    Les tokens entièrement en majuscules sont le nom de famille.
    """
    tokens = full.split()
    last = [t for t in tokens if t == t.upper() and any(c.isalpha() for c in t)]
    first = [t for t in tokens if t not in last]
    if not last or not first:  # convention non respectée : on ne devine pas
        return full, ""
    return " ".join(last), " ".join(first)


def esc(value):
    """Échappement vCard : backslash, virgule, point-virgule, saut de ligne."""
    return (value.replace("\\", "\\\\")
                 .replace(";", "\\;")
                 .replace(",", "\\,")
                 .replace("\n", "\\n"))


def fold(line):
    """Repli à 75 octets, continuation préfixée d'une espace (RFC 2426).

    Le découpage se fait sur les octets UTF-8 sans couper un caractère,
    sinon les prénoms accentués ressortent cassés sur certains téléphones.
    """
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    out, buf, size = [], [], 0
    limit = 75
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            out.append("".join(buf))
            buf, size, limit = [ch], n, 74  # +1 pour l'espace de continuation
        else:
            buf.append(ch)
            size += n
    out.append("".join(buf))
    return "\r\n ".join(out)


def vcard(m):
    last, first = split_name(m["name"])
    phone = "+" + m["phone"]
    is_landline = phone == STANDARD

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{esc(last)};{esc(first)};;;",
        f"FN:{esc(m['name'])}",
        f"ORG:{esc(ORG)}",
        f"TITLE:{esc(m['role'])}",
    ]
    # Vanessa partage le numéro du standard : une seule entrée, pas de CELL.
    #
    # L'étiquette explicite passe par le groupement item1./X-ABLabel : c'est la
    # convention Apple, honorée par iOS et macOS. Les autres plateformes
    # ignorent le X-ABLabel et retombent sur TYPE=WORK,VOICE, ce qui reste
    # correct pour un fixe (l'absence de CELL suffit à le distinguer).
    if is_landline:
        lines.append(f"item1.TEL;TYPE=WORK,VOICE:{phone}")
        lines.append("item1.X-ABLabel:Standard (fixe)")
    else:
        lines.append(f"TEL;TYPE=CELL,VOICE,PREF:{phone}")
        lines.append(f"item1.TEL;TYPE=WORK,VOICE:{STANDARD}")
        lines.append("item1.X-ABLabel:Standard (fixe)")

    lines.append(f"URL:{SITE}")
    if m.get("linkedin"):
        lines.append(f"X-SOCIALPROFILE;TYPE=linkedin:{m['linkedin']}")
    lines.append("END:VCARD")

    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def write_vcards(team):
    VCF.mkdir(exist_ok=True)
    for old in VCF.glob("*.vcf"):
        old.unlink()

    for m in team:
        m["slug"] = slug(m["name"])
        (VCF / f"{m['slug']}.vcf").write_bytes(vcard(m).encode("utf-8"))

    combined = "".join(vcard(m) for m in team)
    (VCF / "greype-france.vcf").write_bytes(combined.encode("utf-8"))
    print(f"OK : {len(team)} vCard + 1 fichier complet dans vcf/")


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

    slg = e(m["slug"])
    actions.append(
        f'<a class="btn vcard" href="vcf/{slg}.vcf" download '
        f'title="Ajouter {name} aux contacts" '
        f'aria-label="Télécharger la fiche contact de {name}">💾</a>'
    )

    acts = "\n          ".join(actions)
    return f"""      <div class="card">
        <div class="card-top"></div>
        <div class="card-content">
          <label class="pick">
            <input type="checkbox" class="pick-box" value="{slg}" data-name="{name}">
            <span class="pick-label">Sélectionner {name}</span>
          </label>
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

    write_vcards(team)

    slugs = [m["slug"] for m in team]
    if len(set(slugs)) != len(slugs):
        sys.exit("ERREUR : deux personnes produisent le même nom de fichier vCard")

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
