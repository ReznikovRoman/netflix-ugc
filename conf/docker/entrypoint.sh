#!/bin/sh

gunicorn --worker-class aiohttp.GunicornWebWorker \
  --workers 2 \
  --bind 0.0.0.0:$NUGC_SERVER_PORT \
  main:create_app

# Run the main container process
exec "$@"