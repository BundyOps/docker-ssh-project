FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client python3-paramiko && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev2

COPY --chown=dev2:dev2 dev2/ssh_config     /home/dev2/.ssh/config
COPY --chown=dev2:dev2 keys/id_dev2          /home/dev2/.ssh/id_dev2
COPY --chown=dev2:dev2 keys/id_dev2.pub      /home/dev2/.ssh/id_dev2.pub
COPY --chown=dev2:dev2 dev2/keepalive.py   /home/dev2/keepalive.py
COPY --chown=dev2:dev2 dev2/entrypoint.sh  /home/dev2/entrypoint.sh

RUN chmod 700 /home/dev2/.ssh && \
    chmod 600 /home/dev2/.ssh/config && \
    chmod 600 /home/dev2/.ssh/id_dev2 && \
    chmod 644 /home/dev2/.ssh/id_dev2.pub && \
    chmod 755 /home/dev2/keepalive.py && \
    chmod 755 /home/dev2/entrypoint.sh

USER dev2
WORKDIR /home/dev2
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install "paramiko<4" tenacity sshtunnel
# No ENTRYPOINT, no CMD — compose decides what to run.
# CMD ["sleep", "infinity"]
