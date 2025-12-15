# 🚀 Démarrage Rapide - CS2 Gap Analyzer

## ⚡ Utilisation en 3 étapes

### 1️⃣ Placer vos démos
```bash
# Copiez vos fichiers .dem dans le dossier demos/
cp ~/chemin/vers/match.dem demos/
```

### 2️⃣ Lancer l'analyzer
```bash
./run.sh
```
ou
```bash
venv/bin/python analyzer.py
```

### 3️⃣ Suivre le menu
Le menu interactif vous guide pour :
- 📊 Générer un rapport complet
- 🗺️  Créer une heatmap
- 📍 Analyser le positionnement
- 🔧 Calibrer les maps

## 📋 Menu Principal

```
🎮 CS2 GAP ANALYZER - Menu Principal
======================================================================

📋 OPTIONS DISPONIBLES:
----------------------------------------------------------------------
  1. 📊 Analyse complète (rapport + heatmap)
  2. 📝 Rapport textuel uniquement
  3. 🗺️  Heatmap uniquement
  4. 📍 Vue détaillée positionnement
  5. 🔧 Calibrer coordonnées map
  6. ℹ️  Aide / Documentation
  0. ❌ Quitter
```

## 🎯 Exemple d'utilisation

1. **Lancer le programme**
   ```bash
   ./run.sh
   ```

2. **Choisir "1" pour analyse complète**

3. **Sélectionner votre demo**
   - Le programme liste automatiquement les .dem dans demos/
   - Tapez le numéro correspondant

4. **Entrer le nom du joueur**
   - Nom exact (sensible à la casse)
   - Ex: "weshboys"

5. **Attendre l'analyse** (~10-30 secondes)

6. **Consulter les résultats**
   - `output/rapport.txt` - Rapport textuel
   - `output/heatmap.png` - Visualisation

## 💡 Conseils

### Pour de meilleurs résultats :
- ✅ Utilisez des demos récents (CS2)
- ✅ Vérifiez le nom exact du joueur (in-game)
- ✅ Placez une image radar dans `maps/` pour une heatmap plus claire

### Résolution de problèmes :
- **"Aucun fichier .dem trouvé"** → Placez vos demos dans `demos/`
- **"No position data"** → Vérifiez le nom du joueur (casse exacte)
- **"Heatmap désalignée"** → Utilisez l'option 5 (calibration)

## 📊 Que fait chaque option ?

### Option 1 - Analyse complète ⭐ (Recommandé)
Génère **tout** en une fois :
- Rapport détaillé (K/D, crosshair, économie, etc.)
- Heatmap visuelle des positions
- Recommandations prioritaires

**Sortie** :
- `output/*_report.txt` - Rapport complet
- `output/*_events.json` - Données brutes
- `output/heatmap.png` - Visualisation

### Option 2 - Rapport uniquement
Génère juste le rapport textuel.
Utile si vous voulez juste les stats sans la visualisation.

### Option 3 - Heatmap uniquement
Génère juste la heatmap visuelle.
Utile si vous avez déjà le rapport et voulez juste la map.

### Option 4 - Vue positionnement
Affiche un tableau détaillé par zone :
```
Zone                  Kills  Deaths    K/D     Status
----------------------------------------------------------------------
Long                      4       7   0.57          🟡
A Site                    3       1   3.00          🟢
```

### Option 5 - Calibration
Analyse les coordonnées pour aligner correctement la heatmap.
À utiliser si les markers sont mal placés sur la map.

### Option 6 - Aide
Affiche la documentation et les guides.

## 🗺️ Améliorer les heatmaps

Pour avoir une vraie map en background :

1. **Télécharger une image radar**
   - Site : https://readtldr.gg/simpleradar
   - Choisir votre map (ex: Dust2)

2. **Placer dans maps/**
   ```bash
   # Renommer en fonction de la map
   cp ~/Downloads/radar_dust2.png maps/de_dust2.png
   ```

3. **Régénérer la heatmap**
   - L'image sera automatiquement détectée !

## 📁 Structure des fichiers

```
cs2-gap-analyzer/
├── run.sh                    ← 🚀 LANCER ICI
├── analyzer.py               ← Menu interactif
├── demos/                    ← 📂 Placer vos .dem ici
│   └── match.dem
├── maps/                     ← 🗺️ Images radar (optionnel)
│   └── de_dust2.png
└── output/                   ← 📊 Résultats générés
    ├── *_report.txt
    ├── *_events.json
    └── heatmap.png
```

## 🆘 Besoin d'aide ?

- 📖 **Guides complets** : README.md, HEATMAP_GUIDE.md
- 💬 **Menu aide** : Option 6 dans le menu
- 🔧 **Problème de map** : Option 5 (calibration)

---

💡 **Tip** : Ajoutez `./run.sh` à vos favoris pour un accès rapide !
