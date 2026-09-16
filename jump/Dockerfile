FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev && \
    mkdir -p /home/dev/.ssh /run/sshd && \
    chown -R dev:dev /home/dev/.ssh && \
    chmod 700 /home/dev/.ssh

RUN useradd -m -s /bin/bash dev2 && \
    mkdir -p /home/dev2/.ssh && \
    chown -R dev2:dev2 /home/dev2/.ssh && \
    chmod 700 /home/dev2/.ssh

COPY --chown=dev:dev keys/id_ed25519.pub /home/dev/.ssh/authorized_keys
COPY --chown=dev2:dev2 keys/id_dev2.pub /home/dev2/.ssh/authorized_keys

RUN chmod 600 /home/dev/.ssh/authorized_keys
RUN chmod 600 /home/dev2/.ssh/authorized_keys

RUN printf '\n\
AllowAgentForwarding yes\n\
PubkeyAuthentication yes\n\
AllowTcpForwarding yes\n\
PermitRootLogin no\n' >> /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
