# CS2 Gap Analyzer 🎮

Analyseur de démos CS2 pour identifier tes axes d'amélioration et devenir pro.

## 🎯 Objectif

Après chaque game, obtenir un rapport ultra-précis qui te dit :
- **🎯 Crosshair Placement** : Mesure exacte de l'angle entre ton crosshair et l'ennemi (flicks requis)
- **💀 Morts évitables** : Analyse avec facteurs de risque réels (no teammate, no utility)
- **💪 Duels désavantagés** : Détection précise des duels pris sans avantage
- **💥 Flashes utiles** : Effectiveness réelle + pop-flash detection
- **📊 Top 3 priorités** : Classées par severity avec recommandations actionnables

Analyse géométrique avancée. Rapports détaillés. Maximum d'impact.

## 🚀 Installation

### 1. Installer Python 3.12 et tkinter
```bash
brew install python@3.12
brew install python-tk@3.12
```

### 2. Créer un environnement virtuel
```bash
python3.12 -m venv venv
```

### 3. Activer l'environnement
```bash
source venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

**Note** : Tu dois activer l'environnement virtuel (`source venv/bin/activate`) chaque fois que tu veux utiliser l'outil.

## 📖 Utilisation

### Récupérer tes démos CS2

1. Dans CS2, va dans **Watch > Your Matches**
2. Télécharge la démo de ta dernière game
3. Place-la dans le dossier `demos/` (ou note son chemin)

### Analyser une démo

```bash
# Active l'environnement virtuel si pas déjà fait
source venv/bin/activate

# Lance l'analyse
python main.py demos/match.dem "TonPseudoCS2"
```

**⚠️ Important** : Le pseudo doit correspondre EXACTEMENT à ton nom in-game (sensible à la casse).

### Exemple de sortie

```
======================================================================
   CS2 GAP ANALYZER - RAPPORT D'ANALYSE
   Joueur: TonPseudo
======================================================================

📊 VUE D'ENSEMBLE
----------------------------------------------------------------------
K/D Ratio            : 0.75  (15 kills / 20 deaths)
Headshot Rate        : 42.0%
Crosshair Placement  : 65% mauvais (avg offset: 45°)
Morts évitables      : 55%
Duels désavantagés   : 45%
Flashes utiles       : 40% (15% pop flashes)

🎯 PRIORITÉS D'AMÉLIORATION (par ordre d'importance)
----------------------------------------------------------------------

1. 🎯 CROSSHAIR PLACEMENT
   65% des duels avec mauvais pre-aim (>30°)
   → Travailler le pre-aim sur angles communs (DM focus)

2. ⚠️ MORTS ÉVITABLES
   55% des morts étaient évitables
   → Jouer avec équipe, utiliser utility avant de peek

3. 💪 DUELS DÉSAVANTAGÉS
   45% des duels pris sans avantage
   → Créer avantage avant de peek (flash + jiggle peek)

🎯 DÉTAILS CROSSHAIR PLACEMENT
----------------------------------------------------------------------
Offset moyen         : 45.3° (objectif: <20°)
Mauvais placement    : 13/20 duels (>30° flick requis)

Pires exemples (>60° flick requis):
  • Vs PlayerX: 87° off target
  • Vs PlayerY: 72° off target
  • Vs PlayerZ: 65° off target

💀 ANALYSE DES MORTS
----------------------------------------------------------------------
Morts évitables      : 11/20
Sans avantage        : 9/20

Facteurs de risque principaux:
  • Aucun coéquipier pour trade : 8
  • Aucune utility utilisée     : 11

💥 UTILISATION DES UTILITAIRES
----------------------------------------------------------------------
Total flashes        : 8
Flashes utiles       : 3 (38%)
Pop flashes          : 1 (13%)

Efficacité:
  • Ennemis flashés (>1s)      : 2
  • Kill dans les 3s après     : 2

======================================================================
💡 TIP: Focus sur 1-2 points à la fois pour amélioration maximale
======================================================================
```

### Sauvegarder les résultats

Pour garder une trace des analyses (JSON + rapport texte) :

```bash
python main.py demos/match.dem "TonPseudoCS2" --save
```

Les fichiers seront créés dans le dossier `output/`.

## 📊 Métriques expliquées

### 🎯 Crosshair Placement (NOUVEAU !)
Mesure l'angle entre la direction de ton crosshair et la position de l'ennemi au moment où tu meurs :
- **Bon** : <30° (pre-aim correct)
- **Mauvais** : 30-60° (flick moyen requis)
- **Terrible** : >60° (gros flick requis)

Objectif : Avg offset <20° et <30% de mauvais placement.

### 💀 Morts évitables (AMÉLIORÉ)
Une mort est "évitable" si tu as des facteurs de risque ET aucun avantage :
- **Facteurs de risque** : No teammate pour trade, no utility utilisée
- **Avantages** : Flash active, teammates nearby, close range (<500 units)

### 💪 Duels désavantagés
Duel pris sans aucun avantage parmi :
- Flash active sur ennemi
- Supériorité numérique
- Close range ou angle advantage
- Teammate pour trade

### 💥 Flashes utiles (AMÉLIORÉ)
Flash "utile" si :
- Aveugle ennemi >1 seconde, OU
- Kill dans les 3s après

**Pop-flash** : Flash suivie d'un peek dans la seconde (mouvement >100 units)

## 🛠 Architecture

```
CS2 Demo (.dem)
      ↓
Parser (demoparser2) + Geometry
      ↓
Events JSON (deaths, kills, flashes + angles pitch/yaw)
      ↓
Analyzer (analyses précises avec calculs géométriques)
      ↓
Report (rapport détaillé et actionnable)
```

### Fichiers principaux

- `main.py` - Point d'entrée CLI
- `src/parser.py` - Extraction des events avec angles
- `src/geometry.py` - Calculs FOV, crosshair offset, line of sight
- `src/game_state.py` - Tracking d'état (smokes, visible enemies, HP)
- `src/analyzer.py` - Analyses avancées avec métriques précises
- `src/report.py` - Génération de rapports détaillés avec priorités

## 🔧 Structure du projet

```
cs2-gap-analyzer/
├── main.py              # Script principal
├── requirements.txt     # Dépendances
├── README.md           # Ce fichier
├── src/
│   ├── parser.py       # Parser de démos
│   ├── analyzer.py     # Analyseur de gameplay
│   └── report.py       # Générateur de rapports
├── demos/              # Tes fichiers .dem (à créer)
├── output/             # Rapports générés
└── tests/              # Tests (à venir)
```

## 💡 Conseils d'utilisation

1. **Analyse après chaque game** - Plus tu analyses, plus tu progresses vite
2. **Focus sur UNE priorité à la fois** - Ne cherche pas à tout corriger d'un coup
3. **Track ton évolution** - Utilise `--save` et compare tes stats sur plusieurs games
4. **Vérifie ton pseudo** - Si l'outil ne trouve rien, c'est probablement une erreur de pseudo

## 🐛 Problèmes courants

### "Demo file not found"
- Vérifie que le fichier .dem existe
- Utilise le chemin complet si nécessaire

### "Player not found in demo"
- Vérifie l'orthographe exacte de ton pseudo in-game
- Le nom est sensible à la casse

### "demoparser2 not installed"
- Lance : `pip install -r requirements.txt`

## 🚀 Features récentes

- [x] **Crosshair Placement Analysis** - Mesure précise des angles de flick
- [x] **Geometric Calculations** - FOV, line of sight, crosshair offset
- [x] **Pop-flash Detection** - Tracking de mouvement après flash
- [x] **Priority System** - Top 3 ranked par severity
- [x] **Detailed Reports** - Breakdown complet avec exemples

## 🔮 Roadmap

- [ ] Tests unitaires
- [ ] GameState integration (visible enemies at death)
- [ ] Statistiques par map et side (T/CT)
- [ ] Économie et buy analysis
- [ ] Comparaison entre games (progression tracking)

## 📝 Licence

MIT - Fais-en ce que tu veux pour devenir pro !
