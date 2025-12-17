"""
CS2 Gap Report Generator - Detailed actionable reports
"""
from typing import Dict, Any, List
from pathlib import Path
from src.elo_estimator import EloEstimator
from src.elo_report import EloReportGenerator


class ReportGenerator:
    """Generate detailed, actionable reports from analysis results"""
    
    def __init__(self, analysis: Dict[str, Any], player_name: str):
        self.analysis = analysis
        self.player_name = player_name
        self.summary = analysis["summary"]
        self.priorities = analysis["priorities"]
        self.crosshair = analysis.get("crosshair", {})
        self.deaths = analysis.get("deaths", [])
        self.kills = analysis.get("kills", [])
        self.flashes = analysis.get("flashes", [])
        self.economy = analysis.get("economy", {})
        self.positioning = analysis.get("positioning", {})
        self.positioning_recommendations = analysis.get("positioning_recommendations", [])
    
    def generate_console_report(self) -> str:
        """
        Generate comprehensive, actionable report
        
        Returns:
            Formatted text report string
        """
        lines = []
        
        # Header
        lines.append("\n" + "=" * 70)
        lines.append("   CS2 GAP ANALYZER - RAPPORT D'ANALYSE")
        lines.append(f"   Joueur: {self.player_name}")
        lines.append("=" * 70)
        lines.append("")
        
        # Overview section
        lines.extend(self._generate_overview())
        lines.append("")
        
        # Priorities section
        lines.extend(self._generate_priorities())
        lines.append("")
        
        # Detailed breakdowns
        lines.extend(self._generate_crosshair_details())
        lines.append("")
        
        lines.extend(self._generate_deaths_details())
        lines.append("")
        
        lines.extend(self._generate_utility_details())
        lines.append("")
        
        lines.extend(self._generate_economy_details())
        lines.append("")
        
        lines.extend(self._generate_positioning_details())
        lines.append("")
        
        # Elo estimation
        lines.extend(self._generate_elo_estimation())
        lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("💡 TIP: Focus sur 1-2 points à la fois pour amélioration maximale")
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_overview(self) -> List[str]:
        """Generate overview statistics section"""
        lines = []
        lines.append("📊 VUE D'ENSEMBLE")
        lines.append("-" * 70)
        
        kd = self.summary['kd_ratio']
        hsr = self.summary['headshot_rate']
        kills = self.summary['total_kills']
        deaths = self.summary['total_deaths']
        
        lines.append(f"K/D Ratio            : {kd:.2f}  ({kills} kills / {deaths} deaths)")
        lines.append(f"Headshot Rate        : {hsr:.1f}%")
        lines.append(f"Crosshair Placement  : {self.summary['bad_crosshair_pct']:.0f}% mauvais (avg offset: {self.summary['avg_crosshair_offset']:.0f}°)")
        lines.append(f"Morts évitables      : {self.summary['avoidable_deaths_pct']:.0f}%")
        lines.append(f"Duels désavantagés   : {self.summary['no_advantage_duels_pct']:.0f}%")
        lines.append(f"Flashes utiles       : {self.summary['flash_useful_pct']:.0f}% ({self.summary['pop_flash_pct']:.0f}% pop flashes)")
        lines.append(f"Impact économique    : {self.summary['total_value_lost']}$ perdus (avg: {self.summary['avg_death_cost']:.0f}$/mort)")
        lines.append(f"Morts coûteuses      : {self.summary['expensive_deaths_pct']:.0f}% (>3000$)")
        
        return lines
    
    def _generate_priorities(self) -> List[str]:
        """Generate priorities section with detailed recommendations"""
        lines = []
        lines.append("🎯 PRIORITÉS D'AMÉLIORATION (par ordre d'importance)")
        lines.append("-" * 70)
        
        if not self.priorities:
            lines.append("✨ Excellent niveau général !")
            return lines
        
        for i, priority in enumerate(self.priorities, 1):
            lines.append(f"\n{i}. {priority['category']}")
            lines.append(f"   {priority['stats']}")
            lines.append(f"   → {priority['recommendation']}")
        
        return lines
    
    def _generate_crosshair_details(self) -> List[str]:
        """Generate detailed crosshair placement analysis"""
        lines = []
        lines.append("🎯 DÉTAILS CROSSHAIR PLACEMENT")
        lines.append("-" * 70)
        
        avg_offset = self.crosshair.get('avg_offset', 0)
        bad_count = self.crosshair.get('bad_placement_count', 0)
        total = self.crosshair.get('total_analyzed', 0)
        
        if total == 0:
            lines.append("Pas assez de données pour analyse")
            return lines
        
        lines.append(f"Offset moyen         : {avg_offset:.1f}° (objectif: <20°)")
        lines.append(f"Mauvais placement    : {bad_count}/{total} duels (>30° flick requis)")
        
        # Show worst placements as examples
        terrible = self.crosshair.get('terrible_placements', [])
        if terrible:
            lines.append(f"\nPires exemples (>60° flick requis):")
            for ex in terrible[:3]:  # Top 3 worst
                lines.append(f"  • Vs {ex['attacker']}: {ex['offset']:.0f}° off target")
        
        return lines
    
    def _generate_deaths_details(self) -> List[str]:
        """Generate detailed deaths analysis"""
        lines = []
        lines.append("💀 ANALYSE DES MORTS")
        lines.append("-" * 70)
        
        avoidable_deaths = [d for d in self.deaths if d['is_avoidable']]
        no_advantage_deaths = [d for d in self.deaths if not d['had_any_advantage']]
        
        lines.append(f"Morts évitables      : {len(avoidable_deaths)}/{len(self.deaths)}")
        lines.append(f"Sans avantage        : {len(no_advantage_deaths)}/{len(self.deaths)}")
        
        # Show risk factors breakdown
        if avoidable_deaths:
            no_teammate_count = sum(1 for d in avoidable_deaths if d['risk_factors']['no_teammate'])
            no_utility_count = sum(1 for d in avoidable_deaths if d['risk_factors']['no_utility'])
            
            lines.append(f"\nFacteurs de risque principaux:")
            lines.append(f"  • Aucun coéquipier pour trade : {no_teammate_count}")
            lines.append(f"  • Aucune utility utilisée     : {no_utility_count}")
        
        return lines
    
    def _generate_utility_details(self) -> List[str]:
        """Generate detailed utility usage analysis"""
        lines = []
        lines.append("💥 UTILISATION DES UTILITAIRES")
        lines.append("-" * 70)
        
        total_flashes = len(self.flashes)
        if total_flashes == 0:
            lines.append("Aucune flash détectée")
            return lines
        
        useful_flashes = [f for f in self.flashes if f['is_useful']]
        pop_flashes = [f for f in self.flashes if f['is_pop_flash']]
        
        lines.append(f"Total flashes        : {total_flashes}")
        lines.append(f"Flashes utiles       : {len(useful_flashes)} ({len(useful_flashes)/total_flashes*100:.0f}%)")
        lines.append(f"Pop flashes          : {len(pop_flashes)} ({len(pop_flashes)/total_flashes*100:.0f}%)")
        
        # Flash effectiveness breakdown
        hit_enemy = sum(1 for f in self.flashes if f['hit_someone'])
        followed_kill = sum(1 for f in self.flashes if f['followed_by_kill'])
        
        lines.append(f"\nEfficacité:")
        lines.append(f"  • Ennemis flashés (>1s)      : {hit_enemy}")
        lines.append(f"  • Kill dans les 3s après     : {followed_kill}")
        
        return lines
    
    def _generate_economy_details(self) -> List[str]:
        """Generate detailed economic analysis"""
        lines = []
        lines.append("💰 ANALYSE ÉCONOMIQUE")
        lines.append("-" * 70)
        
        if not self.economy:
            lines.append("Pas de données économiques")
            return lines
        
        eco_summary = self.economy.get('summary', {})
        eco_discipline = self.economy.get('eco_discipline', {})
        round_types = self.economy.get('round_types', {})
        
        # Overall stats
        total_lost = eco_summary.get('total_value_lost', 0)
        avg_cost = eco_summary.get('avg_death_cost', 0)
        expensive_deaths = eco_summary.get('expensive_deaths', 0)
        
        lines.append(f"Valeur totale perdue : {total_lost}$")
        lines.append(f"Coût moyen par mort  : {avg_cost:.0f}$")
        lines.append(f"Morts coûteuses      : {expensive_deaths} (>3000$)")
        
        # Eco discipline
        high_value_deaths = eco_discipline.get('high_value_deaths', 0)
        rifle_deaths = eco_discipline.get('rifle_deaths', 0)
        awp_deaths = eco_discipline.get('awp_deaths', 0)
        
        lines.append(f"\nDiscipline économique:")
        lines.append(f"  • Morts avec équipement cher (>3500$): {high_value_deaths}")
        lines.append(f"  • Morts avec rifle               : {rifle_deaths}")
        lines.append(f"  • Morts avec AWP                 : {awp_deaths}")
        
        # Worst losses
        worst = eco_discipline.get('worst_losses', [])
        if worst:
            lines.append(f"\nPires pertes économiques:")
            for loss in worst[:3]:
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
        
        return lines
    
    def _generate_positioning_details(self) -> List[str]:
        """Generate detailed positioning analysis"""
        lines = []
        lines.append("🗺️  ANALYSE DE POSITIONNEMENT")
        lines.append("-" * 70)
        
        if not self.positioning:
            lines.append("Pas de données de positionnement")
            return lines
        
        map_name = self.positioning.get('map_name', 'unknown')
        death_zones = self.positioning.get('death_zones', {})
        kill_zones = self.positioning.get('kill_zones', {})
        zone_performance = self.positioning.get('zone_performance', {})
        danger_zones = self.positioning.get('danger_zones', [])
        strong_zones = self.positioning.get('strong_zones', [])
        
        lines.append(f"Map: {map_name}")
        lines.append("")
        
        # Most dangerous zones
        most_dangerous = death_zones.get('most_dangerous', [])
        if most_dangerous:
            lines.append("Zones les plus dangereuses:")
            for zone_name, data in most_dangerous[:3]:
                count = data['count']
                perf = zone_performance.get(zone_name, {})
                kd = perf.get('kd_ratio', 0)
                lines.append(f"  • {zone_name}: {count} morts (K/D {kd:.2f})")
            lines.append("")
        
        # Strong zones
        if strong_zones:
            lines.append("Zones performantes:")
            for zone_info in strong_zones[:3]:
                zone = zone_info['zone']
                kd = zone_info['kd_ratio']
                kills = zone_info['kills']
                deaths = zone_info['deaths']
                lines.append(f"  • {zone}: K/D {kd:.2f} ({kills}K/{deaths}D)")
            lines.append("")
        
        # Recommendations
        if self.positioning_recommendations:
            lines.append("Recommandations:")
            for rec in self.positioning_recommendations:
                lines.append(f"  {rec}")
        
        return lines
    
    def _generate_elo_estimation(self) -> List[str]:
        """Generate Elo/Rank estimation section"""
        lines = []
        lines.append("🎯 ESTIMATION DE RANG/ELO")
        lines.append("-" * 70)
        
        try:
            estimator = EloEstimator(self.analysis)
            estimation = estimator.estimate_rank()
            
            # Quick summary
            lines.append(f"Rang estimé: {estimation['label']}")
            lines.append(f"Elo estimé: ~{estimation['estimated_elo']}")
            lines.append(f"Confiance: {estimation['confidence']}")
            
            # Strengths/Weaknesses
            if estimation['strengths']:
                lines.append(f"\n💪 Forces: {', '.join(estimation['strengths'])}")
            if estimation['weaknesses']:
                lines.append(f"⚠️  Faiblesses: {', '.join(estimation['weaknesses'])}")
            
            lines.append("\n💡 Pour un rapport Elo complet, utilise le rapport modulaire 'priorities'")
            
        except Exception as e:
            lines.append(f"⚠️  Impossible d'estimer le rang: {e}")
        
        return lines
    
    def save_report(self, output_path: str):
        """Save report to text file"""
        report = self.generate_console_report()
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {output_path}")
    
    def print_report(self):
        """Print report to console"""
        print(self.generate_console_report())
    
