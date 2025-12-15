# 🗺️ Guide Heatmap - CS2 Gap Analyzer

## 📊 Qu'est-ce qu'une heatmap ?

Une heatmap visualise graphiquement où vous mourrez et tuez sur la map, permettant d'identifier rapidement :
- 🔴 **Zones dangereuses** : Où vous mourrez le plus
- 🟢 **Zones fortes** : Où vous performez bien
- 📍 **Patterns de jeu** : Tendances de positionnement

## 🚀 Utilisation

### Option 1 : Heatmap basique (sans image de map)

```bash
venv/bin/python generate_heatmap.py demos/match.dem "PlayerName"
```

Génère une heatmap avec zones rectangulaires colorées.

### Option 2 : Heatmap avec overlay (recommandé)

```bash
venv/bin/python generate_heatmap_overlay.py demos/match.dem "PlayerName"
```

Génère une heatmap plus détaillée avec :
- Zones dangereuses et fortes dans des encadrés
- Stats globales affichées
- Meilleure lisibilité

### Option 3 : Heatmap avec vraie map (MEILLEUR)

1. **Télécharger les images de map radar** :
   - Site recommandé : https://readtldr.gg/simpleradar
   - Ou extraire depuis les fichiers CS2 : `csgo/resource/overviews/`

2. **Placer dans le dossier `maps/`** :
   ```
   maps/
   ├── de_dust2.png
   ├── de_mirage.png
   └── de_inferno.png
   ```

3. **Générer la heatmap** :
   ```bash
   venv/bin/python generate_heatmap_overlay.py demos/match.dem "PlayerName"
   ```

Le script détectera automatiquement l'image et la superposera !

## 📖 Lecture de la heatmap

### Symboles
- 🔴 **Cercle rouge** = Mort
- 🟢 **Triangle vert** = Kill

### Zones colorées
- **Rouge clair** = Zone dangereuse (box en bas à droite)
- **Vert clair** = Zone forte (box en haut à droite)
- **Gris** = Zones de la map

### Stats affichées
- **Coin haut gauche** : K/D global, HSR, Crosshair offset moyen
- **Coin haut droit** : Top 3 zones fortes
- **Coin bas droit** : Top 3 zones dangereuses

## 💡 Interprétation

### Exemple concret :
```
Zone "Long" : 7 morts, 4 kills → K/D 0.57
→ Action : Éviter cette zone ou changer d'approche
```

### Patterns à identifier :

1. **Cluster de morts** (beaucoup de 🔴 au même endroit)
   - ❌ Mauvais : Vous mourrez toujours au même spot
   - ✅ Action : Changer d'angle/position/timing

2. **Morts dispersées** (🔴 partout)
   - ❌ Mauvais : Manque de consistency
   - ✅ Action : Focus sur 2-3 positions clés

3. **Zone sans kills** (pas de 🟢)
   - ❌ Mauvais : Vous n'engagez jamais ici
   - ✅ Action : Essayer de jouer cette zone plus souvent

4. **Zone avec kills groupés** (cluster de 🟢)
   - ✅ Bon : Zone forte à exploiter davantage

## 🎯 Recommandations basées sur la heatmap

Le script génère automatiquement des recommandations :

```
🔴 ÉVITER Long: 7 morts, K/D 0.57
   → Jouer plus safe ou éviter cette zone

⚠️  Long Doors également problématique: 2 morts
   → Point d'entrée dangereux

✅ EXPLOITER A Site: K/D 3.00
   → Zone forte, jouer plus souvent ici
```

## 📁 Structure des fichiers

```
cs2-gap-analyzer/
├── generate_heatmap.py              # Script basique
├── generate_heatmap_overlay.py      # Script avancé (recommandé)
├── maps/
│   ├── README.md                    # Guide pour obtenir les maps
│   ├── de_dust2.png                 # Image radar (à ajouter)
│   └── de_mirage.png                # Image radar (à ajouter)
└── output/
    ├── heatmap.png                  # Heatmap basique
    └── heatmap_overlay.png          # Heatmap avec overlay
```

## 🔧 Options avancées

### Spécifier le nom du fichier de sortie
```bash
venv/bin/python generate_heatmap_overlay.py demos/match.dem "PlayerName" my_custom_name.png
```

### Analyser plusieurs demos
```bash
for demo in demos/*.dem; do
    venv/bin/python generate_heatmap_overlay.py "$demo" "PlayerName" "output/$(basename $demo .dem)_heatmap.png"
done
```

## ❓ Troubleshooting

### "Map image not found"
- Normal si vous n'avez pas ajouté d'image dans `maps/`
- Le script fonctionne quand même en mode fallback
- Pour améliorer : télécharger et placer les images radar

### "No position data to plot"
- Aucune mort/kill trouvée pour ce joueur
- Vérifier le nom du joueur (sensible à la casse)
- Vérifier que le demo contient bien des données

### Image floue ou mal alignée
- Vérifier la résolution de l'image radar (min 1024x1024)
- Ajuster les coordonnées dans `MAP_BOUNDS` si nécessaire
- Utiliser une image radar "propre" (sans HUD)

## 🎨 Personnalisation

Vous pouvez modifier les couleurs et styles dans `generate_heatmap_overlay.py` :
- `c='red'` → Couleur des morts
- `c='limegreen'` → Couleur des kills
- `s=200` → Taille des markers
- `alpha=0.7` → Transparence

## 📚 Ressources

- **SimpleRadar** : https://readtldr.gg/simpleradar (maps gratuites)
- **CS2 Overviews** : Dossier game files `csgo/resource/overviews/`
- **DDS Converter** : Pour convertir .dds → .png

---

💡 **Tip** : Utilisez la heatmap après chaque session pour identifier les patterns et ajuster votre gameplay !
