FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client python3-paramiko && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev1

COPY --chown=dev1:dev1 dev1/ssh_config     /home/dev1/.ssh/config
COPY --chown=dev1:dev1 keys/id_ed25519          /home/dev1/.ssh/id_ed25519
COPY --chown=dev1:dev1 keys/id_ed25519.pub      /home/dev1/.ssh/id_ed25519.pub
COPY --chown=dev1:dev1 dev1/keepalive.py   /home/dev1/keepalive.py
COPY --chown=dev1:dev1 dev1/entrypoint.sh  /home/dev1/entrypoint.sh

RUN chmod 700 /home/dev1/.ssh && \
    chmod 600 /home/dev1/.ssh/config && \
    chmod 600 /home/dev1/.ssh/id_ed25519 && \
    chmod 644 /home/dev1/.ssh/id_ed25519.pub && \
    chmod 755 /home/dev1/keepalive.py && \
    chmod 755 /home/dev1/entrypoint.sh

USER dev1
WORKDIR /home/dev1
# No ENTRYPOINT, no CMD — compose decides what to run.
# CMD ["sleep", "infinity"]
