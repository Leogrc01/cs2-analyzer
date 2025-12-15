"""
CS2 Game State - Track game state across ticks for advanced analysis
"""
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from src.geometry import is_in_fov, line_of_sight_clear, calculate_distance


@dataclass
class PlayerState:
    """Player state at a specific tick"""
    name: str
    tick: int
    team: str
    position: Dict[str, float]
    pitch: float
    yaw: float
    health: int
    alive: bool
    visible_enemies: List[str]  # Names of enemies in FOV and LOS


@dataclass
class RoundState:
    """Round state information"""
    round_num: int
    start_tick: int
    end_tick: Optional[int]
    winning_team: Optional[str]
    t_side: Set[str]  # Player names on T side
    ct_side: Set[str]  # Player names on CT side
    bomb_planted: bool
    bomb_plant_tick: Optional[int]


@dataclass
class SmokeGrenade:
    """Active smoke grenade"""
    tick: int
    position: Dict[str, float]
    thrower: str
    start_tick: int
    end_tick: int  # Smoke lasts ~18 seconds (1152 ticks at 64 tick/sec)
    
    def is_active(self, tick: int) -> bool:
        """Check if smoke is active at given tick"""
        return self.start_tick <= tick <= self.end_tick


class GameState:
    """
    Track complete game state across all ticks
    Allows querying: "Who was visible at tick X?" "Was there smoke blocking LOS?"
    """
    
    def __init__(self, ticks_df, player_name: str):
        """
        Initialize game state from ticks dataframe
        
        Args:
            ticks_df: Dataframe from demoparser2 with player positions/angles
            player_name: Name of player being analyzed
        """
        self.player_name = player_name
        self.ticks_df = ticks_df
        self.smokes: List[SmokeGrenade] = []
        self.rounds: List[RoundState] = []
        self.player_hp_cache: Dict[int, Dict[str, int]] = {}  # tick -> {player: hp}
        
    def add_smoke(self, tick: int, position: Dict[str, float], thrower: str):
        """Add smoke grenade to tracking"""
        SMOKE_DURATION_TICKS = 1152  # ~18 seconds at 64 tick/sec
        smoke = SmokeGrenade(
            tick=tick,
            position=position,
            thrower=thrower,
            start_tick=tick,
            end_tick=tick + SMOKE_DURATION_TICKS
        )
        self.smokes.append(smoke)
    
    def add_round(self, round_state: RoundState):
        """Add round information"""
        self.rounds.append(round_state)
    
    def get_active_smokes(self, tick: int) -> List[SmokeGrenade]:
        """Get all smokes active at given tick"""
        return [smoke for smoke in self.smokes if smoke.is_active(tick)]
    
    def get_visible_enemies(self, tick: int, player_name: str) -> List[Dict[str, Any]]:
        """
        Get all enemies visible to player at given tick
        Considers FOV and line of sight (smoke blocking)
        
        Returns:
            List of enemy dicts with name, position, distance
        """
        # Get tick data
        tick_data = self.ticks_df[self.ticks_df['tick'] == tick]
        
        if tick_data.empty:
            return []
        
        # Get player state
        player_data = tick_data[tick_data['name'] == player_name]
        if player_data.empty:
            return []
        
        player_row = player_data.iloc[0]
        player_pos = {
            'x': float(player_row.get('X', 0)),
            'y': float(player_row.get('Y', 0)),
            'z': float(player_row.get('Z', 0))
        }
        player_pitch = float(player_row.get('pitch', 0))
        player_yaw = float(player_row.get('yaw', 0))
        player_team = player_row.get('team_name', '')
        
        # Get active smokes
        active_smokes = self.get_active_smokes(tick)
        smoke_dicts = [{
            'position': smoke.position,
            'radius': 250
        } for smoke in active_smokes]
        
        # Check all enemies
        visible_enemies = []
        enemies = tick_data[
            (tick_data['team_name'] != player_team) & 
            (tick_data['health'] > 0)
        ]
        
        for _, enemy in enemies.iterrows():
            enemy_name = enemy.get('name', 'Unknown')
            enemy_pos = {
                'x': float(enemy.get('X', 0)),
                'y': float(enemy.get('Y', 0)),
                'z': float(enemy.get('Z', 0))
            }
            
            # Check if in FOV
            in_fov = is_in_fov(player_pos, player_pitch, player_yaw, enemy_pos)
            
            if in_fov:
                # Check line of sight (not blocked by smoke)
                los_clear = line_of_sight_clear(player_pos, enemy_pos, smoke_dicts)
                
                if los_clear:
                    distance = calculate_distance(player_pos, enemy_pos)
                    visible_enemies.append({
                        'name': enemy_name,
                        'position': enemy_pos,
                        'distance': distance,
                        'health': int(enemy.get('health', 100))
                    })
        
        return visible_enemies
    
    def get_teammates_with_los(self, tick: int, player_name: str, 
                                target_pos: Dict[str, float]) -> List[str]:
        """
        Get teammates who have line of sight to target position
        Useful for determining trade potential
        
        Returns:
            List of teammate names with clear LOS to target
        """
        tick_data = self.ticks_df[self.ticks_df['tick'] == tick]
        
        if tick_data.empty:
            return []
        
        # Get player team
        player_data = tick_data[tick_data['name'] == player_name]
        if player_data.empty:
            return []
        
        player_team = player_data.iloc[0].get('team_name', '')
        
        # Get active smokes
        active_smokes = self.get_active_smokes(tick)
        smoke_dicts = [{
            'position': smoke.position,
            'radius': 250
        } for smoke in active_smokes]
        
        # Check all teammates
        teammates_with_los = []
        teammates = tick_data[
            (tick_data['team_name'] == player_team) & 
            (tick_data['name'] != player_name) &
            (tick_data['health'] > 0)
        ]
        
        for _, teammate in teammates.iterrows():
            teammate_pos = {
                'x': float(teammate.get('X', 0)),
                'y': float(teammate.get('Y', 0)),
                'z': float(teammate.get('Z', 0))
            }
            
            # Check if teammate has LOS to target
            if line_of_sight_clear(teammate_pos, target_pos, smoke_dicts):
                distance = calculate_distance(teammate_pos, target_pos)
                # Only count if within reasonable distance (< 2000 units)
                if distance < 2000:
                    teammates_with_los.append(teammate.get('name', 'Unknown'))
        
        return teammates_with_los
    
    def get_player_hp(self, tick: int, player_name: str) -> int:
        """Get player HP at given tick"""
        if tick in self.player_hp_cache and player_name in self.player_hp_cache[tick]:
            return self.player_hp_cache[tick][player_name]
        
        tick_data = self.ticks_df[self.ticks_df['tick'] == tick]
        player_data = tick_data[tick_data['name'] == player_name]
        
        if player_data.empty:
            return 100  # Default
        
        hp = int(player_data.iloc[0].get('health', 100))
        
        # Cache result
        if tick not in self.player_hp_cache:
            self.player_hp_cache[tick] = {}
        self.player_hp_cache[tick][player_name] = hp
        
        return hp
    
    def get_round_at_tick(self, tick: int) -> Optional[RoundState]:
        """Get round state for given tick"""
        for round_state in self.rounds:
            if round_state.start_tick <= tick:
                if round_state.end_tick is None or tick <= round_state.end_tick:
                    return round_state
        return None
    
    def get_player_side(self, tick: int, player_name: str) -> str:
        """Get player side (T/CT) at given tick"""
        round_state = self.get_round_at_tick(tick)
        if not round_state:
            # Fallback to tick data
            tick_data = self.ticks_df[self.ticks_df['tick'] == tick]
            player_data = tick_data[tick_data['name'] == player_name]
            if not player_data.empty:
                team = player_data.iloc[0].get('team_name', '')
                return 'T' if 'TERRORIST' in team.upper() or team == '2' else 'CT'
            return 'Unknown'
        
        if player_name in round_state.t_side:
            return 'T'
        elif player_name in round_state.ct_side:
            return 'CT'
        return 'Unknown'
    
    def was_utility_thrown_before(self, player_name: str, death_tick: int, 
                                   window_ticks: int = 320) -> Dict[str, bool]:
        """
        Check if player threw any utility before death
        
        Args:
            player_name: Player name
            death_tick: Tick of death
            window_ticks: Time window to check (default 5 seconds = 320 ticks)
        
        Returns:
            Dict with utility types as keys: {flash: bool, smoke: bool, molly: bool}
        """
        # This would require parsing grenade events
        # Placeholder implementation - will be filled by parser
        return {
            'flash': False,
            'smoke': False,
            'molly': False,
            'he': False
        }
