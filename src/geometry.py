"""
CS2 Geometry - Advanced geometric calculations for game analysis
"""
import math
from typing import Dict, Tuple, List, Optional


class Vector3:
    """3D Vector for position and direction calculations"""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def magnitude(self) -> float:
        """Calculate vector magnitude (length)"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Vector3':
        """Return normalized vector (unit vector)"""
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x / mag, self.y / mag, self.z / mag)
    
    def dot(self, other: 'Vector3') -> float:
        """Dot product with another vector"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    @staticmethod
    def from_dict(d: Dict[str, float]) -> 'Vector3':
        """Create Vector3 from position dict"""
        return Vector3(d.get('x', 0), d.get('y', 0), d.get('z', 0))


def calculate_distance(pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
    """Calculate 3D Euclidean distance between two positions"""
    dx = pos1['x'] - pos2['x']
    dy = pos1['y'] - pos2['y']
    dz = pos1['z'] - pos2['z']
    return math.sqrt(dx**2 + dy**2 + dz**2)


def calculate_2d_distance(pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
    """Calculate 2D distance (ignoring Z axis) - useful for map zones"""
    dx = pos1['x'] - pos2['x']
    dy = pos1['y'] - pos2['y']
    return math.sqrt(dx**2 + dy**2)


def angles_to_direction(pitch: float, yaw: float) -> Vector3:
    """
    Convert pitch/yaw angles to direction vector
    
    CS2 uses:
    - Pitch: vertical angle (-90 to 90, where -90 is up, 90 is down)
    - Yaw: horizontal angle (0-360, where 0 is north/forward)
    """
    # Convert to radians
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)
    
    # Calculate direction vector
    x = math.cos(pitch_rad) * math.cos(yaw_rad)
    y = math.cos(pitch_rad) * math.sin(yaw_rad)
    z = -math.sin(pitch_rad)  # Negative because pitch down is positive
    
    return Vector3(x, y, z)


def is_in_fov(player_pos: Dict[str, float], 
              player_pitch: float, 
              player_yaw: float,
              target_pos: Dict[str, float],
              fov_degrees: float = 90.0) -> bool:
    """
    Check if target is within player's field of view
    
    Args:
        player_pos: Player position {x, y, z}
        player_pitch: Vertical aim angle
        player_yaw: Horizontal aim angle
        target_pos: Target position {x, y, z}
        fov_degrees: Field of view in degrees (default 90° for CS2)
    
    Returns:
        True if target is in FOV
    """
    # Get player view direction
    view_dir = angles_to_direction(player_pitch, player_yaw)
    
    # Calculate vector from player to target
    player_vec = Vector3.from_dict(player_pos)
    target_vec = Vector3.from_dict(target_pos)
    to_target = (target_vec - player_vec).normalize()
    
    # Calculate angle between view direction and target direction
    dot_product = view_dir.dot(to_target)
    
    # Clamp dot product to [-1, 1] to avoid math domain errors
    dot_product = max(-1.0, min(1.0, dot_product))
    
    # Calculate angle in degrees
    angle = math.degrees(math.acos(dot_product))
    
    # Check if within FOV (half angle on each side)
    return angle <= (fov_degrees / 2.0)


def calculate_crosshair_offset_angle(player_pos: Dict[str, float],
                                     player_pitch: float,
                                     player_yaw: float,
                                     target_pos: Dict[str, float]) -> float:
    """
    Calculate angle between crosshair and target position
    This measures how far player needs to flick to hit target
    
    Returns:
        Angle in degrees (0° = perfect aim, larger = worse placement)
    """
    # Get current crosshair direction
    crosshair_dir = angles_to_direction(player_pitch, player_yaw)
    
    # Calculate direction to target
    player_vec = Vector3.from_dict(player_pos)
    target_vec = Vector3.from_dict(target_pos)
    to_target = (target_vec - player_vec).normalize()
    
    # Calculate angle between them
    dot_product = crosshair_dir.dot(to_target)
    dot_product = max(-1.0, min(1.0, dot_product))  # Clamp to avoid math errors
    
    angle = math.degrees(math.acos(dot_product))
    return angle


def line_of_sight_clear(pos1: Dict[str, float], 
                        pos2: Dict[str, float],
                        smokes: List[Dict[str, any]]) -> bool:
    """
    Check if line of sight between two positions is clear (not blocked by smoke)
    
    Simplified implementation: checks if line intersects with any active smoke spheres
    
    Args:
        pos1: Start position
        pos2: End position
        smokes: List of active smoke grenades with position and radius
    
    Returns:
        True if line of sight is clear
    """
    if not smokes:
        return True
    
    # Convert to vectors
    start = Vector3.from_dict(pos1)
    end = Vector3.from_dict(pos2)
    
    # Direction and length of line segment
    direction = end - start
    length = direction.magnitude()
    
    if length == 0:
        return True
    
    direction = direction.normalize()
    
    # Check each smoke
    for smoke in smokes:
        smoke_pos = Vector3.from_dict(smoke['position'])
        smoke_radius = smoke.get('radius', 250)  # CS2 smoke radius ~250 units
        
        # Vector from start to smoke center
        to_smoke = smoke_pos - start
        
        # Project onto line direction (closest point on line to smoke center)
        projection = to_smoke.dot(direction)
        
        # Check if projection is within line segment
        if 0 <= projection <= length:
            # Find closest point on line segment
            closest_point = start + Vector3(
                direction.x * projection,
                direction.y * projection,
                direction.z * projection
            )
            
            # Distance from closest point to smoke center
            distance = (smoke_pos - closest_point).magnitude()
            
            # If line passes through smoke sphere, vision is blocked
            if distance <= smoke_radius:
                return False
    
    return True


def get_map_zone(position: Dict[str, float], map_name: str) -> str:
    """
    Identify map zone based on position coordinates
    
    Hardcoded zones for common competitive maps
    This is a simplified approach - real implementation would need precise map data
    
    Returns:
        Zone name (e.g., "A Site", "Mid", "B Long", "Unknown")
    """
    x, y = position['x'], position['y']
    
    # Map-specific zone definitions
    # These are approximate and would need to be calibrated with real map data
    zones = {
        'de_dust2': [
            # Format: (min_x, max_x, min_y, max_y, zone_name)
            (-1000, -400, -500, 500, "A Long"),
            (-400, 200, -500, 500, "A Site"),
            (200, 800, -500, 500, "CT Spawn"),
            (-1000, -400, 500, 1500, "Catwalk"),
            (-400, 200, 500, 1500, "Mid"),
            (200, 800, 500, 1500, "B Site"),
            (800, 1400, 500, 1500, "B Tunnel"),
        ],
        'de_mirage': [
            (-2000, -1000, -1000, 0, "T Spawn"),
            (-1000, 0, -1000, 0, "A Ramp"),
            (0, 1000, -1000, 0, "A Site"),
            (-1000, 0, 0, 1000, "Mid"),
            (0, 1000, 0, 1000, "B Apartments"),
            (1000, 2000, 0, 1000, "B Site"),
        ],
        'de_inferno': [
            (-2000, -1000, -1000, 0, "T Spawn"),
            (-1000, 0, -1000, 0, "Banana"),
            (0, 1000, -1000, 0, "B Site"),
            (-1000, 0, 0, 1000, "Mid"),
            (0, 1000, 0, 1000, "A Site"),
            (1000, 2000, 0, 1000, "CT Spawn"),
        ],
    }
    
    # Get zones for this map
    map_zones = zones.get(map_name.lower(), [])
    
    # Find matching zone
    for min_x, max_x, min_y, max_y, zone_name in map_zones:
        if min_x <= x <= max_x and min_y <= y <= max_y:
            return zone_name
    
    return "Unknown"


def calculate_angle_advantage(player_pos: Dict[str, float],
                             enemy_pos: Dict[str, float],
                             player_peek_angle: float) -> str:
    """
    Determine if player has angle advantage (peeker's advantage)
    
    Returns:
        "wide" - wide peek (disadvantage)
        "normal" - normal peek
        "tight" - tight angle (advantage)
        "close" - close range (<500 units, easier to trade)
    """
    distance = calculate_distance(player_pos, enemy_pos)
    
    if distance < 500:
        return "close"
    
    # Simplified: use peek angle to determine advantage
    # In reality, this would require more complex geometry with wall positions
    if player_peek_angle > 60:
        return "wide"
    elif player_peek_angle > 30:
        return "normal"
    else:
        return "tight"


def calculate_vector_angle(v1: Vector3, v2: Vector3) -> float:
    """Calculate angle between two vectors in degrees"""
    dot = v1.dot(v2)
    mag1 = v1.magnitude()
    mag2 = v2.magnitude()
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    cos_angle = dot / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp
    
    return math.degrees(math.acos(cos_angle))
