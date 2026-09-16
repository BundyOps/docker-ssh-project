#!/usr/bin/env python3
"""
Step 2.5: Passwordless SSH that stays connected.
- Retries on initial connect failure.
- Detects mid-session disconnection and reconnects.
- Runs until Ctrl-C / SIGTERM.
"""

import logging
import signal
import sys
import time
from pathlib import Path

import paramiko
from paramiko.ssh_exception import (
    AuthenticationException,
    NoValidConnectionsError,
    SSHException,
)
from socket import error as SocketError
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

KEEPALIVE_INTERVAL = 15   # seconds between keep-alive probes
HEALTHCHECK_PERIOD = 5    # seconds between is_active() checks
# -----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("stayalive")

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


# ---------------------------------------------------------------------------
# The long-running operation that tenacity will retry
# ---------------------------------------------------------------------------
class Disconnected(Exception):
    """Raised from the keep-alive loop when the SSH session dies."""


def run_session() -> None:
    """
    Connect, then block until the session dies or we're told to stop.
    Raises Disconnected (retryable) when the transport drops.
    """
    if _shutdown:
        raise KeyboardInterrupt

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    log.info("Connecting to %s@%s:%d ...", SSH_USER, SSH_HOST, SSH_PORT)
    client.connect(
        hostname=SSH_HOST,
        port=SSH_PORT,
        username=SSH_USER,
        key_filename=str(SSH_KEY),
        allow_agent=False,
        look_for_keys=False,
        timeout=10,
        banner_timeout=10,
        auth_timeout=10,
    )
    log.info("Connected.")

    transport = client.get_transport()
    transport.set_keepalive(KEEPALIVE_INTERVAL)

    try:
        # ---- stay-alive loop ----
        while not _shutdown:
            if not transport.is_active():
                log.warning("Transport is no longer active.")
                raise Disconnected("SSH transport died")
            time.sleep(HEALTHCHECK_PERIOD)

        if _shutdown:
            raise KeyboardInterrupt

    finally:
        try:
            client.close()
        except Exception:
            pass
        log.info("Session closed.")


# ---------------------------------------------------------------------------
# Retry wrapper around the whole session
# ---------------------------------------------------------------------------
@retry(
    retry=retry_if_exception_type(TRANSIENT_ERRORS + (Disconnected,)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before_sleep=before_sleep_log(log, logging.WARNING),
    reraise=True,
)
def run_session_with_retry() -> None:
    run_session()


def main() -> int:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if not SSH_KEY.exists():
        log.error("Private key not found: %s", SSH_KEY)
        return 1

    try:
        run_session_with_retry()
    except AuthenticationException as e:
        log.error("Authentication failed (fatal): %s", e)
        return 2
    except RetryError as e:
        log.error("Gave up: %s", e)
        return 3
    except KeyboardInterrupt:
        log.info("Interrupted. Goodbye.")
        return 0

    log.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
