# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

CS2 Gap Analyzer is a Python tool that analyzes Counter-Strike 2 demo files (.dem) to identify gameplay improvement areas. It parses game events using demoparser2, analyzes player decisions, and generates actionable feedback reports.

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running the analyzer
```bash
# Basic usage
python main.py demos/match.dem "PlayerName"

# With output saving
python main.py demos/match.dem "PlayerName" --save

# Custom output directory
python main.py demos/match.dem "PlayerName" --save --output-dir custom/path
```

### Testing
Currently no test framework is configured. The `tests/` directory exists but is empty.

## Architecture

### Data Flow Pipeline
The application follows a linear 5-step pipeline with advanced geometric analysis:

```
.dem file → Parser → Events → Analyzer (+ Geometry) → Report
```

1. **Parser** (`src/parser.py`): Extracts raw events from CS2 demo files using demoparser2
2. **Events**: Structured JSON containing deaths, kills, flashes with positions AND angles (pitch/yaw)
3. **Geometry** (`src/geometry.py`): Advanced calculations (FOV, crosshair offset, line of sight)
4. **GameState** (`src/game_state.py`): Track game state across ticks (visible enemies, smokes, HP)
5. **Analyzer** (`src/analyzer.py`): Applies precise gameplay analysis with real metrics
6. **Report** (`src/report.py`): Formats detailed, actionable analysis with priorities
7. **Output**: Console display and optional file saves (JSON + text)

### Core Modules

#### `src/parser.py` - DemoParser
Wraps demoparser2 to extract events with full geometric data:
- **Deaths**: Position, angles (pitch/yaw), attacker position, nearby teammates, tick
- **Kills**: Position, angles, victim position, weapon, headshot flag
- **Flashes**: Thrower, blind duration, effectiveness, pop-flash detection (movement tracking)

Key logic:
- Uses `parse_event("player_death")` and `parse_event("player_blind")` from demoparser2
- Parses tick data with `parse_ticks()` to get positions (X, Y, Z) AND angles (pitch, yaw)
- Calculates teammate proximity using 800-unit radius (trade distance)
- Converts CS2 tick rates (64 ticks/sec) to time windows
- Pop-flash detection: tracks player movement >100 units within 1s after flash

#### `src/geometry.py` - Geometric Calculations
Advanced math for precise analysis:
- **Vector3 class**: 3D vector operations (magnitude, normalize, dot product)
- **angles_to_direction()**: Convert pitch/yaw to direction vector
- **is_in_fov()**: Check if target in player's field of view (default 90°)
- **calculate_crosshair_offset_angle()**: Measure degrees between crosshair and target
- **line_of_sight_clear()**: Check if smoke blocks vision (sphere intersection)
- **calculate_distance()**: 3D Euclidean distance
- **get_map_zone()**: Map position to zone name (hardcoded for dust2, mirage, inferno)

#### `src/game_state.py` - Game State Tracking
Tracks complete game state across all ticks:
- **GameState class**: Query visibility, smokes, HP at any tick
- **get_visible_enemies()**: Returns enemies in FOV with clear LOS (no smoke blocking)
- **get_teammates_with_los()**: Find teammates who can trade (LOS to target position)
- **get_player_hp()**: HP tracking with caching
- **Smoke tracking**: 18-second duration (1152 ticks), sphere-based LOS blocking

#### `src/analyzer.py` - GapAnalyzer
Advanced analysis with precise metrics and crosshair placement:

**Crosshair Placement Analysis** (NEW - MOST IMPORTANT):
- Measures angle between crosshair direction and enemy position at moment of death/kill
- Categorizes: Good (<30°), Bad (30-60°), Terrible (>60°)
- Calculates average offset across all duels
- Returns detailed stats: % bad placement, worst examples, avg offset

**Deaths Analysis** (IMPROVED):
- Avoidable death if risk factors present AND no advantage:
  - Risk factors: no teammate, no utility used
  - Advantages: flash active, teammates nearby, close range (<500 units)
- Tracks: is_avoidable, had_any_advantage, risk_factors breakdown

**Kills Analysis** (NEW):
- Analyzes crosshair placement on successful kills
- Measures offset angle at moment of kill
- Good placement indicator: offset <30°

**Flash Effectiveness** (IMPROVED):
- Useful if: hit enemy (>1s blind) OR followed by kill
- Pop-flash detection: player moved >100 units within 1s (peeked after throw)
- Tracks: is_useful, is_pop_flash, hit_someone, followed_by_kill

**Priority Generation** (REVAMPED):
- Evaluates 6 metrics: crosshair placement, avoidable deaths, no-advantage duels, flash utility, pop-flash rate, HSR
- Ranks by severity (percentage)
- Returns top 3 priorities with category, stats, recommendation, severity score
- Detailed format: emoji category + % stats + actionable recommendation

#### `src/report.py` - ReportGenerator
Generates detailed, actionable reports with multiple sections:

**Report Structure**:
1. **Overview**: K/D, HSR, crosshair %, avoidable deaths %, no-advantage duels %, flash utility %
2. **Priorities**: Top 3 ranked by severity with emoji category + stats + recommendation
3. **Crosshair Details**: Avg offset, bad placement count, worst examples (>60° flicks)
4. **Deaths Details**: Avoidable count, no-advantage count, risk factors breakdown
5. **Utility Details**: Total flashes, useful %, pop-flash %, effectiveness breakdown

Format is console-friendly with emojis, clear sections, and actionable next steps.

### Important Constants
- **Geometry**: `FOV = 90°`, smoke radius = 250 units, close range = 500 units
- **Crosshair**: Bad threshold = 30°, Terrible threshold = 60°
- **Timing**: 3s = 192 ticks, 5s = 320 ticks, 1s = 64 ticks (at 64 tick/sec)
- **Distances**: Trade distance = 800 units, close range = 500 units
- **Flash**: Effective blind = >1.0s, pop-flash = peek within 1s (>100 units moved)
- **Smoke**: Duration = 18s (1152 ticks)

### Player Name Handling
Player names are **case-sensitive** and must match exactly as they appear in-game. The parser filters events by exact string match on `user_name` and `attacker_name` fields from demoparser2.

### Output Structure
When using `--save`:
- `{demo_name}_events.json` - Raw parsed events
- `{demo_name}_report.txt` - Formatted text report
- Both saved to `output/` directory (configurable with `--output-dir`)

## Key Limitations
### What's Implemented
✅ Crosshair placement analysis (precise angle measurement)
✅ Pop-flash detection (movement tracking)
✅ Geometric calculations (FOV, LOS, crosshair offset)
✅ Smoke LOS blocking (sphere intersection)
✅ Map zones (hardcoded for dust2, mirage, inferno)

### Known Limitations
⚠️ Map zones are approximate (not BSP-parsed)
⚠️ LOS smoke blocking is simplified (sphere check only)
⚠️ No wall collision detection (assumes open space)
⚠️ Single-player analysis only
⚠️ Pop-flash detection uses movement heuristic (>100 units in 1s)
⚠️ Visible enemies require GameState integration (not yet used in analyzer)
