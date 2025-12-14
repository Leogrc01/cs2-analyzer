"""
CS2 Demo Parser - Extracts essential game events from .dem files
"""
from pathlib import Path
from typing import Dict, List, Any
import json


class DemoParser:
    """Parse CS2 demo files and extract relevant events"""
    
    def __init__(self, demo_path: str):
        self.demo_path = Path(demo_path)
        if not self.demo_path.exists():
            raise FileNotFoundError(f"Demo file not found: {demo_path}")
    
    def parse(self, player_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract deaths, kills, and flashes for the specified player.
        
        Args:
            player_name: Name of the player to analyze
            
        Returns:
            Dictionary with 'deaths', 'kills', and 'flashes' lists
        """
        try:
            from demoparser2 import DemoParser as DP
        except ImportError:
            raise ImportError(
                "demoparser2 not installed. Run: pip install demoparser2"
            )
        
        parser = DP(str(self.demo_path))
        
        # Extract player death events
        deaths_df = parser.parse_event("player_death")
        
        # Extract player hurt events for flash detection
        try:
            blind_df = parser.parse_event("player_blind")
        except:
            blind_df = None
        
        # Extract player positions and info
        ticks_df = parser.parse_ticks(["X", "Y", "Z", "pitch", "yaw", "health", "team_name"])
        
        deaths = self._extract_deaths(deaths_df, ticks_df, player_name)
        kills = self._extract_kills(deaths_df, ticks_df, player_name)
        flashes = self._extract_flashes(blind_df, deaths_df, player_name)
        
        return {
            "deaths": deaths,
            "kills": kills,
            "flashes": flashes
        }
    
    def _extract_deaths(self, deaths_df, ticks_df, player_name: str) -> List[Dict]:
        """Extract death events for player"""
        if deaths_df is None or deaths_df.empty:
            return []
        
        player_deaths = deaths_df[deaths_df['user_name'] == player_name]
        
        deaths = []
        for _, death in player_deaths.iterrows():
            tick = death.get('tick', 0)
            
            # Get player position at death
            tick_data = ticks_df[ticks_df['tick'] == tick]
            player_data = tick_data[tick_data['name'] == player_name]
            
            death_info = {
                "tick": int(tick),
                "victim": player_name,
                "attacker": death.get('attacker_name', 'Unknown'),
                "weapon": death.get('weapon', 'unknown'),
                "headshot": bool(death.get('headshot', False)),
                "position": self._get_position(player_data),
                "attacker_position": self._get_attacker_position(tick_data, death.get('attacker_name')),
                "teammates_nearby": self._get_nearby_teammates(tick_data, player_data, player_name)
            }
            deaths.append(death_info)
        
        return deaths
    
    def _extract_kills(self, deaths_df, ticks_df, player_name: str) -> List[Dict]:
        """Extract kill events for player"""
        if deaths_df is None or deaths_df.empty:
            return []
        
        player_kills = deaths_df[deaths_df['attacker_name'] == player_name]
        
        kills = []
        for _, kill in player_kills.iterrows():
            tick = kill.get('tick', 0)
            
            tick_data = ticks_df[ticks_df['tick'] == tick]
            player_data = tick_data[tick_data['name'] == player_name]
            
            kill_info = {
                "tick": int(tick),
                "attacker": player_name,
                "victim": kill.get('user_name', 'Unknown'),
                "weapon": kill.get('weapon', 'unknown'),
                "headshot": bool(kill.get('headshot', False)),
                "position": self._get_position(player_data)
            }
            kills.append(kill_info)
        
        return kills
    
    def _extract_flashes(self, blind_df, deaths_df, player_name: str) -> List[Dict]:
        """Extract flash events thrown by player"""
        flashes = []
        
        if blind_df is None or blind_df.empty:
            return flashes
        
        # Get flashes thrown by player
        player_flashes = blind_df[blind_df['attacker_name'] == player_name]
        
        for _, flash in player_flashes.iterrows():
            tick = flash.get('tick', 0)
            blind_duration = flash.get('blind_duration', 0)
            
            flash_info = {
                "tick": int(tick),
                "thrower": player_name,
                "victim": flash.get('user_name', 'Unknown'),
                "blind_duration": float(blind_duration),
                "effective": blind_duration > 1.0,  # Flash > 1 second is considered effective
                "followed_by_kill": self._check_kill_after_flash(deaths_df, player_name, tick)
            }
            flashes.append(flash_info)
        
        return flashes
    
    def _get_position(self, player_data) -> Dict[str, float]:
        """Get player position from tick data"""
        if player_data.empty:
            return {"x": 0.0, "y": 0.0, "z": 0.0}
        
        row = player_data.iloc[0]
        return {
            "x": float(row.get('X', 0)),
            "y": float(row.get('Y', 0)),
            "z": float(row.get('Z', 0))
        }
    
    def _get_attacker_position(self, tick_data, attacker_name: str) -> Dict[str, float]:
        """Get attacker position"""
        attacker_data = tick_data[tick_data['name'] == attacker_name]
        return self._get_position(attacker_data)
    
    def _get_nearby_teammates(self, tick_data, player_data, player_name: str) -> int:
        """Count teammates within tradeable distance (~800 units)"""
        if player_data.empty:
            return 0
        
        player_row = player_data.iloc[0]
        player_team = player_row.get('team_name', '')
        player_pos = self._get_position(player_data)
        
        # Get teammates on same team
        teammates = tick_data[
            (tick_data['team_name'] == player_team) & 
            (tick_data['name'] != player_name) &
            (tick_data['health'] > 0)
        ]
        
        nearby_count = 0
        TRADE_DISTANCE = 800  # CS2 units
        
        for _, teammate in teammates.iterrows():
            tm_pos = {
                "x": float(teammate.get('X', 0)),
                "y": float(teammate.get('Y', 0)),
                "z": float(teammate.get('Z', 0))
            }
            
            distance = self._calculate_distance(player_pos, tm_pos)
            if distance < TRADE_DISTANCE:
                nearby_count += 1
        
        return nearby_count
    
    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate 3D distance between two positions"""
        dx = pos1['x'] - pos2['x']
        dy = pos1['y'] - pos2['y']
        dz = pos1['z'] - pos2['z']
        return (dx**2 + dy**2 + dz**2) ** 0.5
    
    def _check_kill_after_flash(self, deaths_df, player_name: str, flash_tick: int) -> bool:
        """Check if player got a kill within 3 seconds (192 ticks) of flash"""
        if deaths_df is None or deaths_df.empty:
            return False
        
        TICKS_3_SECONDS = 192  # CS2 runs at ~64 ticks/sec
        
        kills_after = deaths_df[
            (deaths_df['attacker_name'] == player_name) &
            (deaths_df['tick'] > flash_tick) &
            (deaths_df['tick'] <= flash_tick + TICKS_3_SECONDS)
        ]
        
        return len(kills_after) > 0
    
    def save_events(self, events: Dict, output_path: str):
        """Save extracted events to JSON file"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Events saved to: {output_path}")
