#!/usr/bin/env bash
#
# generate.sh — create the lab SSH keypairs used by docker-ssh-project.
#
# Creates:
#   keys/id_ed25519       developer's private key
#   keys/id_ed25519.pub   developer's public key  (→ jump, internal authorized_keys)
#   keys/id_dev2          developer2's private key
#   keys/id_dev2.pub      developer2's public key (→ jump authorized_keys)
#
# Idempotent: existing keys are left alone unless --force is given.
# The keys/ directory is .gitignore'd — never commit it.

set -euo pipefail

# --- Resolve repo root (works regardless of cwd) -----------------------------
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
KEYS_DIR="$REPO_ROOT/keys"

FORCE=0
for arg in "$@"; do
    case "$arg" in
        -f|--force) FORCE=1 ;;
        -h|--help)
            sed -n '2,12p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            exit 1
            ;;
    esac
done

# --- Preflight ---------------------------------------------------------------
if ! command -v ssh-keygen >/dev/null 2>&1; then
    echo "ERROR: ssh-keygen not found. Install openssh-client." >&2
    exit 1
fi

mkdir -p "$KEYS_DIR"
chmod 700 "$KEYS_DIR"

# --- Helper ------------------------------------------------------------------
gen_key() {
    local name="$1"       # e.g. id_ed25519
    local comment="$2"    # e.g. dev@docker-ssh-project
    local priv="$KEYS_DIR/$name"
    local pub="$priv.pub"

    if [[ -f "$priv" && $FORCE -eq 0 ]]; then
        echo "  [skip] $name already exists (use --force to overwrite)"
        return 0
    fi

    if [[ -f "$priv" && $FORCE -eq 1 ]]; then
        echo "  [overwrite] $name"
        rm -f "$priv" "$pub"
    else
        echo "  [create] $name"
    fi

    # -N "" = no passphrase (fine for a container lab; NOT for production)
    # -t ed25519 = modern, short, fast
    # -C = comment stored in the pub key (shows up in authorized_keys)
    ssh-keygen -t ed25519 -N "" -C "$comment" -f "$priv" >/dev/null

    chmod 600 "$priv"
    chmod 644 "$pub"
}

# --- Generate ----------------------------------------------------------------
echo "Generating lab keys in: $KEYS_DIR"
gen_key id_ed25519 "dev@docker-ssh-project"
gen_key id_dev2    "dev2@docker-ssh-project"

# --- Summary -----------------------------------------------------------------
echo
echo "Done. Files:"
ls -l "$KEYS_DIR"
echo
echo "Fingerprints:"
for pub in "$KEYS_DIR"/*.pub; do
    [[ -f "$pub" ]] || continue
    printf '  %-30s ' "$(basename "$pub")"
    ssh-keygen -lf "$pub" | awk '{print $2}'
done
echo
echo "Next:"
echo "  docker compose up --build"
echo
echo "NOTE: keys/ is gitignored. Never commit the private keys."
