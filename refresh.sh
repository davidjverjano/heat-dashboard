#!/bin/bash
# ────────────────────────────────────────────────────────────────
# Courtside Cre8ives — One-Command Data Refresh
# ────────────────────────────────────────────────────────────────
# Run this from your Mac whenever you want fresh data:
#   ./refresh.sh
#
# What it does:
#   1. Clones the repo (or pulls latest)
#   2. Installs dependencies
#   3. Runs the NBA API refresh (works from your residential IP)
#   4. Commits and pushes updated data files
#   5. Streamlit Cloud auto-redeploys with new data
# ────────────────────────────────────────────────────────────────

set -e

REPO="https://github.com/davidjverjano/heat-dashboard.git"
DIR="$HOME/heat-dashboard"

echo "🏀 Courtside Cre8ives — Data Refresh"
echo "======================================"
echo ""

# Clone or pull
if [ -d "$DIR" ]; then
    echo "📂 Pulling latest from GitHub..."
    cd "$DIR"
    git pull --ff-only
else
    echo "📂 Cloning repository..."
    git clone "$REPO" "$DIR"
    cd "$DIR"
fi

# Set up Python venv if needed
if [ ! -d "$DIR/.venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install --quiet nba_api pandas

echo ""
echo "🔄 Fetching live data from NBA API..."
echo "   (this takes 2-3 minutes)"
echo ""
python scripts/refresh_data.py

echo ""
echo "📤 Pushing updated data to GitHub..."
git add data/
if git diff --cached --quiet; then
    echo "   No data changes — everything is already up to date."
else
    git commit -m "data: manual refresh $(date +%Y-%m-%d_%H:%M)"
    git push
    echo ""
    echo "✅ Done! Data pushed to GitHub."
    echo "   Streamlit Cloud will auto-redeploy in ~1-2 minutes."
    echo "   🔗 https://heat-dashboard-bsmwpqiiehyxmw9u99bkel.streamlit.app/"
fi

echo ""
echo "🏀 All set!"
