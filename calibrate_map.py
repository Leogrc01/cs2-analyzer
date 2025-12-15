#!/usr/bin/env python3
"""
Map Calibration Tool - Find the correct bounds for map overlay

This tool helps you find the correct x/y bounds to align game coordinates
with the radar image for each map.

Usage: python calibrate_map.py demos/match.dem "PlayerName"
"""
import sys
from src.parser import DemoParser

def analyze_coordinate_range(demo_path, player_name):
    """Analyze the coordinate ranges in a demo to help with calibration"""
    
    print(f"📂 Parsing {demo_path}...")
    parser = DemoParser(demo_path)
    events = parser.parse(player_name)
    
    map_name = events.get('map_name', 'unknown')
    deaths = events.get('deaths', [])
    kills = events.get('kills', [])
    
    if not deaths and not kills:
        print("❌ No position data found")
        return
    
    # Collect all positions
    all_positions = []
    for death in deaths:
        pos = death.get('position', {})
        if pos:
            all_positions.append((pos.get('x', 0), pos.get('y', 0)))
    
    for kill in kills:
        pos = kill.get('position', {})
        if pos:
            all_positions.append((pos.get('x', 0), pos.get('y', 0)))
    
    if not all_positions:
        print("❌ No valid positions found")
        return
    
    # Calculate ranges
    x_coords = [p[0] for p in all_positions]
    y_coords = [p[1] for p in all_positions]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    # Add some padding (10%)
    x_range = x_max - x_min
    y_range = y_max - y_min
    x_padding = x_range * 0.15
    y_padding = y_range * 0.15
    
    x_min_padded = int(x_min - x_padding)
    x_max_padded = int(x_max + x_padding)
    y_min_padded = int(y_min - y_padding)
    y_max_padded = int(y_max + y_padding)
    
    # Display results
    print("\n" + "="*70)
    print(f"🗺️  CALIBRATION DATA FOR: {map_name}")
    print("="*70)
    print(f"\nTotal positions analyzed: {len(all_positions)}")
    print(f"\nCoordinate ranges found:")
    print(f"  X: {x_min:.0f} to {x_max:.0f} (range: {x_range:.0f})")
    print(f"  Y: {y_min:.0f} to {y_max:.0f} (range: {y_range:.0f})")
    
    print(f"\n📋 RECOMMENDED MAP_BOUNDS (with 15% padding):")
    print("="*70)
    print(f"'{map_name}': {{")
    print(f"    'x_min': {x_min_padded},")
    print(f"    'x_max': {x_max_padded},")
    print(f"    'y_min': {y_min_padded},")
    print(f"    'y_max': {y_max_padded},")
    print(f"    'scale': 1024")
    print(f"}},")
    print("="*70)
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Copy the MAP_BOUNDS config above")
    print(f"2. Edit generate_heatmap_overlay.py")
    print(f"3. Replace the entry for '{map_name}' in MAP_BOUNDS dictionary")
    print(f"4. Re-run the heatmap generation")
    print(f"\n⚠️  NOTE: You may need to fine-tune these values by ±10-20%")
    print(f"   if the alignment is still not perfect.")
    
    # Show sample positions for verification
    print(f"\n📍 Sample positions (first 5):")
    for i, (x, y) in enumerate(all_positions[:5], 1):
        print(f"  {i}. X={x:.0f}, Y={y:.0f}")
    
    print("\n" + "="*70)


def main():
    if len(sys.argv) < 3:
        print("Usage: python calibrate_map.py <demo_file> <player_name>")
        print("\nThis tool analyzes coordinate ranges in your demo to help")
        print("calibrate the map overlay alignment.")
        sys.exit(1)
    
    demo_path = sys.argv[1]
    player_name = sys.argv[2]
    
    analyze_coordinate_range(demo_path, player_name)


if __name__ == "__main__":
    main()
