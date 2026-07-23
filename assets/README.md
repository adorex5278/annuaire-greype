# assets/

Copies locales servant de **repli** si la ressource distante ne répond pas.
Le mécanisme est dans `index.html` : fonction `fallbackImg()` + attributs
`data-fallbacks` (chaîne essayée dans l'ordre).

## Logo de la page

| Ordre | Fichier | Rôle |
|---|---|---|
| 1 | `public.saintcharlesinternational.com/.../greype.jpg` | source, mise à jour via INPI |
| 2 | `assets/logo.jpg` | copie exacte du logo réel (300x150) |
| 3 | `assets/logo-fallback.svg` | wordmark généré, dernier recours |

## Favicon

| Ordre | Fichier |
|---|---|
| 1 | logo distant |
| 2 | `assets/favicon.png` (64x64) / `assets/apple-touch-icon.png` (180x180) |

Ces deux PNG sont un **recadrage sur la pastille verte** du logo : c'est ce qui
reste lisible à 16 px dans un onglet. `assets/favicon-wordmark.png` contient la
variante avec le logo entier si on la préfère — il suffit de changer le
`data-fallback` du `<link rel="icon">`.

`assets/favicon-fallback.svg` (monogramme G) n'est plus branché, conservé au cas où.

## Icônes des fiches financières

| Ordre | Fichier |
|---|---|
| 1 | `google.com/s2/favicons?domain=...` |
| 2 | `assets/icons/<site>.png` — vraie favicon du site |
| 3 | `assets/icons/<site>.svg` — pastille générée |

Sites : `societe`, `pappers`, `infogreffe`, `annuaire`, `inpi`, `agencebio`.

## Après un changement de logo

Le logo de la page se met à jour tout seul (source distante). Il reste à
régénérer les copies locales :

```bash
cp nouveau-logo.jpg assets/logo.jpg
convert assets/logo.jpg -crop 144x144+3+3 +repage -resize 64x64   assets/favicon.png
convert assets/logo.jpg -crop 144x144+3+3 +repage -resize 180x180 assets/apple-touch-icon.png
```

---

# Modifier l'équipe

Les cartes de `index.html` sont **générées**. Ne pas les éditer à la main :
tout ce qui se trouve entre `<!-- TEAM:START -->` et `<!-- TEAM:END -->`
est écrasé au prochain build.

```bash
# 1. éditer la liste
nano team.json
# 2. régénérer
python3 build.py
# 3. committer les deux fichiers
git add team.json index.html && git commit -m "MAJ equipe" && git push
```

Champs d'une entrée : `name`, `role`, `phone` (chiffres uniquement, indicatif
pays compris, sans `+`), `display` (version lisible), puis au choix
`whatsapp`, `sms` (booléens), `linkedin`, `pappers` (URL).

`build.py` refuse de générer si un champ obligatoire manque, si `phone`
contient autre chose que des chiffres, ou si `phone` et `display` ne
correspondent pas — de quoi éviter qu'un numéro erroné parte en ligne.

---

# Fiches contact (vCard)

`build.py` génère `vcf/` en même temps que les cartes :

- `vcf/<prenom>-<nom>.vcf` — une fiche par personne, bouton 💾 sur sa carte
- `vcf/greype-france-standard.vcf` — le standard, en tant que société
  (`X-ABShowAs:COMPANY`), avec les horaires en NOTE
- `vcf/greype-france.vcf` — le standard puis les 11 personnes, lien au-dessus
  de la grille

Le dossier est **entièrement régénéré** à chaque build : ne rien y ajouter
à la main, tout fichier étranger sera supprimé.

Format vCard 3.0, UTF-8, fins de ligne CRLF, repli des lignes à 75 octets
sans couper un caractère multi-octets — sinon les prénoms accentués
ressortent cassés sur certains téléphones.

Chaque fiche porte le mobile de la personne (type CELL, marqué préféré) et
le standard, étiqueté « Standard (fixe) » via le groupement `item1.` /
`X-ABLabel` — convention Apple honorée par iOS et macOS. Ailleurs le label
est ignoré et le numéro reste en `TYPE=WORK,VOICE`, ce qui le distingue
déjà d'un mobile.

La sélection multiple de la page recompose les fichiers individuels côté
navigateur (`fetch` + Blob). Elle nécessite que la page soit servie en
HTTP(S) : ouverte en `file://`, l'assemblage échoue et un message renvoie
vers les boutons 💾 individuels, qui fonctionnent toujours.
