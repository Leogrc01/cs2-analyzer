"""
CS2 Positioning Analyzer - Zone-based performance analysis
"""
from typing import Dict, List, Any, Tuple
from collections import defaultdict


# Refined map zone coordinates based on actual CS2 map layouts
MAP_ZONES = {
    'de_dust2': [
        # Format: (min_x, max_x, min_y, max_y, zone_name)
        (-2600, -1800, 1400, 2600, "T Spawn"),
        (-1800, -800, 1400, 2600, "Long Doors"),
        (-800, 600, 1400, 2600, "Long"),
        (600, 1600, 1400, 2600, "A Site"),
        (1600, 2600, 1400, 2600, "CT Spawn"),
        
        (-2600, -1800, -600, 1400, "Tunnels"),
        (-1800, -800, -600, 1400, "Mid Doors"),
        (-800, 600, -600, 1400, "Mid"),
        (600, 1600, -600, 1400, "B Doors"),
        (1600, 2600, -600, 1400, "B Site"),
        
        (-2600, -1800, -2600, -600, "Lower Tunnels"),
        (-1800, 2600, -2600, -600, "Outside B"),
    ],
    'de_mirage': [
        (-3300, -2200, -1800, -300, "T Spawn"),
        (-2200, -1100, -1800, -300, "T Ramp"),
        (-1100, 200, -1800, -300, "Palace"),
        (200, 1400, -1800, -300, "A Site"),
        (1400, 2600, -1800, -300, "CT Spawn"),
        
        (-2200, -1100, -300, 1200, "Top Mid"),
        (-1100, 200, -300, 1200, "Mid"),
        (200, 1400, -300, 1200, "Connector"),
        
        (-2200, -1100, 1200, 2600, "Underpass"),
        (-1100, 200, 1200, 2600, "Apartments"),
        (200, 1400, 1200, 2600, "B Site"),
    ],
    'de_inferno': [
        (-2800, -1600, -2400, -800, "T Spawn"),
        (-1600, -400, -2400, -800, "Banana"),
        (-400, 800, -2400, -800, "B Site"),
        
        (-2800, -1600, -800, 800, "Second Mid"),
        (-1600, -400, -800, 800, "Mid"),
        (-400, 800, -800, 800, "Arch"),
        (800, 2000, -800, 800, "Pit"),
        
        (-1600, -400, 800, 2200, "Apartments"),
        (-400, 800, 800, 2200, "Balcony"),
        (800, 2000, 800, 2200, "A Site"),
        (2000, 3200, 800, 2200, "CT Spawn"),
    ],
}


class PositioningAnalyzer:
    """Analyze player positioning and zone-based performance"""
    
    def __init__(self, deaths: List[Dict[str, Any]], kills: List[Dict[str, Any]], map_name: str = "unknown"):
        self.deaths = deaths
        self.kills = kills
        self.map_name = map_name.lower()
        
    def analyze(self) -> Dict[str, Any]:
        """
        Run comprehensive positioning analysis
        
        Returns:
            Dictionary with zone-based performance metrics
        """
        # Analyze deaths by zone
        death_zones = self._analyze_death_zones()
        
        # Analyze kills by zone
        kill_zones = self._analyze_kill_zones()
        
        # Calculate performance metrics per zone
        zone_performance = self._calculate_zone_performance(death_zones, kill_zones)
        
        # Identify problematic zones
        danger_zones = self._identify_danger_zones(zone_performance)
        
        # Identify strong zones
        strong_zones = self._identify_strong_zones(zone_performance)
        
        # Generate heatmap data
        heatmap_data = self._generate_heatmap_data()
        
        return {
            'death_zones': death_zones,
            'kill_zones': kill_zones,
            'zone_performance': zone_performance,
            'danger_zones': danger_zones,
            'strong_zones': strong_zones,
            'heatmap_data': heatmap_data,
            'map_name': self.map_name
        }
    
    def _analyze_death_zones(self) -> Dict[str, Any]:
        """Analyze where player dies most often"""
        zone_deaths = defaultdict(lambda: {'count': 0, 'deaths': []})
        
        for death in self.deaths:
            position = death.get('position', {})
            zone = self._get_zone(position)
            
            zone_deaths[zone]['count'] += 1
            zone_deaths[zone]['deaths'].append({
                'tick': death['tick'],
                'attacker': death.get('attacker', 'Unknown'),
                'weapon': death.get('weapon', 'unknown'),
                'position': position
            })
        
        # Sort by death count
        sorted_zones = sorted(zone_deaths.items(), key=lambda x: x[1]['count'], reverse=True)
        
        return {
            'by_zone': dict(zone_deaths),
            'most_dangerous': sorted_zones[:3] if sorted_zones else [],
            'total_deaths': len(self.deaths)
        }
    
    def _analyze_kill_zones(self) -> Dict[str, Any]:
        """Analyze where player gets kills"""
        zone_kills = defaultdict(lambda: {'count': 0, 'kills': []})
        
        for kill in self.kills:
            position = kill.get('position', {})
            zone = self._get_zone(position)
            
            zone_kills[zone]['count'] += 1
            zone_kills[zone]['kills'].append({
                'tick': kill['tick'],
                'victim': kill.get('victim', 'Unknown'),
                'weapon': kill.get('weapon', 'unknown'),
                'headshot': kill.get('headshot', False),
                'position': position
            })
        
        # Sort by kill count
        sorted_zones = sorted(zone_kills.items(), key=lambda x: x[1]['count'], reverse=True)
        
        return {
            'by_zone': dict(zone_kills),
            'most_kills': sorted_zones[:3] if sorted_zones else [],
            'total_kills': len(self.kills)
        }
    
    def _calculate_zone_performance(self, death_zones: Dict, kill_zones: Dict) -> Dict[str, Any]:
        """Calculate K/D and performance per zone"""
        all_zones = set(death_zones['by_zone'].keys()) | set(kill_zones['by_zone'].keys())
        
        performance = {}
        for zone in all_zones:
            deaths = death_zones['by_zone'].get(zone, {}).get('count', 0)
            kills = kill_zones['by_zone'].get(zone, {}).get('count', 0)
            
            kd_ratio = kills / deaths if deaths > 0 else kills
            
            performance[zone] = {
                'kills': kills,
                'deaths': deaths,
                'kd_ratio': round(kd_ratio, 2),
                'engagements': kills + deaths,
                'performance': 'strong' if kd_ratio > 1.0 else 'weak' if kd_ratio < 0.5 else 'average'
            }
        
        return performance
    
    def _identify_danger_zones(self, zone_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify zones where player performs poorly"""
        danger_zones = []
        
        for zone, perf in zone_performance.items():
            # Danger zone criteria: low K/D AND significant engagement
            if perf['kd_ratio'] < 0.7 and perf['engagements'] >= 2:
                danger_zones.append({
                    'zone': zone,
                    'kd_ratio': perf['kd_ratio'],
                    'deaths': perf['deaths'],
                    'kills': perf['kills'],
                    'severity': self._calculate_danger_severity(perf)
                })
        
        # Sort by severity (most dangerous first)
        danger_zones.sort(key=lambda x: x['severity'], reverse=True)
        
        return danger_zones
    
    def _identify_strong_zones(self, zone_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify zones where player performs well"""
        strong_zones = []
        
        for zone, perf in zone_performance.items():
            # Strong zone criteria: good K/D AND engagement
            if perf['kd_ratio'] >= 1.5 and perf['engagements'] >= 2:
                strong_zones.append({
                    'zone': zone,
                    'kd_ratio': perf['kd_ratio'],
                    'deaths': perf['deaths'],
                    'kills': perf['kills']
                })
        
        # Sort by K/D
        strong_zones.sort(key=lambda x: x['kd_ratio'], reverse=True)
        
        return strong_zones
    
    def _calculate_danger_severity(self, performance: Dict[str, Any]) -> float:
        """Calculate how dangerous a zone is (0-100)"""
        # Weight deaths heavily, consider K/D
        death_weight = performance['deaths'] * 10
        kd_penalty = (1.0 - performance['kd_ratio']) * 20
        
        return min(100, death_weight + kd_penalty)
    
    def _generate_heatmap_data(self) -> Dict[str, List[Tuple[float, float]]]:
        """Generate coordinate-based heatmap data"""
        death_coords = []
        kill_coords = []
        
        for death in self.deaths:
            pos = death.get('position', {})
            if pos:
                death_coords.append((pos.get('x', 0), pos.get('y', 0)))
        
        for kill in self.kills:
            pos = kill.get('position', {})
            if pos:
                kill_coords.append((pos.get('x', 0), pos.get('y', 0)))
        
        return {
            'death_positions': death_coords,
            'kill_positions': kill_coords
        }
    
    def _get_zone(self, position: Dict[str, float]) -> str:
        """Get zone name for a position"""
        if not position:
            return "Unknown"
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        
        # Get zones for this map
        map_zones = MAP_ZONES.get(self.map_name, [])
        
        # Find matching zone
        for min_x, max_x, min_y, max_y, zone_name in map_zones:
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return zone_name
        
        return "Unknown"
    
    def generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate actionable positioning recommendations"""
        recommendations = []
        
        danger_zones = analysis_result.get('danger_zones', [])
        strong_zones = analysis_result.get('strong_zones', [])
        
        # Recommendations for danger zones
        if danger_zones:
            top_danger = danger_zones[0]
            zone = top_danger['zone']
            kd = top_danger['kd_ratio']
            deaths = top_danger['deaths']
            
            recommendations.append(
                f"🔴 ÉVITER {zone}: {deaths} morts, K/D {kd:.2f} - Jouer plus safe ou éviter cette zone"
            )
            
            if len(danger_zones) > 1:
                second_danger = danger_zones[1]
                recommendations.append(
                    f"⚠️  {second_danger['zone']} également problématique: {second_danger['deaths']} morts"
                )
        
        # Recommendations for strong zones
        if strong_zones:
            top_strong = strong_zones[0]
            zone = top_strong['zone']
            kd = top_strong['kd_ratio']
            
            recommendations.append(
                f"✅ EXPLOITER {zone}: K/D {kd:.2f} - Zone forte, jouer plus souvent ici"
            )
        
        # General positioning advice
        total_deaths = analysis_result['death_zones']['total_deaths']
        unique_death_zones = len([z for z in danger_zones if z['deaths'] > 0])
        
        if unique_death_zones > 5:
            recommendations.append(
                "💡 Morts dispersées sur plusieurs zones - Manque de consistency, focus sur 2-3 positions clés"
            )
        
        return recommendations
