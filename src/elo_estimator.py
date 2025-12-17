"""
CS2 Elo/Rank Estimator - Estimate player skill level based on stats
"""
from typing import Dict, Any, List, Tuple
import statistics


# Benchmark data based on CS2 competitive ranks and Faceit levels
# Data compiled from community stats and pro player benchmarks
RANK_BENCHMARKS = {
    'Silver': {
        'elo_range': (0, 5000),
        'kd_ratio': 0.65,
        'headshot_rate': 20,
        'crosshair_offset': 55,
        'bad_crosshair_pct': 75,
        'avoidable_deaths_pct': 60,
        'flash_useful_pct': 25,
        'expensive_deaths_pct': 65,
        'consistency': 0.6,
        'label': '🥈 Silver (0-5000 Elo)'
    },
    'Gold Nova': {
        'elo_range': (5000, 8000),
        'kd_ratio': 0.85,
        'headshot_rate': 28,
        'crosshair_offset': 42,
        'bad_crosshair_pct': 62,
        'avoidable_deaths_pct': 50,
        'flash_useful_pct': 35,
        'expensive_deaths_pct': 55,
        'consistency': 0.5,
        'label': '🥇 Gold Nova (5000-8000 Elo)'
    },
    'Master Guardian': {
        'elo_range': (8000, 11000),
        'kd_ratio': 1.0,
        'headshot_rate': 35,
        'crosshair_offset': 32,
        'bad_crosshair_pct': 48,
        'avoidable_deaths_pct': 40,
        'flash_useful_pct': 45,
        'expensive_deaths_pct': 45,
        'consistency': 0.4,
        'label': '⚔️ Master Guardian (8000-11000 Elo)'
    },
    'Legendary Eagle': {
        'elo_range': (11000, 14000),
        'kd_ratio': 1.15,
        'headshot_rate': 42,
        'crosshair_offset': 25,
        'bad_crosshair_pct': 35,
        'avoidable_deaths_pct': 30,
        'flash_useful_pct': 55,
        'expensive_deaths_pct': 35,
        'consistency': 0.32,
        'label': '🦅 Legendary Eagle (11000-14000 Elo)'
    },
    'Supreme/Global': {
        'elo_range': (14000, 18000),
        'kd_ratio': 1.3,
        'headshot_rate': 48,
        'crosshair_offset': 20,
        'bad_crosshair_pct': 25,
        'avoidable_deaths_pct': 22,
        'flash_useful_pct': 65,
        'expensive_deaths_pct': 25,
        'consistency': 0.25,
        'label': '🌟 Supreme/Global (14000-18000 Elo)'
    },
    'Faceit 1-3': {
        'elo_range': (18000, 20000),
        'kd_ratio': 1.4,
        'headshot_rate': 52,
        'crosshair_offset': 18,
        'bad_crosshair_pct': 20,
        'avoidable_deaths_pct': 18,
        'flash_useful_pct': 70,
        'expensive_deaths_pct': 20,
        'consistency': 0.22,
        'label': '🔶 Faceit 1-3 (18000-20000 Elo)'
    },
    'Faceit 4-7': {
        'elo_range': (20000, 24000),
        'kd_ratio': 1.55,
        'headshot_rate': 56,
        'crosshair_offset': 15,
        'bad_crosshair_pct': 15,
        'avoidable_deaths_pct': 15,
        'flash_useful_pct': 75,
        'expensive_deaths_pct': 15,
        'consistency': 0.18,
        'label': '🔷 Faceit 4-7 (20000-24000 Elo)'
    },
    'Faceit 8-10': {
        'elo_range': (24000, 28000),
        'kd_ratio': 1.75,
        'headshot_rate': 62,
        'crosshair_offset': 12,
        'bad_crosshair_pct': 10,
        'avoidable_deaths_pct': 10,
        'flash_useful_pct': 82,
        'expensive_deaths_pct': 10,
        'consistency': 0.15,
        'label': '💎 Faceit 8-10 (24000-28000 Elo)'
    },
    'Semi-Pro': {
        'elo_range': (28000, 32000),
        'kd_ratio': 2.0,
        'headshot_rate': 68,
        'crosshair_offset': 10,
        'bad_crosshair_pct': 5,
        'avoidable_deaths_pct': 5,
        'flash_useful_pct': 88,
        'expensive_deaths_pct': 5,
        'consistency': 0.12,
        'label': '🏆 Semi-Pro (28000-32000 Elo)'
    },
    'Professional': {
        'elo_range': (32000, 40000),
        'kd_ratio': 2.3,
        'headshot_rate': 75,
        'crosshair_offset': 8,
        'bad_crosshair_pct': 3,
        'avoidable_deaths_pct': 3,
        'flash_useful_pct': 92,
        'expensive_deaths_pct': 3,
        'consistency': 0.10,
        'label': '👑 Professional (32000+ Elo)'
    }
}

# Metric weights for overall score
METRIC_WEIGHTS = {
    'kd_ratio': 0.25,
    'headshot_rate': 0.15,
    'crosshair_offset': 0.20,
    'avoidable_deaths_pct': 0.15,
    'flash_useful_pct': 0.10,
    'expensive_deaths_pct': 0.10,
    'consistency': 0.05
}


class EloEstimator:
    """Estimate player Elo/Rank based on performance metrics"""
    
    def __init__(self, analysis: Dict[str, Any]):
        self.analysis = analysis
        self.summary = analysis.get('summary', {})
    
    def estimate_rank(self) -> Dict[str, Any]:
        """
        Estimate player rank based on stats
        
        Returns:
            Dictionary with estimated rank, Elo, confidence, and breakdown
        """
        # Extract player stats
        player_stats = {
            'kd_ratio': self.summary.get('avg_kd_ratio' if 'avg_kd_ratio' in self.summary else 'kd_ratio', 0),
            'headshot_rate': self.summary.get('avg_headshot_rate' if 'avg_headshot_rate' in self.summary else 'headshot_rate', 0),
            'crosshair_offset': self.summary.get('avg_crosshair_offset', 0),
            'bad_crosshair_pct': self.summary.get('avg_bad_crosshair_pct' if 'avg_bad_crosshair_pct' in self.summary else 'bad_crosshair_pct', 0),
            'avoidable_deaths_pct': self.summary.get('avg_avoidable_deaths_pct' if 'avg_avoidable_deaths_pct' in self.summary else 'avoidable_deaths_pct', 0),
            'flash_useful_pct': self.summary.get('avg_flash_useful_pct' if 'avg_flash_useful_pct' in self.summary else 'flash_useful_pct', 0),
            'expensive_deaths_pct': self.summary.get('avg_expensive_deaths_pct' if 'avg_expensive_deaths_pct' in self.summary else 'expensive_deaths_pct', 0),
            'consistency': self.summary.get('std_kd_ratio', 0.5)  # Lower is better
        }
        
        # Calculate scores for each metric against each rank
        metric_scores = self._calculate_metric_scores(player_stats)
        
        # Calculate weighted overall score for each rank
        rank_scores = self._calculate_rank_scores(metric_scores)
        
        # Find best matching rank
        best_rank = max(rank_scores.items(), key=lambda x: x[1]['weighted_score'])
        estimated_rank = best_rank[0]
        
        # Estimate specific Elo within range
        estimated_elo = self._estimate_elo(estimated_rank, rank_scores[estimated_rank], player_stats)
        
        # Calculate confidence
        confidence = self._calculate_confidence(rank_scores, estimated_rank)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(metric_scores, estimated_rank)
        
        # Get adjacent ranks for context
        rank_list = list(RANK_BENCHMARKS.keys())
        rank_idx = rank_list.index(estimated_rank)
        
        next_rank = rank_list[rank_idx + 1] if rank_idx < len(rank_list) - 1 else None
        prev_rank = rank_list[rank_idx - 1] if rank_idx > 0 else None
        
        return {
            'estimated_rank': estimated_rank,
            'estimated_elo': estimated_elo,
            'elo_range': RANK_BENCHMARKS[estimated_rank]['elo_range'],
            'label': RANK_BENCHMARKS[estimated_rank]['label'],
            'confidence': confidence,
            'player_stats': player_stats,
            'rank_scores': rank_scores,
            'metric_breakdown': metric_scores[estimated_rank],
            'strengths': strengths,
            'weaknesses': weaknesses,
            'next_rank': next_rank,
            'prev_rank': prev_rank,
            'progression': self._calculate_progression(estimated_rank, next_rank, player_stats) if next_rank else None
        }
    
    def _calculate_metric_scores(self, player_stats: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Calculate how close player is to each rank's benchmarks"""
        scores = {}
        
        for rank, benchmarks in RANK_BENCHMARKS.items():
            scores[rank] = {}
            
            # K/D (higher is better)
            scores[rank]['kd_ratio'] = self._score_metric(
                player_stats['kd_ratio'],
                benchmarks['kd_ratio'],
                higher_is_better=True,
                tolerance=0.3
            )
            
            # HSR (higher is better)
            scores[rank]['headshot_rate'] = self._score_metric(
                player_stats['headshot_rate'],
                benchmarks['headshot_rate'],
                higher_is_better=True,
                tolerance=10
            )
            
            # Crosshair offset (lower is better)
            scores[rank]['crosshair_offset'] = self._score_metric(
                player_stats['crosshair_offset'],
                benchmarks['crosshair_offset'],
                higher_is_better=False,
                tolerance=10
            )
            
            # Bad crosshair % (lower is better)
            scores[rank]['bad_crosshair_pct'] = self._score_metric(
                player_stats['bad_crosshair_pct'],
                benchmarks['bad_crosshair_pct'],
                higher_is_better=False,
                tolerance=15
            )
            
            # Avoidable deaths (lower is better)
            scores[rank]['avoidable_deaths_pct'] = self._score_metric(
                player_stats['avoidable_deaths_pct'],
                benchmarks['avoidable_deaths_pct'],
                higher_is_better=False,
                tolerance=15
            )
            
            # Flash useful (higher is better)
            scores[rank]['flash_useful_pct'] = self._score_metric(
                player_stats['flash_useful_pct'],
                benchmarks['flash_useful_pct'],
                higher_is_better=True,
                tolerance=15
            )
            
            # Expensive deaths (lower is better)
            scores[rank]['expensive_deaths_pct'] = self._score_metric(
                player_stats['expensive_deaths_pct'],
                benchmarks['expensive_deaths_pct'],
                higher_is_better=False,
                tolerance=15
            )
            
            # Consistency (lower is better)
            scores[rank]['consistency'] = self._score_metric(
                player_stats['consistency'],
                benchmarks['consistency'],
                higher_is_better=False,
                tolerance=0.2
            )
        
        return scores
    
    def _score_metric(self, player_value: float, benchmark: float, 
                     higher_is_better: bool, tolerance: float) -> float:
        """
        Score a single metric (0-100)
        
        100 = exactly at benchmark
        >80 = within tolerance
        <50 = significantly off
        """
        if higher_is_better:
            diff = player_value - benchmark
        else:
            diff = benchmark - player_value
        
        # Perfect match
        if abs(player_value - benchmark) < tolerance * 0.1:
            return 100
        
        # Within tolerance
        if diff >= 0:
            score = min(100, 80 + (diff / tolerance) * 20)
        else:
            # Below benchmark
            score = max(0, 80 + (diff / tolerance) * 80)
        
        return round(score, 1)
    
    def _calculate_rank_scores(self, metric_scores: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """Calculate weighted overall score for each rank"""
        rank_scores = {}
        
        for rank, scores in metric_scores.items():
            weighted_score = sum(
                scores[metric] * METRIC_WEIGHTS[metric]
                for metric in METRIC_WEIGHTS.keys()
            )
            
            rank_scores[rank] = {
                'weighted_score': round(weighted_score, 1),
                'metric_scores': scores
            }
        
        return rank_scores
    
    def _estimate_elo(self, rank: str, rank_score: Dict[str, Any], 
                     player_stats: Dict[str, float]) -> int:
        """Estimate specific Elo within rank range"""
        elo_min, elo_max = RANK_BENCHMARKS[rank]['elo_range']
        
        # Use weighted score to position within range
        score = rank_score['weighted_score']
        
        # Score 80-100 = within this rank
        # Position based on how close to 100
        if score >= 80:
            position = (score - 80) / 20  # 0 to 1
        else:
            position = 0.3  # Below expectations, lower in range
        
        estimated_elo = int(elo_min + (elo_max - elo_min) * position)
        
        return estimated_elo
    
    def _calculate_confidence(self, rank_scores: Dict[str, Dict[str, Any]], 
                             estimated_rank: str) -> str:
        """Calculate confidence in estimation"""
        best_score = rank_scores[estimated_rank]['weighted_score']
        
        # Get scores of adjacent ranks
        rank_list = list(RANK_BENCHMARKS.keys())
        rank_idx = rank_list.index(estimated_rank)
        
        adjacent_scores = []
        if rank_idx > 0:
            adjacent_scores.append(rank_scores[rank_list[rank_idx - 1]]['weighted_score'])
        if rank_idx < len(rank_list) - 1:
            adjacent_scores.append(rank_scores[rank_list[rank_idx + 1]]['weighted_score'])
        
        if not adjacent_scores:
            return 'High'
        
        # Confidence based on score difference
        avg_adjacent = statistics.mean(adjacent_scores)
        diff = best_score - avg_adjacent
        
        if diff > 15:
            return 'High'
        elif diff > 8:
            return 'Medium'
        else:
            return 'Low'
    
    def _identify_strengths_weaknesses(self, metric_scores: Dict[str, Dict[str, float]], 
                                      rank: str) -> Tuple[List[str], List[str]]:
        """Identify strongest and weakest metrics"""
        scores = metric_scores[rank]
        
        sorted_metrics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [m[0] for m in sorted_metrics[:3] if m[1] >= 75]
        weaknesses = [m[0] for m in sorted_metrics[-3:] if m[1] < 60]
        
        # Translate to readable names
        metric_names = {
            'kd_ratio': 'K/D Ratio',
            'headshot_rate': 'Headshot Rate',
            'crosshair_offset': 'Crosshair Placement',
            'bad_crosshair_pct': 'Pre-Aim Quality',
            'avoidable_deaths_pct': 'Decision Making',
            'flash_useful_pct': 'Utility Usage',
            'expensive_deaths_pct': 'Economy Discipline',
            'consistency': 'Consistency'
        }
        
        strengths = [metric_names.get(m, m) for m in strengths]
        weaknesses = [metric_names.get(m, m) for m in weaknesses]
        
        return strengths, weaknesses
    
    def _calculate_progression(self, current_rank: str, next_rank: str, 
                              player_stats: Dict[str, float]) -> Dict[str, Any]:
        """Calculate what's needed to reach next rank"""
        if not next_rank:
            return None
        
        current_bench = RANK_BENCHMARKS[current_rank]
        next_bench = RANK_BENCHMARKS[next_rank]
        
        gaps = {}
        
        for metric in METRIC_WEIGHTS.keys():
            player_val = player_stats[metric]
            next_val = next_bench[metric]
            
            # Determine if higher or lower is better
            higher_is_better = metric in ['kd_ratio', 'headshot_rate', 'flash_useful_pct']
            
            if higher_is_better:
                gap = next_val - player_val
                status = 'need_improvement' if gap > 0 else 'already_there'
            else:
                gap = player_val - next_val
                status = 'need_improvement' if gap > 0 else 'already_there'
            
            gaps[metric] = {
                'current': round(player_val, 1),
                'target': round(next_val, 1),
                'gap': round(abs(gap), 1),
                'status': status
            }
        
        return {
            'next_rank': next_rank,
            'next_label': next_bench['label'],
            'gaps': gaps
        }
