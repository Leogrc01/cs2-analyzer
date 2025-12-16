#!/usr/bin/env python3
"""
CS2 Gap Analyzer - Analyze multiple demos from a map folder
"""
import sys
import json
from pathlib import Path
from typing import List

from src.parser import DemoParser
from src.analyzer import GapAnalyzer
from src.aggregated_analysis import AggregatedAnalyzer


def find_demo_files(folder_path: str) -> List[Path]:
    """Find all .dem files in folder"""
    folder = Path(folder_path)
    
    if not folder.exists():
        return []
    
    dem_files = list(folder.glob("*.dem"))
    dem_files.sort()  # Sort for chronological order
    
    return dem_files


def analyze_demo(demo_path: Path, player_name: str) -> dict:
    """Analyze a single demo and return results"""
    try:
        print(f"  📊 Parsing {demo_path.name}...")
        parser = DemoParser(str(demo_path))
        events = parser.parse_player_events(player_name)
        
        if not events or not events.get("deaths"):
            print(f"    ⚠️  No events found (wrong player name or no data)")
            return None
        
        print(f"    ✅ Found {len(events.get('deaths', []))} deaths, {len(events.get('kills', []))} kills")
        
        analyzer = GapAnalyzer(events)
        analysis = analyzer.analyze()
        
        return analysis
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None


def generate_aggregated_report(aggregated_stats: dict, output_path: str):
    """Generate human-readable aggregated report"""
    lines = []
    
    meta = aggregated_stats['meta']
    summary = aggregated_stats['summary']
    crosshair = aggregated_stats['crosshair']
    deaths = aggregated_stats['deaths']
    utility = aggregated_stats['utility']
    economy = aggregated_stats['economy']
    positioning = aggregated_stats['positioning']
    priorities = aggregated_stats['priorities']
    trends = aggregated_stats['trends']
    best_worst = aggregated_stats['best_worst']
    
    # Header
    lines.append("=" * 80)
    lines.append("   📊 CS2 GAP ANALYZER - ANALYSE AGRÉGÉE PAR MAP")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"🗺️  Map: {meta['map_name']}")
    lines.append(f"📁 Total demos analyzed: {meta['total_demos']}")
    lines.append(f"📋 Demos: {', '.join(meta['demo_names'])}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    # Summary
    lines.append("📊 VUE D'ENSEMBLE AGRÉGÉE")
    lines.append("-" * 80)
    lines.append(f"K/D Ratio (moyenne)     : {summary['avg_kd_ratio']:.2f} (σ={summary['std_kd_ratio']:.2f}, {summary['consistency_kd']} consistency)")
    lines.append(f"Headshot Rate (moyenne) : {summary['avg_headshot_rate']:.1f}% (σ={summary['std_headshot_rate']:.1f}%, {summary['consistency_hsr']} consistency)")
    lines.append(f"Crosshair Placement     : {summary['avg_bad_crosshair_pct']:.0f}% mauvais (avg offset: {summary['avg_crosshair_offset']:.0f}°)")
    lines.append(f"Morts évitables         : {summary['avg_avoidable_deaths_pct']:.0f}%")
    lines.append(f"Duels désavantagés      : {summary['avg_no_advantage_duels_pct']:.0f}%")
    lines.append(f"Flashes utiles          : {summary['avg_flash_useful_pct']:.0f}% ({summary['avg_pop_flash_pct']:.0f}% pop flashes)")
    lines.append(f"Impact économique       : {summary['total_value_lost']}$ perdus total (avg: {summary['avg_death_cost']}$/mort)")
    lines.append(f"Morts coûteuses         : {summary['avg_expensive_deaths_pct']:.0f}%")
    lines.append("")
    lines.append(f"📈 TOTAUX:")
    lines.append(f"   Kills: {summary['total_kills']} | Deaths: {summary['total_deaths']} | Flashes: {summary['total_flashes']}")
    lines.append("")
    
    # Trends
    if trends.get('available'):
        lines.append("📈 TENDANCES (première moitié vs seconde moitié)")
        lines.append("-" * 80)
        
        kd_emoji = "📈" if trends['kd_trend'] == 'Improving' else "📉" if trends['kd_trend'] == 'Declining' else "➡️"
        hsr_emoji = "📈" if trends['hsr_trend'] == 'Improving' else "📉" if trends['hsr_trend'] == 'Declining' else "➡️"
        xhair_emoji = "📈" if trends['crosshair_trend'] == 'Improving' else "📉" if trends['crosshair_trend'] == 'Declining' else "➡️"
        
        lines.append(f"{kd_emoji} K/D: {trends['kd_trend']} ({trends['kd_change']:+.2f})")
        lines.append(f"{hsr_emoji} HSR: {trends['hsr_trend']} ({trends['hsr_change']:+.1f}%)")
        lines.append(f"{xhair_emoji} Crosshair: {trends['crosshair_trend']} ({trends['crosshair_change']:+.1f}% bad placement)")
        lines.append("")
    
    # Best/Worst demos
    if best_worst:
        lines.append("🏆 MEILLEURES / PIRES PERFORMANCES")
        lines.append("-" * 80)
        lines.append(f"🥇 Best K/D    : {best_worst['best_kd']['demo']} (K/D: {best_worst['best_kd']['value']:.2f})")
        lines.append(f"🥉 Worst K/D   : {best_worst['worst_kd']['demo']} (K/D: {best_worst['worst_kd']['value']:.2f})")
        lines.append(f"🎯 Best Aim    : {best_worst['best_crosshair']['demo']} ({best_worst['best_crosshair']['value']:.0f}% bad)")
        lines.append(f"⚠️  Worst Aim  : {best_worst['worst_crosshair']['demo']} ({best_worst['worst_crosshair']['value']:.0f}% bad)")
        lines.append("")
    
    # Priorities
    if priorities:
        lines.append("🎯 PRIORITÉS RÉCURRENTES SUR CETTE MAP")
        lines.append("-" * 80)
        for i, priority in enumerate(priorities, 1):
            lines.append(f"{i}. {priority['category']}")
            lines.append(f"   Fréquence: {priority['frequency']:.0f}% ({priority['appears_in']})")
            lines.append(f"   Sévérité moyenne: {priority['avg_severity']:.1f}%")
            lines.append("")
    
    # Crosshair details
    lines.append("🎯 CROSSHAIR PLACEMENT AGRÉGÉ")
    lines.append("-" * 80)
    lines.append(f"Offset moyen        : {crosshair['avg_offset']:.1f}°")
    lines.append(f"Total duels         : {crosshair['total_analyzed']}")
    lines.append(f"Mauvais placement   : {crosshair['total_bad_placement']}/{crosshair['total_analyzed']} ({crosshair['bad_placement_pct']:.0f}%)")
    
    if crosshair['worst_placements']:
        lines.append(f"\nPires 5 placements (tous demos confondus):")
        for i, placement in enumerate(crosshair['worst_placements'][:5], 1):
            lines.append(f"  {i}. {placement['offset']:.0f}° vs {placement['attacker']}")
    lines.append("")
    
    # Deaths
    lines.append("💀 ANALYSE DES MORTS AGRÉGÉE")
    lines.append("-" * 80)
    lines.append(f"Total morts          : {deaths['total_deaths']}")
    lines.append(f"Morts évitables      : {deaths['total_avoidable']} ({deaths['avoidable_pct']:.0f}%)")
    lines.append(f"Sans avantage        : {deaths['total_no_advantage']} ({deaths['no_advantage_pct']:.0f}%)")
    
    if deaths['most_common_death_weapons']:
        lines.append(f"\nArmes les plus mortelles:")
        for weapon, count in deaths['most_common_death_weapons']:
            pct = round(count / deaths['total_deaths'] * 100, 0)
            lines.append(f"  • {weapon}: {count} morts ({pct:.0f}%)")
    lines.append("")
    
    # Utility
    lines.append("💥 UTILISATION DES UTILITAIRES")
    lines.append("-" * 80)
    lines.append(f"Total flashes        : {utility['total_flashes']}")
    lines.append(f"Flashes utiles       : {utility['total_useful']} ({utility['useful_pct']:.0f}%)")
    lines.append(f"Pop flashes          : {utility['total_pop_flashes']} ({utility['pop_flash_pct']:.0f}%)")
    lines.append("")
    
    # Economy
    lines.append("💰 ANALYSE ÉCONOMIQUE")
    lines.append("-" * 80)
    lines.append(f"Valeur totale perdue : {economy['total_value_lost']}$")
    lines.append(f"Coût moyen par mort  : {economy['avg_death_cost']}$")
    lines.append(f"Morts coûteuses      : {economy['avg_expensive_deaths_pct']:.0f}%")
    
    if economy['round_types']:
        lines.append(f"\nPerformance par type de round:")
        for buy_type, stats in economy['round_types'].items():
            buy_label = {
                'full_buy': 'Full Buy',
                'force_buy': 'Force Buy',
                'eco': 'Eco',
                'pistol': 'Pistol'
            }.get(buy_type, buy_type)
            lines.append(f"  • {buy_label:12s}: {stats['deaths']} morts (avg {stats['avg_value_lost']}$/mort)")
    lines.append("")
    
    # Positioning
    lines.append(f"🗺️  POSITIONNEMENT SUR {positioning['map_name'].upper()}")
    lines.append("-" * 80)
    
    if positioning['worst_zones']:
        lines.append("⚠️  ZONES À ÉVITER (K/D faible):")
        for zone_info in positioning['worst_zones']:
            lines.append(f"  • {zone_info['zone']:20s}: K/D {zone_info['kd_ratio']:.2f} ({zone_info['kills']}K/{zone_info['deaths']}D)")
        lines.append("")
    
    if positioning['best_zones']:
        lines.append("✅ ZONES PERFORMANTES (K/D élevé):")
        for zone_info in positioning['best_zones']:
            lines.append(f"  • {zone_info['zone']:20s}: K/D {zone_info['kd_ratio']:.2f} ({zone_info['kills']}K/{zone_info['deaths']}D)")
        lines.append("")
    
    # Recommendations
    lines.append("=" * 80)
    lines.append("💡 RECOMMANDATIONS SPÉCIFIQUES À CETTE MAP")
    lines.append("=" * 80)
    
    # Priority-based recommendations
    if priorities:
        top_priority = priorities[0]
        lines.append(f"\n🎯 PRIORITÉ #1: {top_priority['category']}")
        lines.append(f"   Apparaît dans {top_priority['appears_in']}")
        lines.append(f"   → Travailler cet aspect spécifiquement sur {meta['map_name']}")
    
    # Positioning recommendations
    if positioning['worst_zones']:
        worst_zone = positioning['worst_zones'][0]
        lines.append(f"\n⚠️  ZONE DANGEREUSE: {worst_zone['zone']}")
        lines.append(f"   K/D {worst_zone['kd_ratio']:.2f} - Éviter ou changer d'approche")
    
    if positioning['best_zones']:
        best_zone = positioning['best_zones'][0]
        lines.append(f"\n✅ ZONE FORTE: {best_zone['zone']}")
        lines.append(f"   K/D {best_zone['kd_ratio']:.2f} - Exploiter cette force")
    
    # Consistency recommendations
    if summary['consistency_kd'] == 'Low':
        lines.append(f"\n📊 CONSISTENCY: Performances variables (σ={summary['std_kd_ratio']:.2f})")
        lines.append(f"   → Travailler la consistency sur {meta['map_name']}")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python analyze_map_folder.py <folder_path> <player_name> [output_dir]")
        print("\nExample:")
        print("  python analyze_map_folder.py demos/dust2 'PlayerName' output")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    player_name = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    
    # Find demo files
    demo_files = find_demo_files(folder_path)
    
    if not demo_files:
        print(f"❌ No .dem files found in: {folder_path}")
        print("\n💡 Make sure you have .dem files in the folder:")
        print(f"   {folder_path}/")
        print(f"   ├── match1.dem")
        print(f"   ├── match2.dem")
        print(f"   └── match3.dem")
        sys.exit(1)
    
    print(f"\n📊 CS2 GAP ANALYZER - ANALYSE AGRÉGÉE")
    print("=" * 70)
    print(f"📁 Folder: {folder_path}")
    print(f"👤 Player: {player_name}")
    print(f"📋 Found {len(demo_files)} demo files")
    print("=" * 70)
    print("")
    
    # Analyze all demos
    aggregator = AggregatedAnalyzer()
    successful_analyses = 0
    
    for demo_file in demo_files:
        analysis = analyze_demo(demo_file, player_name)
        
        if analysis:
            aggregator.add_analysis(analysis, demo_file.stem)
            successful_analyses += 1
    
    if successful_analyses == 0:
        print("\n❌ No successful analyses")
        print("💡 Make sure the player name is spelled exactly as in-game (case-sensitive)")
        sys.exit(1)
    
    print(f"\n✅ Successfully analyzed {successful_analyses}/{len(demo_files)} demos")
    print("\n📈 Computing aggregated statistics...")
    
    # Compute aggregated stats
    aggregated_stats = aggregator.compute_aggregated_stats()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate outputs
    folder_name = Path(folder_path).name
    map_name = aggregated_stats['meta']['map_name']
    
    print("\n💾 Generating output files...")
    
    # 1. Text report
    report_file = output_path / f"{folder_name}_aggregated_report.txt"
    generate_aggregated_report(aggregated_stats, str(report_file))
    print(f"   ✅ Report: {report_file}")
    
    # 2. JSON data
    json_file = output_path / f"{folder_name}_aggregated_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(aggregated_stats, f, indent=2, ensure_ascii=False)
    print(f"   ✅ JSON: {json_file}")
    
    # Print summary to console
    print("\n" + "=" * 70)
    print("✅ ANALYSE AGRÉGÉE TERMINÉE!")
    print("=" * 70)
    
    summary = aggregated_stats['summary']
    print(f"\n📊 RÉSUMÉ ({map_name.upper()}):")
    print(f"   K/D moyen: {summary['avg_kd_ratio']:.2f}")
    print(f"   HSR moyen: {summary['avg_headshot_rate']:.1f}%")
    print(f"   Crosshair: {summary['avg_bad_crosshair_pct']:.0f}% mauvais")
    print(f"   Consistency: {summary['consistency_kd']} (σ={summary['std_kd_ratio']:.2f})")
    
    # Show trends if available
    trends = aggregated_stats['trends']
    if trends.get('available'):
        print(f"\n📈 TENDANCE:")
        print(f"   K/D: {trends['kd_trend']} ({trends['kd_change']:+.2f})")
        print(f"   HSR: {trends['hsr_trend']} ({trends['hsr_change']:+.1f}%)")
    
    print(f"\n📁 Fichiers générés dans {output_dir}/")
    print("")


if __name__ == "__main__":
    main()
