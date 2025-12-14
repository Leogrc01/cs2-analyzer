"""
CS2 Gap Analyzer - Analyzes parsed game events to identify improvement areas
"""
from typing import Dict, List, Any


class GapAnalyzer:
    """Analyze game events to detect avoidable mistakes"""
    
    def __init__(self, events: Dict[str, List[Dict[str, Any]]]):
        self.deaths = events.get("deaths", [])
        self.kills = events.get("kills", [])
        self.flashes = events.get("flashes", [])
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run all analyses and return comprehensive results
        
        Returns:
            Dictionary with analysis results and recommendations
        """
        avoidable_deaths = self.analyze_avoidable_deaths()
        disadvantaged_duels = self.analyze_disadvantaged_duels()
        flash_effectiveness = self.analyze_flash_effectiveness()
        
        # Calculate percentages
        total_deaths = len(self.deaths)
        avoidable_count = len([d for d in avoidable_deaths if d["is_avoidable"]])
        avoidable_pct = (avoidable_count / total_deaths * 100) if total_deaths > 0 else 0
        
        total_duels = len(self.deaths)  # Each death is a lost duel
        disadvantaged_count = len([d for d in disadvantaged_duels if d["is_disadvantaged"]])
        disadvantaged_pct = (disadvantaged_count / total_duels * 100) if total_duels > 0 else 0
        
        total_flashes = len(self.flashes)
        useful_count = len([f for f in flash_effectiveness if f["is_useful"]])
        useful_pct = (useful_count / total_flashes * 100) if total_flashes > 0 else 0
        
        # Generate recommendation
        priority = self._determine_priority(avoidable_pct, disadvantaged_pct, useful_pct)
        
        return {
            "summary": {
                "avoidable_deaths_pct": round(avoidable_pct, 1),
                "disadvantaged_duels_pct": round(disadvantaged_pct, 1),
                "useful_flashes_pct": round(useful_pct, 1),
                "total_deaths": total_deaths,
                "total_kills": len(self.kills),
                "total_flashes": total_flashes
            },
            "details": {
                "avoidable_deaths": avoidable_deaths,
                "disadvantaged_duels": disadvantaged_duels,
                "flash_effectiveness": flash_effectiveness
            },
            "priority": priority
        }
    
    def analyze_avoidable_deaths(self) -> List[Dict[str, Any]]:
        """
        ÉTAPE 2: Detect avoidable deaths
        
        Death is avoidable if 2+ of these conditions are true:
        - No teammate nearby (< 800 units) → not tradable
        - Multiple enemies visible → bad angle
        - No recent flash (< 3 seconds before death) → dry peek
        
        Returns:
            List of death analyses with avoidability flag
        """
        TICKS_3_SECONDS = 192
        
        results = []
        
        for death in self.deaths:
            tick = death["tick"]
            teammates_nearby = death.get("teammates_nearby", 0)
            
            # Condition 1: No teammate nearby
            no_teammate = teammates_nearby == 0
            
            # Condition 2: Multiple enemies (approximated - if headshot likely 1v1)
            # This is simplified - in reality we'd need to track visible enemies
            multiple_enemies = not death.get("headshot", False)
            
            # Condition 3: No recent flash
            recent_flash = self._has_recent_flash(tick, TICKS_3_SECONDS)
            no_flash = not recent_flash
            
            # Count conditions met
            conditions_met = sum([no_teammate, multiple_enemies, no_flash])
            is_avoidable = conditions_met >= 2
            
            results.append({
                "tick": tick,
                "is_avoidable": is_avoidable,
                "reasons": {
                    "no_teammate_nearby": no_teammate,
                    "multiple_enemies": multiple_enemies,
                    "no_recent_flash": no_flash
                },
                "conditions_met": conditions_met,
                "attacker": death.get("attacker", "Unknown"),
                "weapon": death.get("weapon", "unknown")
            })
        
        return results
    
    def analyze_disadvantaged_duels(self) -> List[Dict[str, Any]]:
        """
        ÉTAPE 3: Detect duels taken without advantage
        
        A duel has advantage if at least ONE of:
        - Flash active (within 3 seconds before death)
        - Numerical superiority (teammates nearby)
        - Closed angle / 1v1 (approximated by headshot)
        - Trade possible (teammate nearby)
        
        Returns:
            List of duel analyses with disadvantage flag
        """
        TICKS_3_SECONDS = 192
        
        results = []
        
        for death in self.deaths:
            tick = death["tick"]
            teammates_nearby = death.get("teammates_nearby", 0)
            
            # Advantage 1: Flash active
            has_flash = self._has_recent_flash(tick, TICKS_3_SECONDS)
            
            # Advantage 2: Numerical superiority
            has_numbers = teammates_nearby > 0
            
            # Advantage 3: Closed angle (approximated - headshot suggests 1v1 fair fight)
            closed_angle = death.get("headshot", False)
            
            # Advantage 4: Trade possible
            trade_possible = teammates_nearby > 0
            
            # Has advantage if any condition is true
            has_advantage = has_flash or has_numbers or closed_angle or trade_possible
            is_disadvantaged = not has_advantage
            
            results.append({
                "tick": tick,
                "is_disadvantaged": is_disadvantaged,
                "advantages": {
                    "flash_active": has_flash,
                    "numerical_superiority": has_numbers,
                    "closed_angle": closed_angle,
                    "trade_possible": trade_possible
                },
                "had_any_advantage": has_advantage
            })
        
        return results
    
    def analyze_flash_effectiveness(self) -> List[Dict[str, Any]]:
        """
        ÉTAPE 4: Analyze flash effectiveness
        
        Flash is useful if:
        - It hit someone (blind_duration > 1.0 seconds), OR
        - There was a kill within 3 seconds after
        
        Returns:
            List of flash analyses with usefulness flag
        """
        results = []
        
        for flash in self.flashes:
            hit_someone = flash.get("effective", False)  # blind_duration > 1.0
            followed_by_kill = flash.get("followed_by_kill", False)
            
            is_useful = hit_someone or followed_by_kill
            
            results.append({
                "tick": flash["tick"],
                "is_useful": is_useful,
                "hit_someone": hit_someone,
                "followed_by_kill": followed_by_kill,
                "blind_duration": flash.get("blind_duration", 0),
                "victim": flash.get("victim", "Unknown")
            })
        
        return results
    
    def _has_recent_flash(self, death_tick: int, tick_window: int) -> bool:
        """Check if player threw a flash within tick_window before death"""
        for flash in self.flashes:
            flash_tick = flash["tick"]
            if death_tick - tick_window <= flash_tick < death_tick:
                return True
        return False
    
    def _determine_priority(self, avoidable_pct: float, 
                           disadvantaged_pct: float, 
                           useful_flash_pct: float) -> List[str]:
        """
        Determine training priorities based on percentages
        
        Returns:
            List of prioritized recommendations
        """
        priorities = []
        
        # Build list of issues with their severity
        issues = [
            (avoidable_pct, "Réduire les morts évitables - jouer avec ton équipe"),
            (disadvantaged_pct, "Ne prendre que des duels avec avantage (flash, nombre, trade)"),
            (100 - useful_flash_pct if useful_flash_pct < 50 else 0, 
             "Améliorer l'utilité des flashes - flash avant de peek")
        ]
        
        # Sort by severity (highest percentage = biggest problem)
        issues.sort(reverse=True, key=lambda x: x[0])
        
        # Return top 2 priorities
        for severity, recommendation in issues[:2]:
            if severity > 40:  # Only include if it's a significant issue
                priorities.append(recommendation)
        
        # Always include crosshair placement as general advice
        if len(priorities) < 2:
            priorities.append("Améliorer le crosshair placement")
        
        return priorities
