"""
CS2 Highlights Analyzer - Identify key moments for review
"""
from typing import Dict, List, Any, Tuple


class HighlightsAnalyzer:
    """Analyze gameplay to identify key moments worth reviewing"""
    
    TICKS_PER_SECOND = 64  # CS2 tick rate
    
    def __init__(self, events: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]):
        self.deaths = events.get("deaths", [])
        self.kills = events.get("kills", [])
        self.flashes = events.get("flashes", [])
        self.map_name = events.get("map_name", "unknown")
        self.analysis = analysis
        
        # Extract detailed analyses
        self.deaths_analysis = analysis.get("deaths", [])
        self.economy = analysis.get("economy", {})
        self.crosshair = analysis.get("crosshair", {})
    
    def identify_highlights(self) -> List[Dict[str, Any]]:
        """
        Identify key moments to review
        
        Returns:
            List of highlight moments with priority, context, and tick information
        """
        highlights = []
        
        # 1. Critical avoidable deaths
        highlights.extend(self._find_avoidable_deaths())
        
        # 2. Major economic losses
        highlights.extend(self._find_expensive_deaths())
        
        # 3. Terrible crosshair placement
        highlights.extend(self._find_terrible_crosshair())
        
        # 4. Wasted flashes before death
        highlights.extend(self._find_wasted_flashes())
        
        # 5. Perfect kills (for learning)
        highlights.extend(self._find_perfect_kills())
        
        # Sort by priority (highest first)
        highlights.sort(key=lambda x: x['priority'], reverse=True)
        
        return highlights
    
    def _find_avoidable_deaths(self) -> List[Dict[str, Any]]:
        """Identify avoidable deaths (high priority)"""
        highlights = []
        
        for death_data, death_event in zip(self.deaths_analysis, self.deaths):
            if not death_data.get('is_avoidable'):
                continue
            
            # Get context
            risk_factors = death_data.get('risk_factors', {})
            reasons = []
            if risk_factors.get('no_teammate'):
                reasons.append("aucun coéquipier")
            if risk_factors.get('no_utility'):
                reasons.append("aucune utility")
            
            tick = death_event['tick']
            round_num = death_event.get('round', 0)
            time_in_round = self._tick_to_time(tick)
            
            # Get crosshair info if available
            crosshair_offset = self._get_crosshair_offset_for_death(death_event)
            crosshair_note = ""
            if crosshair_offset and crosshair_offset > 60:
                crosshair_note = f", crosshair {crosshair_offset:.0f}° (TERRIBLE)"
            elif crosshair_offset and crosshair_offset > 30:
                crosshair_note = f", crosshair {crosshair_offset:.0f}°"
            
            # Get equipment value
            equip_value = death_event.get('equipment_value', 0)
            value_note = f" ({equip_value}$)" if equip_value > 2000 else ""
            
            highlights.append({
                'priority': 90,  # Very high priority
                'category': '❌ MORT ÉVITABLE',
                'tick': tick,
                'round': round_num,
                'time': time_in_round,
                'description': f"{', '.join(reasons)}{crosshair_note}",
                'attacker': death_event.get('attacker', 'Unknown'),
                'weapon': death_event.get('weapon', 'unknown'),
                'position': self._format_position(death_event.get('position', {})),
                'economic_impact': equip_value,
                'context': f"Perte: {equip_value}${value_note}"
            })
        
        return highlights
    
    def _find_expensive_deaths(self) -> List[Dict[str, Any]]:
        """Identify expensive deaths (major economic losses)"""
        highlights = []
        
        worst_losses = self.economy.get('eco_discipline', {}).get('worst_losses', [])
        
        for loss in worst_losses:
            if loss['total_value'] < 4000:  # Only very expensive deaths
                continue
            
            tick = loss['tick']
            round_num = loss.get('round', 0)
            time_in_round = self._tick_to_time(tick)
            
            # Find the death event to get more context
            death_event = self._find_death_by_tick(tick)
            if not death_event:
                continue
            
            highlights.append({
                'priority': 80,
                'category': '💰 PERTE ÉCONOMIQUE MAJEURE',
                'tick': tick,
                'round': round_num,
                'time': time_in_round,
                'description': f"{loss['total_value']}$ perdus ({loss['weapon']})",
                'attacker': loss['attacker'],
                'weapon': loss['weapon'],
                'position': self._format_position(death_event.get('position', {})),
                'economic_impact': loss['total_value'],
                'context': f"Équipement: {loss['weapon']} + armor + kit"
            })
        
        return highlights
    
    def _find_terrible_crosshair(self) -> List[Dict[str, Any]]:
        """Identify deaths with terrible crosshair placement"""
        highlights = []
        
        terrible_placements = self.crosshair.get('terrible_placements', [])
        
        for placement in terrible_placements:
            tick = placement['tick']
            offset = placement['offset']
            attacker = placement['attacker']
            
            # Find the death event
            death_event = self._find_death_by_tick(tick)
            if not death_event:
                continue
            
            round_num = death_event.get('round', 0)
            time_in_round = self._tick_to_time(tick)
            equip_value = death_event.get('equipment_value', 0)
            
            highlights.append({
                'priority': 70,
                'category': '🎯 CROSSHAIR PLACEMENT TERRIBLE',
                'tick': tick,
                'round': round_num,
                'time': time_in_round,
                'description': f"{offset}° flick requis",
                'attacker': attacker,
                'weapon': death_event.get('weapon', 'unknown'),
                'position': self._format_position(death_event.get('position', {})),
                'economic_impact': equip_value,
                'context': f"Regardait à {offset}° de l'ennemi"
            })
        
        return highlights
    
    def _find_wasted_flashes(self) -> List[Dict[str, Any]]:
        """Identify useless flashes followed by death"""
        highlights = []
        
        for flash in self.flashes:
            if flash.get('is_useful'):
                continue  # Skip useful flashes
            
            flash_tick = flash['tick']
            
            # Check if died shortly after (within 3 seconds)
            death_after = self._find_death_after_tick(flash_tick, window_ticks=192)
            if not death_after:
                continue
            
            round_num = flash.get('round', 0)
            time_in_round = self._tick_to_time(flash_tick)
            
            highlights.append({
                'priority': 50,
                'category': '💥 FLASH GASPILLÉE',
                'tick': flash_tick,
                'round': round_num,
                'time': time_in_round,
                'description': "Flash inutile suivie de mort",
                'attacker': death_after.get('attacker', 'Unknown'),
                'weapon': death_after.get('weapon', 'unknown'),
                'position': self._format_position(flash.get('position', {})),
                'economic_impact': 200,  # Flash cost
                'context': f"Mort {(death_after['tick'] - flash_tick) / self.TICKS_PER_SECOND:.1f}s après flash"
            })
        
        return highlights
    
    def _find_perfect_kills(self) -> List[Dict[str, Any]]:
        """Identify perfect kills to learn from"""
        highlights = []
        
        kills_analysis = self.analysis.get("kills", [])
        
        for kill_data, kill_event in zip(kills_analysis, self.kills):
            # Perfect kill: headshot + good crosshair placement
            if not kill_data.get('headshot'):
                continue
            
            if kill_data.get('crosshair_offset', 999) > 20:
                continue  # Not perfect crosshair
            
            tick = kill_event['tick']
            round_num = kill_event.get('round', 0)
            time_in_round = self._tick_to_time(tick)
            
            highlights.append({
                'priority': 30,  # Lower priority (for learning)
                'category': '✅ KILL PARFAIT',
                'tick': tick,
                'round': round_num,
                'time': time_in_round,
                'description': f"Headshot + pre-aim parfait ({kill_data['crosshair_offset']:.0f}°)",
                'attacker': 'YOU',
                'weapon': kill_event.get('weapon', 'unknown'),
                'position': self._format_position(kill_event.get('position', {})),
                'economic_impact': 0,
                'context': f"Victime: {kill_event.get('victim', 'Unknown')}"
            })
        
        return highlights
    
    def _get_crosshair_offset_for_death(self, death_event: Dict[str, Any]) -> float:
        """Get crosshair offset for a specific death"""
        tick = death_event['tick']
        
        terrible = self.crosshair.get('terrible_placements', [])
        bad = self.crosshair.get('bad_placements', [])
        
        for placement in terrible:
            if placement['tick'] == tick:
                return placement['offset']
        
        for placement in bad:
            if placement['tick'] == tick:
                return placement['offset']
        
        return None
    
    def _find_death_by_tick(self, tick: int) -> Dict[str, Any]:
        """Find death event by tick"""
        for death in self.deaths:
            if death['tick'] == tick:
                return death
        return None
    
    def _find_death_after_tick(self, tick: int, window_ticks: int = 192) -> Dict[str, Any]:
        """Find death event after given tick within window"""
        for death in self.deaths:
            if tick < death['tick'] <= tick + window_ticks:
                return death
        return None
    
    def _tick_to_time(self, tick: int) -> str:
        """Convert tick to round time (approximate)"""
        # Approximate: assume round starts at tick 0
        seconds = tick / self.TICKS_PER_SECOND
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def _format_position(self, pos: Dict[str, float]) -> str:
        """Format position as readable string"""
        if not pos:
            return "Unknown"
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        z = pos.get('z', 0)
        return f"({x:.0f}, {y:.0f}, {z:.0f})"
