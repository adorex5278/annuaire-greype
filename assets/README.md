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
