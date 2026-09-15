FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev

COPY --chown=dev:dev dev1/ssh_config    /home/dev/.ssh/config
COPY --chown=dev:dev keys/id_ed25519         /home/dev/.ssh/id_ed25519
COPY --chown=dev:dev keys/id_ed25519.pub     /home/dev/.ssh/id_ed25519.pub

RUN chmod 700 /home/dev/.ssh && \
    chmod 600 /home/dev/.ssh/config && \
    chmod 600 /home/dev/.ssh/id_ed25519 && \
    chmod 644 /home/dev/.ssh/id_ed25519.pub

USER dev
WORKDIR /home/dev
CMD ["sleep", "infinity"]
