#!/usr/bin/env python3
"""
Step 2: Same passwordless SSH connection as step 1,
but wrapped in a tenacity retry loop that keeps trying forever.
"""

import logging
import signal
import sys
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
    stop_after_delay,
    wait_exponential,
)

# ---------- configuration ----------
SSH_HOST = "jump"
SSH_PORT = 22
SSH_USER = "dev2"
SSH_KEY  = Path.home() / ".ssh" / "id_dev2"

# Retry policy
RETRY_MAX_SECONDS = 0        # 0 = retry forever
RETRY_WAIT_MIN    = 2        # first backoff
RETRY_WAIT_MAX    = 30       # cap
# -----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("connect")

# ---- exceptions we consider "transient" (worth retrying) ----
# Note: AuthenticationException is deliberately EXCLUDED — a bad key
# will never fix itself by retrying. We want that to fail loudly.
TRANSIENT_ERRORS = (
    NoValidConnectionsError,   # host down / wrong port
    SocketError,               # low-level socket failure
    SSHException,              # generic SSH-level failure (banner, kex, ...)
    TimeoutError,              # connect() timeout
    ConnectionError,           # broken pipe / reset / refused
    OSError,                   # catch-all for network-level issues
)

_shutdown = False


def _handle_signal(signum, _frame):
    global _shutdown
    log.info("Received signal %s, shutting down...", signum)
    _shutdown = True


def _stop_policy():
    """Return a tenacity stop strategy honoring --never or a max duration."""
    if RETRY_MAX_SECONDS <= 0:
        from tenacity import stop_never
        return stop_never
    return stop_after_delay(RETRY_MAX_SECONDS)


def connect() -> paramiko.SSHClient:
    """One connection attempt. Raises on failure."""
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
    )
    log.info("Connected.")
    return client


@retry(
    retry=retry_if_exception_type(TRANSIENT_ERRORS),
    wait=wait_exponential(multiplier=1, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
    stop=_stop_policy(),
    before_sleep=before_sleep_log(log, logging.WARNING),
    reraise=True,
)
def connect_with_retry() -> paramiko.SSHClient:
    """Try to connect, retrying transient failures with exponential backoff."""
    if _shutdown:
        # let the outer loop exit cleanly
        raise KeyboardInterrupt
    return connect()


def main() -> int:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if not SSH_KEY.exists():
        log.error("Private key not found: %s", SSH_KEY)
        return 1

    try:
        client = connect_with_retry()
    except AuthenticationException as e:
        # Fatal — don't retry, tell the human.
        log.error("Authentication failed (fix the key, not the network): %s", e)
        return 2
    except RetryError as e:
        log.error("Gave up after retries: %s", e)
        return 3
    except KeyboardInterrupt:
        log.info("Interrupted while retrying.")
        return 0

    try:
        stdin, stdout, stderr = client.exec_command("hostname && whoami")
        log.info("Remote says:\n%s", stdout.read().decode().strip())
    finally:
        client.close()
        log.info("Connection closed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
