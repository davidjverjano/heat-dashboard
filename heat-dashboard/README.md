# Courtside Cre8ives — Miami Heat Analytics Dashboard

A polished, branded Streamlit dashboard for Miami Heat analytics covering the 2024-25 NBA season.

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

## Pages

| Page | Description |
|------|-------------|
| **Overview** | KPIs (record, win%, net rating), win/loss timeline, upcoming schedule |
| **Last Game** | Box score, advanced stats, top performer, four factors comparison |
| **Weekly Trends** | Rolling ratings, date range selector, four factors sparklines |
| **Season View** | Team vs league/conference comparison, radar chart, category rankings, splits |
| **Players** | Roster stats table, usage vs efficiency scatter, player deep dives |
| **Narratives** | Auto-generated text insights on form, players, trends, schedule |

## Data Schema

All data is stored in the `data/` folder as CSV and JSON files:

| File | Description |
|------|-------------|
| `team_info.json` | Team metadata (name, arena, coach, season) |
| `team_game_log.csv` | Game-by-game team stats with four factors |
| `player_game_log.csv` | Per-game player stats |
| `player_season_stats.csv` | Aggregated season averages per player |
| `schedule.csv` | Upcoming/remaining games |
| `league_averages.json` | League and Eastern Conference averages |

## Adding New Pages

1. Create a new file in `pages/` following the naming convention: `N_PageName.py`
2. Import shared components from `components/` and data loaders from `utils/`
3. Streamlit auto-discovers pages from the `pages/` directory

## Adding New Components

- **Charts**: Add Plotly chart functions to `components/charts.py`
- **Metrics**: Add KPI/card components to `components/metrics.py`
- **Tables**: Add styled table displays to `components/tables.py`
- **Theme**: Colors and Plotly defaults live in `components/theme.py`

## Data Refresh

The data files are designed to be drop-in replaceable. See `scripts/refresh_data.py` for the stub refresh script.

To enable automated data refresh:
1. Install `nba_api`: `pip install nba_api`
2. Fill in the stub functions in `scripts/refresh_data.py` with actual API calls
3. Run on a schedule (e.g., cron job): `python scripts/refresh_data.py`

The dashboard reads fresh data on each page load (Streamlit caching with 5-minute TTL).

### Data Sources

- [nba_api](https://github.com/swar/nba_api) — Python package for NBA.com API
- [Basketball-Reference](https://www.basketball-reference.com) — Comprehensive stats
- [Databallr](https://databallr.com) — Advanced analytics
- [ESPN](https://www.espn.com/nba/) — Schedules and scores

## Brand Kit

- **Colors**: Asphalt Black, Off White, Rich Red, Dark Red, Yellow Flame, Warm Coral, Mamey, Warm Grey
- **Font**: Hyperspace Race Capsule (loaded via CSS @font-face)
- **Logos**: Courtside Cre8ives icon and wordmark in `assets/`

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- NumPy
