#!/usr/bin/env python3
"""
CS2 Gap Analyzer - Main Entry Point

Usage:
    python main.py <demo_file.dem> <player_name>
    
Example:
    python main.py demos/match.dem "YourSteamName"
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parser import DemoParser
from analyzer import GapAnalyzer
from report import ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Analyse CS2 demo files to identify improvement areas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py demos/match.dem "PlayerName"
  python main.py ~/Downloads/match123.dem "PlayerName" --save
        """
    )
    
    parser.add_argument(
        "demo_file",
        type=str,
        help="Path to CS2 demo file (.dem)"
    )
    
    parser.add_argument(
        "player_name",
        type=str,
        help="Your in-game player name (case-sensitive)"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save detailed JSON events and text report to output/"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for saved files (default: output/)"
    )
    
    args = parser.parse_args()
    
    # Validate demo file
    demo_path = Path(args.demo_file)
    if not demo_path.exists():
        print(f"❌ Error: Demo file not found: {args.demo_file}")
        sys.exit(1)
    
    if not demo_path.suffix == ".dem":
        print(f"⚠️  Warning: File doesn't have .dem extension")
    
    print(f"🎮 Analyzing CS2 demo: {demo_path.name}")
    print(f"👤 Player: {args.player_name}")
    print()
    
    try:
        # ÉTAPE 1: Parse demo
        print("📂 Parsing demo file...")
        demo_parser = DemoParser(str(demo_path))
        events = demo_parser.parse(args.player_name)
        
        print(f"   ✓ Found {len(events['deaths'])} deaths")
        print(f"   ✓ Found {len(events['kills'])} kills")
        print(f"   ✓ Found {len(events['flashes'])} flashes")
        print()
        
        # ÉTAPES 2-4: Analyze events
        print("🔍 Analyzing gameplay...")
        analyzer = GapAnalyzer(events)
        analysis = analyzer.analyze()
        print("   ✓ Analysis complete")
        print()
        
        # ÉTAPE 5: Generate report
        reporter = ReportGenerator(analysis, args.player_name)
        reporter.print_report()
        
        # Save if requested
        if args.save:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save events JSON
            demo_name = demo_path.stem
            events_file = output_dir / f"{demo_name}_events.json"
            demo_parser.save_events(events, str(events_file))
            
            # Save report
            report_file = output_dir / f"{demo_name}_report.txt"
            reporter.save_report(str(report_file))
            
            print()
            print(f"💾 Files saved to: {output_dir}/")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Install dependencies with:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
