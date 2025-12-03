#!/usr/bin/env bash
set -euo pipefail

mkdir -p /cron /data
chmod 755 /cron /data

CRON_FILE=/app/cron/2fa-cron
if [ -f "$CRON_FILE" ]; then
  if [ -w "$CRON_FILE" ]; then
    chmod 0644 "$CRON_FILE" || true
  else
    echo "Warning: cron file not writable; skipping chmod"
  fi
  crontab "$CRON_FILE" || echo "crontab install failed" >&2
fi

# start cron in background
if command -v service >/dev/null 2>&1; then
  service cron start || /etc/init.d/cron start || cron &
else
  cron &
fi

sleep 1

# Ensure PYTHONPATH is defined and includes /app
PYTHONPATH="${PYTHONPATH:-}"
export PYTHONPATH="/app${PYTHONPATH:+:}${PYTHONPATH}"

# Force start uvicorn (preferred). If uvicorn not installed, fall back.
if python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('uvicorn') else 1)"; then
  echo "Starting uvicorn app:app"
  exec python -u -m uvicorn app:app --host 0.0.0.0 --port 8080
fi

# If uvicorn missing, try module-style (app.main) which may start a server
if python -c "import importlib,sys; importlib.util.find_spec('app.main')" >/dev/null 2>&1; then
  echo "uvicorn missing — starting python module: app.main"
  exec python -u -m app.main
fi

# Fallback to file candidates
CANDIDATES=("/app.py" "/app/app.py" "/app/app/app.py" "/app/main.py" "/app/app/main.py")
for c in "${CANDIDATES[@]}"; do
  if [ -f "$c" ]; then
    echo "Fallback: starting Python file: $c"
    exec python -u "$c"
  fi
done

echo "ERROR: no entrypoint found. Contents of /app:"
ls -la /app || true
find /app -maxdepth 3 -type f -print -exec ls -l {} \; || true
exit 1
