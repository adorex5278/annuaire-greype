# assets/

Visuels de **repli** utilisés uniquement si la ressource distante ne répond pas.

## Chaîne de repli du logo

1. `https://public.saintcharlesinternational.com/.../greype.jpg` (source, mise à jour via INPI)
2. `assets/logo.jpg` — copie locale du vrai logo, **absente pour l'instant**
3. `assets/logo-fallback.svg` — wordmark généré

Pour un repli identique au logo réel : déposer le fichier sous le nom exact
`assets/logo.jpg`. Aucune modification du HTML n'est nécessaire, il est déjà
dans la chaîne.

## Favicon

`assets/favicon-fallback.svg` (monogramme G). Bascule automatique si le logo
distant ne charge pas.

## Icônes des fiches financières

`assets/icons/*.svg` — pastilles générées, utilisées si le service
`google.com/s2/favicons` est indisponible ou bloqué.

Pour utiliser les vraies favicons hors ligne : récupérer chaque `favicon.ico`
et remplacer le SVG correspondant (garder le même nom de fichier).
