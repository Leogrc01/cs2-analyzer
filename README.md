# 🎮 CS2 Gap Analyzer

Outil d'analyse avancée pour démos Counter-Strike 2. Identifie automatiquement les axes d'amélioration de votre gameplay à travers l'analyse de crosshair placement, économie, positionnement et utility usage.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![CS2](https://img.shields.io/badge/CS2-Compatible-green.svg)

## ✨ Fonctionnalités

### 📊 Analyse Complète
- **Crosshair Placement** : Mesure précise des angles de flick nécessaires
- **Analyse Économique** : Tracking des pertes d'équipement et discipline eco
- **Positionnement** : Identification des zones dangereuses vs zones performantes
- **Utility Usage** : Efficacité des flashes, détection de pop-flashes
- **Recommandations Prioritaires** : Top 3 des axes d'amélioration par sévérité

### 🗺️ Heatmap Visuelle
- Visualisation graphique des positions de mort et kill
- Support d'overlay sur images radar réelles
- Détection automatique des zones dangereuses (K/D < 0.7)
- Identification des zones fortes (K/D ≥ 1.5)
- Calibration automatique des coordonnées

### 🎯 Métriques Avancées
- K/D par zone de map
- Analyse de morts évitables
- ROI économique par round type
- Pop-flash detection via movement tracking
- Données 100% précises (utilise `current_equip_value` du jeu)

## 🚀 Installation

### Prérequis
- Python 3.12+ (ou 3.10+)
- CS2 demo files (.dem)

### Setup Rapide
```bash
# Cloner le repo
git clone https://github.com/YOUR_USERNAME/cs2-gap-analyzer.git
cd cs2-gap-analyzer

# Créer l'environnement virtuel
python3.12 -m venv venv

# Installer les dépendances
venv/bin/pip install -r requirements.txt

# Lancer le menu interactif
./run.sh
```

## 📖 Utilisation

### Mode Interactif (Recommandé) ⭐
```bash
./run.sh
```

Menu guidé avec toutes les options :
- 📊 Analyse complète (rapport + heatmap)
- 📝 Rapport textuel uniquement
- 🗺️ Heatmap uniquement
- 📍 Vue détaillée positionnement
- 🔧 Calibration des coordonnées

### Mode Ligne de Commande
```bash
# Analyse complète
venv/bin/python main.py demos/match.dem "PlayerName" --save

# Heatmap avec overlay
venv/bin/python generate_heatmap_overlay.py demos/match.dem "PlayerName"
```

## 📊 Exemple de Rapport

```
🎮 CS2 GAP ANALYZER - RAPPORT D'ANALYSE
======================================================================

📊 VUE D'ENSEMBLE
K/D Ratio            : 0.67  (10 kills / 15 deaths)
Headshot Rate        : 40.0%
Crosshair Placement  : 27% mauvais (avg offset: 27°)
Impact économique    : 55550$ perdus (avg: 3703$/mort)
Morts coûteuses      : 67% (>3000$)

🎯 PRIORITÉS D'AMÉLIORATION
1. ⚡ POP FLASH
   Seulement 4% de pop flashes
   → Apprendre les pop flashes de chaque map

2. 💰 DISCIPLINE ÉCONOMIQUE
   67% des morts perdent >3000$
   → Préserver équipement cher, jouer plus safe en full buy

🗺️ ANALYSE DE POSITIONNEMENT
Map: de_dust2

Zones les plus dangereuses:
  • Long: 7 morts (K/D 0.57)
  • Long Doors: 2 morts (K/D 0.00)

Zones performantes:
  • A Site: K/D 3.00 (3K/1D)

Recommandations:
  🔴 ÉVITER Long - Jouer plus safe ou éviter cette zone
  ✅ EXPLOITER A Site - Zone forte, jouer plus souvent ici
```

## 🗺️ Heatmap avec Overlay

![Heatmap Example](docs/heatmap_example.png)

Pour de meilleurs résultats, ajoutez des images radar :
1. Télécharger depuis [SimpleRadar](https://readtldr.gg/simpleradar)
2. Placer dans `maps/de_dust2.png`
3. L'overlay sera automatiquement appliqué

## 🏗️ Architecture

```
cs2-gap-analyzer/
├── analyzer.py                  # 🚀 Menu interactif principal
├── run.sh                       # 🚀 Launch script
├── main.py                      # CLI analysis tool
├── src/
│   ├── parser.py               # Demo parsing (demoparser2)
│   ├── analyzer.py             # Core analysis engine
│   ├── economy.py              # Economic analysis
│   ├── positioning.py          # Zone-based performance
│   ├── geometry.py             # FOV, crosshair calculations
│   └── report.py               # Report generation
├── demos/                       # 📂 Place .dem files here
├── maps/                        # 🗺️ Radar images (optional)
└── output/                      # 📊 Generated reports
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage rapide
- **[HEATMAP_GUIDE.md](HEATMAP_GUIDE.md)** - Documentation heatmaps
- **[WARP.md](WARP.md)** - Documentation technique complète

## 🔬 Détails Techniques

### Crosshair Placement
Mesure l'angle entre crosshair et position ennemie :
- Good : <30° | Bad : 30-60° | Terrible : >60°

### Analyse Économique
- Utilise `current_equip_value` du jeu (100% précis)
- Inclut ALL equipment: armes, armor, helmet, kit, grenades
- Catégorisation auto : pistol/eco/force/full buy

### Positionnement
- Coordonnées précises pour dust2, mirage, inferno
- Détection auto danger zones (K/D < 0.7)
- Strong zones (K/D ≥ 1.5)

## 🤝 Contribution

Contributions bienvenues ! 
- Issues pour bugs/suggestions
- PR pour nouvelles features
- Ajout de coordonnées pour nouvelles maps

## 📝 Roadmap

- [ ] Support maps: Nuke, Anubis, Vertigo, Ancient
- [ ] Analyse multi-joueur
- [ ] Timeline événements
- [ ] Tilt pattern detection
- [ ] Export HTML interactif
- [ ] Movement analysis

## 🙏 Remerciements

- **demoparser2** - CS2 demo parsing
- **matplotlib** - Visualisation
- **SimpleRadar** - Images radar

## 📄 License

MIT License

---

⭐ **Tip** : Utilisez après chaque session pour tracker votre progression !

💡 **Discord** : [Rejoindre pour support et discussions](https://discord.gg/YOUR_LINK)
