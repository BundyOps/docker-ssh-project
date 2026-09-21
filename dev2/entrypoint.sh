#!/bin/bash
set -euo pipefail

cd /home/dev2

# Install the key from the Compose secret
install -m 700 -d /home/dev2/.ssh
install -m 600 /run/secrets/ssh_key_dev2     /home/dev2/.ssh/id_dev2
install -m 644 /run/secrets/ssh_key_dev2_pub /home/dev2/.ssh/id_dev2.pub

source /home/dev2/.venv/bin/activate

exec python3 /home/dev2/keepalive.py
