#!/bin/bash
set -e

eval "$(ssh-agent -s)"
ssh-add /home/dev1/.ssh/id_ed25519

cat > /home/dev1/agent.env <<EOF
export SSH_AUTH_SOCK=$SSH_AUTH_SOCK
export SSH_AGENT_PID=$SSH_AGENT_PID
EOF
chmod 600 /home/dev1/agent.env

echo "ssh-agent ready, key loaded:"
ssh-add -l

exec python3 /home/dev1/keepalive.py
