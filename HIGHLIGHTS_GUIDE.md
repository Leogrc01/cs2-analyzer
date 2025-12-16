# 🎬 Guide des Highlights CS2

## Vue d'ensemble

Le système de highlights identifie automatiquement les moments clés de votre démo pour review rapide et ciblée.

## Qu'est-ce qui est identifié ?

### 🔴 Moments Critiques (Priorité Haute)

1. **❌ Morts Évitables**
   - Aucun coéquipier pour trade
   - Aucune utility utilisée
   - Crosshair terrible (>60°)
   - **Pourquoi revoir** : Erreurs majeures de décision

2. **💰 Pertes Économiques Majeures**
   - Mort avec >4000$ d'équipement
   - Full buy + kit perdu
   - **Pourquoi revoir** : Impact économique élevé sur l'équipe

### 🟡 Moments Importants

3. **🎯 Crosshair Placement Terrible**
   - Offset >60° (regardait complètement ailleurs)
   - **Pourquoi revoir** : Problème fondamental de pre-aim

### 🟢 Points d'Amélioration

4. **💥 Flashes Gaspillées**
   - Flash inutile suivie de mort
   - **Pourquoi revoir** : Mauvais usage d'utility

### ✅ Exemples Positifs

5. **✅ Kills Parfaits**
   - Headshot + pre-aim parfait (<20°)
   - **Pourquoi revoir** : Apprendre de vos bons moments

## Comment utiliser

### Méthode 1: Fichier Texte (Recommandé pour débuter)

```bash
# Générer les highlights
./run.sh
# Choisir option 3: Générer highlights

# Ouvrir le fichier
cat output/demo_highlights.txt
```

Le fichier contient :
- Liste prioritisée des moments
- Contexte de chaque moment (round, temps, détails)
- **Commandes CS2** pour sauter directement au tick
- Range de ticks pour créer des clips

### Méthode 2: Script CS2 (Navigation Automatique)

#### Setup (une seule fois)

```bash
# Copier le script vers CS2
cp output/highlights.cfg ~/.steam/steam/steamapps/common/Counter-Strike\ Global\ Offensive/game/csgo/cfg/
```

#### Utilisation

1. Lancer CS2
2. Charger la démo :
   ```
   playdemo demo_name
   ```

3. Ouvrir la console et taper :
   ```
   exec highlights
   ```

4. Utiliser les raccourcis :
   - **F5** : Jump to next highlight
   - **F6** : Slow motion (0.5x)
   - **F7** : Normal speed (1x)

5. Le script saute automatiquement au premier highlight et affiche les infos dans la console

### Méthode 3: JSON (Pour développeurs)

```bash
# Le fichier JSON contient toutes les données
cat output/demo_highlights.json
```

Structure :
```json
{
  "priority": 90,
  "category": "❌ MORT ÉVITABLE",
  "tick": 45320,
  "round": 8,
  "time": "1:45",
  "description": "aucun coéquipier, crosshair 85° (TERRIBLE)",
  "attacker": "Enemy",
  "weapon": "ak47",
  "economic_impact": 4850,
  "context": "Perte: 4850$"
}
```

## Exemple de Workflow

### Review Rapide (10-15 min)

1. Générer highlights
2. Ouvrir `*_highlights.txt`
3. Focus sur les 5 premiers moments critiques (🔴)
4. Charger démo dans CS2
5. Utiliser les commandes `demo_gototick` du fichier
6. Analyser : Qu'est-ce qui s'est passé ? Comment éviter ?

### Review Complète (30+ min)

1. Générer highlights
2. Copier `highlights.cfg` vers CS2
3. Charger démo + `exec highlights`
4. Utiliser F5 pour naviguer entre tous les moments
5. F6 pour ralenti sur les moments complexes
6. Prendre des notes pour chaque catégorie

### Review Ciblée

Utiliser le rapport modulaire pour focus sur un aspect :

```bash
# Focus économique uniquement
./run.sh
# Choisir option 4: Rapport modulaire
# Puis option 5: Analyse économique
```

## Priorités de Review

### Si tu as 10 minutes :
- ✅ Highlights critiques uniquement (🔴)
- ✅ Focus sur les 3 premiers

### Si tu as 20 minutes :
- ✅ Highlights critiques (🔴)
- ✅ Highlights importants (🟡)

### Si tu as 30+ minutes :
- ✅ Tous les highlights
- ✅ Inclure les exemples positifs (pour apprendre)

## Commandes CS2 Utiles

### Navigation
```
demo_gototick <tick>     # Jump to specific tick
demo_timescale 0.5       # Slow motion 0.5x
demo_timescale 0.25      # Very slow 0.25x
demo_timescale 1         # Normal speed
demo_pause               # Pause
demo_resume              # Resume
```

### Contrôles (Shift+F2)
- Ouvre le panneau de contrôle démo
- Permet navigation visuelle
- Affiche timeline du round

### Vision
```
sv_cheats 1                     # Enable cheats (demo only)
r_drawothermodels 2             # Wallhack (see enemies)
cl_draw_only_deathnotices 1     # Clean HUD
```

## Tips pour Review Efficace

### 1. Contexte d'abord
Avant de regarder le moment :
- Lis la description du highlight
- Note le contexte économique
- Identifie le round type (eco, full buy, etc.)

### 2. Multiples POV
Regarde le moment sous plusieurs angles :
- Ta POV (ce que tu voyais)
- POV de l'attaquant (pourquoi il a gagné)
- POV de ton équipe (auraient-ils pu trade ?)

### 3. Prends des Notes
Pour chaque highlight critique :
- Qu'est-ce qui s'est mal passé ?
- Quelle était l'alternative ?
- Comment éviter dans le futur ?

### 4. Patterns
Après review complète :
- Y a-t-il un pattern ? (ex: toujours mort à Long)
- Même type d'erreur répété ?
- Lien avec un des rapports modulaires ?

## Intégration avec d'autres Features

### Avec Heatmap
```bash
# 1. Générer highlights
# 2. Générer heatmap
# 3. Comparer les positions des morts évitables sur la heatmap
```

### Avec Rapport de Positionnement
```bash
# Si beaucoup de morts évitables dans une zone
# → Check le rapport positioning pour voir la K/D de cette zone
```

### Avec Rapport Économique
```bash
# Si beaucoup de pertes économiques
# → Check le rapport economy pour voir les patterns
```

## Troubleshooting

### Le script CS2 ne fonctionne pas
- Vérifie que `highlights.cfg` est dans `csgo/cfg/`
- Assure-toi d'avoir exec après avoir chargé la démo
- Teste avec `echo test` pour voir si la console fonctionne

### Pas de highlights générés
- Vérifie que le player name est exact (case-sensitive)
- La démo doit avoir au moins quelques morts/kills
- Essaye avec une démo de match complet

### Les ticks ne correspondent pas
- C'est normal si tu regardes depuis un autre POV
- Les ticks sont spécifiques à ta POV
- Utilise `demo_gototick` directement

## FAQ

**Q: Combien de highlights sont générés ?**  
A: Dépend de ton niveau, typiquement 5-15 moments par démo complète

**Q: Puis-je filtrer par catégorie ?**  
A: Oui, édite le fichier JSON ou utilise le système de priorités

**Q: Ça fonctionne avec les demos de matchmaking ?**  
A: Oui, tant que c'est un fichier .dem CS2

**Q: Les highlights remplacent-ils le rapport complet ?**  
A: Non, ils sont complémentaires. Highlights = review rapide, Rapport = analyse profonde

**Q: Combien de temps prend la génération ?**  
A: ~10-30 secondes selon la taille de la démo

## Prochaines Étapes

Après avoir reviewé tes highlights :

1. **Générer un rapport modulaire** ciblé sur ta plus grande faiblesse
2. **Travailler en DM** les points identifiés (ex: crosshair placement)
3. **Review régulièrement** (1 démo/semaine minimum)
4. **Comparer l'évolution** entre démos
