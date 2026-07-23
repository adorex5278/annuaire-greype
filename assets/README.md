# assets/

Logo, favicons et icônes, avec leurs versions de repli.

**La documentation complète du projet est dans `README.md` à la racine** —
y compris la chaîne de repli des images, la procédure après un changement
de logo, et la liste des choix à ne pas « corriger ».

| Fichier | Rôle |
|---|---|
| `logo.jpg` | copie locale du vrai logo, repli si le serveur distant tombe |
| `logo-fallback.svg` | wordmark généré, dernier recours |
| `favicon.png` / `apple-touch-icon.png` | recadrage sur la pastille du logo |
| `favicon-wordmark.png` | variante logo entier, non branchée |
| `favicon-fallback.svg` | monogramme G, non branché |
| `icons/<site>.png` | vraies favicons des fiches financières |
| `icons/<site>.svg` | pastilles générées, dernier recours |

Le logo distant reste la source de vérité : ces fichiers ne se mettent pas
à jour tout seuls, il faut les régénérer après un changement de logo.
