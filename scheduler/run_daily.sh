#!/bin/bash
# Daily cron job for Blooming Essie BI pipeline.
# Add to crontab with: crontab -e
# Example (runs every day at 6:00 AM):
#   0 6 * * * /bin/bash /Users/juancruzcibran/Desktop/Blooming\ Essie/scheduler/run_daily.sh

PROJECT_DIR="/Users/juancruzcibran/Desktop/Blooming Essie"
LOG_FILE="$PROJECT_DIR/logs/pipeline.log"

mkdir -p "$PROJECT_DIR/logs"

echo "--- $(date '+%Y-%m-%d %H:%M:%S') Starting pipeline ---" >> "$LOG_FILE"

cd "$PROJECT_DIR" && python3 main.py >> "$LOG_FILE" 2>&1

echo "--- $(date '+%Y-%m-%d %H:%M:%S') Pipeline finished ---" >> "$LOG_FILE"
