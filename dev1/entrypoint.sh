#!/bin/bash
set -euo pipefail

install -m 700 -d /home/dev/.ssh
install -m 600 /run/secrets/ssh_key     /home/dev/.ssh/id_ed25519
install -m 644 /run/secrets/ssh_key_pub /home/dev/.ssh/id_ed25519.pub

eval "$(ssh-agent -s)"
ssh-add /home/dev/.ssh/id_ed25519

echo "ssh-agent ready, key loaded:"
ssh-add -l

exec python3 /home/dev/keepalive.py






