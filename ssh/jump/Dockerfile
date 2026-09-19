FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev1 && \
    mkdir -p /home/dev1/.ssh /run/sshd && \
    chown -R dev1:dev1 /home/dev1/.ssh && \
    chmod 700 /home/dev1/.ssh

RUN useradd -m -s /bin/bash dev2 && \
    mkdir -p /home/dev2/.ssh && \
    chown -R dev2:dev2 /home/dev2/.ssh && \
    chmod 700 /home/dev2/.ssh

COPY --chown=dev1:dev1 keys/id_ed25519.pub /home/dev1/.ssh/authorized_keys
COPY --chown=dev1:dev1 jump/ssh_config     /home/dev1/.ssh/config
RUN chmod 600 /home/dev1/.ssh/authorized_keys /home/dev1/.ssh/config

COPY --chown=dev2:dev2 keys/id_dev2.pub /home/dev2/.ssh/authorized_keys
COPY --chown=dev2:dev2 jump/ssh_config2     /home/dev2/.ssh/config
RUN chmod 600 /home/dev2/.ssh/authorized_keys /home/dev2/.ssh/config

# Jump's own private key for reaching app-vm on behalf of dev2's tunnel
COPY --chown=dev2:dev2 keys/jump /home/dev2/.ssh/jump
COPY --chown=dev2:dev2 keys/jump.pub /home/dev2/.ssh/jump.pub
RUN chmod 600 /home/dev2/.ssh/jump
RUN chmod 644 /home/dev2/.ssh/jump.pub



RUN printf '\n\
AllowAgentForwarding yes\n\
PubkeyAuthentication yes\n\
AllowTcpForwarding yes\n\
PermitRootLogin no\n' >> /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
