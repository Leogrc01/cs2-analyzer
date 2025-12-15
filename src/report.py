"""
CS2 Gap Report Generator - Detailed actionable reports
"""
from typing import Dict, Any, List
from pathlib import Path


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
    
