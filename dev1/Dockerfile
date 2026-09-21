FROM docker.arvancloud.ir/ubuntu:26.10

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client python3-paramiko && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev

COPY --chown=dev:dev dev1/ssh_config     /home/dev/.ssh/config
COPY --chown=dev:dev keys/id_ed25519          /home/dev/.ssh/id_ed25519
COPY --chown=dev:dev keys/id_ed25519.pub      /home/dev/.ssh/id_ed25519.pub
COPY --chown=dev:dev dev1/keepalive.py   /home/dev/keepalive.py
COPY --chown=dev:dev dev1/entrypoint.sh  /home/dev/entrypoint.sh

RUN chmod 700 /home/dev/.ssh && \
    chmod 600 /home/dev/.ssh/config && \
    chmod 600 /home/dev/.ssh/id_ed25519 && \
    chmod 644 /home/dev/.ssh/id_ed25519.pub && \
    chmod 755 /home/dev/keepalive.py && \
    chmod 755 /home/dev/entrypoint.sh

USER dev
WORKDIR /home/dev
