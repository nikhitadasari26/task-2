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

# Ensure PYTHONPATH contains /app
PYTHONPATH="${PYTHONPATH:-}"
export PYTHONPATH="/app${PYTHONPATH:+:}${PYTHONPATH}"

# Force start uvicorn pointing to app.main:app (explicit module)
if python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('uvicorn') else 1)"; then
  echo "Starting uvicorn app.main:app"
  exec python -u -m uvicorn app.main:app --host 0.0.0.0 --port 8080
fi

# fallback to module-style (if uvicorn missing)
if python -c "import importlib,sys; importlib.util.find_spec('app.main')" >/dev/null 2>&1; then
  echo "uvicorn missing — starting python module: app.main"
  exec python -u -m app.main
fi

# fallback file candidates
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
