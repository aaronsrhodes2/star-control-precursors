#!/bin/bash
# Supervisor: keeps the SCZ audio-server alive even if MusicGen crashes
# the Python process (we've seen silent OOM-style deaths after long
# generation streaks). On crash, sleep briefly + relaunch. Logs each
# (re)start with a timestamp so we can correlate with regen failures.
#
# Usage:
#   SCZ_AUDIO_MODEL=musicgen-stereo-medium \
#     bash audio-server/run_supervised.sh

cd "$(dirname "$0")"
LOG=mg_supervisor.log
SERVER_LOG=mg_start.log

while true; do
  echo "[$(date -Iseconds)] supervisor: starting server (SCZ_AUDIO_MODEL=${SCZ_AUDIO_MODEL:-default})" \
    | tee -a "$LOG"
  # Append to server log so we keep the model-load history visible.
  .venv/Scripts/python.exe app.py >> "$SERVER_LOG" 2>&1
  code=$?
  echo "[$(date -Iseconds)] supervisor: server exited code=$code, restarting in 5s" \
    | tee -a "$LOG"
  sleep 5
done
