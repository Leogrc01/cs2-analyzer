"""
Modular Report Generator - Generate specific sections of analysis
"""
from typing import Dict, Any, List
from pathlib import Path
from src.elo_estimator import EloEstimator
from src.elo_report import EloReportGenerator


class ModularReportGenerator:
    """Generate specific sections of analysis reports"""
    
    def __init__(self, analysis: Dict[str, Any], player_name: str):
        self.analysis = analysis
        self.player_name = player_name
        self.summary = analysis.get("summary", {})
        self.priorities = analysis.get("priorities", [])
        self.crosshair = analysis.get("crosshair", {})
        self.deaths = analysis.get("deaths", [])
        self.kills = analysis.get("kills", [])
        self.flashes = analysis.get("flashes", [])
        self.economy = analysis.get("economy", {})
        self.positioning = analysis.get("positioning", {})
        self.positioning_recommendations = analysis.get("positioning_recommendations", [])
    
    def generate_section(self, section_name: str) -> str:
        """
        Generate a specific section of the report
        
        Args:
            section_name: Name of section to generate
                         ('overview', 'crosshair', 'deaths', 'economy', 'positioning', 'priorities')
        
        Returns:
            Formatted section text
        """
        sections = {
            'overview': self._generate_overview,
            'crosshair': self._generate_crosshair,
            'deaths': self._generate_deaths,
            'utility': self._generate_utility,
            'economy': self._generate_economy,
            'positioning': self._generate_positioning,
            'priorities': self._generate_priorities,
            'elo': self._generate_elo
        }
        
        if section_name not in sections:
            return f"❌ Section inconnue: {section_name}\n"
        
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append(f"   RAPPORT: {section_name.upper()}")
        lines.append(f"   Joueur: {self.player_name}")
        lines.append("=" * 70)
        lines.append("")
        
        section_func = sections[section_name]
        lines.extend(section_func())
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_overview(self) -> List[str]:
        """Generate overview section"""
        lines = []
        lines.append("📊 VUE D'ENSEMBLE")
        lines.append("-" * 70)
        
        kd = self.summary.get('kd_ratio', 0)
        hsr = self.summary.get('headshot_rate', 0)
        kills = self.summary.get('total_kills', 0)
        deaths = self.summary.get('total_deaths', 0)
        
        lines.append(f"K/D Ratio            : {kd:.2f}  ({kills} kills / {deaths} deaths)")
        lines.append(f"Headshot Rate        : {hsr:.1f}%")
        lines.append(f"Crosshair Placement  : {self.summary.get('bad_crosshair_pct', 0):.0f}% mauvais (avg offset: {self.summary.get('avg_crosshair_offset', 0):.0f}°)")
        lines.append(f"Morts évitables      : {self.summary.get('avoidable_deaths_pct', 0):.0f}%")
        lines.append(f"Duels désavantagés   : {self.summary.get('no_advantage_duels_pct', 0):.0f}%")
        lines.append(f"Flashes utiles       : {self.summary.get('flash_useful_pct', 0):.0f}% ({self.summary.get('pop_flash_pct', 0):.0f}% pop flashes)")
        lines.append(f"Impact économique    : {self.summary.get('total_value_lost', 0)}$ perdus (avg: {self.summary.get('avg_death_cost', 0):.0f}$/mort)")
        lines.append(f"Morts coûteuses      : {self.summary.get('expensive_deaths_pct', 0):.0f}% (>3000$)")
        
        return lines
    
    def _generate_crosshair(self) -> List[str]:
        """Generate crosshair placement section"""
        lines = []
        lines.append("🎯 CROSSHAIR PLACEMENT")
        lines.append("-" * 70)
        
        avg_offset = self.crosshair.get('avg_offset', 0)
        bad_count = self.crosshair.get('bad_placement_count', 0)
        total = self.crosshair.get('total_analyzed', 0)
        
        if total == 0:
            lines.append("Pas assez de données pour analyse")
            return lines
        
        lines.append(f"Offset moyen         : {avg_offset:.1f}° (objectif: <20°)")
        lines.append(f"Mauvais placement    : {bad_count}/{total} duels (>30° flick requis)")
        lines.append(f"Pourcentage bon      : {((total-bad_count)/total*100):.0f}%")
        
        # Show worst placements
        terrible = self.crosshair.get('terrible_placements', [])
        if terrible:
            lines.append(f"\nPires exemples (>60° flick requis):")
            for ex in terrible[:5]:
                lines.append(f"  • Vs {ex['attacker']}: {ex['offset']:.0f}° off target (tick {ex['tick']})")
        
        bad = self.crosshair.get('bad_placements', [])
        if bad and not terrible:
            lines.append(f"\nMauvais placements (30-60°):")
            for ex in bad[:5]:
                lines.append(f"  • Vs {ex['attacker']}: {ex['offset']:.0f}° off target (tick {ex['tick']})")
        
        lines.append("\n💡 RECOMMANDATION:")
        if avg_offset > 40:
            lines.append("  → Focus DM avec concentration sur pre-aim")
            lines.append("  → Apprendre les angles communs de chaque map")
        elif avg_offset > 25:
            lines.append("  → Bon niveau, continuer le pre-aim training")
            lines.append("  → Focus sur anticipation des positions ennemies")
        else:
            lines.append("  → Excellent pre-aim ! Maintenir avec DM régulier")
        
        return lines
    
    def _generate_deaths(self) -> List[str]:
        """Generate deaths analysis section"""
        lines = []
        lines.append("💀 ANALYSE DES MORTS")
        lines.append("-" * 70)
        
        avoidable_deaths = [d for d in self.deaths if d.get('is_avoidable')]
        no_advantage_deaths = [d for d in self.deaths if not d.get('had_any_advantage')]
        
        total = len(self.deaths)
        lines.append(f"Total morts          : {total}")
        lines.append(f"Morts évitables      : {len(avoidable_deaths)}/{total} ({len(avoidable_deaths)/total*100:.0f}%)")
        lines.append(f"Sans avantage        : {len(no_advantage_deaths)}/{total} ({len(no_advantage_deaths)/total*100:.0f}%)")
        
        # Risk factors breakdown
        if avoidable_deaths:
            no_teammate_count = sum(1 for d in avoidable_deaths if d.get('risk_factors', {}).get('no_teammate'))
            no_utility_count = sum(1 for d in avoidable_deaths if d.get('risk_factors', {}).get('no_utility'))
            
            lines.append(f"\nFacteurs de risque principaux:")
            lines.append(f"  • Aucun coéquipier pour trade : {no_teammate_count}")
            lines.append(f"  • Aucune utility utilisée     : {no_utility_count}")
        
        # Most common death weapons
        weapons = {}
        for death in self.deaths:
            weapon = death.get('weapon', 'unknown')
            weapons[weapon] = weapons.get(weapon, 0) + 1
        
        if weapons:
            lines.append(f"\nArmes les plus mortelles:")
            sorted_weapons = sorted(weapons.items(), key=lambda x: x[1], reverse=True)
            for weapon, count in sorted_weapons[:5]:
                lines.append(f"  • {weapon}: {count} morts ({count/total*100:.0f}%)")
        
        lines.append("\n💡 RECOMMANDATION:")
        avoid_pct = len(avoidable_deaths) / total * 100 if total > 0 else 0
        if avoid_pct > 50:
            lines.append("  → Priorité HAUTE: Jouer avec équipe, utiliser utility")
            lines.append("  → Éviter les peeks solitaires sans info")
        elif avoid_pct > 30:
            lines.append("  → Améliorer la communication avec l'équipe")
            lines.append("  → Flash avant peek dans situations à risque")
        else:
            lines.append("  → Bon jeu d'équipe ! Continuer ainsi")
        
        return lines
    
    def _generate_utility(self) -> List[str]:
        """Generate utility usage section"""
        lines = []
        lines.append("💥 UTILISATION DES UTILITAIRES")
        lines.append("-" * 70)
        
        total_flashes = len(self.flashes)
        if total_flashes == 0:
            lines.append("Aucune flash détectée")
            return lines
        
        useful_flashes = [f for f in self.flashes if f.get('is_useful')]
        pop_flashes = [f for f in self.flashes if f.get('is_pop_flash')]
        
        lines.append(f"Total flashes        : {total_flashes}")
        lines.append(f"Flashes utiles       : {len(useful_flashes)} ({len(useful_flashes)/total_flashes*100:.0f}%)")
        lines.append(f"Pop flashes          : {len(pop_flashes)} ({len(pop_flashes)/total_flashes*100:.0f}%)")
        
        # Flash effectiveness breakdown
        hit_enemy = sum(1 for f in self.flashes if f.get('hit_someone'))
        followed_kill = sum(1 for f in self.flashes if f.get('followed_by_kill'))
        
        lines.append(f"\nEfficacité:")
        lines.append(f"  • Ennemis flashés (>1s)      : {hit_enemy} ({hit_enemy/total_flashes*100:.0f}%)")
        lines.append(f"  • Kill dans les 3s après     : {followed_kill} ({followed_kill/total_flashes*100:.0f}%)")
        
        lines.append("\n💡 RECOMMANDATION:")
        useful_pct = len(useful_flashes) / total_flashes * 100 if total_flashes > 0 else 0
        if useful_pct < 40:
            lines.append("  → Priorité HAUTE: Apprendre les flashes de chaque map")
            lines.append("  → Ne flash que pour créer avantage, pas au hasard")
        elif useful_pct < 60:
            lines.append("  → Améliorer le timing des flashes")
            lines.append("  → Apprendre plus de pop flashes")
        else:
            lines.append("  → Excellente utilisation ! Continuer")
        
        return lines
    
    def _generate_economy(self) -> List[str]:
        """Generate economy section"""
        lines = []
        lines.append("💰 ANALYSE ÉCONOMIQUE")
        lines.append("-" * 70)
        
        if not self.economy:
            lines.append("Pas de données économiques")
            return lines
        
        eco_summary = self.economy.get('summary', {})
        eco_discipline = self.economy.get('eco_discipline', {})
        round_types = self.economy.get('round_types', {})
        
        total_lost = eco_summary.get('total_value_lost', 0)
        avg_cost = eco_summary.get('avg_death_cost', 0)
        expensive_deaths = eco_summary.get('expensive_deaths', 0)
        total_deaths = eco_summary.get('total_deaths', 0)
        
        lines.append(f"Valeur totale perdue : {total_lost}$")
        lines.append(f"Coût moyen par mort  : {avg_cost:.0f}$")
        lines.append(f"Morts coûteuses      : {expensive_deaths}/{total_deaths} (>3000$)")
        
        # Eco discipline
        high_value_deaths = eco_discipline.get('high_value_deaths', 0)
        rifle_deaths = eco_discipline.get('rifle_deaths', 0)
        awp_deaths = eco_discipline.get('awp_deaths', 0)
        
        lines.append(f"\nDiscipline économique:")
        lines.append(f"  • Morts avec équipement cher (>3500$): {high_value_deaths}")
        lines.append(f"  • Morts avec rifle                  : {rifle_deaths}")
        lines.append(f"  • Morts avec AWP                    : {awp_deaths}")
        
        # Worst losses
        worst = eco_discipline.get('worst_losses', [])
        if worst:
            lines.append(f"\nPires pertes économiques:")
            for loss in worst[:5]:
                weapon = loss['weapon']
                value = loss['total_value']
                attacker = loss['attacker']
                lines.append(f"  • {value}$ ({weapon}) vs {attacker}")
        
        # Round type breakdown
        if round_types:
            lines.append(f"\nPerformance par type de round:")
            for buy_type, stats in round_types.items():
                deaths = stats.get('deaths', 0)
                avg_lost = stats.get('avg_value_lost', 0)
                if deaths > 0:
                    buy_label = {
                        'full_buy': 'Full Buy',
                        'force_buy': 'Force Buy',
                        'eco': 'Eco',
                        'pistol': 'Pistol'
                    }.get(buy_type, buy_type)
                    lines.append(f"  • {buy_label:12s}: {deaths} morts (avg {avg_lost:.0f}$/mort)")
        
        lines.append("\n💡 RECOMMANDATION:")
        expensive_pct = expensive_deaths / total_deaths * 100 if total_deaths > 0 else 0
        if expensive_pct > 60:
            lines.append("  → Priorité HAUTE: Préserver équipement cher")
            lines.append("  → Jouer plus safe en full buy, éviter peeks risqués")
        elif expensive_pct > 40:
            lines.append("  → Améliorer discipline économique")
            lines.append("  → Drop équipement avant mort si possible")
        else:
            lines.append("  → Bonne discipline ! Continuer")
        
        return lines
    
    def _generate_positioning(self) -> List[str]:
        """Generate positioning section"""
        lines = []
        lines.append("🗺️  ANALYSE DE POSITIONNEMENT")
        lines.append("-" * 70)
        
        if not self.positioning:
            lines.append("Pas de données de positionnement")
            return lines
        
        map_name = self.positioning.get('map_name', 'unknown')
        death_zones = self.positioning.get('death_zones', {})
        zone_performance = self.positioning.get('zone_performance', {})
        danger_zones = self.positioning.get('danger_zones', [])
        strong_zones = self.positioning.get('strong_zones', [])
        
        lines.append(f"Map: {map_name}")
        lines.append("")
        
        # Dangerous zones
        most_dangerous = death_zones.get('most_dangerous', [])
        if most_dangerous:
            lines.append("Zones les plus dangereuses:")
            for zone_name, data in most_dangerous[:5]:
                count = data['count']
                perf = zone_performance.get(zone_name, {})
                kd = perf.get('kd_ratio', 0)
                kills = perf.get('kills', 0)
                deaths = perf.get('deaths', 0)
                lines.append(f"  • {zone_name:20s}: {count} morts (K/D {kd:.2f}, {kills}K/{deaths}D)")
            lines.append("")
        
        # Strong zones
        if strong_zones:
            lines.append("Zones performantes:")
            for zone_info in strong_zones[:5]:
                zone = zone_info['zone']
                kd = zone_info['kd_ratio']
                kills = zone_info['kills']
                deaths = zone_info['deaths']
                lines.append(f"  • {zone:20s}: K/D {kd:.2f} ({kills}K/{deaths}D)")
            lines.append("")
        
        # Danger zones (low K/D)
        if danger_zones:
            lines.append("⚠️  Zones à éviter (K/D faible):")
            for zone_info in danger_zones[:3]:
                zone = zone_info['zone']
                kd = zone_info['kd_ratio']
                severity = zone_info.get('severity', 0)
                lines.append(f"  • {zone:20s}: K/D {kd:.2f} (sévérité: {severity:.1f})")
            lines.append("")
        
        # Recommendations
        if self.positioning_recommendations:
            lines.append("💡 RECOMMANDATIONS:")
            for rec in self.positioning_recommendations:
                lines.append(f"  {rec}")
        
        return lines
    
    def _generate_priorities(self) -> List[str]:
        """Generate priorities section"""
        lines = []
        lines.append("🎯 PRIORITÉS D'AMÉLIORATION")
        lines.append("-" * 70)
        
        if not self.priorities:
            lines.append("✨ Excellent niveau général !")
            lines.append("Continue ton bon travail et maintiens la consistency")
            return lines
        
        lines.append("Top 3 des points à travailler (par ordre d'importance):")
        lines.append("")
        
        for i, priority in enumerate(self.priorities, 1):
            lines.append(f"{i}. {priority['category']}")
            lines.append(f"   {priority['stats']}")
            lines.append(f"   → {priority['recommendation']}")
            lines.append(f"   Sévérité: {priority['severity']:.0f}%")
            lines.append("")
        
        lines.append("💡 TIP: Focus sur le point #1 pour impact maximal")
        
        return lines
    
    def _generate_elo(self) -> List[str]:
        """Generate Elo estimation section"""
        lines = []
        lines.append("🎯 ESTIMATION DE RANG/ELO")
        lines.append("-" * 70)
        
        try:
            estimator = EloEstimator(self.analysis)
            estimation = estimator.estimate_rank()
            
            # Use the full Elo report generator
            elo_report_gen = EloReportGenerator(estimation, self.player_name)
            full_report = elo_report_gen.generate_report()
            
            # Extract just the body (skip the header)
            report_lines = full_report.split('\n')
            # Skip first 4 lines (header) and last 4 lines (footer)
            body_lines = report_lines[4:-4]
            
            lines.extend(body_lines)
            
        except Exception as e:
            lines.append(f"⚠️  Impossible d'estimer le rang: {e}")
            lines.append("")
            lines.append("Vérifie que les données d'analyse sont complètes.")
        
        return lines
    
    def save_section(self, section_name: str, output_path: str):
        """Save a specific section to file"""
        report = self.generate_section(section_name)
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Section '{section_name}' saved to: {output_path}")
    
    def print_section(self, section_name: str):
        """Print a specific section to console"""
        print(self.generate_section(section_name))
