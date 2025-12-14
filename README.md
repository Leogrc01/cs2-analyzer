# CS2 Gap Analyzer 🎮

Analyseur de démos CS2 pour identifier tes axes d'amélioration et devenir pro.

## 🎯 Objectif

Après chaque game, obtenir un rapport clair qui te dit :
- **% de morts évitables** (pas de mate proche pour trade)
- **% de duels sans avantage** (pris sans flash, nombre, angle)
- **% de flashes utiles** (qui touchent ou donnent un kill)
- **UNE priorité d'entraînement** pour la prochaine game

Lecture en 30 secondes. Zéro interface. Maximum d'impact.

## 🚀 Installation

### 1. Prérequis
- Python 3.10+
- pip (gestionnaire de paquets Python)

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 📖 Utilisation

### Récupérer tes démos CS2

1. Dans CS2, va dans **Watch > Your Matches**
2. Télécharge la démo de ta dernière game
3. Place-la dans le dossier `demos/` (ou note son chemin)

### Analyser une démo

```bash
python main.py demos/match.dem "TonPseudoCS2"
```

**⚠️ Important** : Le pseudo doit correspondre EXACTEMENT à ton nom in-game (sensible à la casse).

### Exemple de sortie

```
==================================================
CS2 GAP REPORT
Joueur: TonPseudo
==================================================

📊 STATISTIQUES
--------------------------------------------------
Morts évitables       : 61%
Duels sans avantage   : 54%
Flash utiles          : 18%

Total kills           : 15
Total deaths          : 18
K/D ratio             : 0.83

🎯 FOCUS NEXT GAMES
--------------------------------------------------
1. Réduire les morts évitables - jouer avec ton équipe
2. Ne prendre que des duels avec avantage (flash, nombre, trade)

==================================================
```

### Sauvegarder les résultats

Pour garder une trace des analyses (JSON + rapport texte) :

```bash
python main.py demos/match.dem "TonPseudoCS2" --save
```

Les fichiers seront créés dans le dossier `output/`.

## 📊 Métriques expliquées

### Morts évitables
Une mort est considérée "évitable" si **2 ou plus** de ces conditions sont vraies :
- Aucun coéquipier proche (<800 unités) → pas tradable
- Plusieurs ennemis visibles → mauvais angle
- Pas de flash récente (<3s) → duel sec

### Duels sans avantage
Un duel est "sans avantage" si tu n'as **AUCUN** de ces éléments :
- Flash active (lancée <3s avant)
- Supériorité numérique (mates proches)
- Angle fermé / 1v1
- Trade possible (mate proche)

### Flashes utiles
Une flash est "utile" si :
- Elle aveugle quelqu'un >1 seconde, OU
- Tu obtiens un kill <3s après

## 🛠 Architecture

```
CS2 Demo (.dem)
      ↓
Parser (demoparser2)
      ↓
Events JSON (deaths, kills, flashes)
      ↓
Analyzer (règles simples)
      ↓
Report (texte lisible)
```

### Fichiers principaux

- `main.py` - Point d'entrée CLI
- `src/parser.py` - Extraction des events depuis .dem
- `src/analyzer.py` - Analyse des morts, duels, flashes
- `src/report.py` - Génération du rapport texte

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

## 🚀 Roadmap

- [ ] Tests unitaires
- [ ] Support de plusieurs joueurs dans une démo
- [ ] Statistiques par map
- [ ] Analyse de positioning (heatmaps)
- [ ] Comparaison entre games

## 📝 Licence

MIT - Fais-en ce que tu veux pour devenir pro !
