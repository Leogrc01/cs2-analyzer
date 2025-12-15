"""
CS2 Gap Analyzer - Advanced analysis for gameplay improvement
"""
from typing import Dict, List, Any, Tuple
from src.geometry import (
    calculate_crosshair_offset_angle,
    is_in_fov,
    line_of_sight_clear,
    calculate_distance
)
from src.economy import EconomyAnalyzer
from src.positioning import PositioningAnalyzer


class GapAnalyzer:
    """Advanced gameplay analyzer with crosshair placement and precise metrics"""
    
    def __init__(self, events: Dict[str, List[Dict[str, Any]]]):
        self.deaths = events.get("deaths", [])
        self.kills = events.get("kills", [])
        self.flashes = events.get("flashes", [])
        self.map_name = events.get("map_name", "unknown")
        
        # Thresholds for analysis
        self.CROSSHAIR_BAD_THRESHOLD = 30.0  # degrees
        self.CROSSHAIR_TERRIBLE_THRESHOLD = 60.0  # degrees
        self.TRADE_DISTANCE = 800  # CS2 units
        self.TICKS_3_SECONDS = 192
        self.TICKS_5_SECONDS = 320
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run comprehensive gameplay analysis
        
        Returns:
            Dictionary with precise analysis results and actionable recommendations
        """
        # Core analyses
        crosshair_analysis = self.analyze_crosshair_placement()
        deaths_analysis = self.analyze_deaths_advanced()
        kills_analysis = self.analyze_kills_advanced()
        flash_analysis = self.analyze_flash_effectiveness_advanced()
        
        # Economic analysis
        economy_analyzer = EconomyAnalyzer(self.deaths, self.kills)
        economy_analysis = economy_analyzer.analyze()
        
        # Positioning analysis
        positioning_analyzer = PositioningAnalyzer(self.deaths, self.kills, self.map_name)
        positioning_analysis = positioning_analyzer.analyze()
        positioning_recommendations = positioning_analyzer.generate_recommendations(positioning_analysis)
        
        # Calculate key percentages
        total_deaths = len(self.deaths)
        total_kills = len(self.kills)
        total_flashes = len(self.flashes)
        
        # Crosshair placement stats
        bad_crosshair_count = crosshair_analysis['bad_placement_count']
        bad_crosshair_pct = (bad_crosshair_count / total_deaths * 100) if total_deaths > 0 else 0
        
        # Deaths stats
        avoidable_count = len([d for d in deaths_analysis if d['is_avoidable']])
        avoidable_pct = (avoidable_count / total_deaths * 100) if total_deaths > 0 else 0
        
        no_advantage_count = len([d for d in deaths_analysis if not d['had_any_advantage']])
        no_advantage_pct = (no_advantage_count / total_deaths * 100) if total_deaths > 0 else 0
        
        # Flash stats
        good_flashes = len([f for f in flash_analysis if f['is_useful']])
        flash_useful_pct = (good_flashes / total_flashes * 100) if total_flashes > 0 else 0
        
        pop_flashes = len([f for f in flash_analysis if f['is_pop_flash']])
        pop_flash_pct = (pop_flashes / total_flashes * 100) if total_flashes > 0 else 0
        
        # Headshot rate
        headshot_kills = len([k for k in self.kills if k.get('headshot', False)])
        hsr = (headshot_kills / total_kills * 100) if total_kills > 0 else 0
        
        # Generate prioritized recommendations
        priorities = self._determine_priorities(
            bad_crosshair_pct,
            avoidable_pct,
            no_advantage_pct,
            flash_useful_pct,
            pop_flash_pct,
            hsr,
            economy_analysis['summary']['expensive_death_pct']
        )
        
        return {
            "summary": {
                "total_kills": total_kills,
                "total_deaths": total_deaths,
                "kd_ratio": round(total_kills / total_deaths, 2) if total_deaths > 0 else total_kills,
                "headshot_rate": round(hsr, 1),
                "bad_crosshair_pct": round(bad_crosshair_pct, 1),
                "avoidable_deaths_pct": round(avoidable_pct, 1),
                "no_advantage_duels_pct": round(no_advantage_pct, 1),
                "flash_useful_pct": round(flash_useful_pct, 1),
                "pop_flash_pct": round(pop_flash_pct, 1),
                "avg_crosshair_offset": round(crosshair_analysis['avg_offset'], 1),
                "total_flashes": total_flashes,
                "total_value_lost": economy_analysis['summary']['total_value_lost'],
                "avg_death_cost": economy_analysis['summary']['avg_death_cost'],
                "expensive_deaths_pct": economy_analysis['summary']['expensive_death_pct']
            },
            "crosshair": crosshair_analysis,
            "deaths": deaths_analysis,
            "kills": kills_analysis,
            "flashes": flash_analysis,
            "economy": economy_analysis,
            "positioning": positioning_analysis,
            "positioning_recommendations": positioning_recommendations,
            "priorities": priorities
        }
    
    def analyze_crosshair_placement(self) -> Dict[str, Any]:
        """
        Analyze crosshair placement by measuring angle between crosshair and enemy position at death
        
        Returns:
            Dict with crosshair placement statistics
        """
        offsets = []
        bad_placements = []
        terrible_placements = []
        
        for death in self.deaths:
            player_pos = death.get('position', {})
            attacker_pos = death.get('attacker_position', {})
            pitch = death.get('pitch', 0.0)
            yaw = death.get('yaw', 0.0)
            
            # Skip if missing data
            if not player_pos or not attacker_pos:
                continue
            
            # Calculate angle between crosshair and attacker position
            offset = calculate_crosshair_offset_angle(player_pos, pitch, yaw, attacker_pos)
            offsets.append(offset)
            
            # Categorize placement quality
            if offset > self.CROSSHAIR_TERRIBLE_THRESHOLD:
                terrible_placements.append({
                    'tick': death['tick'],
                    'offset': round(offset, 1),
                    'attacker': death.get('attacker', 'Unknown')
                })
            elif offset > self.CROSSHAIR_BAD_THRESHOLD:
                bad_placements.append({
                    'tick': death['tick'],
                    'offset': round(offset, 1),
                    'attacker': death.get('attacker', 'Unknown')
                })
        
        avg_offset = sum(offsets) / len(offsets) if offsets else 0
        bad_count = len([o for o in offsets if o > self.CROSSHAIR_BAD_THRESHOLD])
        
        return {
            'avg_offset': avg_offset,
            'bad_placement_count': bad_count,
            'terrible_placements': terrible_placements,
            'bad_placements': bad_placements,
            'total_analyzed': len(offsets)
        }
    
    def analyze_deaths_advanced(self) -> List[Dict[str, Any]]:
        """
        Advanced death analysis with real metrics
        
        Death is avoidable if multiple risk factors present:
        - No teammates nearby for trade
        - No utility usage before death
        - Bad positioning (isolated)
        
        Returns:
            List of detailed death analyses
        """
        results = []
        
        for death in self.deaths:
            tick = death['tick']
            teammates_nearby = death.get('teammates_nearby', 0)
            
            # Risk factors
            no_teammate = teammates_nearby == 0
            isolated = teammates_nearby < 2
            no_flash_before = not self._has_recent_flash(tick, self.TICKS_3_SECONDS)
            
            # Check if had any advantage
            had_flash = not no_flash_before
            had_numbers = teammates_nearby > 0
            close_range = self._is_close_range_death(death)
            
            had_advantage = had_flash or had_numbers or close_range
            
            # Avoidable if 2+ risk factors
            risk_count = sum([no_teammate, no_flash_before])
            is_avoidable = risk_count >= 1 and not had_advantage
            
            results.append({
                'tick': tick,
                'is_avoidable': is_avoidable,
                'had_any_advantage': had_advantage,
                'risk_factors': {
                    'no_teammate': no_teammate,
                    'isolated': isolated,
                    'no_utility': no_flash_before
                },
                'attacker': death.get('attacker', 'Unknown'),
                'weapon': death.get('weapon', 'unknown')
            })
        
        return results
    
    def analyze_kills_advanced(self) -> List[Dict[str, Any]]:
        """
        Analyze kill quality and crosshair placement on successful kills
        
        Returns:
            List of kill analyses
        """
        results = []
        
        for kill in self.kills:
            player_pos = kill.get('position', {})
            victim_pos = kill.get('victim_position', {})
            pitch = kill.get('pitch', 0.0)
            yaw = kill.get('yaw', 0.0)
            
            # Calculate crosshair offset at moment of kill
            offset = 0.0
            if player_pos and victim_pos:
                offset = calculate_crosshair_offset_angle(player_pos, pitch, yaw, victim_pos)
            
            results.append({
                'tick': kill['tick'],
                'victim': kill.get('victim', 'Unknown'),
                'headshot': kill.get('headshot', False),
                'weapon': kill.get('weapon', 'unknown'),
                'crosshair_offset': round(offset, 1),
                'good_placement': offset < self.CROSSHAIR_BAD_THRESHOLD
            })
        
        return results
    
    def analyze_flash_effectiveness_advanced(self) -> List[Dict[str, Any]]:
        """
        Advanced flash analysis with pop-flash detection
        
        Flash is useful if:
        - Hit enemy (blind_duration > 1.0s), OR
        - Followed by kill, OR
        - Pop flash that created opening
        
        Returns:
            List of flash analyses
        """
        results = []
        
        for flash in self.flashes:
            hit_someone = flash.get('effective', False)
            followed_by_kill = flash.get('followed_by_kill', False)
            is_pop_flash = flash.get('pop_flash', False)
            
            # Flash is useful if any condition met
            is_useful = hit_someone or followed_by_kill
            
            results.append({
                'tick': flash['tick'],
                'is_useful': is_useful,
                'is_pop_flash': is_pop_flash,
                'hit_someone': hit_someone,
                'followed_by_kill': followed_by_kill,
                'blind_duration': flash.get('blind_duration', 0),
                'victim': flash.get('victim', 'Unknown')
            })
        
        return results
    
    def _has_recent_flash(self, death_tick: int, tick_window: int) -> bool:
        """Check if player threw a flash within tick_window before death"""
        for flash in self.flashes:
            flash_tick = flash["tick"]
            if death_tick - tick_window <= flash_tick < death_tick:
                return True
        return False
    
    def _is_close_range_death(self, death: Dict[str, Any]) -> bool:
        """Check if death occurred at close range (<500 units)"""
        player_pos = death.get('position', {})
        attacker_pos = death.get('attacker_position', {})
        
        if not player_pos or not attacker_pos:
            return False
        
        distance = calculate_distance(player_pos, attacker_pos)
        return distance < 500
    
    def _determine_priorities(self, bad_crosshair_pct: float,
                            avoidable_pct: float,
                            no_advantage_pct: float,
                            flash_useful_pct: float,
                            pop_flash_pct: float,
                            hsr: float,
                            expensive_deaths_pct: float = 0) -> List[Tuple[str, str, str]]:
        """
        Determine training priorities based on all metrics
        
        Returns:
            List of (priority_name, description, recommendation) tuples
        """
        issues = []
        
        # Crosshair placement (most important fundamental)
        if bad_crosshair_pct > 50:
            issues.append((
                bad_crosshair_pct,
                "🎯 CROSSHAIR PLACEMENT",
                f"{bad_crosshair_pct:.0f}% des duels avec mauvais pre-aim (>30°)",
                "Travailler le pre-aim sur angles communs (DM focus)"
            ))
        
        # Avoidable deaths
        if avoidable_pct > 40:
            issues.append((
                avoidable_pct,
                "⚠️ MORTS ÉVITABLES",
                f"{avoidable_pct:.0f}% des morts étaient évitables",
                "Jouer avec équipe, utiliser utility avant de peek"
            ))
        
        # Fighting without advantage
        if no_advantage_pct > 40:
            issues.append((
                no_advantage_pct,
                "💪 DUELS DÉSAVANTAGÉS",
                f"{no_advantage_pct:.0f}% des duels pris sans avantage",
                "Créer avantage avant de peek (flash + jiggle peek)"
            ))
        
        # Flash usage
        if flash_useful_pct < 60:
            issues.append((
                100 - flash_useful_pct,
                "💥 UTILITY USAGE",
                f"Seulement {flash_useful_pct:.0f}% des flashes utiles",
                "Flash pour créer avantage, pas pour gaspiller"
            ))
        
        # Pop flash technique
        if pop_flash_pct < 40 and len(self.flashes) > 3:
            issues.append((
                100 - pop_flash_pct,
                "⚡ POP FLASH",
                f"Seulement {pop_flash_pct:.0f}% de pop flashes",
                "Apprendre les pop flashes de chaque map"
            ))
        
        # Headshot rate (secondary)
        if hsr < 35:
            issues.append((
                35 - hsr,
                "🎮 HEADSHOT RATE",
                f"HSR à {hsr:.0f}% (objectif: 40%+)",
                "Deathmatch avec focus tête uniquement"
            ))
        
        # Economic discipline
        if expensive_deaths_pct > 50:
            issues.append((
                expensive_deaths_pct * 0.8,  # Weight it a bit lower
                "💰 DISCIPLINE ÉCONOMIQUE",
                f"{expensive_deaths_pct:.0f}% des morts perdent >3000$",
                "Préserver équipement cher, jouer plus safe en full buy"
            ))
        
        # Sort by severity and return top 3
        issues.sort(reverse=True, key=lambda x: x[0])
        
        # Format as list of dicts
        priorities = []
        for severity, category, stats, recommendation in issues[:3]:
            priorities.append({
                'category': category,
                'stats': stats,
                'recommendation': recommendation,
                'severity': round(severity, 1)
            })
        
        # Always have at least one priority
        if not priorities:
            priorities.append({
                'category': "✨ CONTINUE",
                'stats': "Bon niveau général",
                'recommendation': "Focus sur la consistency et la clutch mentality",
                'severity': 0
            })
        
        return priorities
