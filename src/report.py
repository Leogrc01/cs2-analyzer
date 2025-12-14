"""
CS2 Gap Report Generator - Creates readable text reports
"""
from typing import Dict, Any
from pathlib import Path


class ReportGenerator:
    """Generate readable reports from analysis results"""
    
    def __init__(self, analysis: Dict[str, Any], player_name: str):
        self.analysis = analysis
        self.player_name = player_name
        self.summary = analysis["summary"]
        self.priorities = analysis["priority"]
    
    def generate_console_report(self) -> str:
        """
        ÉTAPE 5: Generate a 30-second readable report
        
        Returns:
            Formatted text report string
        """
        lines = []
        lines.append("=" * 50)
        lines.append("CS2 GAP REPORT")
        lines.append(f"Joueur: {self.player_name}")
        lines.append("=" * 50)
        lines.append("")
        
        # Main stats
        lines.append("📊 STATISTIQUES")
        lines.append("-" * 50)
        lines.append(f"Morts évitables       : {self.summary['avoidable_deaths_pct']:.0f}%")
        lines.append(f"Duels sans avantage   : {self.summary['disadvantaged_duels_pct']:.0f}%")
        lines.append(f"Flash utiles          : {self.summary['useful_flashes_pct']:.0f}%")
        lines.append("")
        lines.append(f"Total kills           : {self.summary['total_kills']}")
        lines.append(f"Total deaths          : {self.summary['total_deaths']}")
        lines.append(f"K/D ratio             : {self._calculate_kd():.2f}")
        lines.append("")
        
        # Priorities
        lines.append("🎯 FOCUS NEXT GAMES")
        lines.append("-" * 50)
        for i, priority in enumerate(self.priorities, 1):
            lines.append(f"{i}. {priority}")
        lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
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
    
    def _calculate_kd(self) -> float:
        """Calculate K/D ratio"""
        kills = self.summary['total_kills']
        deaths = self.summary['total_deaths']
        return kills / deaths if deaths > 0 else kills
