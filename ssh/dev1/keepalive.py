#!/usr/bin/env python3
"""
Keep an SSH session to the jump host alive, authenticating via
the running ssh-agent (SSH_AUTH_SOCK), with agent forwarding enabled.

Reconnects forever with exponential backoff.
"""

import os
import socket
import time
import sys
import paramiko
from paramiko.agent import AgentRequestHandler

HOST = "jump"
PORT = 22
USER = "dev1"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def enable_agent_forwarding(client):
    """
    Enable agent forwarding on an existing SSHClient connection.
    This works by opening a session channel and attaching an
    AgentRequestHandler to it. The handler sets up the forwarding
    locally and on the remote side.
    """
    transport = client.get_transport()
    # Open a regular session channel
    session = transport.open_session()
    # Attach the agent request handler to the session
    # This creates the forwarded agent socket on the remote host
    AgentRequestHandler(session)
    # Store the session so it isn't garbage collected
    client._agent_forwarding_session = session

def connect_once():
    """Open one SSH session using the agent, with forwarding enabled."""
    if not os.environ.get("SSH_AUTH_SOCK"):
        raise RuntimeError("SSH_AUTH_SOCK is not set — start ssh-agent and ssh-add first")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Authenticate via the agent. allow_agent=True makes paramiko
    # talk to SSH_AUTH_SOCK, exactly like the ssh(1) client does.
    # We disable any file-based fallbacks so it's agent-only.
    client.connect(
        hostname=HOST,
        port=PORT,
        username=USER,
        allow_agent=True,
        look_for_keys=False,
        password=None,
        timeout=10,
    )

    # Now enable agent forwarding on the live connection.
    enable_agent_forwarding(client)

    return client

def run_session(client):
    """Do something useful while connected. Replace with your real work."""
    transport = client.get_transport()
    log(f"connected to {USER}@{HOST} (transport active={transport.is_active()})")
    # Show that the agent is available on the remote side
    stdin, stdout, stderr = client.exec_command(
        "echo SSH_AUTH_SOCK=$SSH_AUTH_SOCK; ssh-add -l"
    )
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    log("remote output:")
    print(out)
    if err:
        print(err)

    # Stay connected: poll the transport and reconnect when it dies
    while transport.is_active():
        transport = client.get_transport()
        log(f"in while: connected to {USER}@{HOST} (transport active={transport.is_active()})")

        # Show that the agent is available on the remote side
        stdin, stdout, stderr = client.exec_command(
            "echo SSH_AUTH_SOCK=$SSH_AUTH_SOCK; ssh-add -l"
        )
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        log("remote output:")
        print(out)
        if err:
            print(err)
        
        cmd = (
            "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
            "dev@internal 'hostname; whoami'"
        )

        _, out, err = client.exec_command(cmd)
        stdout = out.read().decode()
        stderr = err.read().decode()
        rc = out.channel.recv_exit_status()

        log(f"inner ssh rc={rc}")
        log("--- stdout ---")
        print(stdout, flush=True)
        if stderr.strip():
            log("--- stderr ---")
            print(stderr, flush=True)
        
        time.sleep(2)

    log("transport closed — will reconnect")

def main():
    backoff = 1
    client = None
    while True:
        try:
            client = connect_once()
            backoff = 1
            run_session(client)
        except (paramiko.SSHException, socket.error, RuntimeError) as e:
            log(f"connection failed: {e} — retrying in {backoff}s")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)
        except KeyboardInterrupt:
            log("interrupted, exiting")
            sys.exit(0)
        finally:
            if client is not None:
                try:
                    # Clean up the session used for forwarding
                    if hasattr(client, '_agent_forwarding_session'):
                        client._agent_forwarding_session.close()
                    client.close()
                except Exception:
                    pass
                client = None

if __name__ == "__main__":
    main()
