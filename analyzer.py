#!/usr/bin/env python3
"""
CS2 Gap Analyzer - Interactive Menu
Main entry point for easy analysis
"""
import os
import sys
from pathlib import Path


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print("🎮 CS2 GAP ANALYZER - Menu Principal")
    print("="*70 + "\n")


def print_menu():
    """Display main menu options"""
    print("📋 OPTIONS DISPONIBLES:")
    print("-" * 70)
    print("  1. 📊 Analyse complète (rapport + heatmap)")
    print("  2. 📝 Rapport textuel uniquement")
    print("  3. 🎬 Générer highlights (timestamps + script CS2)")
    print("  4. 📑 Rapport modulaire (section spécifique)")
    print("  5. 🗺️  Heatmap uniquement")
    print("  6. 📍 Vue détaillée positionnement")
    print("  7. 🔧 Calibrer coordonnées map")
    print("  8. ℹ️  Aide / Documentation")
    print("  0. ❌ Quitter")
    print("-" * 70)


def list_demos(demos_folder="demos"):
    """List available demo files"""
    if not os.path.exists(demos_folder):
        return []
    
    demos = [f for f in os.listdir(demos_folder) if f.endswith('.dem')]
    return sorted(demos)


def select_demo():
    """Interactive demo file selection"""
    demos_folder = "demos"
    demos = list_demos(demos_folder)
    
    if not demos:
        print(f"\n⚠️  Aucun fichier .dem trouvé dans le dossier '{demos_folder}/'")
        print(f"💡 Placez vos démos CS2 dans le dossier '{demos_folder}/'")
        
        manual = input("\n📂 Entrer un chemin manuel ? (o/n): ").strip().lower()
        if manual == 'o':
            path = input("Chemin du fichier .dem: ").strip()
            if os.path.exists(path):
                return path
            else:
                print("❌ Fichier introuvable")
                return None
        return None
    
    print(f"\n📂 FICHIERS .DEM DISPONIBLES ({len(demos)} trouvés):")
    print("-" * 70)
    for i, demo in enumerate(demos, 1):
        size = os.path.getsize(os.path.join(demos_folder, demo)) / (1024*1024)
        print(f"  {i}. {demo} ({size:.1f} MB)")
    print(f"  0. Chemin manuel")
    print("-" * 70)
    
    while True:
        try:
            choice = input("\n🎯 Sélectionner un fichier (numéro): ").strip()
            
            if choice == '0':
                path = input("Chemin du fichier .dem: ").strip()
                if os.path.exists(path):
                    return path
                else:
                    print("❌ Fichier introuvable")
                    continue
            
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                return os.path.join(demos_folder, demos[idx])
            else:
                print("❌ Numéro invalide")
        except ValueError:
            print("❌ Entrer un numéro valide")
        except KeyboardInterrupt:
            return None


def get_player_name():
    """Get player name from user"""
    print("\n👤 NOM DU JOUEUR:")
    print("💡 Le nom doit correspondre EXACTEMENT au pseudo in-game (sensible à la casse)")
    name = input("Nom du joueur à analyser: ").strip()
    
    if not name:
        print("❌ Nom vide")
        return None
    
    return name


def run_full_analysis(demo_path, player_name):
    """Run complete analysis with report and heatmap"""
    print("\n🔍 Analyse complète en cours...")
    print("="*70)
    
    # Run main analysis with save
    cmd = f'venv/bin/python main.py "{demo_path}" "{player_name}" --save'
    print(f"\n📊 Génération du rapport...")
    os.system(cmd)
    
    # Generate heatmap
    print(f"\n🎨 Génération de la heatmap...")
    cmd_heatmap = f'venv/bin/python generate_heatmap_overlay.py "{demo_path}" "{player_name}" output/heatmap.png'
    os.system(cmd_heatmap)
    
    print("\n✅ ANALYSE TERMINÉE!")
    print(f"📁 Fichiers générés dans output/:")
    print(f"   • Rapport: output/*_report.txt")
    print(f"   • Events: output/*_events.json")
    print(f"   • Heatmap: output/heatmap.png")


def run_report_only(demo_path, player_name):
    """Run report analysis only"""
    print("\n📝 Génération du rapport...")
    cmd = f'venv/bin/python main.py "{demo_path}" "{player_name}" --save'
    os.system(cmd)


def run_heatmap_only(demo_path, player_name):
    """Generate heatmap only"""
    print("\n🗺️  Génération de la heatmap...")
    cmd = f'venv/bin/python generate_heatmap_overlay.py "{demo_path}" "{player_name}" output/heatmap.png'
    os.system(cmd)
    print("\n✅ Heatmap générée: output/heatmap.png")


def run_positioning_view(demo_path, player_name):
    """Show detailed positioning view"""
    print("\n📍 Vue détaillée du positionnement...")
    cmd = f'venv/bin/python show_positioning.py "{demo_path}" "{player_name}"'
    os.system(cmd)


def run_calibration(demo_path, player_name):
    """Run map calibration tool"""
    print("\n🔧 Outil de calibration des coordonnées...")
    cmd = f'venv/bin/python calibrate_map.py "{demo_path}" "{player_name}"'
    os.system(cmd)


def run_highlights(demo_path, player_name):
    """Generate highlights with timestamps and CS2 script"""
    print("\n🎬 Génération des highlights...")
    cmd = f'venv/bin/python generate_highlights.py "{demo_path}" "{player_name}" output'
    os.system(cmd)
    print("\n✅ HIGHLIGHTS GÉNÉRÉS!")
    print(f"📁 Fichiers disponibles dans output/:")
    print(f"   • output/*_highlights.txt - Liste des moments clés")
    print(f"   • output/highlights.cfg - Script CS2 de navigation")
    print(f"   • output/*_highlights.json - Données JSON")
    print(f"\n💡 NEXT STEP: Copier highlights.cfg vers:")
    print(f"   ~/.steam/steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg/")


def run_modular_report(demo_path, player_name):
    """Generate modular report for specific section"""
    print("\n📑 RAPPORT MODULAIRE")
    print("=" * 70)
    print("\nSections disponibles:")
    print("  1. 📊 Vue d'ensemble")
    print("  2. 🎯 Crosshair placement")
    print("  3. 💀 Analyse des morts")
    print("  4. 💥 Utilisation des utilitaires")
    print("  5. 💰 Analyse économique")
    print("  6. 🗺️  Positionnement")
    print("  7. 🎯 Priorités d'amélioration")
    print("  0. Annuler")
    print("=" * 70)
    
    section_map = {
        '1': 'overview',
        '2': 'crosshair',
        '3': 'deaths',
        '4': 'utility',
        '5': 'economy',
        '6': 'positioning',
        '7': 'priorities'
    }
    
    choice = input("\n➤ Choisir une section: ").strip()
    
    if choice == '0':
        return
    
    if choice not in section_map:
        print("❌ Choix invalide")
        return
    
    section = section_map[choice]
    print(f"\n📝 Génération du rapport {section}...")
    cmd = f'venv/bin/python generate_modular_report.py "{demo_path}" "{player_name}" {section} output'
    os.system(cmd)


def show_help():
    """Display help and documentation"""
    print("\n" + "="*70)
    print("ℹ️  AIDE & DOCUMENTATION")
    print("="*70)
    
    print("\n📖 GUIDES DISPONIBLES:")
    print("  • README.md - Guide principal")
    print("  • HEATMAP_GUIDE.md - Guide des heatmaps")
    print("  • maps/README.md - Guide pour les images de maps")
    
    print("\n🎯 UTILISATION RAPIDE:")
    print("  1. Placez vos fichiers .dem dans le dossier 'demos/'")
    print("  2. Lancez: venv/bin/python analyzer.py")
    print("  3. Suivez le menu interactif")
    
    print("\n📊 TYPES D'ANALYSES:")
    print("  • Rapport complet: Vue d'ensemble + priorités + détails")
    print("  • Heatmap: Visualisation des zones de mort/kill")
    print("  • Positionnement: Vue tableau par zone")
    
    print("\n🗺️  HEATMAP AVEC IMAGE:")
    print("  1. Téléchargez une image radar de map")
    print("  2. Placez-la dans maps/ (ex: maps/de_dust2.png)")
    print("  3. Générez la heatmap normalement")
    
    print("\n🔧 CALIBRATION:")
    print("  Si la heatmap n'est pas alignée, utilisez l'option 5")
    print("  pour calibrer les coordonnées de la map.")
    
    print("\n💡 ASTUCE:")
    print("  Pour de meilleurs résultats, utilisez des demos récents")
    print("  et assurez-vous que le nom du joueur est exact!")
    
    print("\n" + "="*70)
    input("\n⏎ Appuyez sur Entrée pour continuer...")


def main():
    """Main interactive menu loop"""
    
    # Check if venv exists
    if not os.path.exists("venv"):
        print("❌ Environnement virtuel non trouvé!")
        print("💡 Exécutez: python3 -m venv venv && venv/bin/pip install -r requirements.txt")
        sys.exit(1)
    
    while True:
        try:
            print_header()
            print_menu()
            
            choice = input("\n➤ Votre choix: ").strip()
            
            if choice == '0':
                print("\n👋 Au revoir!")
                break
            
            elif choice == '8':
                show_help()
                continue
            
            elif choice in ['1', '2', '3', '4', '5', '6', '7']:
                # Select demo file
                demo_path = select_demo()
                if not demo_path:
                    input("\n⏎ Appuyez sur Entrée pour continuer...")
                    continue
                
                # Get player name
                player_name = get_player_name()
                if not player_name:
                    input("\n⏎ Appuyez sur Entrée pour continuer...")
                    continue
                
                # Execute selected action
                if choice == '1':
                    run_full_analysis(demo_path, player_name)
                elif choice == '2':
                    run_report_only(demo_path, player_name)
                elif choice == '3':
                    run_highlights(demo_path, player_name)
                elif choice == '4':
                    run_modular_report(demo_path, player_name)
                elif choice == '5':
                    run_heatmap_only(demo_path, player_name)
                elif choice == '6':
                    run_positioning_view(demo_path, player_name)
                elif choice == '7':
                    run_calibration(demo_path, player_name)
                
                input("\n⏎ Appuyez sur Entrée pour continuer...")
            
            else:
                print("\n❌ Choix invalide. Entrez un numéro de 0 à 8.")
                input("\n⏎ Appuyez sur Entrée pour continuer...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            input("\n⏎ Appuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
