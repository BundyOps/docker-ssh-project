#!/bin/bash
set -e

eval "$(ssh-agent -s)"
ssh-add /home/dev/.ssh/id_ed25519

cat > /home/dev/agent.env <<EOF
export SSH_AUTH_SOCK=$SSH_AUTH_SOCK
export SSH_AGENT_PID=$SSH_AGENT_PID
EOF
chmod 600 /home/dev/agent.env

echo "ssh-agent ready, key loaded:"
ssh-add -l

exec python3 /home/dev/keepalive.py
