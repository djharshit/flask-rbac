#!/bin/sh

doppler run --command='gunicorn --log-level info --access-logfile - -w 2 -b 0.0.0.0:$PORT server:app'