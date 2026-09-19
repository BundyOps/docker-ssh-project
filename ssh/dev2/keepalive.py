#!/usr/bin/env python3
"""
Step 3: Persistent SSH local port-forward with passwordless auth.

Equivalent to:
    ssh -N -L 8080:stage-api:3000 dev2@jump
but auto-reconnects forever.
"""

import logging
import signal
import sys
import time
from pathlib import Path

from paramiko.ssh_exception import (
    AuthenticationException,
    NoValidConnectionsError,
    SSHException,
)
from socket import error as SocketError
from sshtunnel import SSHTunnelForwarder
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    wait_exponential,
)

# ---------- configuration ----------
SSH_HOST = "jump"
SSH_PORT = 22
SSH_USER = "dev2"
SSH_KEY  = Path.home() / ".ssh" / "id_dev2"

LOCAL_BIND    = ("127.0.0.1", 8080)      # what we expose locally
REMOTE_TARGET = ("internal", 80)      # host:port as seen FROM the jump server
# -----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("tunnel")

TRANSIENT_ERRORS = (
    NoValidConnectionsError,
    SocketError,
    SSHException,
    TimeoutError,
    ConnectionError,
    OSError,
)

_shutdown = False


def _handle_signal(signum, _frame):
    global _shutdown
    log.info("Received signal %s, shutting down...", signum)
    _shutdown = True


class Disconnected(Exception):
    """Raised when the tunnel drops mid-session. Retryable."""


# ---------------------------------------------------------------------------
# The long-running operation tenacity retries
# ---------------------------------------------------------------------------
def run_tunnel() -> None:
    if _shutdown:
        raise KeyboardInterrupt

    server = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_pkey=str(SSH_KEY),
        allow_agent=False,
        local_bind_address=LOCAL_BIND,
        remote_bind_address=REMOTE_TARGET,
        set_keepalive=15,
    )

    log.info(
        "Opening tunnel %s:%d -> %s:%d via %s@%s ...",
        LOCAL_BIND[0], LOCAL_BIND[1],
        REMOTE_TARGET[0], REMOTE_TARGET[1],
        SSH_USER, SSH_HOST,
    )
    server.start()
    log.info("Tunnel UP. Local port %d is forwarded.", LOCAL_BIND[1])

    try:
        while not _shutdown:
            if not server.is_active:
                raise Disconnected("tunnel dropped")
            time.sleep(1)
        raise KeyboardInterrupt
    finally:
        try:
            server.stop()
        except Exception:
            pass
        log.info("Tunnel closed.")


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------
@retry(
    retry=retry_if_exception_type(TRANSIENT_ERRORS + (Disconnected,)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before_sleep=before_sleep_log(log, logging.WARNING),
    reraise=True,
)
def run_tunnel_with_retry() -> None:
    run_tunnel()


def main() -> int:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if not SSH_KEY.exists():
        log.error("Private key not found: %s", SSH_KEY)
        return 1

    try:
        run_tunnel_with_retry()
    except AuthenticationException as e:
        log.error("Authentication failed (fatal): %s", e)
        return 2
    except RetryError as e:
        log.error("Gave up: %s", e)
        return 3
    except KeyboardInterrupt:
        log.info("Interrupted. Goodbye.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
