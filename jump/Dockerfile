FROM docker.arvancloud.ir/ubuntu:26.10

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        openssh-client \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev  && \
    useradd -m -s /bin/bash dev2

RUN install -d -m 700 -o dev  -g dev  /home/dev/.ssh  && \
    install -d -m 700 -o dev2 -g dev2 /home/dev2/.ssh

COPY --chown=dev:dev   keys/id_ed25519.pub /home/dev/.ssh/authorized_keys
COPY --chown=dev2:dev2 keys/id_dev2.pub    /home/dev2/.ssh/authorized_keys

RUN chmod 600 /home/dev/.ssh/authorized_keys  && \
    chmod 600 /home/dev2/.ssh/authorized_keys

RUN printf '\n\
AllowAgentForwarding yes\n\
PubkeyAuthentication yes\n\
AllowTcpForwarding yes\n\
PermitRootLogin no\n' >> /etc/ssh/sshd_config

EXPOSE 22

CMD ["sh", "-c", "mkdir -p /run/sshd && exec /usr/sbin/sshd -D -e"]
