#!/bin/bash
set -e

cd /home/dev2

# Activate the venv
source /home/dev2/.venv/bin/activate

# Run the keepalive script in the foreground
exec python3 /home/dev2/keepalive.py
