#!/usr/bin/env python3
"""
Generate visual heatmap from CS2 demo analysis
Usage: python generate_heatmap.py demos/match.dem "PlayerName"
"""
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from src.parser import DemoParser
from src.analyzer import GapAnalyzer
from src.positioning import MAP_ZONES


def plot_heatmap(analysis, output_path='heatmap.png'):
    """Generate and save heatmap visualization"""
    positioning = analysis['positioning']
    heatmap_data = positioning['heatmap_data']
    map_name = positioning['map_name']
    
    death_positions = heatmap_data['death_positions']
    kill_positions = heatmap_data['kill_positions']
    
    if not death_positions and not kill_positions:
        print("❌ No position data to plot")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot map zones as rectangles (if available)
    zones = MAP_ZONES.get(map_name, [])
    for min_x, max_x, min_y, max_y, zone_name in zones:
        rect = patches.Rectangle(
            (min_x, min_y),
            max_x - min_x,
            max_y - min_y,
            linewidth=0.5,
            edgecolor='gray',
            facecolor='none',
            alpha=0.3
        )
        ax.add_patch(rect)
        
        # Add zone label at center
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        ax.text(center_x, center_y, zone_name, 
                ha='center', va='center', 
                fontsize=8, alpha=0.5, color='gray')
    
    # Plot deaths (red)
    if death_positions:
        deaths_x = [pos[0] for pos in death_positions]
        deaths_y = [pos[1] for pos in death_positions]
        ax.scatter(deaths_x, deaths_y, 
                  c='red', s=100, alpha=0.6, 
                  label=f'Deaths ({len(death_positions)})',
                  edgecolors='darkred', linewidths=1.5)
    
    # Plot kills (green)
    if kill_positions:
        kills_x = [pos[0] for pos in kill_positions]
        kills_y = [pos[1] for pos in kill_positions]
        ax.scatter(kills_x, kills_y, 
                  c='green', s=100, alpha=0.6, 
                  label=f'Kills ({len(kill_positions)})',
                  edgecolors='darkgreen', linewidths=1.5, marker='^')
    
    # Styling
    ax.set_xlabel('X Coordinate', fontsize=12)
    ax.set_ylabel('Y Coordinate', fontsize=12)
    ax.set_title(f'Heatmap de Positionnement - {map_name}', fontsize=16, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    
    # Add summary stats
    summary = analysis['summary']
    stats_text = f"K/D: {summary['kd_ratio']:.2f} | HSR: {summary['headshot_rate']:.1f}%"
    ax.text(0.02, 0.98, stats_text, 
            transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Add danger zones info
    danger_zones = positioning.get('danger_zones', [])
    if danger_zones:
        danger_text = "Zones dangereuses:\n"
        for dz in danger_zones[:3]:
            danger_text += f"• {dz['zone']} (K/D {dz['kd_ratio']:.2f})\n"
        
        ax.text(0.98, 0.02, danger_text.strip(), 
                transform=ax.transAxes,
                fontsize=9, verticalalignment='bottom',
                horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Heatmap saved to: {output_path}")
    
    # Display
    try:
        plt.show()
    except:
        print("💡 Heatmap saved but couldn't display (headless environment)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_heatmap.py <demo_file> <player_name> [output.png]")
        sys.exit(1)
    
    demo_path = sys.argv[1]
    player_name = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else 'heatmap.png'
    
    # Parse and analyze
    print(f"📂 Parsing {demo_path}...")
    parser = DemoParser(demo_path)
    events = parser.parse(player_name)
    
    print(f"🔍 Analyzing {player_name}...")
    analyzer = GapAnalyzer(events)
    analysis = analyzer.analyze()
    
    # Generate heatmap
    print(f"🎨 Generating heatmap...")
    plot_heatmap(analysis, output_path)
    
    # Show positioning summary
    pos = analysis['positioning']
    print(f"\n📊 Summary:")
    print(f"  Map: {pos['map_name']}")
    print(f"  Total engagements: {len(events['deaths']) + len(events['kills'])}")
    print(f"  Danger zones: {len(pos['danger_zones'])}")
    print(f"  Strong zones: {len(pos['strong_zones'])}")


if __name__ == "__main__":
    main()
