"""
CS2 Elo Report Generator - Format Elo estimation results
"""
from typing import Dict, Any, List


class EloReportGenerator:
    """Generate readable Elo estimation reports"""
    
    def __init__(self, estimation: Dict[str, Any], player_name: str):
        self.estimation = estimation
        self.player_name = player_name
    
    def generate_report(self) -> str:
        """Generate complete Elo estimation report"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("   🎯 CS2 ELO/RANK ESTIMATION")
        lines.append("=" * 80)
        lines.append(f"👤 Player: {self.player_name}")
        lines.append("")
        
        # Estimated rank
        lines.extend(self._generate_rank_section())
        lines.append("")
        
        # Metric breakdown
        lines.extend(self._generate_metric_breakdown())
        lines.append("")
        
        # Strengths and weaknesses
        lines.extend(self._generate_strengths_weaknesses())
        lines.append("")
        
        # Progression path
        if self.estimation['progression']:
            lines.extend(self._generate_progression())
            lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("💡 NOTE: Cette estimation est basée sur tes performances dans les demos")
        lines.append("   analysées. Le rang réel peut varier selon les adversaires et la map.")
        lines.append("=" * 80)
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_rank_section(self) -> List[str]:
        """Generate estimated rank section"""
        lines = []
        
        rank = self.estimation['estimated_rank']
        elo = self.estimation['estimated_elo']
        elo_range = self.estimation['elo_range']
        label = self.estimation['label']
        confidence = self.estimation['confidence']
        
        lines.append("🏆 RANG ESTIMÉ")
        lines.append("-" * 80)
        lines.append(f"Rang: {label}")
        lines.append(f"Elo estimé: ~{elo} (range: {elo_range[0]}-{elo_range[1]})")
        lines.append(f"Confiance: {confidence}")
        
        # Context
        if confidence == 'Low':
            lines.append("")
            lines.append("⚠️  Confiance faible: Tes stats correspondent à plusieurs rangs.")
            lines.append("   Plus de demos amélioreront la précision.")
        elif confidence == 'Medium':
            lines.append("")
            lines.append("ℹ️  Confiance moyenne: Estimation basée sur plusieurs métriques.")
        else:
            lines.append("")
            lines.append("✅ Confiance haute: Tes stats correspondent bien à ce rang.")
        
        return lines
    
    def _generate_metric_breakdown(self) -> List[str]:
        """Generate detailed metric breakdown"""
        lines = []
        
        lines.append("📊 ANALYSE PAR MÉTRIQUE")
        lines.append("-" * 80)
        
        metrics = self.estimation['metric_breakdown']
        player_stats = self.estimation['player_stats']
        
        # Sort by score
        sorted_metrics = sorted(metrics.items(), key=lambda x: x[1], reverse=True)
        
        metric_info = {
            'kd_ratio': ('K/D Ratio', lambda v: f"{v:.2f}"),
            'headshot_rate': ('Headshot Rate', lambda v: f"{v:.1f}%"),
            'crosshair_offset': ('Crosshair Offset', lambda v: f"{v:.0f}°"),
            'bad_crosshair_pct': ('Bad Crosshair %', lambda v: f"{v:.0f}%"),
            'avoidable_deaths_pct': ('Avoidable Deaths %', lambda v: f"{v:.0f}%"),
            'flash_useful_pct': ('Flash Useful %', lambda v: f"{v:.0f}%"),
            'expensive_deaths_pct': ('Expensive Deaths %', lambda v: f"{v:.0f}%"),
            'consistency': ('Consistency (σ)', lambda v: f"{v:.2f}")
        }
        
        for metric, score in sorted_metrics:
            if metric not in metric_info:
                continue
            
            name, formatter = metric_info[metric]
            value = player_stats[metric]
            
            # Score indicator
            if score >= 85:
                indicator = "✅"
            elif score >= 70:
                indicator = "🟢"
            elif score >= 55:
                indicator = "🟡"
            else:
                indicator = "🔴"
            
            lines.append(f"{indicator} {name:25s}: {formatter(value):>8s} (score: {score:.0f}/100)")
        
        return lines
    
    def _generate_strengths_weaknesses(self) -> List[str]:
        """Generate strengths and weaknesses section"""
        lines = []
        
        strengths = self.estimation['strengths']
        weaknesses = self.estimation['weaknesses']
        
        if strengths:
            lines.append("💪 FORCES")
            lines.append("-" * 80)
            for strength in strengths:
                lines.append(f"  ✅ {strength}")
            lines.append("")
        
        if weaknesses:
            lines.append("⚠️  FAIBLESSES À TRAVAILLER")
            lines.append("-" * 80)
            for weakness in weaknesses:
                lines.append(f"  🔴 {weakness}")
        
        return lines
    
    def _generate_progression(self) -> List[str]:
        """Generate progression to next rank section"""
        lines = []
        
        progression = self.estimation['progression']
        
        lines.append(f"📈 PROGRESSION VERS {progression['next_label']}")
        lines.append("-" * 80)
        
        gaps = progression['gaps']
        
        # Sort by gap size (biggest gaps first)
        sorted_gaps = sorted(gaps.items(), key=lambda x: x[1]['gap'], reverse=True)
        
        metric_names = {
            'kd_ratio': 'K/D Ratio',
            'headshot_rate': 'Headshot Rate',
            'crosshair_offset': 'Crosshair Offset',
            'bad_crosshair_pct': 'Bad Crosshair %',
            'avoidable_deaths_pct': 'Avoidable Deaths %',
            'flash_useful_pct': 'Flash Useful %',
            'expensive_deaths_pct': 'Expensive Deaths %',
            'consistency': 'Consistency'
        }
        
        lines.append("Objectifs pour le rang suivant:")
        lines.append("")
        
        for metric, data in sorted_gaps:
            if data['status'] == 'already_there':
                continue
            
            name = metric_names.get(metric, metric)
            current = data['current']
            target = data['target']
            gap = data['gap']
            
            # Determine direction
            if metric in ['kd_ratio', 'headshot_rate', 'flash_useful_pct']:
                direction = "↑"
                text = f"{current:.1f} → {target:.1f} (+{gap:.1f})"
            else:
                direction = "↓"
                text = f"{current:.1f} → {target:.1f} (-{gap:.1f})"
            
            lines.append(f"  {direction} {name:25s}: {text}")
        
        # Already achieved
        already_there = [m for m, d in sorted_gaps if d['status'] == 'already_there']
        if already_there:
            lines.append("")
            lines.append("✅ Déjà au niveau du rang suivant:")
            for metric in already_there:
                name = metric_names.get(metric, metric)
                lines.append(f"  • {name}")
        
        return lines
