# docker-ssh-project

A hands-on Docker Compose lab demonstrating SSH tunneling, SSH agent forwarding, jump hosts, and healthcheck-based startup ordering.

---

## What it does

This project builds a small isolated network with four containers:

- a **jump host** (`jump`) that acts as the only entry point into a private LAN,
- an **internal service** (`internal`) running nginx and sshd, reachable only through `jump`,
- a **developer container** (`developer`) that reaches `internal` by hopping through `jump` using SSH agent forwarding, and
- a **second developer container** (`developer2`) that opens a local SSH tunnel `127.0.0.1:8080 -> internal:80` through `jump`.

It exists to demonstrate, in a reproducible way:

- Docker Compose networking (`companyLAN` vs `worldwideNET`)
- SSH public-key authentication between containers
- SSH agent forwarding (`ssh -A`)
- Programmatic SSH tunnels with `sshtunnel` / `paramiko`
- Correct container startup ordering using `depends_on: condition: service_healthy`

---

## Architecture

                 worldwideNET
   ┌───────────────┐         ┌───────────────┐
   │  developer    │         │  developer2   │
   │  (agent fwd)  │         │  (SSH tunnel) │
   └───────┬───────┘         └───────┬───────┘
           │                         │
           └───────────┬─────────────┘
                       │
                 companyLAN
                       │
                 ┌─────▼─────┐
                 │   jump    │   ← only host allowed into companyLAN
                 │  (sshd)   │
                 └─────┬─────┘
                       │
                 ┌─────▼─────┐
                 │ internal  │   ← nginx:80 + sshd:22
                 └───────────┘

| Container | Role | Networks | Exposed services |
|---|---|---|---|
| `jump` | SSH jump host | `companyLAN`, `worldwideNET` | sshd :22 |
| `internal` | Target service | `companyLAN` | nginx :80, sshd :22 |
| `developer` | Agent-forwarding client | `companyLAN`, `worldwideNET` | — |
| `developer2` | SSH-tunnel client | `companyLAN`, `worldwideNET` | local :8080 |

---

## Quick start

    git clone <your-repo-url> docker-ssh-project
    cd docker-ssh-project

    # Generate the lab SSH keypairs (only needed once)
    ./generate.sh

    # Build and start everything
    docker compose up --build

Then, in a second terminal:

    # Verify the SSH tunnel from developer2 is up
    docker compose exec developer2 curl -s http://127.0.0.1:8080 | head -n 5
    # → <!DOCTYPE html>
    # → <html>
    # → <head>
    # → <title>Welcome to nginx!</title>
    # → ...

    # Verify agent forwarding from developer
    docker compose exec developer \
      ssh -A -o StrictHostKeyChecking=no dev@jump \
      "ssh -o StrictHostKeyChecking=no dev@internal 'hostname; whoami'"
    # → internal
    # → dev

Press `Ctrl+C` to stop. To clean up:

    docker compose down -v

---

## Prerequisites

- **Docker Engine 24+**
- **Docker Compose v2** (the `docker compose` subcommand, not `docker-compose`)
  - Required for `depends_on: condition: service_healthy`
- **Bash** (for `generate.sh` and `entrypoint.sh` scripts)
- *(Optional)* `jq` — for inspecting container health: `docker inspect ... | jq`

The `sshd` containers' healthchecks rely on `netcat-openbsd` (`nc -z localhost 22`), which is installed inside the images.

---

## Usage

### 1. Reach the internal nginx through the tunnel (developer2)

`developer2` opens an SSH tunnel on container-local `127.0.0.1:8080` that forwards to `internal:80`. Anything on port 8080 inside `developer2` reaches the internal nginx.

    docker compose exec developer2 curl -s http://127.0.0.1:8080

Expected output: the default nginx welcome page.

### 2. Hop through the jump host with agent forwarding (developer)

`developer` loads its private key into `ssh-agent` at container start and forwards the agent into the `jump` host. From there, the `jump` host can use that agent to authenticate to `internal` — without the private key ever leaving the developer container.

    docker compose exec developer \
      ssh -A dev@jump "ssh dev@internal 'hostname'"

Expected output:

    internal

### 3. Inspect container health

    docker compose ps

Expected: `jump` and `internal` show `(healthy)`; `developer` and `developer2` show `(running)`.

If `jq` is installed:

    docker inspect --format='{{json .State.Health}}' \
      docker-ssh-project-jump-1 | jq

### 4. View logs

    docker compose logs -f developer2
    docker compose logs -f jump

---

## Configuration

All configuration lives in `docker-compose.yml` and the per-container `ssh_config` / `keepalive.py` files.

### Networks

| Network | Purpose |
|---|---|
| `companyLAN` | Private network containing `jump` and `internal` |
| `worldwideNET` | Public network containing `jump`, `developer`, `developer2` |

### Secrets

The private keys are **not** baked into the images. They are mounted at runtime via Compose secrets:

    secrets:
      ssh_key:
        file: ./keys/id_ed25519
      ssh_key_dev2:
        file: ./keys/id_dev2

These files are generated by `./generate.sh` and are `.gitignore`d.

### Ports and users

| Container | SSH user | Key file | Local port |
|---|---|---|---|
| `jump` | `dev`, `dev2` | `id_ed25519.pub`, `id_dev2.pub` (in `authorized_keys`) | 22 |
| `internal` | `dev` | `id_ed25519.pub` | 22, 80 |
| `developer` | — | `id_ed25519` (loaded into `ssh-agent`) | — |
| `developer2` | — | `id_dev2` | 8080 → `internal:80` |

### Environment variables

| Variable | Used by | Default | Description |
|---|---|---|---|
| `SSH_AUTH_SOCK` | `developer`, `developer2` | set by `entrypoint.sh` | Path to the running `ssh-agent` socket |
| `SSH_AGENT_PID` | `developer`, `developer2` | set by `entrypoint.sh` | PID of the running `ssh-agent` |

### Startup ordering

`developer` and `developer2` declare:

    depends_on:
      jump:
        condition: service_healthy
      internal:
        condition: service_healthy

`jump` and `internal` expose a healthcheck:

    healthcheck:
      test: ["CMD-SHELL", "nc -z localhost 22 || exit 1"]
      interval: 3s
      timeout: 3s
      retries: 20
      start_period: 5s

This is what prevents the `Could not resolve IP address for jump` error that occurs when clients start before the SSH daemon is ready.

---

## Project structure

    docker-ssh-project/
    ├── developer/                 # agent-forwarding client
    │   ├── Dockerfile
    │   ├── entrypoint.sh          # starts ssh-agent, loads key, runs keepalive.py
    │   ├── keepalive.py           # paramiko loop w/ agent forwarding
    │   └── ssh_config
    ├── developer2/                # SSH-tunnel client
    │   ├── Dockerfile
    │   ├── entrypoint.sh          # activates venv, installs key from secret, runs keepalive.py
    │   ├── keepalive.py           # sshtunnel loop -> internal:80
    │   └── ssh_config
    ├── jump/                      # SSH jump host
    │   └── Dockerfile
    ├── internal/                  # nginx + sshd target
    │   └── Dockerfile
    ├── keys/                      # generated keypairs (gitignored)
    │   ├── id_ed25519
    │   ├── id_ed25519.pub
    │   ├── id_dev2
    │   └── id_dev2.pub
    ├── generate.sh                # creates the keypairs above
    ├── docker-compose.yml
    ├── .gitignore
    └── README.md

---

## Troubleshooting

### `Could not resolve IP address for jump` / `Could not establish session to SSH gateway`

The client container started before `jump`'s sshd was ready to accept connections. Make sure:

1. `jump` has a `healthcheck` defined.
2. `developer` and `developer2` use `depends_on: condition: service_healthy`.

`depends_on` alone (without `condition: service_healthy`) only waits for the container to be created — not for sshd to be listening.

### `container jump is unhealthy`

Check the healthcheck logs:

    docker inspect --format='{{json .State.Health}}' \
      docker-ssh-project-jump-1 | jq

Common causes:

- `nc` is not installed in the image (the healthcheck uses `nc -z localhost 22`).
- `start_period` is too short — increase it if sshd takes longer to come up.
- sshd isn't actually listening — check `docker compose logs jump`.

### `Connection closed by ::1 port ... [preauth]` in `jump` / `internal` logs

Harmless. The healthcheck opens a TCP connection to port 22 every few seconds and closes it without completing the SSH handshake. sshd logs every such connection. To silence:

    # in /etc/ssh/sshd_config
    LogLevel ERROR

### `SSH_AUTH_SOCK is not set` in `developer` / `developer2`

The `entrypoint.sh` failed to start `ssh-agent`. Check that:

- `openssh-client` is installed in the image.
- `entrypoint.sh` runs as the correct user (`dev` / `dev2`).
- The `ssh-agent` block in `entrypoint.sh` is present and not behind a failed `&&`.

### Tunnel is up but `curl http://127.0.0.1:8080` returns nothing

The tunnel forwards to `internal:80`. Verify:

- `internal` is on the same network as `jump` (`companyLAN`).
- nginx is actually running inside `internal`: `docker compose exec internal service nginx status` or `docker compose exec internal curl -s http://localhost:80`.

---

## How it works (short version)

- **Networks.** `internal` is only on `companyLAN`. The only way in is through `jump`, which is dual-homed on `companyLAN` and `worldwideNET`. This mirrors a real DMZ / jump-host setup.
- **Auth.** Each container ships with a public key in `authorized_keys` on the destination host. Private keys are mounted at runtime via Compose secrets.
- **Agent forwarding.** `developer`'s `entrypoint.sh` starts `ssh-agent`, adds `id_ed25519`, then runs `keepalive.py`. The script connects to `jump` with `allow_agent=True` and forwards the agent socket so that `jump` can authenticate to `internal` on the developer's behalf.
- **Tunnel.** `developer2`'s `keepalive.py` uses `sshtunnel.SSHTunnelForwarder` to open `127.0.0.1:8080 -> internal:80` via `dev2@jump`. `tenacity` retries with exponential backoff on failure.
- **Startup ordering.** Healthchecks on `jump` and `internal` ensure `developer` / `developer2` only start once SSH is actually accepting connections.

---


