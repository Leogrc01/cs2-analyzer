#!/usr/bin/env python3
"""
Quick script to visualize positioning analysis
Usage: python show_positioning.py demos/match.dem "PlayerName"
"""
import sys
from src.parser import DemoParser
from src.analyzer import GapAnalyzer


def main():
    if len(sys.argv) < 3:
        print("Usage: python show_positioning.py <demo_file> <player_name>")
        sys.exit(1)
    
    demo_path = sys.argv[1]
    player_name = sys.argv[2]
    
    # Parse and analyze
    print(f"📂 Parsing {demo_path}...")
    parser = DemoParser(demo_path)
    events = parser.parse(player_name)
    
    print(f"🔍 Analyzing {player_name}...")
    analyzer = GapAnalyzer(events)
    analysis = analyzer.analyze()
    
    # Display positioning summary
    pos = analysis['positioning']
    recommendations = analysis['positioning_recommendations']
    
    print("\n" + "="*70)
    print("🗺️  POSITIONNEMENT - RÉSUMÉ")
    print("="*70)
    print(f"Map: {pos['map_name']}")
    print()
    
    # Zone performance table
    zone_perf = pos['zone_performance']
    if zone_perf:
        print("Performance par zone:")
        print(f"{'Zone':<20} {'Kills':>6} {'Deaths':>7} {'K/D':>6} {'Status':>10}")
        print("-" * 70)
        
        # Sort by engagements
        sorted_zones = sorted(
            zone_perf.items(),
            key=lambda x: x[1]['engagements'],
            reverse=True
        )
        
        for zone_name, perf in sorted_zones[:10]:  # Top 10 zones
            status = "🟢" if perf['kd_ratio'] >= 1.0 else "🔴" if perf['kd_ratio'] < 0.5 else "🟡"
            print(f"{zone_name:<20} {perf['kills']:>6} {perf['deaths']:>7} {perf['kd_ratio']:>6.2f} {status:>10}")
    
    print()
    
    # Heatmap data summary
    heatmap = pos['heatmap_data']
    print(f"Heatmap: {len(heatmap['death_positions'])} death positions, {len(heatmap['kill_positions'])} kill positions")
    print()
    
    # Recommendations
    if recommendations:
        print("💡 RECOMMANDATIONS:")
        for rec in recommendations:
            print(f"  {rec}")
    
    print()
    print("="*70)


if __name__ == "__main__":
    main()
