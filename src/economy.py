"""
CS2 Economy Analyzer - Economic impact analysis
"""
from typing import Dict, List, Any, Tuple


# CS2 weapon and equipment prices (2024)
WEAPON_PRICES = {
    # Pistols
    'usp_silencer': 0,
    'glock': 0,
    'hkp2000': 0,
    'p250': 300,
    'fiveseven': 500,
    'tec9': 500,
    'cz75a': 500,
    'deagle': 700,
    'elite': 300,
    'revolver': 600,
    
    # SMGs
    'mac10': 1050,
    'mp9': 1250,
    'mp7': 1500,
    'ump45': 1200,
    'p90': 2350,
    'bizon': 1400,
    'mp5sd': 1500,
    
    # Rifles
    'famas': 2050,
    'galilar': 1800,
    'm4a1': 2900,
    'm4a1_silencer': 2900,
    'ak47': 2700,
    'aug': 3300,
    'sg556': 3000,
    
    # Snipers
    'ssg08': 1700,
    'awp': 4750,
    'scar20': 5000,
    'g3sg1': 5000,
    
    # Heavy
    'nova': 1050,
    'xm1014': 2000,
    'mag7': 1300,
    'sawedoff': 1100,
    'negev': 1700,
    'm249': 5200,
    
    # Default/Unknown
    'knife': 0,
    'unknown': 0,
    'world': 0,
    'inferno': 0,
    'hegrenade': 0,
    'flashbang': 0,
    'smokegrenade': 0,
    'molotov': 0,
    'incgrenade': 0,
}

ARMOR_PRICE = 650
HELMET_PRICE = 350  # Additional cost with armor
KIT_PRICE = 400


class EconomyAnalyzer:
    """Analyze economic impact of player decisions"""
    
    def __init__(self, deaths: List[Dict[str, Any]], kills: List[Dict[str, Any]]):
        self.deaths = deaths
        self.kills = kills
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run comprehensive economic analysis
        
        Returns:
            Dictionary with economic metrics and insights
        """
        # Analyze deaths
        death_value_analysis = self._analyze_death_value()
        eco_discipline = self._analyze_eco_discipline()
        
        # Analyze kills
        kill_roi = self._analyze_kill_roi()
        
        # Round type breakdown
        round_type_stats = self._analyze_round_types()
        
        # Calculate totals
        total_value_lost = sum(d['total_value'] for d in death_value_analysis)
        avg_death_cost = total_value_lost / len(self.deaths) if self.deaths else 0
        
        # Expensive deaths (>3000$)
        expensive_deaths = [d for d in death_value_analysis if d['total_value'] > 3000]
        expensive_death_count = len(expensive_deaths)
        expensive_death_pct = (expensive_death_count / len(self.deaths) * 100) if self.deaths else 0
        
        return {
            'summary': {
                'total_value_lost': int(total_value_lost),
                'avg_death_cost': int(avg_death_cost),
                'expensive_deaths': expensive_death_count,
                'expensive_death_pct': round(expensive_death_pct, 1),
                'total_value_gained': sum(k['value'] for k in kill_roi),
                'net_economy': sum(k['value'] for k in kill_roi) - total_value_lost
            },
            'death_values': death_value_analysis,
            'eco_discipline': eco_discipline,
            'kill_roi': kill_roi,
            'round_types': round_type_stats
        }
    
    def _analyze_death_value(self) -> List[Dict[str, Any]]:
        """
        Calculate value lost at each death using REAL inventory data
        
        Returns:
            List of deaths with economic impact
        """
        results = []
        
        for death in self.deaths:
            weapon = death.get('weapon', 'unknown')
            
            # Prefer game's calculated equipment value (most accurate)
            equip_value_game = death.get('equip_value', 0)
            
            if equip_value_game > 0:
                # Use game's calculation (includes all weapons, nades, etc.)
                total_value = equip_value_game
                
                # Break down components for reporting (approximate)
                weapon_value = WEAPON_PRICES.get(weapon, 0)
                armor_actual = death.get('armor_value', 0)
                has_helmet = death.get('has_helmet', False)
                has_kit = death.get('has_defuser', False)
                
                if armor_actual > 0:
                    armor_value = ARMOR_PRICE
                    helmet_value = HELMET_PRICE if has_helmet else 0
                else:
                    armor_value = 0
                    helmet_value = 0
                
                kit_value = KIT_PRICE if has_kit else 0
            else:
                # Fallback: calculate from individual components
                weapon_value = WEAPON_PRICES.get(weapon, 0)
                armor_actual = death.get('armor_value', 0)
                has_helmet = death.get('has_helmet', False)
                has_kit = death.get('has_defuser', False)
                
                if armor_actual > 0:
                    armor_value = ARMOR_PRICE
                    helmet_value = HELMET_PRICE if has_helmet else 0
                else:
                    armor_value = 0
                    helmet_value = 0
                
                kit_value = KIT_PRICE if has_kit else 0
                total_value = weapon_value + armor_value + helmet_value + kit_value
            
            # Categorize buy type
            buy_type = self._categorize_buy_type(total_value)
            
            results.append({
                'tick': death['tick'],
                'weapon': weapon,
                'weapon_value': weapon_value,
                'armor_value': armor_value,
                'helmet_value': helmet_value,
                'kit_value': kit_value,
                'total_value': total_value,
                'buy_type': buy_type,
                'attacker': death.get('attacker', 'Unknown'),
                'armor_actual': armor_actual,
                'had_helmet': has_helmet,
                'had_defuser': has_kit
            })
        
        return results
    
    def _analyze_eco_discipline(self) -> Dict[str, Any]:
        """
        Analyze eco discipline - expensive deaths that were avoidable
        
        Returns:
            Eco discipline stats
        """
        death_values = self._analyze_death_value()
        
        # High value deaths (>3500$)
        high_value_deaths = [d for d in death_values if d['total_value'] > 3500]
        
        # Deaths with rifles/awp
        rifle_deaths = [d for d in death_values if d['weapon_value'] >= 2700]
        awp_deaths = [d for d in death_values if d['weapon_value'] >= 4750]
        
        # SMG/pistol deaths (eco/force buy)
        eco_deaths = [d for d in death_values if d['total_value'] < 2000]
        force_buy_deaths = [d for d in death_values if 2000 <= d['total_value'] < 3500]
        
        total = len(self.deaths)
        
        return {
            'high_value_deaths': len(high_value_deaths),
            'high_value_death_pct': (len(high_value_deaths) / total * 100) if total > 0 else 0,
            'rifle_deaths': len(rifle_deaths),
            'awp_deaths': len(awp_deaths),
            'eco_deaths': len(eco_deaths),
            'force_buy_deaths': len(force_buy_deaths),
            'worst_losses': sorted(high_value_deaths, key=lambda x: x['total_value'], reverse=True)[:3]
        }
    
    def _analyze_kill_roi(self) -> List[Dict[str, Any]]:
        """
        Analyze return on investment for kills
        
        Returns:
            List of kills with estimated value gained
        """
        results = []
        
        for kill in self.kills:
            weapon_used = kill.get('weapon', 'unknown')
            weapon_value = WEAPON_PRICES.get(weapon_used, 0)
            
            # Kill reward in CS2 (simplified)
            kill_reward = self._get_kill_reward(weapon_used)
            
            # Estimate enemy equipment value
            # In reality, we'd need full demo parsing
            estimated_enemy_value = self._estimate_enemy_value(weapon_value)
            
            results.append({
                'tick': kill['tick'],
                'victim': kill.get('victim', 'Unknown'),
                'weapon': weapon_used,
                'kill_reward': kill_reward,
                'value': kill_reward,  # Simplified (doesn't include enemy weapon pickup)
                'headshot': kill.get('headshot', False)
            })
        
        return results
    
    def _analyze_round_types(self) -> Dict[str, Any]:
        """
        Break down performance by round type (full buy, force, eco)
        
        Returns:
            Stats by round type
        """
        death_values = self._analyze_death_value()
        
        # Group by buy type
        by_type = {
            'full_buy': [],
            'force_buy': [],
            'eco': [],
            'pistol': []
        }
        
        for dv in death_values:
            by_type[dv['buy_type']].append(dv)
        
        # Calculate stats for each type
        stats = {}
        for buy_type, deaths in by_type.items():
            if deaths:
                stats[buy_type] = {
                    'deaths': len(deaths),
                    'avg_value_lost': int(sum(d['total_value'] for d in deaths) / len(deaths)),
                    'total_value_lost': int(sum(d['total_value'] for d in deaths))
                }
            else:
                stats[buy_type] = {
                    'deaths': 0,
                    'avg_value_lost': 0,
                    'total_value_lost': 0
                }
        
        return stats
    
    # Removed _estimate_has_armor - now using real data from demo
    
    def _categorize_buy_type(self, total_value: int) -> str:
        """Categorize buy based on total equipment value"""
        if total_value < 1000:
            return 'pistol'
        elif total_value < 2000:
            return 'eco'
        elif total_value < 3500:
            return 'force_buy'
        else:
            return 'full_buy'
    
    def _get_kill_reward(self, weapon: str) -> int:
        """Get kill reward for weapon type"""
        # CS2 kill rewards
        rewards = {
            'knife': 1500,
            'awp': 100,
            'ssg08': 300,
        }
        
        # SMG bonus
        if weapon in ['mac10', 'mp9', 'mp7', 'ump45', 'p90', 'bizon', 'mp5sd']:
            return 600
        
        # Shotgun/Zeus
        if weapon in ['nova', 'xm1014', 'mag7', 'sawedoff', 'taser']:
            return 900
        
        return rewards.get(weapon, 300)  # Default rifle/pistol reward
    
    def _estimate_enemy_value(self, weapon_value: int) -> int:
        """
        Estimate enemy equipment value (simplified)
        
        In reality, would need full demo parsing
        """
        if weapon_value >= 4000:
            return 5000  # AWP + full armor
        elif weapon_value >= 2500:
            return 3500  # Rifle + armor
        elif weapon_value >= 1500:
            return 2000  # SMG + armor
        else:
            return 1000  # Pistol/eco
