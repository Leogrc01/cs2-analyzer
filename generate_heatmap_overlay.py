#!/usr/bin/env python3
"""
Generate visual heatmap with map image overlay
Usage: python generate_heatmap_overlay.py demos/match.dem "PlayerName"

Place your map images (radar images) in the 'maps/' folder:
- maps/de_dust2.png
- maps/de_mirage.png
- maps/de_inferno.png

Map images should be CS2 radar overviews (can be found online or extracted from game files)
"""
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
from PIL import Image
import numpy as np
from src.parser import DemoParser
from src.analyzer import GapAnalyzer
from src.positioning import MAP_ZONES


# Map coordinate bounds for proper scaling
# These need to be calibrated based on the actual radar image
MAP_BOUNDS = {
    'de_dust2': {
        'x_min': -2551, 'x_max': 1880,
        'y_min': -161, 'y_max': 3260,
        'scale': 1024  # Radar image size
    },
    'de_mirage': {
        'x_min': -3500, 'x_max': 2700,
        'y_min': -3200, 'y_max': 2800,
        'scale': 1024
    },
    'de_inferno': {
        'x_min': -3000, 'x_max': 3500,
        'y_min': -2800, 'y_max': 2500,
        'scale': 1024
    }
}


def plot_heatmap_with_overlay(analysis, output_path='heatmap_overlay.png'):
    """Generate heatmap with map image overlay"""
    positioning = analysis['positioning']
    heatmap_data = positioning['heatmap_data']
    map_name = positioning['map_name']
    
    death_positions = heatmap_data['death_positions']
    kill_positions = heatmap_data['kill_positions']
    
    if not death_positions and not kill_positions:
        print("❌ No position data to plot")
        return
    
    # Try to load map image
    map_image_path = f"maps/{map_name}.png"
    has_map_image = os.path.exists(map_image_path)
    
    if not has_map_image:
        print(f"⚠️  Map image not found at {map_image_path}")
        print(f"💡 Download a radar image for {map_name} and place it in the 'maps/' folder")
        print(f"   Continuing with basic visualization...")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 16))
    
    # Get map bounds
    bounds = MAP_BOUNDS.get(map_name, {
        'x_min': -3000, 'x_max': 3000,
        'y_min': -3000, 'y_max': 3000,
        'scale': 1024
    })
    
    # If map image exists, display it as background
    if has_map_image:
        try:
            img = Image.open(map_image_path)
            # Display image with proper bounds
            ax.imshow(img, 
                     extent=[bounds['x_min'], bounds['x_max'], 
                            bounds['y_min'], bounds['y_max']],
                     aspect='auto', alpha=0.7, zorder=0)
            print(f"✅ Using map overlay: {map_image_path}")
        except Exception as e:
            print(f"⚠️  Could not load map image: {e}")
            has_map_image = False
    
    # If no image, draw zone rectangles
    if not has_map_image:
        zones = MAP_ZONES.get(map_name, [])
        for min_x, max_x, min_y, max_y, zone_name in zones:
            rect = patches.Rectangle(
                (min_x, min_y),
                max_x - min_x,
                max_y - min_y,
                linewidth=0.5,
                edgecolor='gray',
                facecolor='lightgray',
                alpha=0.2,
                zorder=0
            )
            ax.add_patch(rect)
            
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            ax.text(center_x, center_y, zone_name, 
                   ha='center', va='center', 
                   fontsize=10, alpha=0.6, color='gray',
                   fontweight='bold', zorder=1)
    
    # Plot deaths (red circles with black border)
    if death_positions:
        deaths_x = [pos[0] for pos in death_positions]
        deaths_y = [pos[1] for pos in death_positions]
        
        # Main death markers
        ax.scatter(deaths_x, deaths_y, 
                  c='red', s=200, alpha=0.7, 
                  label=f'Deaths ({len(death_positions)})',
                  edgecolors='black', linewidths=2,
                  zorder=10)
        
        # Add glow effect
        ax.scatter(deaths_x, deaths_y, 
                  c='red', s=400, alpha=0.2,
                  edgecolors='none',
                  zorder=9)
    
    # Plot kills (green triangles with black border)
    if kill_positions:
        kills_x = [pos[0] for pos in kill_positions]
        kills_y = [pos[1] for pos in kill_positions]
        
        # Main kill markers
        ax.scatter(kills_x, kills_y, 
                  c='limegreen', s=250, alpha=0.8, 
                  label=f'Kills ({len(kill_positions)})',
                  edgecolors='black', linewidths=2,
                  marker='^', zorder=10)
        
        # Add glow effect
        ax.scatter(kills_x, kills_y, 
                  c='limegreen', s=450, alpha=0.2,
                  edgecolors='none', marker='^',
                  zorder=9)
    
    # Set axis limits based on map bounds
    ax.set_xlim(bounds['x_min'], bounds['x_max'])
    ax.set_ylim(bounds['y_min'], bounds['y_max'])
    
    # Styling
    ax.set_xlabel('X Coordinate', fontsize=14, fontweight='bold')
    ax.set_ylabel('Y Coordinate', fontsize=14, fontweight='bold')
    ax.set_title(f'Heatmap de Positionnement - {map_name.upper()}', 
                fontsize=20, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=14, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_aspect('equal', adjustable='box')
    
    # Add summary stats box (top left)
    summary = analysis['summary']
    stats_text = (
        f"K/D: {summary['kd_ratio']:.2f}\n"
        f"HSR: {summary['headshot_rate']:.1f}%\n"
        f"Crosshair: {summary['avg_crosshair_offset']:.0f}°"
    )
    ax.text(0.02, 0.98, stats_text, 
            transform=ax.transAxes,
            fontsize=12, verticalalignment='top',
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', 
                     alpha=0.9, edgecolor='black', linewidth=2))
    
    # Add danger zones box (bottom right)
    danger_zones = positioning.get('danger_zones', [])
    if danger_zones:
        danger_text = "⚠️ ZONES DANGEREUSES\n" + "─" * 25 + "\n"
        for i, dz in enumerate(danger_zones[:3], 1):
            danger_text += f"{i}. {dz['zone']}\n   K/D: {dz['kd_ratio']:.2f} | {dz['deaths']} morts\n"
        
        ax.text(0.98, 0.02, danger_text.strip(), 
                transform=ax.transAxes,
                fontsize=11, verticalalignment='bottom',
                horizontalalignment='right',
                fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#ffcccc', 
                         alpha=0.95, edgecolor='darkred', linewidth=2))
    
    # Add strong zones box (top right)
    strong_zones = positioning.get('strong_zones', [])
    if strong_zones:
        strong_text = "✅ ZONES FORTES\n" + "─" * 20 + "\n"
        for i, sz in enumerate(strong_zones[:3], 1):
            strong_text += f"{i}. {sz['zone']}\n   K/D: {sz['kd_ratio']:.2f}\n"
        
        ax.text(0.98, 0.98, strong_text.strip(), 
                transform=ax.transAxes,
                fontsize=11, verticalalignment='top',
                horizontalalignment='right',
                fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#ccffcc', 
                         alpha=0.95, edgecolor='darkgreen', linewidth=2))
    
    plt.tight_layout()
    
    # Save with high quality
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"✅ Heatmap saved to: {output_path}")
    
    # Display
    try:
        plt.show()
    except:
        print("💡 Heatmap saved but couldn't display (headless environment)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_heatmap_overlay.py <demo_file> <player_name> [output.png]")
        sys.exit(1)
    
    demo_path = sys.argv[1]
    player_name = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else 'heatmap_overlay.png'
    
    # Parse and analyze
    print(f"📂 Parsing {demo_path}...")
    parser = DemoParser(demo_path)
    events = parser.parse(player_name)
    
    print(f"🔍 Analyzing {player_name}...")
    analyzer = GapAnalyzer(events)
    analysis = analyzer.analyze()
    
    # Generate heatmap
    print(f"🎨 Generating heatmap with overlay...")
    plot_heatmap_with_overlay(analysis, output_path)
    
    # Show positioning summary
    pos = analysis['positioning']
    print(f"\n📊 Summary:")
    print(f"  Map: {pos['map_name']}")
    print(f"  Total deaths: {len(events['deaths'])}")
    print(f"  Total kills: {len(events['kills'])}")
    print(f"  Danger zones: {len(pos['danger_zones'])}")
    print(f"  Strong zones: {len(pos['strong_zones'])}")


if __name__ == "__main__":
    main()
