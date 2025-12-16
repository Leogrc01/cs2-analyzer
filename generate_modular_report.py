#!/usr/bin/env python3
"""
CS2 Gap Analyzer - Generate modular reports
"""
import sys
from pathlib import Path

from src.parser import DemoParser
from src.analyzer import GapAnalyzer
from src.modular_report import ModularReportGenerator


AVAILABLE_SECTIONS = {
    'overview': '📊 Vue d\'ensemble',
    'crosshair': '🎯 Crosshair placement',
    'deaths': '💀 Analyse des morts',
    'utility': '💥 Utilisation des utilitaires',
    'economy': '💰 Analyse économique',
    'positioning': '🗺️  Positionnement',
    'priorities': '🎯 Priorités d\'amélioration'
}


def main():
    """Main entry point"""
    if len(sys.argv) < 4:
        print("Usage: python generate_modular_report.py <demo_path> <player_name> <section> [output_dir]")
        print(f"\nAvailable sections:")
        for key, label in AVAILABLE_SECTIONS.items():
            print(f"  - {key:12s}: {label}")
        sys.exit(1)
    
    demo_path = sys.argv[1]
    player_name = sys.argv[2]
    section = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "output"
    
    # Validate section
    if section not in AVAILABLE_SECTIONS:
        print(f"❌ Section inconnue: {section}")
        print(f"\nSections disponibles:")
        for key, label in AVAILABLE_SECTIONS.items():
            print(f"  - {key:12s}: {label}")
        sys.exit(1)
    
    # Validate demo file
    if not Path(demo_path).exists():
        print(f"❌ Demo file not found: {demo_path}")
        sys.exit(1)
    
    print(f"\n📊 Generating {AVAILABLE_SECTIONS[section]} report")
    print(f"👤 Player: {player_name}")
    print(f"📂 Demo: {demo_path}")
    print("=" * 70)
    
    # Parse demo
    print("\n🔍 Parsing demo...")
    parser = DemoParser(demo_path)
    events = parser.parse_player_events(player_name)
    
    if not events or not events.get("deaths"):
        print(f"❌ No events found for player: {player_name}")
        print("💡 Make sure the player name is spelled exactly as in-game (case-sensitive)")
        sys.exit(1)
    
    print(f"   ✅ Found {len(events.get('deaths', []))} deaths, {len(events.get('kills', []))} kills")
    
    # Analyze gameplay
    print("\n📈 Analyzing gameplay...")
    analyzer = GapAnalyzer(events)
    analysis = analyzer.analyze()
    print("   ✅ Analysis complete")
    
    # Generate modular report
    print(f"\n📝 Generating {section} report...")
    report_gen = ModularReportGenerator(analysis, player_name)
    
    # Print to console
    report_gen.print_section(section)
    
    # Save to file
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    demo_name = Path(demo_path).stem
    report_file = output_path / f"{demo_name}_{section}_report.txt"
    report_gen.save_section(section, str(report_file))
    
    print(f"\n✅ Done! Report saved to: {report_file}")


if __name__ == "__main__":
    main()
