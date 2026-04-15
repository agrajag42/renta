#!/bin/sh
set -e

# Start FastAPI feedback API in background
python3 -m uvicorn feedback_api:app --host 127.0.0.1 --port 8081 --log-level warning &

# Start nginx in foreground (primary process)
sed -i "s/LISTEN_PORT/$PORT/g" /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'
