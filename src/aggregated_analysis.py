"""
CS2 Aggregated Analysis - Analyze multiple demos and compute averages
"""
from typing import Dict, List, Any, Tuple
from pathlib import Path
import statistics


class AggregatedAnalyzer:
    """Analyze multiple demos and compute aggregated statistics"""
    
    def __init__(self):
        self.analyses = []
        self.demo_names = []
        self.map_name = None
    
    def add_analysis(self, analysis: Dict[str, Any], demo_name: str):
        """Add an analysis result to the aggregation"""
        self.analyses.append(analysis)
        self.demo_names.append(demo_name)
        
        # Set map name from first demo (should be same for all in folder)
        if not self.map_name:
            positioning = analysis.get('positioning', {})
            self.map_name = positioning.get('map_name', 'unknown')
    
    def compute_aggregated_stats(self) -> Dict[str, Any]:
        """
        Compute aggregated statistics across all demos
        
        Returns:
            Dictionary with averaged stats and trends
        """
        if not self.analyses:
            return {}
        
        return {
            'meta': self._compute_meta(),
            'summary': self._aggregate_summary(),
            'crosshair': self._aggregate_crosshair(),
            'deaths': self._aggregate_deaths(),
            'utility': self._aggregate_utility(),
            'economy': self._aggregate_economy(),
            'positioning': self._aggregate_positioning(),
            'priorities': self._aggregate_priorities(),
            'trends': self._compute_trends(),
            'best_worst': self._identify_best_worst_demos()
        }
    
    def _compute_meta(self) -> Dict[str, Any]:
        """Compute metadata about the aggregation"""
        return {
            'total_demos': len(self.analyses),
            'demo_names': self.demo_names,
            'map_name': self.map_name
        }
    
    def _aggregate_summary(self) -> Dict[str, Any]:
        """Aggregate summary statistics"""
        summaries = [a['summary'] for a in self.analyses]
        
        # Compute averages
        avg_kd = statistics.mean([s['kd_ratio'] for s in summaries])
        avg_hsr = statistics.mean([s['headshot_rate'] for s in summaries])
        avg_crosshair = statistics.mean([s['bad_crosshair_pct'] for s in summaries])
        avg_avoidable = statistics.mean([s['avoidable_deaths_pct'] for s in summaries])
        avg_no_advantage = statistics.mean([s['no_advantage_duels_pct'] for s in summaries])
        avg_flash_useful = statistics.mean([s['flash_useful_pct'] for s in summaries])
        avg_pop_flash = statistics.mean([s['pop_flash_pct'] for s in summaries])
        avg_crosshair_offset = statistics.mean([s['avg_crosshair_offset'] for s in summaries])
        
        # Totals
        total_kills = sum([s['total_kills'] for s in summaries])
        total_deaths = sum([s['total_deaths'] for s in summaries])
        total_flashes = sum([s['total_flashes'] for s in summaries])
        total_value_lost = sum([s['total_value_lost'] for s in summaries])
        avg_death_cost = statistics.mean([s['avg_death_cost'] for s in summaries])
        avg_expensive_deaths = statistics.mean([s['expensive_deaths_pct'] for s in summaries])
        
        # Standard deviations (consistency)
        std_kd = statistics.stdev([s['kd_ratio'] for s in summaries]) if len(summaries) > 1 else 0
        std_hsr = statistics.stdev([s['headshot_rate'] for s in summaries]) if len(summaries) > 1 else 0
        
        return {
            'avg_kd_ratio': round(avg_kd, 2),
            'std_kd_ratio': round(std_kd, 2),
            'avg_headshot_rate': round(avg_hsr, 1),
            'std_headshot_rate': round(std_hsr, 1),
            'avg_bad_crosshair_pct': round(avg_crosshair, 1),
            'avg_avoidable_deaths_pct': round(avg_avoidable, 1),
            'avg_no_advantage_duels_pct': round(avg_no_advantage, 1),
            'avg_flash_useful_pct': round(avg_flash_useful, 1),
            'avg_pop_flash_pct': round(avg_pop_flash, 1),
            'avg_crosshair_offset': round(avg_crosshair_offset, 1),
            'total_kills': total_kills,
            'total_deaths': total_deaths,
            'total_flashes': total_flashes,
            'total_value_lost': total_value_lost,
            'avg_death_cost': round(avg_death_cost, 0),
            'avg_expensive_deaths_pct': round(avg_expensive_deaths, 1),
            'consistency_kd': 'High' if std_kd < 0.3 else 'Medium' if std_kd < 0.6 else 'Low',
            'consistency_hsr': 'High' if std_hsr < 5 else 'Medium' if std_hsr < 10 else 'Low'
        }
    
    def _aggregate_crosshair(self) -> Dict[str, Any]:
        """Aggregate crosshair statistics"""
        crosshairs = [a['crosshair'] for a in self.analyses]
        
        avg_offset = statistics.mean([c['avg_offset'] for c in crosshairs])
        total_analyzed = sum([c['total_analyzed'] for c in crosshairs])
        total_bad = sum([c['bad_placement_count'] for c in crosshairs])
        
        # Collect all terrible placements
        all_terrible = []
        for c in crosshairs:
            all_terrible.extend(c.get('terrible_placements', []))
        
        # Sort and get worst
        all_terrible.sort(key=lambda x: x['offset'], reverse=True)
        
        return {
            'avg_offset': round(avg_offset, 1),
            'total_analyzed': total_analyzed,
            'total_bad_placement': total_bad,
            'bad_placement_pct': round((total_bad / total_analyzed * 100) if total_analyzed > 0 else 0, 1),
            'worst_placements': all_terrible[:10]  # Top 10 worst across all demos
        }
    
    def _aggregate_deaths(self) -> Dict[str, Any]:
        """Aggregate deaths statistics"""
        all_deaths_analyses = [a['deaths'] for a in self.analyses]
        
        total_deaths = sum([len(d) for d in all_deaths_analyses])
        total_avoidable = sum([len([x for x in d if x.get('is_avoidable')]) for d in all_deaths_analyses])
        total_no_advantage = sum([len([x for x in d if not x.get('had_any_advantage')]) for d in all_deaths_analyses])
        
        # Most common death weapons across all demos
        weapon_counts = {}
        for deaths in all_deaths_analyses:
            for death in deaths:
                weapon = death.get('weapon', 'unknown')
                weapon_counts[weapon] = weapon_counts.get(weapon, 0) + 1
        
        sorted_weapons = sorted(weapon_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_deaths': total_deaths,
            'total_avoidable': total_avoidable,
            'avoidable_pct': round((total_avoidable / total_deaths * 100) if total_deaths > 0 else 0, 1),
            'total_no_advantage': total_no_advantage,
            'no_advantage_pct': round((total_no_advantage / total_deaths * 100) if total_deaths > 0 else 0, 1),
            'most_common_death_weapons': sorted_weapons[:5]
        }
    
    def _aggregate_utility(self) -> Dict[str, Any]:
        """Aggregate utility statistics"""
        all_flashes = [a['flashes'] for a in self.analyses]
        
        total_flashes = sum([len(f) for f in all_flashes])
        total_useful = sum([len([x for x in f if x.get('is_useful')]) for f in all_flashes])
        total_pop = sum([len([x for x in f if x.get('is_pop_flash')]) for f in all_flashes])
        
        return {
            'total_flashes': total_flashes,
            'total_useful': total_useful,
            'useful_pct': round((total_useful / total_flashes * 100) if total_flashes > 0 else 0, 1),
            'total_pop_flashes': total_pop,
            'pop_flash_pct': round((total_pop / total_flashes * 100) if total_flashes > 0 else 0, 1)
        }
    
    def _aggregate_economy(self) -> Dict[str, Any]:
        """Aggregate economy statistics"""
        economies = [a['economy'] for a in self.analyses]
        
        total_value_lost = sum([e['summary']['total_value_lost'] for e in economies])
        avg_death_cost = statistics.mean([e['summary']['avg_death_cost'] for e in economies])
        avg_expensive_pct = statistics.mean([e['summary']['expensive_death_pct'] for e in economies])
        
        # Aggregate round type performance
        aggregated_round_types = {}
        for eco in economies:
            for buy_type, stats in eco.get('round_types', {}).items():
                if buy_type not in aggregated_round_types:
                    aggregated_round_types[buy_type] = {'deaths': 0, 'total_value_lost': 0}
                
                aggregated_round_types[buy_type]['deaths'] += stats.get('deaths', 0)
                aggregated_round_types[buy_type]['total_value_lost'] += stats.get('total_value_lost', 0)
        
        # Compute averages
        for buy_type in aggregated_round_types:
            deaths = aggregated_round_types[buy_type]['deaths']
            total_lost = aggregated_round_types[buy_type]['total_value_lost']
            aggregated_round_types[buy_type]['avg_value_lost'] = round(total_lost / deaths, 0) if deaths > 0 else 0
        
        return {
            'total_value_lost': total_value_lost,
            'avg_death_cost': round(avg_death_cost, 0),
            'avg_expensive_deaths_pct': round(avg_expensive_pct, 1),
            'round_types': aggregated_round_types
        }
    
    def _aggregate_positioning(self) -> Dict[str, Any]:
        """Aggregate positioning statistics"""
        positionings = [a['positioning'] for a in self.analyses]
        
        # Aggregate zone performance
        aggregated_zones = {}
        
        for pos in positionings:
            zone_perf = pos.get('zone_performance', {})
            for zone_name, stats in zone_perf.items():
                if zone_name not in aggregated_zones:
                    aggregated_zones[zone_name] = {'kills': 0, 'deaths': 0}
                
                aggregated_zones[zone_name]['kills'] += stats.get('kills', 0)
                aggregated_zones[zone_name]['deaths'] += stats.get('deaths', 0)
        
        # Compute K/D for each zone
        for zone in aggregated_zones:
            kills = aggregated_zones[zone]['kills']
            deaths = aggregated_zones[zone]['deaths']
            aggregated_zones[zone]['kd_ratio'] = round(kills / deaths, 2) if deaths > 0 else kills
            aggregated_zones[zone]['engagements'] = kills + deaths
        
        # Identify best and worst zones
        zones_with_stats = [(name, stats) for name, stats in aggregated_zones.items() if stats['engagements'] >= 3]
        zones_with_stats.sort(key=lambda x: x[1]['kd_ratio'])
        
        worst_zones = zones_with_stats[:3]
        best_zones = zones_with_stats[-3:]
        best_zones.reverse()
        
        return {
            'map_name': self.map_name,
            'zone_performance': aggregated_zones,
            'worst_zones': [{'zone': z[0], 'kd_ratio': z[1]['kd_ratio'], 'kills': z[1]['kills'], 'deaths': z[1]['deaths']} for z in worst_zones],
            'best_zones': [{'zone': z[0], 'kd_ratio': z[1]['kd_ratio'], 'kills': z[1]['kills'], 'deaths': z[1]['deaths']} for z in best_zones]
        }
    
    def _aggregate_priorities(self) -> List[Dict[str, Any]]:
        """Aggregate priorities across all demos"""
        # Count how often each priority category appears
        priority_counts = {}
        
        for analysis in self.analyses:
            for priority in analysis.get('priorities', []):
                category = priority['category']
                if category not in priority_counts:
                    priority_counts[category] = {'count': 0, 'total_severity': 0}
                
                priority_counts[category]['count'] += 1
                priority_counts[category]['total_severity'] += priority.get('severity', 0)
        
        # Compute averages and sort
        aggregated_priorities = []
        for category, data in priority_counts.items():
            avg_severity = data['total_severity'] / data['count']
            frequency = round((data['count'] / len(self.analyses) * 100), 0)
            
            aggregated_priorities.append({
                'category': category,
                'frequency': frequency,  # % of demos where this appears
                'avg_severity': round(avg_severity, 1),
                'appears_in': f"{data['count']}/{len(self.analyses)} demos"
            })
        
        aggregated_priorities.sort(key=lambda x: x['avg_severity'], reverse=True)
        
        return aggregated_priorities[:5]  # Top 5
    
    def _compute_trends(self) -> Dict[str, Any]:
        """Compute trends over time (assuming chronological order)"""
        if len(self.analyses) < 2:
            return {'available': False}
        
        summaries = [a['summary'] for a in self.analyses]
        
        # Compare first half vs second half
        mid = len(summaries) // 2
        first_half = summaries[:mid]
        second_half = summaries[mid:]
        
        avg_kd_first = statistics.mean([s['kd_ratio'] for s in first_half])
        avg_kd_second = statistics.mean([s['kd_ratio'] for s in second_half])
        
        avg_hsr_first = statistics.mean([s['headshot_rate'] for s in first_half])
        avg_hsr_second = statistics.mean([s['headshot_rate'] for s in second_half])
        
        avg_crosshair_first = statistics.mean([s['bad_crosshair_pct'] for s in first_half])
        avg_crosshair_second = statistics.mean([s['bad_crosshair_pct'] for s in second_half])
        
        return {
            'available': True,
            'kd_trend': 'Improving' if avg_kd_second > avg_kd_first else 'Declining' if avg_kd_second < avg_kd_first else 'Stable',
            'kd_change': round(avg_kd_second - avg_kd_first, 2),
            'hsr_trend': 'Improving' if avg_hsr_second > avg_hsr_first else 'Declining' if avg_hsr_second < avg_hsr_first else 'Stable',
            'hsr_change': round(avg_hsr_second - avg_hsr_first, 1),
            'crosshair_trend': 'Improving' if avg_crosshair_second < avg_crosshair_first else 'Declining' if avg_crosshair_second > avg_crosshair_first else 'Stable',
            'crosshair_change': round(avg_crosshair_second - avg_crosshair_first, 1)
        }
    
    def _identify_best_worst_demos(self) -> Dict[str, Any]:
        """Identify best and worst performing demos"""
        if not self.analyses:
            return {}
        
        summaries = [a['summary'] for a in self.analyses]
        
        # Best/worst by K/D
        kd_with_names = [(s['kd_ratio'], name) for s, name in zip(summaries, self.demo_names)]
        kd_with_names.sort(key=lambda x: x[0])
        
        # Best/worst by crosshair
        crosshair_with_names = [(s['bad_crosshair_pct'], name) for s, name in zip(summaries, self.demo_names)]
        crosshair_with_names.sort(key=lambda x: x[0])
        
        return {
            'best_kd': {'demo': kd_with_names[-1][1], 'value': kd_with_names[-1][0]},
            'worst_kd': {'demo': kd_with_names[0][1], 'value': kd_with_names[0][0]},
            'best_crosshair': {'demo': crosshair_with_names[0][1], 'value': crosshair_with_names[0][0]},
            'worst_crosshair': {'demo': crosshair_with_names[-1][1], 'value': crosshair_with_names[-1][0]}
        }
