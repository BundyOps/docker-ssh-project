FROM docker.arvancloud.ir/ubuntu:26.10

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-client \
        python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev2

COPY --chown=dev2:dev2 dev2/ssh_config      /home/dev2/.ssh/config
COPY --chown=dev2:dev2 dev2/keepalive.py    /home/dev2/keepalive.py
COPY --chown=dev2:dev2 dev2/entrypoint.sh   /home/dev2/entrypoint.sh
COPY --chown=dev2:dev2 dev2/requirements.txt /home/dev2/requirements.txt

RUN chmod 700 /home/dev2/.ssh && \
    chmod 600 /home/dev2/.ssh/config && \
    chmod 755 /home/dev2/entrypoint.sh

USER dev2
WORKDIR /home/dev2

RUN python3 -m venv /home/dev2/.venv && \
    /home/dev2/.venv/bin/pip install --no-cache-dir -r /home/dev2/requirements.txt

ENTRYPOINT ["/home/dev2/entrypoint.sh"]
