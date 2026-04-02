#!/bin/bash
DASHBOARD_DIR="$HOME/eddy-agent/eddy-dashboard"

python3 "$DASHBOARD_DIR/scripts/generate-status.py"

cd "$DASHBOARD_DIR"
git add -A
git commit -m "status: $(date '+%Y-%m-%d %H:%M')" --allow-empty 2>/dev/null
git push origin main 2>/dev/null
