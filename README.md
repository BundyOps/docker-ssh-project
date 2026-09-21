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


