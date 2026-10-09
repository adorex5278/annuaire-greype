# annuaire-greype

Annuaire public de l'équipe GREYPE FRANCE + page de coordonnées bancaires.
Site statique servi par GitHub Pages depuis la branche `main`, dossier racine.

- Production : https://adorex5278.github.io/annuaire-greype/index.html
- Pas de build CI, pas de dépendances, pas de framework. Du HTML/CSS/JS à la main
  plus un script Python de génération.

---

## ⚠️ À LIRE AVANT DE MODIFIER QUOI QUE CE SOIT

Cette section existe parce que plusieurs choix du projet **ressemblent à des bugs
sans en être**. Les « corriger » casserait quelque chose. Si vous êtes un agent
(Copilot, Claude, autre) qui découvre ce dépôt, lisez cette liste en entier.

### 1. Les cartes de l'équipe sont générées — ne pas les éditer à la main

Dans `index.html`, tout ce qui se trouve entre :

```html
<!-- TEAM:START -->
<!-- TEAM:END -->
```

est **écrasé** au prochain `python3 build.py`. La source de vérité est
`team.json`. Modifier le HTML directement donne un travail perdu au build
suivant, et surtout une divergence silencieuse entre les cartes et les vCard.

**Piège associé** : ne jamais citer les marqueurs avec leurs délimiteurs de
commentaire ailleurs dans `index.html`. Un commentaire HTML ne s'imbrique pas,
le premier `-->` referme le bloc — et `build.py` écrirait les cartes au mauvais
endroit. Le script refuse désormais de tourner si un marqueur apparaît plus
d'une fois, mais autant ne pas déclencher le garde-fou. Écrire « TEAM:START »
en toutes lettres, sans délimiteurs.

### 2. `vcf/` est intégralement régénéré

`build.py` **supprime tous les `.vcf`** du dossier avant de les réécrire.
Ne rien y déposer à la main : ce sera perdu sans avertissement.

### 3. Le logo est hébergé dans le dépôt

Depuis octobre 2026, le logo est le GIF animé du site officiel
(https://www.greype-france.com/), copié dans `assets/logo.gif`. L'ancien logo
distant (`public.saintcharlesinternational.com`, logo vert) n'est plus utilisé
et a été retiré de la CSP.

`assets/logo.jpg` (dernière image du GIF) sert de repli et d'image de partage
(`og:image`, qui doit rester une URL absolue). Ces fichiers ne se mettent pas à
jour tout seuls : après un changement de logo, les régénérer (voir plus bas).

### 4. La CSP est active et se trouve dans le `<head>`

`index.html` et `greypebank.html` ont un
`<meta http-equiv="Content-Security-Policy">`. **Toute nouvelle ressource
externe doit être ajoutée à la directive correspondante**, sinon elle est
bloquée silencieusement (visible seulement dans la console).

Piège déjà rencontré : les favicons des fiches financières viennent de
`google.com/s2/favicons`, qui **redirige vers `gstatic.com`**. Les deux
domaines doivent figurer dans `img-src`.

### 5. Ne jamais imbriquer deux documents HTML

Les fichiers de ce dépôt viennent à l'origine d'exports CodePen, qui
enveloppent le code dans un second document complet :

```html
<!DOCTYPE html><html lang="en"><head><title>nom du pen</title></head><body>
  <!DOCTYPE html><html lang="fr"><head>...le vrai contenu...
```

Le navigateur ne garde que le **premier** `<head>`. Conséquence : les balises
Open Graph, le `viewport` et la CSP se retrouvent dans le `<body>` et sont
ignorés — donc aucun aperçu au partage et un affichage mobile cassé. Ce défaut
a été corrigé partout. **Si vous réimportez depuis CodePen, retirez
l'enveloppe.**

### 6. `greypebank.html` contient des IBAN

Le `<meta name="robots" content="noindex, nofollow">` est **délibéré**. Ne pas
le retirer sans décision explicite du propriétaire.

Corollaire : toute modification de cette page touche à des coordonnées
bancaires publiques. Une erreur d'un chiffre est un détournement de virement.
Vérifier les IBAN avec la clé mod-97 après toute modification (voir
« Contrôles » plus bas).

### 7. Le CodePen redirige — ne pas le supprimer

Un QR code imprimé et distribué pointe sur
`https://codepen.io/Adrien-Gehan/full/JoPzPjv`. Ce pen ne contient plus les
RIB : seulement un bouton vers `greypebank.html`, avec `target="_top"` pour
sortir de l'iframe CodePen.

Le `target="_top"` est indispensable : dans l'iframe CodePen,
`navigator.clipboard` est bloqué par la permissions policy (`clipboard-write`
absent de l'attribut `allow`), et les boutons de copie ne fonctionneraient pas.
Une redirection automatique ne marche pas non plus : le sandbox n'autorise
`allow-top-navigation-by-user-activation`, donc uniquement après un clic.

### 8. Vanessa SAINT-DENIS partage le numéro du standard

Ce n'est pas un doublon à corriger. `build.py` le détecte et produit une seule
entrée `TEL` de type `WORK` dans sa vCard, au lieu de dupliquer le numéro en
mobile + fixe.

---

## Structure

```
index.html          annuaire (cartes générées entre les marqueurs TEAM:*)
greypebank.html     coordonnées bancaires, 2 banques, noindex
404.html            page d'erreur GitHub Pages, volontairement sans ressource externe
team.json           SOURCE DE VÉRITÉ de l'équipe
build.py            génère les cartes de index.html + tout le dossier vcf/
vcf/                GÉNÉRÉ — 11 fiches + le standard + 1 fichier groupé
assets/             logo, favicons, icônes, et leurs replis
```

---

## Tâches courantes

### Modifier l'équipe

```bash
nano team.json
python3 build.py
git add team.json index.html vcf/
git commit -m "MAJ equipe"
git push
```

Champs d'une entrée : `name`, `role`, `phone` (chiffres uniquement, indicatif
pays compris, **sans** `+`), `display` (version lisible), puis au choix
`whatsapp`, `sms` (booléens), `linkedin`, `pappers` (URL).

`build.py` refuse de générer si un champ obligatoire manque, si `phone`
contient autre chose que des chiffres, si `phone` et `display` divergent, ou si
deux personnes produisent le même nom de fichier vCard.

### Après un changement de logo

Remplacer le GIF puis régénérer les images fixes :

```bash
cp nouveau-logo.gif assets/logo.gif
convert 'assets/logo.gif[-1]' -background white -flatten assets/logo.jpg
convert assets/logo.jpg -crop 191x133+0+0 +repage -gravity center -background white -extent 203x203 -resize 64x64   assets/favicon.png
convert assets/logo.jpg -crop 191x133+0+0 +repage -gravity center -background white -extent 203x203 -resize 180x180 assets/apple-touch-icon.png
```

Le recadrage `191x133+0+0` isole le personnage à gauche du logo (le mot
« GREYPE » est illisible à 16 px dans un onglet). À réajuster si la composition
change.

### Modifier un RIB

Éditer `greypebank.html`. La valeur copiée est **lue dans le `<span>` affiché** :
un seul endroit à modifier. Les IBAN sont affichés par groupes de 4 chiffres et
copiés sans espaces (classe `.iban`). Ne pas réintroduire la valeur en dur dans
le `onclick`.

---

## Mécanismes à connaître

### Chaîne de repli des images

Helper `fallbackImg()` dans `index.html`. Attribut `data-fallbacks` contenant
une liste séparée par des virgules, essayée dans l'ordre :

```html
<img src="assets/logo.gif"
     data-fallbacks="assets/logo.jpg,assets/logo-fallback.svg"
     onerror="fallbackImg(this)">
```

Les favicons pointent directement sur les PNG locaux, sans repli.

### Icônes SVG

Définies une seule fois dans un sprite (`<symbol id="ico-wa">`, `#ico-li`) et
réutilisées via `<use href="#...">`. Ne pas les redupliquer dans chaque carte.

### vCard

Format 3.0, **UTF-8**, fins de ligne **CRLF**, repli des lignes à 75 octets sans
couper un caractère multi-octets. Ce dernier point n'est pas cosmétique : un `ë`
scindé en deux moitiés par un repli mal placé casse l'import sur certains
téléphones.

Le standard est une fiche société (`X-ABShowAs:COMPANY`), sinon iOS découpe
« GREYPE FRANCE » en prénom / nom. Le libellé « Standard (fixe) » passe par le
groupement `item1.` / `X-ABLabel`, convention Apple ignorée sans dommage
ailleurs.

La sélection multiple recompose les fichiers individuels côté navigateur
(`fetch` + `Blob`) plutôt que d'embarquer une copie des numéros dans la page.
Nécessite HTTP(S) : en `file://` l'assemblage échoue et un message renvoie vers
les boutons 💾 individuels.

---

## Contrôles avant de committer

```bash
# 1. le générateur est-il reproductible ?
python3 build.py && python3 build.py && git diff --stat

# 2. conformité des vCard
python3 - <<'EOF'
import pathlib
for f in sorted(pathlib.Path("vcf").glob("*.vcf")):
    raw = f.read_bytes(); txt = raw.decode("utf-8")
    assert raw.count(b"\n") == raw.count(b"\r\n"), f"{f.name}: LF isolé"
    assert txt.count("BEGIN:VCARD") == txt.count("END:VCARD"), f"{f.name}: déséquilibre"
    for i, l in enumerate(txt.split("\r\n")):
        assert len(l.encode()) <= 75, f"{f.name} l.{i+1}: {len(l.encode())} octets"
print("vCard conformes")
EOF

# 3. clé de contrôle des IBAN de greypebank.html
python3 - <<'EOF'
import re, pathlib
s = pathlib.Path("greypebank.html").read_text(encoding="utf-8")
for iban in re.findall(r"FR[0-9 ]{25,35}", s):
    c = iban.replace(" ", "")
    r = c[4:] + c[:4]
    n = "".join(str(ord(x) - 55) if x.isalpha() else x for x in r)
    print(("OK   " if int(n) % 97 == 1 else "ERREUR"), c)
EOF
```

Puis vérifier à la main, dans `index.html` et `greypebank.html` : un seul
`<!DOCTYPE>`, un seul `<html>`, un seul `<head>`, un seul `<body>`.

---

## Ce qui ne peut pas être vérifié en local

- Le type MIME des `.vcf` servis par GitHub Pages (détermine si iOS ouvre
  l'app Contacts directement ou passe par les téléchargements)
- Le comportement réel de l'import vCard sur iOS et Android

Ces points se testent uniquement sur le site publié, depuis un vrai téléphone.

---

## coordonnees.html — surcouche des fiches société Google Docs

Enrobe le /preview des trois Google Docs (FR/EN/ES) dans une page maîtrisée,
avec un bouton d'impression explicite. Existe parce que le mode /preview masque
la barre d'outils Google, donc le bouton imprimer natif.

- Les IDs des trois docs sont dans l'objet DOCS en haut du <script>. Seul
  endroit à modifier pour changer un document. Les liens Google d'origine ne
  sont pas remplacés, juste ré-employés.
- Le bouton « Imprimer / PDF » ouvre export?format=pdf : il NE PEUT PAS piloter
  l'iframe (cross-origin), il ouvre donc la version PDF. Seule voie possible.
- Langue via ?lang=fr|en|es, sinon langue du navigateur, sinon fr.
- noindex : la fiche contient des données d'entreprise.

Les trois docs doivent être traduits DANS Google (le bouton ne traduit que
l'interface autour, pas le contenu du document).
